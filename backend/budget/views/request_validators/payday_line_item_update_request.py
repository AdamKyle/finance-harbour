from rest_framework.exceptions import ValidationError

from budget.models import PaymentReviewStatus
from core.request_validator_engine import RequestValidatorEngine


class PaydayLineItemUpdateRequest(RequestValidatorEngine):
    rules = {
        "review_status": ("required", "string", ("choices", set(PaymentReviewStatus))),
        "actual_amount_cents": ("nullable", "integer", ("min_value", 0)),
        "scheduled_amount_cents": ("nullable", "integer", ("min_value", 0)),
    }

    def validate(self) -> None:
        super().validate()

        review_status = PaymentReviewStatus(self.validated_data["review_status"])
        self._validated_data["review_status"] = review_status
        actual_amount = self.validated_data.get("actual_amount_cents")
        scheduled_amount = self.validated_data.get("scheduled_amount_cents")

        if review_status == PaymentReviewStatus.UNREVIEWED:
            raise ValidationError({"review_status": ["Choose a completed payment review status."]})

        if review_status == PaymentReviewStatus.PAID and actual_amount is None:
            raise ValidationError({"actual_amount_cents": ["An actual amount is required when paid."]})

        if actual_amount is not None and actual_amount > 2147483647:
            raise ValidationError({"actual_amount_cents": ["This amount is outside the supported range."]})

        if scheduled_amount is not None and scheduled_amount > 2147483647:
            raise ValidationError({"scheduled_amount_cents": ["This amount is outside the supported range."]})

        if review_status == PaymentReviewStatus.SCHEDULED and scheduled_amount is None:
            raise ValidationError({"scheduled_amount_cents": ["An expected amount is required when scheduled."]})

        if review_status == PaymentReviewStatus.NOT_PAID:
            self._validated_data["actual_amount_cents"] = 0

        if review_status in {PaymentReviewStatus.UNKNOWN, PaymentReviewStatus.SCHEDULED}:
            self._validated_data["actual_amount_cents"] = None

        if review_status != PaymentReviewStatus.SCHEDULED:
            self._validated_data["scheduled_amount_cents"] = None
