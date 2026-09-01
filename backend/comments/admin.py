from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "deliverable", "created_at")
    search_fields = ("body", "user__username")
