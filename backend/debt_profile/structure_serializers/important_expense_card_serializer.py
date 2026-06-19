from rest_framework import serializers


class ImportantExpenseCardSerializer(serializers.Serializer):
    key = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    amount_cents = serializers.IntegerField(read_only=True)
    selected = serializers.BooleanField(read_only=True)
