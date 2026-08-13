import datetime

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.request_validator_engine import RequestValidatorEngine
from debt_profile.serializers.debt_entry_serializer import DebtEntrySerializer
from debt_profile.serializers.expense_payment_schedule_serializer import ExpensePaymentScheduleSerializer
from debt_profile.services.payment_schedule_validation import validate_schedule_positions


class DebtProfilePatchRequest(RequestValidatorEngine):
    rules = {
        "income_per_pay_period_cents": (
            "integer",
            ("min_value", 0),
        ),
        "pay_period_type": ("string",),
        "debts": ("list",),
        "next_pay_date": (
            "nullable",
            "string",
        ),
        "payment_schedules": ("list",),
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
        "next_pay_date": {
            "string": "Next pay date must be a string.",
        },
        "payment_schedules": {"list": "Payment schedules must be a list."},
    }

    def validate(self) -> None:
        super().validate()

        self._validate_pay_period_type()
        self._validate_debts()
        self._validate_next_pay_date()
        self._validate_payment_schedules()

    def _validate_payment_schedules(self) -> None:
        schedules = self._validated_data.get("payment_schedules")

        if not isinstance(schedules, list):
            return

        serializer = ExpensePaymentScheduleSerializer(data=schedules, many=True)
        serializer.is_valid(raise_exception=True)
        source_keys = [entry["source_key"] for entry in serializer.validated_data]

        if len(source_keys) != len(set(source_keys)):
            raise ValidationError({"payment_schedules": ["Each debt may have only one payment schedule."]})

        self._validated_data["payment_schedules"] = [dict(entry) for entry in serializer.validated_data]

    def _validate_pay_period_type(self) -> None:
        pay_period_type = self._validated_data.get("pay_period_type")

        if not isinstance(pay_period_type, str):
            return

        valid_types = {"WEEKLY", "BIWEEKLY", "MONTHLY", ""}

        if pay_period_type not in valid_types:
            raise ValidationError({"pay_period_type": ["Select a valid pay period type."]})

    def validate_schedule_positions(self, current_pay_period_type: str) -> None:
        schedules = self._validated_data.get("payment_schedules")

        if not isinstance(schedules, list):
            return

        pay_period_type = self._validated_data.get("pay_period_type", current_pay_period_type)

        if isinstance(pay_period_type, str) and not validate_schedule_positions(schedules, pay_period_type):
            raise ValidationError({"payment_schedules": ["Select a paycheck available for the current pay frequency."]})

    def _validate_debts(self) -> None:
        debts = self._validated_data.get("debts")

        if not isinstance(debts, list):
            return

        serializer = DebtEntrySerializer(data=debts, many=True)

        if not serializer.is_valid():
            raise ValidationError({"debts": serializer.errors})

        self._validated_data["debts"] = [dict(entry) for entry in serializer.validated_data]

    def _validate_next_pay_date(self) -> None:
        raw = self._validated_data.get("next_pay_date")

        if raw is None:
            return

        try:
            parsed = datetime.date.fromisoformat(raw)
        except ValueError:
            raise ValidationError({"next_pay_date": ["Enter a valid date."]}) from None

        today = timezone.localdate()

        if parsed < today:
            raise ValidationError({"next_pay_date": ["Next pay date must not be in the past."]})
