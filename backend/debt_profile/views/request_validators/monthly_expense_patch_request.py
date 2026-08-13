from typing import Literal

from rest_framework.exceptions import ValidationError

from core.request_validator_engine import RequestValidatorEngine
from debt_profile.models import DebtProfile, RecurringExpenseCategory, UtilityType
from debt_profile.serializers.expense_payment_schedule_serializer import ExpensePaymentScheduleSerializer
from debt_profile.serializers.recurring_expense_entry_serializer import RecurringExpenseEntrySerializer
from debt_profile.services.payment_schedule_validation import validate_schedule_positions
from debt_profile.types import RecurringExpenseInput


class MonthlyExpensePatchRequest(RequestValidatorEngine):
    rules = {
        "recurring_expenses": ("list",),
        "payment_schedules": ("list",),
    }
    messages = {
        "recurring_expenses": {"list": "Recurring expenses must be a list."},
        "payment_schedules": {"list": "Payment schedules must be a list."},
    }

    recurring_expenses: list[RecurringExpenseInput] | None = None

    def validate(self) -> None:
        super().validate()

        self._validate_recurring_expenses()
        self._validate_payment_schedules()

    def _validate_recurring_expenses(self) -> None:
        recurring_expenses = self._validated_data.get("recurring_expenses")

        if not isinstance(recurring_expenses, list):
            return

        serializer = RecurringExpenseEntrySerializer(data=recurring_expenses, many=True)

        if not serializer.is_valid():
            raise ValidationError({"recurring_expenses": serializer.errors})

        entries: list[RecurringExpenseInput] = []

        for entry in serializer.validated_data:
            utility_type: UtilityType | Literal[""] = ""

            if entry["utility_type"] != "":
                utility_type = UtilityType(entry["utility_type"])

            entries.append(
                {
                    "source_key": entry["source_key"],
                    "category": RecurringExpenseCategory(entry["category"]),
                    "label": entry["label"],
                    "amount_cents": entry["amount_cents"],
                    "utility_type": utility_type,
                    "includes_internet": entry["includes_internet"],
                    "includes_cable": entry["includes_cable"],
                }
            )

        source_keys = [entry["source_key"] for entry in entries]

        if len(source_keys) != len(set(source_keys)):
            raise ValidationError({"recurring_expenses": ["Source keys must be unique."]})

        includes_internet = any(entry["includes_internet"] is True for entry in entries)
        has_standalone_internet = any(entry["category"] == RecurringExpenseCategory.INTERNET for entry in entries)

        if includes_internet and has_standalone_internet:
            raise ValidationError({"recurring_expenses": ["Internet cannot be both included and standalone."]})

        self._validated_data["recurring_expenses"] = entries
        self.recurring_expenses = entries

    def _validate_payment_schedules(self) -> None:
        schedules = self._validated_data.get("payment_schedules")

        if not isinstance(schedules, list):
            return

        serializer = ExpensePaymentScheduleSerializer(data=schedules, many=True)
        serializer.is_valid(raise_exception=True)
        source_keys = [entry["source_key"] for entry in serializer.validated_data]

        if len(source_keys) != len(set(source_keys)):
            raise ValidationError({"payment_schedules": ["Each expense may have only one payment schedule."]})

        self._validated_data["payment_schedules"] = [dict(entry) for entry in serializer.validated_data]

    def validate_schedule_sources(self, debt_profile: DebtProfile) -> None:
        schedules = self._validated_data.get("payment_schedules")

        if not isinstance(schedules, list):
            return

        recurring_expenses = self.recurring_expenses

        if isinstance(recurring_expenses, list):
            recurring_source_keys = {entry["source_key"] for entry in recurring_expenses}
        else:
            recurring_source_keys = set(
                debt_profile.recurring_expenses.filter(amount_cents__gt=0).values_list("source_key", flat=True)
            )
        debt_source_keys = {
            f"debt:{index}"
            for index, debt in enumerate(debt_profile.debts)
            if int(debt.get("current_payment_cents", 0)) > 0
        }
        allowed_source_keys = recurring_source_keys | debt_source_keys
        invalid_source_keys = {
            str(schedule["source_key"]) for schedule in schedules if schedule["source_key"] not in allowed_source_keys
        }

        if invalid_source_keys:
            raise ValidationError({"payment_schedules": ["Schedules must belong to submitted obligations."]})

        if not validate_schedule_positions(schedules, debt_profile.pay_period_type):
            raise ValidationError({"payment_schedules": ["Select a paycheck available for the current pay frequency."]})
