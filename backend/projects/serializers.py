from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.user.username",
        read_only=True,
    )

    manager_name = serializers.CharField(
        source="manager.username",
        read_only=True,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "client",
            "client_name",
            "manager",
            "manager_name",
            "status",
            "budget",
            "start_date",
            "deadline",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
        ]
