import uuid
import hashlib
import hmac
import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from notifications.models import Notification

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Invoice
from .serializers import InvoiceSerializer
from .paystack import initialize_transaction, verify_transaction


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "CLIENT":
            return Invoice.objects.filter(client=user)

        return Invoice.objects.filter(project__manager=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_sent(self, request, pk=None):
        invoice = self.get_object()

        if request.user.role not in ["ADMIN", "TEAM"]:
            return Response(
                {"detail": "Only owners/team can send invoices."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if invoice.status != Invoice.Status.DRAFT:
            return Response(
                {
                    "detail": (
                        f"Cannot send an invoice with status "
                        f"'{invoice.status}'. Only DRAFT invoices can be sent."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.status = Invoice.Status.SENT
        invoice.save()

        Notification.objects.create(
            recipient=invoice.client,
            title="New Invoice Sent",
            message=(
                f"Invoice {invoice.invoice_number} for "
                f"{invoice.amount} has been sent to you."
            ),
            notification_type=Notification.Type.INVOICE_SENT,
        )

        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()

        if request.user.role not in ["ADMIN", "TEAM"]:
            return Response(
                {"detail": "Only owners/team can mark invoices as paid."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if invoice.status not in [
            Invoice.Status.SENT,
            Invoice.Status.OVERDUE,
        ]:
            return Response(
                {
                    "detail": (
                        f"Cannot mark an invoice with status "
                        f"'{invoice.status}' as paid. "
                        "It must be SENT or OVERDUE first."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.status = Invoice.Status.PAID
        invoice.save()

        Notification.objects.create(
            recipient=invoice.created_by,
            title="Invoice Paid",
            message=(
                f"Invoice {invoice.invoice_number} "
                "has been marked as paid."
            ),
            notification_type=Notification.Type.INVOICE_PAID,
        )

        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def mark_cancelled(self, request, pk=None):
        invoice = self.get_object()

        if request.user.role not in ["ADMIN", "TEAM"]:
            return Response(
                {"detail": "Only owners/team can cancel invoices."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if invoice.status == Invoice.Status.PAID:
            return Response(
                {"detail": "Cannot cancel an invoice that has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.status = Invoice.Status.CANCELLED
        invoice.save()

        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def initiate_payment(self, request, pk=None):
        invoice = self.get_object()

        if request.user.role != "CLIENT":
            return Response(
                {"detail": "Only the client can pay their own invoice."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if invoice.status not in [
            Invoice.Status.SENT,
            Invoice.Status.OVERDUE,
        ]:
            return Response(
                {
                    "detail": (
                        f"This invoice cannot be paid while it has "
                        f"status '{invoice.status}'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reference = f"INV-{invoice.id}-{uuid.uuid4().hex[:8]}"
        amount_kobo = int(invoice.amount * 100)

        paystack_response = initialize_transaction(
            email=invoice.client.email,
            amount_kobo=amount_kobo,
            reference=reference,
        )

        if not paystack_response.get("status"):
            return Response(
                {
                    "detail": "Failed to initialize payment.",
                    "paystack_error": paystack_response.get("message"),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Save the Paystack reference
        invoice.payment_reference = reference
        invoice.save()

        return Response(
            {
                "authorization_url": paystack_response["data"]["authorization_url"],
                "reference": reference,
            }
        )


@csrf_exempt
def paystack_webhook(request):
    if request.method != "POST":
        return JsonResponse(
            {"detail": "Method not allowed"},
            status=405,
        )

    paystack_signature = request.headers.get(
        "x-paystack-signature",
        "",
    )

    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        request.body,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(
        computed_signature,
        paystack_signature,
    ):
        return JsonResponse(
            {"detail": "Invalid signature"},
            status=400,
        )

    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"detail": "Invalid JSON"},
            status=400,
        )

    if event.get("event") == "charge.success":
        reference = event["data"]["reference"]

        if reference.startswith("INV-"):
            try:
                invoice = Invoice.objects.get(payment_reference=reference)
            except Invoice.DoesNotExist:
                return JsonResponse({"detail": "Invoice not found"}, status=404)

            if invoice.status in [Invoice.Status.SENT, Invoice.Status.OVERDUE]:
                invoice.status = Invoice.Status.PAID
                invoice.save()

                Notification.objects.create(
                    recipient=invoice.created_by,
                    title="Invoice Paid",
                    message=(
                        f"Invoice {invoice.invoice_number} "
                        "has been paid via Paystack."
                    ),
                    notification_type=Notification.Type.INVOICE_PAID,
                )

        elif reference.startswith("SUB-"):
            from subscriptions.models import UserSubscription

            try:
                subscription = UserSubscription.objects.get(payment_reference=reference)
            except UserSubscription.DoesNotExist:
                return JsonResponse({"detail": "Subscription not found"}, status=404)

            if subscription.pending_plan:
                old_plan_name = subscription.plan.name
                subscription.plan = subscription.pending_plan
                subscription.pending_plan = None
                subscription.status = UserSubscription.Status.ACTIVE
                subscription.save()

                Notification.objects.create(
                    recipient=subscription.user,
                    title="Subscription Payment Successful",
                    message=(
                        f"Your plan changed from {old_plan_name} to "
                        f"{subscription.plan.name} after successful payment."
                    ),
                    notification_type=Notification.Type.SUBSCRIPTION_CHANGED,
                )

    return JsonResponse({"status": "ok"})