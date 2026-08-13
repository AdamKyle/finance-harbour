from rest_framework.exceptions import ValidationError

from budget.models import PayChequeReviewStatus
from core.request_validator_engine import RequestValidatorEngine


class PaydayPayChequeUpdateRequest(RequestValidatorEngine):
    rules = {
        "review_status": ("required", "string", ("choices", set(PayChequeReviewStatus))),
        "actual_amount_cents": ("nullable", "integer", ("min_value", 0)),
    }

    def validate(self) -> None:
        super().validate()

        review_status = PayChequeReviewStatus(self.validated_data["review_status"])
        self._validated_data["review_status"] = review_status
        actual_amount_cents = self.validated_data.get("actual_amount_cents")

        if review_status == PayChequeReviewStatus.UNREVIEWED:
            raise ValidationError({"review_status": ["Choose a completed pay cheque review status."]})

        if review_status == PayChequeReviewStatus.CONFIRMED and self.validated_data.get("actual_amount_cents") is None:
            raise ValidationError({"actual_amount_cents": ["An actual amount is required when confirmed."]})

        if actual_amount_cents is not None and actual_amount_cents > 2147483647:
            raise ValidationError({"actual_amount_cents": ["This amount is outside the supported range."]})

        if review_status == PayChequeReviewStatus.UNKNOWN:
            self._validated_data["actual_amount_cents"] = None
