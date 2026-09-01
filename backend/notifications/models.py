from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        INVOICE_SENT = "INVOICE_SENT", "Invoice Sent"
        INVOICE_PAID = "INVOICE_PAID", "Invoice Paid"
        INVOICE_OVERDUE = "INVOICE_OVERDUE", "Invoice Overdue"
        DELIVERABLE_APPROVED = "DELIVERABLE_APPROVED", "Deliverable Approved"
        CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"
        NEW_COMMENT = "NEW_COMMENT", "New Comment"
        SUBSCRIPTION_CHANGED = "SUBSCRIPTION_CHANGED", "Subscription Changed"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"
