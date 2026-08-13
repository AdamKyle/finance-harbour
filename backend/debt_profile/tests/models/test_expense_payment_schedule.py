from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, ExpensePaymentSchedule, ExpensePaymentTiming, PaycheckPosition


class ExpensePaymentScheduleTest(TestCase):
    def test_every_paycheck_requires_empty_position_and_null_day(self) -> None:
        user = User.objects.create_user(email="schedule-every@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=user)

        schedule = ExpensePaymentSchedule.objects.create(
            debt_profile=debt_profile,
            source_key="food",
            timing=ExpensePaymentTiming.EVERY_PAYCHECK,
        )

        self.assertEqual(schedule.paycheck_position, "")
        self.assertIsNone(schedule.day_of_month)

    def test_every_paycheck_rejects_position(self) -> None:
        user = User.objects.create_user(email="schedule-every-position@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=user)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpensePaymentSchedule.objects.create(
                debt_profile=debt_profile,
                source_key="food",
                timing=ExpensePaymentTiming.EVERY_PAYCHECK,
                paycheck_position=PaycheckPosition.FIRST,
            )

    def test_paycheck_position_schedule_requires_null_day(self) -> None:
        user = User.objects.create_user(email="schedule-payday@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=user)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpensePaymentSchedule.objects.create(
                debt_profile=debt_profile,
                source_key="insurance",
                timing=ExpensePaymentTiming.PAYCHECK_POSITION,
                paycheck_position=PaycheckPosition.FIRST,
                day_of_month=12,
            )

    def test_day_of_month_schedule_requires_day(self) -> None:
        user = User.objects.create_user(email="schedule-day@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=user)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpensePaymentSchedule.objects.create(
                debt_profile=debt_profile,
                source_key="insurance",
                timing=ExpensePaymentTiming.DAY_OF_MONTH,
                day_of_month=None,
            )

    def test_day_of_month_rejects_day_above_thirty_one(self) -> None:
        user = User.objects.create_user(email="schedule-range@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=user)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpensePaymentSchedule.objects.create(
                debt_profile=debt_profile,
                source_key="insurance",
                timing=ExpensePaymentTiming.DAY_OF_MONTH,
                day_of_month=32,
            )

    def test_source_key_is_unique_per_profile(self) -> None:
        user = User.objects.create_user(email="schedule-unique@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(user=user)
        ExpensePaymentSchedule.objects.create(
            debt_profile=debt_profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpensePaymentSchedule.objects.create(
                debt_profile=debt_profile,
                source_key="insurance",
                timing=ExpensePaymentTiming.PAYCHECK_POSITION,
                paycheck_position=PaycheckPosition.FIRST,
            )
