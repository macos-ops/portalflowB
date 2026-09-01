import uuid
from notifications.models import Notification
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserSubscription, SubscriptionPlan
from .serializers import UserSubscriptionSerializer
from invoices.paystack import initialize_transaction


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        subscription = UserSubscription.objects.filter(user=request.user).first()
        if not subscription:
            return Response({"detail": "No active subscription."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSubscriptionSerializer(subscription).data)

    @action(detail=True, methods=["post"])
    def change_plan(self, request, pk=None):
        subscription = self.get_object()
        new_plan_id = request.data.get("plan")

        if not new_plan_id:
            return Response({"detail": "Missing 'plan' id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "Plan not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        old_plan_name = subscription.plan.name
        subscription.plan = new_plan
        subscription.save()

        Notification.objects.create(
            recipient=subscription.user,
            title="Subscription Changed",
            message=f"Your plan changed from {old_plan_name} to {new_plan.name}.",
            notification_type=Notification.Type.SUBSCRIPTION_CHANGED,
        )

        return Response(UserSubscriptionSerializer(subscription).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        subscription = self.get_object()

        if subscription.status == UserSubscription.Status.CANCELLED:
            return Response({"detail": "Subscription is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = UserSubscription.Status.CANCELLED
        subscription.save()

        Notification.objects.create(
            recipient=subscription.user,
            title="Subscription Cancelled",
            message=f"Your {subscription.plan.name} subscription has been cancelled.",
            notification_type=Notification.Type.SUBSCRIPTION_CHANGED,
        )

        return Response(UserSubscriptionSerializer(subscription).data)

    @action(detail=True, methods=["post"])
    def initiate_payment(self, request, pk=None):
        subscription = self.get_object()
        new_plan_id = request.data.get("plan")

        if not new_plan_id:
            return Response({"detail": "Missing 'plan' id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "Plan not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        amount = (
            new_plan.yearly_price
            if subscription.billing_cycle == UserSubscription.BillingCycle.YEARLY
            else new_plan.monthly_price
        )

        reference = f"SUB-{subscription.id}-{uuid.uuid4().hex[:8]}"
        amount_kobo = int(amount * 100)

        paystack_response = initialize_transaction(
            email=subscription.user.email,
            amount_kobo=amount_kobo,
            reference=reference,
        )

        if not paystack_response.get("status"):
            return Response(
                {"detail": "Failed to initialize payment.", "paystack_error": paystack_response.get("message")},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        subscription.payment_reference = reference
        subscription.pending_plan = new_plan
        subscription.save()

        return Response({
            "authorization_url": paystack_response["data"]["authorization_url"],
            "reference": reference,
        })