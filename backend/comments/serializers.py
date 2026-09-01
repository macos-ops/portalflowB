from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "deliverable", "user", "username", "body", "created_at"]
        read_only_fields = ["user", "created_at"]
