from django.conf import settings
from django.db import models


class ClientProfile(models.Model):
    """
    Extra info tied to a User with role=CLIENT.
    Doesn't duplicate login/auth fields — those live on accounts.User already.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
        limit_choices_to={"role": "CLIENT"},
    )
    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_clients",
        limit_choices_to={"role__in": ["ADMIN", "TEAM"]},
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
