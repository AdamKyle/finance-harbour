from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from budget.models import PaymentReviewStatus
from budget.views.request_validators import PaydayLineItemUpdateRequest


class PaydayLineItemUpdateRequestTest(SimpleTestCase):
    def test_paid_is_valid(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "PAID", "actual_amount_cents": 5000})

        request.validate()

        self.assertEqual(request.validated_data["review_status"], PaymentReviewStatus.PAID)

    def test_not_paid_is_valid_and_normalizes_zero(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "NOT_PAID", "actual_amount_cents": 5000})

        request.validate()

        self.assertEqual(request.validated_data["actual_amount_cents"], 0)

    def test_unknown_is_valid_and_normalizes_null(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "UNKNOWN", "actual_amount_cents": 5000})

        request.validate()

        self.assertIsNone(request.validated_data["actual_amount_cents"])

    def test_scheduled_is_valid_with_expected_amount(self) -> None:
        request = PaydayLineItemUpdateRequest(
            {
                "review_status": "SCHEDULED",
                "actual_amount_cents": 5000,
                "scheduled_amount_cents": 6000,
            }
        )

        request.validate()

        self.assertEqual(
            request.validated_data["review_status"],
            PaymentReviewStatus.SCHEDULED,
        )
        self.assertIsNone(request.validated_data["actual_amount_cents"])
        self.assertEqual(request.validated_data["scheduled_amount_cents"], 6000)

    def test_scheduled_requires_expected_amount(self) -> None:
        request = PaydayLineItemUpdateRequest(
            {"review_status": "SCHEDULED", "actual_amount_cents": None, "scheduled_amount_cents": None}
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_scheduled_amount_rejects_overflow(self) -> None:
        request = PaydayLineItemUpdateRequest(
            {"review_status": "SCHEDULED", "actual_amount_cents": None, "scheduled_amount_cents": 2147483648}
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_scheduled_amount_rejects_negative_value(self) -> None:
        request = PaydayLineItemUpdateRequest(
            {"review_status": "SCHEDULED", "actual_amount_cents": None, "scheduled_amount_cents": -1}
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_required_fields_are_enforced(self) -> None:
        request = PaydayLineItemUpdateRequest({})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_invalid_amount_type_is_rejected(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "PAID", "actual_amount_cents": "five"})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_invalid_choice_is_rejected(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "CONFIRMED", "actual_amount_cents": 5000})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_paid_requires_amount(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "PAID", "actual_amount_cents": None})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_negative_amount_is_rejected(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "PAID", "actual_amount_cents": -1})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_integer_overflow_is_rejected(self) -> None:
        request = PaydayLineItemUpdateRequest({"review_status": "PAID", "actual_amount_cents": 2147483648})

        with self.assertRaises(ValidationError):
            request.validate()
