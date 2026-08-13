from rest_framework import serializers


class PaydayProgressSerializer(serializers.Serializer):
    bill_count = serializers.IntegerField(min_value=0)
    reviewed_bill_count = serializers.IntegerField(min_value=0)
    paid_bill_count = serializers.IntegerField(min_value=0)
    scheduled_bill_count = serializers.IntegerField(min_value=0)
    missed_bill_count = serializers.IntegerField(min_value=0)
    payment_completion_percentage = serializers.FloatField(allow_null=True)
    payment_completion_status = serializers.CharField()
    overall_reconciliation_status = serializers.CharField()
