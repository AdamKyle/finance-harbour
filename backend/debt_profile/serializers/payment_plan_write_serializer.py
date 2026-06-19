from rest_framework import serializers


class PaymentPlanWriteSerializer(serializers.Serializer):
    extra_payment_cents = serializers.IntegerField(min_value=0, required=False)
    spending_payment_percentage_basis_points = serializers.IntegerField(min_value=0, required=False)
