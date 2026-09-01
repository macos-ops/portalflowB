from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "manager",
        "status",
        "budget",
        "deadline",
    )

    list_filter = (
        "status",
        "manager",
    )

    search_fields = (
        "title",
        "client__user__username",
    )

    ordering = ("-created_at",)