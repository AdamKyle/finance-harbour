from rest_framework import serializers

from debt_profile.models import DebtProfile


class DebtProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtProfile
        fields = ["income_per_pay_period_cents", "pay_period_type", "debts"]
        read_only_fields = ["income_per_pay_period_cents", "pay_period_type", "debts"]
