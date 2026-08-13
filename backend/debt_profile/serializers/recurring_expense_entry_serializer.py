from rest_framework import serializers

from debt_profile.models import RecurringExpenseCategory, UtilityType


class RecurringExpenseEntrySerializer(serializers.Serializer):
    source_key = serializers.CharField(max_length=150)
    category = serializers.ChoiceField(choices=RecurringExpenseCategory.choices)
    label = serializers.CharField(max_length=150)
    amount_cents = serializers.IntegerField(min_value=0, max_value=2147483647)
    utility_type = serializers.ChoiceField(choices=UtilityType.choices, allow_blank=True, required=False, default="")
    includes_internet = serializers.BooleanField(required=False, default=False)
    includes_cable = serializers.BooleanField(required=False, default=False)

    def validate(self, attributes: dict[str, object]) -> dict[str, object]:
        category = attributes["category"]
        utility_type = attributes["utility_type"]
        includes_internet = attributes["includes_internet"]
        includes_cable = attributes["includes_cable"]
        source_key = attributes["source_key"]

        expected_source_keys = {
            RecurringExpenseCategory.RENT_OR_MORTGAGE: "rent_or_mortgage",
            RecurringExpenseCategory.UTILITIES: "utilities",
            RecurringExpenseCategory.FOOD: "food",
            RecurringExpenseCategory.INTERNET: "internet",
            RecurringExpenseCategory.PHONE: "phone",
            RecurringExpenseCategory.CAR_PAYMENT: "car_payment",
            RecurringExpenseCategory.INSURANCE: "insurance",
        }

        if category == RecurringExpenseCategory.UTILITIES and utility_type == "":
            raise serializers.ValidationError({"utility_type": "Select a utility type."})

        if category != RecurringExpenseCategory.UTILITIES and (
            utility_type != "" or includes_internet is True or includes_cable is True
        ):
            raise serializers.ValidationError({"category": "Included services belong to the Utilities expense."})

        if category == RecurringExpenseCategory.MISC and not str(source_key).startswith("misc:"):
            raise serializers.ValidationError({"source_key": "Other expenses require a stable misc source key."})

        expected_source_key = expected_source_keys.get(category)

        if expected_source_key is not None and source_key != expected_source_key:
            raise serializers.ValidationError({"source_key": "The source key does not match the expense category."})

        return attributes
