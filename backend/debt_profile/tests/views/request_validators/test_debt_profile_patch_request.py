import datetime

from django.test import TestCase
from django.utils import timezone
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
                        "minimum_payment_cents": 5000,
                        "current_payment_cents": 5000,
                    }
                ]
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("debts", raised_error.exception.detail)

    def test_missing_minimum_payment_fails_validation(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "debts": [
                    {
                        "label": "VISA",
                        "current_balance_cents": 10000,
                        "current_payment_cents": 500,
                    }
                ]
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("debts", raised_error.exception.detail)

    def test_missing_current_payment_fails_validation(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "debts": [
                    {
                        "label": "VISA",
                        "current_balance_cents": 10000,
                        "minimum_payment_cents": 500,
                    }
                ]
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("debts", raised_error.exception.detail)

    def test_zero_minimum_payment_fails_validation(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "debts": [
                    {
                        "label": "VISA",
                        "current_balance_cents": 10000,
                        "minimum_payment_cents": 0,
                        "current_payment_cents": 500,
                    }
                ]
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("debts", raised_error.exception.detail)

    def test_zero_current_payment_fails_validation(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "debts": [
                    {
                        "label": "VISA",
                        "current_balance_cents": 10000,
                        "minimum_payment_cents": 500,
                        "current_payment_cents": 0,
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

    def test_valid_next_pay_date_passes_validation(self) -> None:
        future_date = (timezone.localdate() + datetime.timedelta(days=7)).isoformat()
        request = DebtProfilePatchRequest({"next_pay_date": future_date})

        request.validate()

        self.assertEqual(request.validated_data["next_pay_date"], future_date)

    def test_past_next_pay_date_fails_validation(self) -> None:
        past_date = (timezone.localdate() - datetime.timedelta(days=1)).isoformat()
        request = DebtProfilePatchRequest({"next_pay_date": past_date})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("next_pay_date", raised_error.exception.detail)

    def test_invalid_next_pay_date_format_fails_validation(self) -> None:
        request = DebtProfilePatchRequest({"next_pay_date": "not-a-date"})

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("next_pay_date", raised_error.exception.detail)

    def test_null_next_pay_date_passes_validation(self) -> None:
        request = DebtProfilePatchRequest({"next_pay_date": None})

        request.validate()

        self.assertIsNone(request.validated_data["next_pay_date"])

    def test_today_next_pay_date_passes_validation(self) -> None:
        today = timezone.localdate().isoformat()
        request = DebtProfilePatchRequest({"next_pay_date": today})

        request.validate()

        self.assertEqual(request.validated_data["next_pay_date"], today)

    def test_day_of_month_schedule_without_funding_position_is_rejected(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "payment_schedules": [
                    {
                        "source_key": "debt:0",
                        "timing": "DAY_OF_MONTH",
                        "paycheck_position": None,
                        "day_of_month": 10,
                        "auto_deducted": False,
                    }
                ]
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            request.validate()

        self.assertIn("payment_schedules", raised_error.exception.detail)

    def test_day_of_month_schedule_with_funding_position_is_valid(self) -> None:
        request = DebtProfilePatchRequest(
            {
                "payment_schedules": [
                    {
                        "source_key": "debt:0",
                        "timing": "DAY_OF_MONTH",
                        "paycheck_position": "FIRST",
                        "day_of_month": 10,
                        "auto_deducted": False,
                    }
                ]
            }
        )

        request.validate()

        self.assertEqual(request.validated_data["payment_schedules"][0]["paycheck_position"], "FIRST")
