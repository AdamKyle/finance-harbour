from rest_framework import serializers

from debt_profile.models import MonthlyExpense


class MonthlyExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyExpense
        fields = [
            "rent_or_mortgage_cents",
            "water_cents",
            "electricity_cents",
            "food_cents",
            "internet_cents",
            "phone_cents",
            "car_payment_cents",
            "insurance_cents",
            "misc_expenses",
        ]
        read_only_fields = [
            "rent_or_mortgage_cents",
            "water_cents",
            "electricity_cents",
            "food_cents",
            "internet_cents",
            "phone_cents",
            "car_payment_cents",
            "insurance_cents",
            "misc_expenses",
        ]
