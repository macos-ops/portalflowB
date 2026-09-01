from django.contrib import admin
from .models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "managed_by",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )