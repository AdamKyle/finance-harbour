from django.test import SimpleTestCase

from debt_profile.models import ExpensePaymentTiming, PaycheckPosition
from debt_profile.services.payment_schedule_validation import (
    validate_new_schedule_funding_positions,
    validate_schedule_positions,
)


class PaymentScheduleValidationTest(SimpleTestCase):
    def test_new_day_of_month_with_first_position_is_valid(self) -> None:
        schedules = [
            {
                "source_key": "insurance",
                "timing": ExpensePaymentTiming.DAY_OF_MONTH,
                "paycheck_position": PaycheckPosition.FIRST,
                "day_of_month": 10,
                "auto_deducted": False,
            }
        ]

        self.assertTrue(validate_new_schedule_funding_positions(schedules))

    def test_new_day_of_month_without_position_is_invalid(self) -> None:
        schedules = [
            {
                "source_key": "insurance",
                "timing": ExpensePaymentTiming.DAY_OF_MONTH,
                "paycheck_position": None,
                "day_of_month": 10,
                "auto_deducted": False,
            }
        ]

        self.assertFalse(validate_new_schedule_funding_positions(schedules))

    def test_new_every_paycheck_without_position_is_valid(self) -> None:
        schedules = [
            {
                "source_key": "food",
                "timing": ExpensePaymentTiming.EVERY_PAYCHECK,
                "paycheck_position": None,
                "day_of_month": None,
                "auto_deducted": False,
            }
        ]

        self.assertTrue(validate_new_schedule_funding_positions(schedules))

    def test_new_paycheck_position_schedule_with_position_is_valid(self) -> None:
        schedules = [
            {
                "source_key": "phone",
                "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                "paycheck_position": PaycheckPosition.SECOND,
                "day_of_month": None,
                "auto_deducted": False,
            }
        ]

        self.assertTrue(validate_new_schedule_funding_positions(schedules))

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

    def test_weekly_accepts_day_of_month_fourth_paycheck_position(self) -> None:
        schedules = [
            {
                "source_key": "insurance",
                "timing": ExpensePaymentTiming.DAY_OF_MONTH,
                "paycheck_position": PaycheckPosition.FOURTH,
                "day_of_month": 22,
                "auto_deducted": True,
            }
        ]

        self.assertTrue(validate_schedule_positions(schedules, "WEEKLY"))

    def test_biweekly_rejects_day_of_month_fourth_paycheck_position(self) -> None:
        schedules = [
            {
                "source_key": "insurance",
                "timing": ExpensePaymentTiming.DAY_OF_MONTH,
                "paycheck_position": PaycheckPosition.FOURTH,
                "day_of_month": 22,
                "auto_deducted": False,
            }
        ]

        self.assertFalse(validate_schedule_positions(schedules, "BIWEEKLY"))

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
