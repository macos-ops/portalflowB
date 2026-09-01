from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserSubscriptionViewSet

router = DefaultRouter()
router.register(r"subscriptions", UserSubscriptionViewSet, basename="subscriptions")

urlpatterns = [
    path("", include(router.urls)),
]
