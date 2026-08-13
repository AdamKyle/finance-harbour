from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from budget.views.request_validators.recurring_obligation_create_request import RecurringObligationCreateRequest


class RecurringObligationCreateRequestTest(SimpleTestCase):
    def test_valid_bill_request(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": True,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "DAY_OF_MONTH",
                    "paycheck_position": "FIRST",
                    "day_of_month": 10,
                    "auto_deducted": False,
                },
            }
        )

        request.validate()
        request.validate_schedule_position("BIWEEKLY")

        self.assertEqual(request.validated_data["label"], "Internet")

    def test_valid_debt_request(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "DEBT",
                "label": "Student Loan",
                "is_required": False,
                "current_balance_cents": 1200000,
                "minimum_payment_cents": 10000,
                "current_payment_cents": 15000,
                "payment_schedule": {
                    "timing": "PAYCHECK_POSITION",
                    "paycheck_position": "SECOND",
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )

        request.validate()
        request.validate_schedule_position("BIWEEKLY")

        self.assertEqual(request.validated_data["kind"], "DEBT")

    def test_blank_label_is_rejected(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "   ",
                "is_required": False,
                "amount_cents": 100,
                "payment_schedule": {
                    "timing": "EVERY_PAYCHECK",
                    "paycheck_position": None,
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_bill_rejects_debt_fields(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "current_balance_cents": 0,
                "payment_schedule": {
                    "timing": "EVERY_PAYCHECK",
                    "paycheck_position": None,
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_debt_rejects_bill_amount(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "DEBT",
                "label": "Loan",
                "is_required": False,
                "amount_cents": 100,
                "current_balance_cents": 0,
                "minimum_payment_cents": 100,
                "current_payment_cents": 100,
                "payment_schedule": {
                    "timing": "EVERY_PAYCHECK",
                    "paycheck_position": None,
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_day_of_month_requires_funding_position(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "DAY_OF_MONTH",
                    "paycheck_position": None,
                    "day_of_month": 10,
                    "auto_deducted": False,
                },
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_biweekly_rejects_fourth_position(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "PAYCHECK_POSITION",
                    "paycheck_position": "FOURTH",
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )
        request.validate()

        with self.assertRaises(ValidationError):
            request.validate_schedule_position("BIWEEKLY")

    def test_monthly_rejects_last_position(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "PAYCHECK_POSITION",
                    "paycheck_position": "LAST",
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )
        request.validate()

        with self.assertRaises(ValidationError):
            request.validate_schedule_position("MONTHLY")

    def test_weekly_accepts_third_position(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "PAYCHECK_POSITION",
                    "paycheck_position": "THIRD",
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )

        request.validate()
        request.validate_schedule_position("WEEKLY")

        self.assertEqual(request.validated_data["payment_schedule"]["paycheck_position"], "THIRD")

    def test_weekly_accepts_fourth_position(self) -> None:
        request = RecurringObligationCreateRequest(
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "PAYCHECK_POSITION",
                    "paycheck_position": "FOURTH",
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            }
        )

        request.validate()
        request.validate_schedule_position("WEEKLY")

        self.assertEqual(request.validated_data["payment_schedule"]["paycheck_position"], "FOURTH")
