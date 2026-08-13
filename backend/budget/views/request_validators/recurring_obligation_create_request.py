from rest_framework.exceptions import ValidationError

from core.request_validator_engine import RequestValidatorEngine
from debt_profile.serializers.expense_payment_schedule_serializer import ExpensePaymentScheduleSerializer
from debt_profile.services.payment_schedule_validation import (
    validate_new_schedule_funding_positions,
    validate_schedule_positions,
)


class RecurringObligationCreateRequest(RequestValidatorEngine):
    rules = {
        "kind": ("required", "string", ("choices", {"BILL", "DEBT"})),
        "label": ("required", "string", ("max_length", 150)),
        "is_required": ("required", "boolean"),
        "payment_schedule": ("required", "dict"),
        "amount_cents": ("integer", ("min_value", 1), ("max_value", 2147483647)),
        "current_balance_cents": ("integer", ("min_value", 0), ("max_value", 2147483647)),
        "minimum_payment_cents": ("integer", ("min_value", 1), ("max_value", 2147483647)),
        "current_payment_cents": ("integer", ("min_value", 1), ("max_value", 2147483647)),
    }

    def validate(self) -> None:
        super().validate()

        if not str(self._validated_data["label"]).strip():
            raise ValidationError({"label": ["Enter a payment name."]})

        self._validate_kind_fields()
        self._validate_schedule()

    def validate_schedule_position(self, pay_period_type: str) -> None:
        schedule = self._validated_data["payment_schedule"]

        if not validate_schedule_positions([schedule], pay_period_type):
            raise ValidationError({"payment_schedule": ["Select a paycheck available for the current pay frequency."]})

    def _validate_kind_fields(self) -> None:
        kind = self._validated_data["kind"]
        bill_fields = {"amount_cents"}
        debt_fields = {"current_balance_cents", "minimum_payment_cents", "current_payment_cents"}

        if kind == "BILL":
            if "amount_cents" not in self._validated_data:
                raise ValidationError({"amount_cents": ["Enter a recurring amount."]})

            if debt_fields & self.request_data.keys():
                raise ValidationError({"kind": ["Bill requests cannot contain debt fields."]})

            return

        missing_fields = debt_fields - self._validated_data.keys()

        if missing_fields:
            raise ValidationError({field: ["This field is required."] for field in missing_fields})

        if bill_fields & self.request_data.keys():
            raise ValidationError({"kind": ["Debt requests cannot contain bill fields."]})

    def _validate_schedule(self) -> None:
        submitted_schedule = self._validated_data["payment_schedule"]
        serializer = ExpensePaymentScheduleSerializer(data={"source_key": "pending", **submitted_schedule})
        serializer.is_valid(raise_exception=True)
        schedule = dict(serializer.validated_data)
        schedule.pop("source_key")

        if not validate_new_schedule_funding_positions([schedule]):
            raise ValidationError({"payment_schedule": ["Select the paycheck that will fund this payment."]})

        self._validated_data["payment_schedule"] = schedule
