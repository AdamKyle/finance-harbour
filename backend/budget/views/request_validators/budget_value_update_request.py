import datetime

from rest_framework.exceptions import ValidationError

from budget.enums import BudgetValueField
from core.request_validator_engine import RequestValidatorEngine


class BudgetValueUpdateRequest(RequestValidatorEngine):
    rules = {
        "field": (
            "required",
            "string",
            (
                "choices",
                set(BudgetValueField),
            ),
        ),
        "source_key": ("nullable", "string", ("max_length", 150)),
        "amount_cents": ("nullable", "integer"),
        "going_forward": ("nullable", "boolean"),
        "pay_date": ("nullable", "string"),
    }

    def validate(self) -> None:
        super().validate()

        field = BudgetValueField(self.validated_data["field"])
        self.validated_data["field"] = field

        if field == BudgetValueField.PAY_DATE:
            raw_pay_date = self.validated_data.get("pay_date")

            if raw_pay_date is None:
                raise ValidationError({"pay_date": ["Pay date is required."]})

            try:
                self.validated_data["pay_date"] = datetime.date.fromisoformat(raw_pay_date)
            except ValueError:
                raise ValidationError({"pay_date": ["Enter a valid date."]}) from None

            return

        amount_cents = self.validated_data.get("amount_cents")

        if amount_cents is None:
            raise ValidationError({"amount_cents": ["Amount is required."]})

        if self.validated_data.get("going_forward") is None:
            raise ValidationError({"going_forward": ["Going forward is required."]})

        if amount_cents < -2147483648 or amount_cents > 2147483647:
            raise ValidationError({"amount_cents": ["This amount is outside the supported range."]})

        if field == BudgetValueField.LINE_ITEM and not self.validated_data.get("source_key"):
            raise ValidationError({"source_key": ["A source key is required for a line item."]})

        if field in {BudgetValueField.LINE_ITEM, BudgetValueField.PAY_CHEQUE} and amount_cents < 0:
            raise ValidationError({"amount_cents": ["This amount cannot be negative."]})
