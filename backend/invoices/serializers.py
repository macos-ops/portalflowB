from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    client_name = serializers.CharField(source="client.username", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "project",
            "project_title",
            "client",
            "client_name",
            "invoice_number",
            "amount",
            "status",
            "due_date",
            "notes",
            "is_overdue",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_by", "created_at", "updated_at"]
        