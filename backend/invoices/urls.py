from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, paystack_webhook

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoices")

urlpatterns = [
    path("invoices/paystack-webhook/", paystack_webhook, name="paystack-webhook"),
    path("", include(router.urls)),
]