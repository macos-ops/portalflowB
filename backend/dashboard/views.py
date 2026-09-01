from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from projects.models import Project
from deliverables.models import Deliverable
from invoices.models import Invoice
from notifications.models import Notification


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == "CLIENT":
            projects = Project.objects.filter(client__user=user)
            invoices = Invoice.objects.filter(client=user)
            deliverables = Deliverable.objects.filter(project__client__user=user)
            notifications = Notification.objects.filter(recipient=user).order_by("-created_at")[:5]

            data = {
                "role": "CLIENT",
                "stats": {
                    "active_projects": projects.exclude(status__in=["COMPLETED", "CANCELLED"]).count(),
                    "pending_deliverables": deliverables.filter(
                        status__in=["AWAITING_REVIEW", "CHANGES_REQUESTED"]
                    ).count(),
                    "unpaid_invoices": invoices.filter(status__in=["SENT", "OVERDUE"]).count(),
                },
                "recent_notifications": [
                    {
                        "id": n.id,
                        "title": n.title,
                        "message": n.message,
                        "notification_type": n.notification_type,
                        "is_read": n.is_read,
                        "created_at": n.created_at,
                    }
                    for n in notifications
                ],
            }
            return Response(data)

        # OWNER / TEAM DASHBOARD
        projects = Project.objects.filter(manager=user)
        invoices = Invoice.objects.filter(project__manager=user)
        deliverables = Deliverable.objects.filter(project__manager=user)
        notifications = Notification.objects.filter(recipient=user).order_by("-created_at")[:5]

        revenue = invoices.filter(status=Invoice.Status.PAID).aggregate(total=Sum("amount"))["total"] or 0

        data = {
            "role": user.role,
            "stats": {
                "total_clients": projects.values("client__user").distinct().count(),
                "active_projects": projects.exclude(status__in=["COMPLETED", "CANCELLED"]).count(),
                "pending_deliverables": deliverables.filter(
                    status__in=["AWAITING_REVIEW", "CHANGES_REQUESTED"]
                ).count(),
                "unpaid_invoices": invoices.filter(status__in=["SENT", "OVERDUE"]).count(),
                "total_revenue": str(revenue),
            },
            "recent_notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "notification_type": n.notification_type,
                    "is_read": n.is_read,
                    "created_at": n.created_at,
                }
                for n in notifications
            ],
        }
        return Response(data)