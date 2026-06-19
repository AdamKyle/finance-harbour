from rest_framework import serializers


class MiscExpenseEntrySerializer(serializers.Serializer):
    label = serializers.CharField()
    amount_cents = serializers.IntegerField(min_value=0)


class MonthlyExpenseWriteSerializer(serializers.Serializer):
    rent_or_mortgage_cents = serializers.IntegerField(min_value=0, required=False)
    water_cents = serializers.IntegerField(min_value=0, required=False)
    electricity_cents = serializers.IntegerField(min_value=0, required=False)
    food_cents = serializers.IntegerField(min_value=0, required=False)
    internet_cents = serializers.IntegerField(min_value=0, required=False)
    phone_cents = serializers.IntegerField(min_value=0, required=False)
    car_payment_cents = serializers.IntegerField(min_value=0, required=False)
    insurance_cents = serializers.IntegerField(min_value=0, required=False)
    misc_expenses = serializers.ListField(
        child=MiscExpenseEntrySerializer(),
        required=False,
    )
