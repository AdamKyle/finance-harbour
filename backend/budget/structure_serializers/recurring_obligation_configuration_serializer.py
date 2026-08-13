from rest_framework import serializers


class RecurringObligationConfigurationSerializer(serializers.Serializer):
    pay_period_type = serializers.CharField()
    representative_date = serializers.DateField()
