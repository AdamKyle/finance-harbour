from rest_framework import serializers

from debt_profile.models import PaymentPlan


class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = [
            "extra_payment_cents",
            "spending_payment_percentage_basis_points",
            "plan_data",
            "is_active",
        ]
        read_only_fields = [
            "extra_payment_cents",
            "spending_payment_percentage_basis_points",
            "plan_data",
            "is_active",
        ]
