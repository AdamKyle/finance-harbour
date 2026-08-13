from rest_framework.exceptions import ValidationError

from core.request_validator_engine import RequestValidatorEngine


class BudgetBillCreateRequest(RequestValidatorEngine):
    rules = {
        "title": ("required", "string", ("min_length", 1), ("max_length", 200)),
        "amount_cents": ("required", "integer", ("min_value", 0)),
        "is_required": ("required", "boolean"),
        "going_forward": ("required", "boolean"),
    }

    def validate(self) -> None:
        super().validate()

        if not self.validated_data["title"].strip():
            raise ValidationError({"title": ["Enter a bill name."]})

        if self.validated_data["amount_cents"] > 2147483647:
            raise ValidationError({"amount_cents": ["This amount is outside the supported range."]})
