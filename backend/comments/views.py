from notifications.models import Notification
from rest_framework import viewsets, permissions
from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "CLIENT":
            return Comment.objects.filter(deliverable__project__client__user=user)

        return Comment.objects.filter(deliverable__project__manager=user)

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)

        deliverable = comment.deliverable
        project = deliverable.project

        # Notify whoever didn't write the comment
        if self.request.user.role == "CLIENT":
            recipient = project.manager
        else:
            recipient = project.client.user

        Notification.objects.create(
            recipient=recipient,
            title="New Comment",
            message=f"{self.request.user.username} commented on '{deliverable.title}'.",
            notification_type=Notification.Type.NEW_COMMENT,
        )