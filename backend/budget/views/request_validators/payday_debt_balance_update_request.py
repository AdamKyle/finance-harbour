from rest_framework.exceptions import ValidationError

from budget.models import DebtBalanceReviewStatus
from core.request_validator_engine import RequestValidatorEngine


class PaydayDebtBalanceUpdateRequest(RequestValidatorEngine):
    rules = {
        "source_key": ("required", "string", ("max_length", 150)),
        "title": ("required", "string", ("max_length", 200)),
        "review_status": ("required", "string", ("choices", set(DebtBalanceReviewStatus))),
        "actual_balance_cents": ("nullable", "integer", ("min_value", 0)),
    }

    def validate(self) -> None:
        super().validate()

        review_status = DebtBalanceReviewStatus(self.validated_data["review_status"])
        self._validated_data["review_status"] = review_status
        actual_balance_cents = self.validated_data.get("actual_balance_cents")

        if review_status == DebtBalanceReviewStatus.UNREVIEWED:
            raise ValidationError({"review_status": ["Select Confirmed or Unknown."]})

        if review_status == DebtBalanceReviewStatus.CONFIRMED and actual_balance_cents is None:
            raise ValidationError({"actual_balance_cents": ["An actual balance is required when confirmed."]})

        if actual_balance_cents is not None and actual_balance_cents > 2147483647:
            raise ValidationError({"actual_balance_cents": ["This amount is outside the supported range."]})

        if review_status == DebtBalanceReviewStatus.UNKNOWN:
            self._validated_data["actual_balance_cents"] = None
