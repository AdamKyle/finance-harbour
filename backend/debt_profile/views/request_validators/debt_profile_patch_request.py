from rest_framework.exceptions import ValidationError

from core.request_validator_engine import RequestValidatorEngine
from debt_profile.serializers.debt_entry_serializer import DebtEntrySerializer


class DebtProfilePatchRequest(RequestValidatorEngine):
    rules = {
        "income_per_pay_period_cents": (
            "integer",
            ("min_value", 0),
        ),
        "pay_period_type": ("string",),
        "debts": ("list",),
    }
    messages = {
        "income_per_pay_period_cents": {
            "integer": "Income must be an integer.",
            "min_value": "Income must be zero or more.",
        },
        "pay_period_type": {
            "string": "Pay period type must be a string.",
        },
        "debts": {
            "list": "Debts must be a list.",
        },
    }

    def validate(self) -> None:
        super().validate()

        self._validate_pay_period_type()
        self._validate_debts()

    def _validate_pay_period_type(self) -> None:
        pay_period_type = self._validated_data.get("pay_period_type")

        if not isinstance(pay_period_type, str):
            return

        valid_types = {"WEEKLY", "BIWEEKLY", "MONTHLY", ""}

        if pay_period_type not in valid_types:
            raise ValidationError({"pay_period_type": ["Select a valid pay period type."]})

    def _validate_debts(self) -> None:
        debts = self._validated_data.get("debts")

        if not isinstance(debts, list):
            return

        serializer = DebtEntrySerializer(data=debts, many=True)

        if not serializer.is_valid():
            raise ValidationError({"debts": serializer.errors})
