from rest_framework import viewsets, permissions
from .models import ClientProfile
from .serializers import ClientProfileSerializer


class ClientProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "CLIENT":
            # Clients only ever see their own profile
            return ClientProfile.objects.filter(user=user)

        # Admins and Team members see only clients they manage
        return ClientProfile.objects.filter(managed_by=user)