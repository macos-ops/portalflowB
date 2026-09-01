from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "monthly_price", "yearly_price", "max_clients", "max_projects", "is_active"]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "id",
            "user",
            "plan",
            "plan_name",
            "billing_cycle",
            "status",
            "start_date",
            "end_date",
            "stripe_subscription_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "status", "start_date", "created_at", "updated_at"]
