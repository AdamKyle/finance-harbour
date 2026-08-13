from django.test import SimpleTestCase

from debt_profile.models import ExpensePaymentTiming, PaycheckPosition
from debt_profile.services.payment_schedule_validation import validate_schedule_positions


class PaymentScheduleValidationTest(SimpleTestCase):
    def test_biweekly_rejects_third_paycheck_position(self) -> None:
        schedules = [
            {
                "source_key": "insurance",
                "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                "paycheck_position": PaycheckPosition.THIRD,
                "day_of_month": None,
                "auto_deducted": False,
            }
        ]

        self.assertFalse(validate_schedule_positions(schedules, "BIWEEKLY"))

    def test_weekly_accepts_third_paycheck_position(self) -> None:
        schedules = [
            {
                "source_key": "insurance",
                "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                "paycheck_position": PaycheckPosition.THIRD,
                "day_of_month": None,
                "auto_deducted": False,
            }
        ]

        self.assertTrue(validate_schedule_positions(schedules, "WEEKLY"))

    def test_monthly_accepts_only_first_paycheck_position(self) -> None:
        schedules = [
            {
                "source_key": "insurance",
                "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                "paycheck_position": PaycheckPosition.FIRST,
                "day_of_month": None,
                "auto_deducted": False,
            }
        ]

        self.assertTrue(validate_schedule_positions(schedules, "MONTHLY"))
