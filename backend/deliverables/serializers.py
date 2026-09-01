from rest_framework import serializers
from .models import Deliverable, Asset


class DeliverableSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Deliverable
        fields = [
            "id",
            "project",
            "project_title",
            "title",
            "description",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class AssetSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.username", read_only=True)
    file_name = serializers.CharField(read_only=True)

    class Meta:
        model = Asset
        fields = ["id", "deliverable", "file", "file_name", "uploaded_by", "uploaded_by_name", "uploaded_at"]
        read_only_fields = ["uploaded_by", "uploaded_at"]
