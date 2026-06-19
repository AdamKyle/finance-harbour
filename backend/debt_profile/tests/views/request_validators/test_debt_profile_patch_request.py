from django.test import TestCase
from rest_framework.exceptions import ValidationError

from debt_profile.views.request_validators import DebtProfilePatchRequest


class DebtProfilePatchRequestTest(TestCase):
    def test_valid_income_passes_validation(self) -> None:
        request = DebtProfilePatchRequest({"income_per_pay_period_cents": 100000})

        request.validate()

        self.assertEqual(request.validated_data, {"income_per_pay_period_cents": 100000})

    def test_valid_pay_period_type_passes_validation(self) -> None:
        request = DebtProfilePatchRequest({"pay_period_type": "BIWEEKLY"})

        request.validate()

        self.assertEqual(request.validated_data, {"pay_period_type": "BIWEEKLY"})

    def test_empty_pay_period_type_passes_validation(self) -> None:
        request = DebtProfilePatchRequest({"pay_period_type": ""})

        request.validate()

        self.assertEqual(request.validated_data, {"pay_period_type": ""})

    def test_valid_debts_passes_validation(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "debts": [
                    {
                        "label": "VISA",
                        "current_balance_cents": 10000,
                        "interest_rate_basis_points": 2000,
                        "minimum_payment_cents": 500,
                        "current_payment_cents": 500,
                    }
                ]
            }
        )

        request.validate()

        self.assertIn("debts", request.validated_data)

    def test_empty_payload_passes_validation(self) -> None:
        request = DebtProfilePatchRequest({})

        request.validate()

        self.assertEqual(request.validated_data, {})

    def test_invalid_pay_period_type_fails_validation(self) -> None:
        request = DebtProfilePatchRequest({"pay_period_type": "QUARTERLY"})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("pay_period_type", raised_error.exception.detail)

    def test_negative_income_fails_validation(self) -> None:
        request = DebtProfilePatchRequest({"income_per_pay_period_cents": -100})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("income_per_pay_period_cents", raised_error.exception.detail)

    def test_non_integer_income_fails_validation(self) -> None:
        request = DebtProfilePatchRequest({"income_per_pay_period_cents": "not-an-int"})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("income_per_pay_period_cents", raised_error.exception.detail)

    def test_negative_debt_balance_fails_validation(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "debts": [
                    {
                        "label": "Test",
                        "current_balance_cents": -100,
                        "interest_rate_basis_points": 1500,
                        "minimum_payment_cents": 5000,
                        "current_payment_cents": 5000,
                    }
                ]
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("debts", raised_error.exception.detail)

    def test_debts_must_be_a_list(self) -> None:
        request = DebtProfilePatchRequest({"debts": "not-a-list"})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("debts", raised_error.exception.detail)
