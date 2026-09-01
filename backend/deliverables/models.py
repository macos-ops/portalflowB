from django.conf import settings
from django.db import models


class Deliverable(models.Model):
    class Status(models.TextChoices):
        AWAITING_REVIEW = "AWAITING_REVIEW", "Awaiting Review"
        APPROVED = "APPROVED", "Approved"
        CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="deliverables",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AWAITING_REVIEW,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_deliverables",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.project.title})"


class Asset(models.Model):
    deliverable = models.ForeignKey(
        Deliverable,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    file = models.FileField(upload_to="deliverables/%Y/%m/")
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_assets",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name