from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import DeliverableViewSet, AssetViewSet

router = DefaultRouter()
router.register(r"deliverables", DeliverableViewSet, basename="deliverables")
router.register(r"assets", AssetViewSet, basename="assets")

urlpatterns = [
    path("", include(router.urls)),
]