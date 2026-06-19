from django.test import TestCase
from rest_framework.exceptions import ValidationError

from debt_profile.views.request_validators import MonthlyExpensePatchRequest


class MonthlyExpensePatchRequestTest(TestCase):
    def test_valid_rent_passes_validation(self) -> None:
        request = MonthlyExpensePatchRequest({"rent_or_mortgage_cents": 150000})

        request.validate()

        self.assertEqual(request.validated_data, {"rent_or_mortgage_cents": 150000})

    def test_valid_misc_expenses_passes_validation(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "misc_expenses": [
                    {"label": "Gym", "amount_cents": 5000},
                ]
            }
        )

        request.validate()

        self.assertIn("misc_expenses", request.validated_data)

    def test_empty_payload_passes_validation(self) -> None:
        request = MonthlyExpensePatchRequest({})

        request.validate()

        self.assertEqual(request.validated_data, {})

    def test_all_cent_fields_pass_validation(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "rent_or_mortgage_cents": 150000,
                "water_cents": 5000,
                "electricity_cents": 12000,
                "food_cents": 60000,
                "internet_cents": 8000,
                "phone_cents": 7500,
                "car_payment_cents": 35000,
                "insurance_cents": 15000,
            }
        )

        request.validate()

        self.assertIn("rent_or_mortgage_cents", request.validated_data)
        self.assertIn("water_cents", request.validated_data)

    def test_negative_rent_fails_validation(self) -> None:
        request = MonthlyExpensePatchRequest({"rent_or_mortgage_cents": -100})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("rent_or_mortgage_cents", raised_error.exception.detail)

    def test_non_integer_water_fails_validation(self) -> None:
        request = MonthlyExpensePatchRequest({"water_cents": "not-an-int"})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("water_cents", raised_error.exception.detail)

    def test_misc_expenses_must_be_a_list(self) -> None:
        request = MonthlyExpensePatchRequest({"misc_expenses": "not-a-list"})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("misc_expenses", raised_error.exception.detail)

    def test_invalid_misc_expense_entry_fails_validation(self) -> None:
        request = MonthlyExpensePatchRequest({"misc_expenses": [{"label": "Gym", "amount_cents": -500}]})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("misc_expenses", raised_error.exception.detail)
