from rest_framework import serializers


class RecurringObligationResultSerializer(serializers.Serializer):
    kind = serializers.CharField()
    source_key = serializers.CharField()
    first_effective_budget_period_id = serializers.IntegerField()
