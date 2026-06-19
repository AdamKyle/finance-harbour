from rest_framework.exceptions import ValidationError

from core.request_validator_engine import RequestValidatorEngine
from debt_profile.serializers.misc_expense_entry_serializer import MiscExpenseEntrySerializer


class MonthlyExpensePatchRequest(RequestValidatorEngine):
    rules = {
        "rent_or_mortgage_cents": (
            "integer",
            ("min_value", 0),
        ),
        "water_cents": (
            "integer",
            ("min_value", 0),
        ),
        "electricity_cents": (
            "integer",
            ("min_value", 0),
        ),
        "food_cents": (
            "integer",
            ("min_value", 0),
        ),
        "internet_cents": (
            "integer",
            ("min_value", 0),
        ),
        "phone_cents": (
            "integer",
            ("min_value", 0),
        ),
        "car_payment_cents": (
            "integer",
            ("min_value", 0),
        ),
        "insurance_cents": (
            "integer",
            ("min_value", 0),
        ),
        "misc_expenses": ("list",),
    }
    messages = {
        "rent_or_mortgage_cents": {
            "integer": "Rent or mortgage must be an integer.",
            "min_value": "Rent or mortgage must be zero or more.",
        },
        "water_cents": {
            "integer": "Water must be an integer.",
            "min_value": "Water must be zero or more.",
        },
        "electricity_cents": {
            "integer": "Electricity must be an integer.",
            "min_value": "Electricity must be zero or more.",
        },
        "food_cents": {
            "integer": "Food must be an integer.",
            "min_value": "Food must be zero or more.",
        },
        "internet_cents": {
            "integer": "Internet must be an integer.",
            "min_value": "Internet must be zero or more.",
        },
        "phone_cents": {
            "integer": "Phone must be an integer.",
            "min_value": "Phone must be zero or more.",
        },
        "car_payment_cents": {
            "integer": "Car payment must be an integer.",
            "min_value": "Car payment must be zero or more.",
        },
        "insurance_cents": {
            "integer": "Insurance must be an integer.",
            "min_value": "Insurance must be zero or more.",
        },
        "misc_expenses": {
            "list": "Misc expenses must be a list.",
        },
    }

    def validate(self) -> None:
        super().validate()

        self._validate_misc_expenses()

    def _validate_misc_expenses(self) -> None:
        misc_expenses = self._validated_data.get("misc_expenses")

        if not isinstance(misc_expenses, list):
            return

        serializer = MiscExpenseEntrySerializer(data=misc_expenses, many=True)

        if not serializer.is_valid():
            raise ValidationError({"misc_expenses": serializer.errors})
