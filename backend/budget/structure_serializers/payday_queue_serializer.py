from rest_framework import serializers

from budget.structure_serializers.payday_queue_period_serializer import PaydayQueuePeriodSerializer


class PaydayQueueSerializer(serializers.Serializer):
    effective_date = serializers.DateField()
    unresolved_count = serializers.IntegerField(min_value=0)
    unresolved_periods = PaydayQueuePeriodSerializer(many=True)
    oldest_unresolved_period = PaydayQueuePeriodSerializer(allow_null=True)
    next_future_pay_date = serializers.DateField(allow_null=True)
