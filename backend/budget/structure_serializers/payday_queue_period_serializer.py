from rest_framework import serializers


class PaydayQueuePeriodSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    pay_date = serializers.DateField()
    payday_reconciliation_status = serializers.CharField()
    pay_cheque_review_status = serializers.CharField()
