from rest_framework import serializers


class MiscExpenseEntrySerializer(serializers.Serializer):
    label = serializers.CharField()
    amount_cents = serializers.IntegerField(min_value=0)
