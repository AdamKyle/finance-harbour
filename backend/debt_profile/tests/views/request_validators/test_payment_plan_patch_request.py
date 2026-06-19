from django.test import TestCase
from rest_framework.exceptions import ValidationError

from debt_profile.views.request_validators import PaymentPlanPatchRequest


class PaymentPlanPatchRequestTest(TestCase):
    def test_valid_extra_payment_passes_validation(self) -> None:
        request = PaymentPlanPatchRequest({"extra_payment_cents": 5000})

        request.validate()

        self.assertEqual(request.validated_data, {"extra_payment_cents": 5000})

    def test_valid_spending_percentage_passes_validation(self) -> None:
        request = PaymentPlanPatchRequest({"spending_payment_percentage_basis_points": 1000})

        request.validate()

        self.assertEqual(
            request.validated_data,
            {"spending_payment_percentage_basis_points": 1000},
        )

    def test_empty_payload_passes_validation(self) -> None:
        request = PaymentPlanPatchRequest({})

        request.validate()

        self.assertEqual(request.validated_data, {})

    def test_negative_extra_payment_fails_validation(self) -> None:
        request = PaymentPlanPatchRequest({"extra_payment_cents": -100})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("extra_payment_cents", raised_error.exception.detail)

    def test_negative_spending_percentage_fails_validation(self) -> None:
        request = PaymentPlanPatchRequest({"spending_payment_percentage_basis_points": -1})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("spending_payment_percentage_basis_points", raised_error.exception.detail)

    def test_non_integer_extra_payment_fails_validation(self) -> None:
        request = PaymentPlanPatchRequest({"extra_payment_cents": "not-an-int"})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("extra_payment_cents", raised_error.exception.detail)
