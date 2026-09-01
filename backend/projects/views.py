from rest_framework import permissions, viewsets

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins and Team members only see projects they manage
        if user.role in ["ADMIN", "TEAM"]:
            return Project.objects.filter(manager=user)

        # Clients only see their own projects
        return Project.objects.filter(client__user=user)