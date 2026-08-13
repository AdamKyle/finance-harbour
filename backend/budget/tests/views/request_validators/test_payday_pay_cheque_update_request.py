from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from budget.models import PayChequeReviewStatus
from budget.views.request_validators import PaydayPayChequeUpdateRequest


class PaydayPayChequeUpdateRequestTest(SimpleTestCase):
    def test_confirmed_amount_is_valid_and_typed(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "CONFIRMED", "actual_amount_cents": 10000})

        request.validate()

        self.assertEqual(request.validated_data["review_status"], PayChequeReviewStatus.CONFIRMED)
        self.assertEqual(request.validated_data["actual_amount_cents"], 10000)

    def test_unknown_shape_is_valid_and_clears_amount(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "UNKNOWN", "actual_amount_cents": 10000})

        request.validate()

        self.assertEqual(request.validated_data["review_status"], PayChequeReviewStatus.UNKNOWN)
        self.assertIsNone(request.validated_data["actual_amount_cents"])

    def test_status_is_required(self) -> None:
        request = PaydayPayChequeUpdateRequest({"actual_amount_cents": 10000})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_confirmed_amount_is_required(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "CONFIRMED", "actual_amount_cents": None})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_non_integer_amount_is_rejected(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "CONFIRMED", "actual_amount_cents": "ten"})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_unsupported_status_is_rejected(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "PAID", "actual_amount_cents": 10000})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_unreviewed_status_is_rejected(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "UNREVIEWED", "actual_amount_cents": None})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_negative_amount_is_rejected(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "CONFIRMED", "actual_amount_cents": -1})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_integer_overflow_is_rejected(self) -> None:
        request = PaydayPayChequeUpdateRequest({"review_status": "CONFIRMED", "actual_amount_cents": 2147483648})

        with self.assertRaises(ValidationError):
            request.validate()
