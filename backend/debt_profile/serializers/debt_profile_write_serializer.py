from rest_framework import serializers


class DebtEntrySerializer(serializers.Serializer):
    label = serializers.CharField()
    current_balance_cents = serializers.IntegerField(min_value=0)
    interest_rate_basis_points = serializers.IntegerField(min_value=0)
    minimum_payment_cents = serializers.IntegerField(min_value=0)
    current_payment_cents = serializers.IntegerField(min_value=0)


class DebtProfileWriteSerializer(serializers.Serializer):
    income_per_pay_period_cents = serializers.IntegerField(min_value=0, required=False)
    pay_period_type = serializers.CharField(required=False, allow_blank=True)
    debts = serializers.ListField(child=DebtEntrySerializer(), required=False)

    def validate_pay_period_type(self, value: str) -> str:
        valid_types = {"WEEKLY", "BIWEEKLY", "MONTHLY"}
        if value and value not in valid_types:
            raise serializers.ValidationError("Invalid pay period type.")
        return value
