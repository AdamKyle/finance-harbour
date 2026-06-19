from rest_framework import serializers


class DebtEntrySerializer(serializers.Serializer):
    label = serializers.CharField()
    current_balance_cents = serializers.IntegerField(min_value=0)
    interest_rate_basis_points = serializers.IntegerField(min_value=0)
    minimum_payment_cents = serializers.IntegerField(min_value=0)
    current_payment_cents = serializers.IntegerField(min_value=0)
