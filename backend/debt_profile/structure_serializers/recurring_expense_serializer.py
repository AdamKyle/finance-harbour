from rest_framework import serializers

from debt_profile.models import RecurringExpense


class RecurringExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringExpense
        fields = [
            "source_key",
            "category",
            "label",
            "amount_cents",
            "utility_type",
            "includes_internet",
            "includes_cable",
        ]
        read_only_fields = fields
