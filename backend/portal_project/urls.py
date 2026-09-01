"""
URL configuration for portal_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API
    path("api/", include("clients.urls")),
    path("api/", include("projects.urls")),
    path("api/", include("deliverables.urls")),
    path("api/", include("comments.urls")),
    path("api/", include("invoices.urls")),
    path("api/", include("notifications.urls")),
    path("api/", include("subscriptions.urls")),
    path("api/", include("dashboard.urls")),

    # JWT auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)