from django.contrib import admin
from .models import Deliverable


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "project__title")
