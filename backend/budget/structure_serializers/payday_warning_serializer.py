from rest_framework import serializers


class PaydayWarningSerializer(serializers.Serializer):
    warning_type = serializers.CharField()
    affected_period_id = serializers.IntegerField(min_value=1)
    affected_pay_date = serializers.DateField()
    amount_cents = serializers.IntegerField(allow_null=True)
    important_titles = serializers.ListField(child=serializers.CharField())
    severity = serializers.CharField()
