from rest_framework import serializers


class PaydayDebtBalanceCheckSerializer(serializers.Serializer):
    source_key = serializers.CharField()
    title = serializers.CharField()
    expected_balance_cents = serializers.IntegerField(allow_null=True, min_value=0)
    actual_balance_cents = serializers.IntegerField(allow_null=True, min_value=0)
    review_status = serializers.CharField()
    variance_cents = serializers.IntegerField(allow_null=True)
    variance_percentage = serializers.FloatField(allow_null=True)
    previous_confirmed_balance_cents = serializers.IntegerField(allow_null=True, min_value=0)
    movement_from_previous_percentage = serializers.FloatField(allow_null=True)
    is_uncertain = serializers.BooleanField()
