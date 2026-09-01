from notifications.models import Notification
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Deliverable, Asset
from .serializers import DeliverableSerializer, AssetSerializer


class DeliverableViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "CLIENT":
            return Deliverable.objects.filter(project__client__user=user)

        return Deliverable.objects.filter(project__manager=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        deliverable = self.get_object()

        if request.user.role != "CLIENT":
            return Response(
                {"detail": "Only clients can approve deliverables."},
                status=status.HTTP_403_FORBIDDEN,
            )

        deliverable.status = Deliverable.Status.APPROVED
        deliverable.save()

        Notification.objects.create(
            recipient=deliverable.created_by,
            title="Deliverable Approved",
            message=f"'{deliverable.title}' has been approved by the client.",
            notification_type=Notification.Type.DELIVERABLE_APPROVED,
        )

        return Response(DeliverableSerializer(deliverable).data)

    @action(detail=True, methods=["post"])
    def request_changes(self, request, pk=None):
        deliverable = self.get_object()

        if request.user.role != "CLIENT":
            return Response(
                {"detail": "Only clients can request changes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        deliverable.status = Deliverable.Status.CHANGES_REQUESTED
        deliverable.save()

        Notification.objects.create(
            recipient=deliverable.created_by,
            title="Changes Requested",
            message=f"The client requested changes on '{deliverable.title}'.",
            notification_type=Notification.Type.CHANGES_REQUESTED,
        )

        return Response(DeliverableSerializer(deliverable).data)


class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        if user.role == "CLIENT":
            return Asset.objects.filter(deliverable__project__client__user=user)

        return Asset.objects.filter(deliverable__project__manager=user)

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get("file")
        serializer.save(
            uploaded_by=self.request.user,
            file_name=uploaded_file.name if uploaded_file else "",
        )