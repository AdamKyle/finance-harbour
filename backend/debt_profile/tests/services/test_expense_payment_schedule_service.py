from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, ExpensePaymentSchedule, ExpensePaymentTiming
from debt_profile.services.expense_payment_schedule_service import replace_monthly_expense_payment_schedules


class ExpensePaymentScheduleServiceTest(TestCase):
    def test_owner_schedule_can_change_between_timing_types(self) -> None:
        owner = User.objects.create_user(email="schedule-service-owner@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=owner)
        replace_monthly_expense_payment_schedules(
            debt_profile,
            [
                {
                    "source_key": "insurance",
                    "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                    "paycheck_position": "FIRST",
                    "day_of_month": None,
                    "auto_deducted": False,
                }
            ],
        )

        replace_monthly_expense_payment_schedules(
            debt_profile,
            [
                {
                    "source_key": "insurance",
                    "timing": ExpensePaymentTiming.DAY_OF_MONTH,
                    "paycheck_position": None,
                    "day_of_month": 12,
                    "auto_deducted": True,
                }
            ],
        )

        schedule = ExpensePaymentSchedule.objects.get(debt_profile=debt_profile, source_key="insurance")
        self.assertEqual(schedule.timing, ExpensePaymentTiming.DAY_OF_MONTH)
        self.assertEqual(schedule.day_of_month, 12)

    def test_day_of_month_to_payday_clears_day(self) -> None:
        owner = User.objects.create_user(email="schedule-service-clear@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=owner)
        ExpensePaymentSchedule.objects.create(
            debt_profile=debt_profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
        )

        replace_monthly_expense_payment_schedules(
            debt_profile,
            [
                {
                    "source_key": "insurance",
                    "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                    "paycheck_position": "FIRST",
                    "day_of_month": None,
                    "auto_deducted": False,
                }
            ],
        )

        schedule = ExpensePaymentSchedule.objects.get(debt_profile=debt_profile, source_key="insurance")
        self.assertEqual(schedule.timing, ExpensePaymentTiming.PAYCHECK_POSITION)
        self.assertIsNone(schedule.day_of_month)

    def test_replacement_does_not_modify_another_owners_schedule(self) -> None:
        jane = User.objects.create_user(email="schedule-service-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="schedule-service-bob@example.com", password="StrongPassword123!")
        jane_profile = DebtProfile.objects.create(user=jane)
        bob_profile = DebtProfile.objects.create(user=bob)
        ExpensePaymentSchedule.objects.create(
            debt_profile=jane_profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
        )

        replace_monthly_expense_payment_schedules(
            bob_profile,
            [
                {
                    "source_key": "insurance",
                    "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                    "paycheck_position": "FIRST",
                    "day_of_month": None,
                    "auto_deducted": False,
                }
            ],
        )

        jane_schedule = ExpensePaymentSchedule.objects.get(debt_profile=jane_profile)
        self.assertEqual(jane_schedule.timing, ExpensePaymentTiming.DAY_OF_MONTH)
        self.assertEqual(jane_schedule.day_of_month, 12)
