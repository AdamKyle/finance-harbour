from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from budget.models import DebtBalanceReviewStatus
from budget.views.request_validators import PaydayDebtBalanceUpdateRequest


class PaydayDebtBalanceUpdateRequestTest(SimpleTestCase):
    def test_confirmed_balance_is_valid(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": 500000,
            }
        )

        request.validate()

        self.assertEqual(request.validated_data["review_status"], DebtBalanceReviewStatus.CONFIRMED)

    def test_unknown_balance_is_valid_and_normalizes_null(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "UNKNOWN",
                "actual_balance_cents": 500000,
            }
        )

        request.validate()

        self.assertIsNone(request.validated_data["actual_balance_cents"])

    def test_required_fields_are_enforced(self) -> None:
        request = PaydayDebtBalanceUpdateRequest({})

        with self.assertRaises(ValidationError):
            request.validate()

    def test_invalid_balance_type_is_rejected(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": "many",
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_invalid_choice_is_rejected(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "PAID",
                "actual_balance_cents": 500000,
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_unreviewed_is_rejected_as_a_completed_submission(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "UNREVIEWED",
                "actual_balance_cents": None,
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_confirmed_requires_balance(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": None,
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_negative_balance_is_rejected(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": -1,
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_integer_overflow_is_rejected(self) -> None:
        request = PaydayDebtBalanceUpdateRequest(
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": 2147483648,
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()
