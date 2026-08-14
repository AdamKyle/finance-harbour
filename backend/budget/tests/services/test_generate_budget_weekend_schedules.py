import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    PaycheckPosition,
    RecurringExpense,
    RecurringExpenseCategory,
)


class GenerateBudgetWeekendSchedulesTest(TestCase):
    def test_weekday_payment_date_is_unchanged(self) -> None:
        user = User.objects.create_user(email="weekday-schedule@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="phone", timing=ExpensePaymentTiming.DAY_OF_MONTH, day_of_month=12
        )

        item = generate_budget(user).pay_periods.first().line_items.get(source_key="phone")

        self.assertEqual(item.expected_payment_date, datetime.date(2026, 8, 12))

    def test_saturday_payment_moves_to_monday(self) -> None:
        user = User.objects.create_user(email="saturday-schedule@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position=PaycheckPosition.FIRST,
            day_of_month=29,
        )

        item = generate_budget(user).pay_periods.first().line_items.get(source_key="phone")

        self.assertEqual(item.expected_payment_date, datetime.date(2026, 8, 31))

    def test_sunday_payment_moves_to_monday(self) -> None:
        user = User.objects.create_user(email="sunday-schedule@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position=PaycheckPosition.FIRST,
            day_of_month=30,
        )

        item = generate_budget(user).pay_periods.first().line_items.get(source_key="phone")

        self.assertEqual(item.expected_payment_date, datetime.date(2026, 8, 31))

    def test_month_boundary_weekend_uses_responsible_pay_period(self) -> None:
        user = User.objects.create_user(email="boundary-schedule@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 10, 9),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position=PaycheckPosition.LAST,
            day_of_month=31,
        )

        plan = generate_budget(user)
        item = plan.pay_periods.get(pay_date=datetime.date(2026, 10, 23)).line_items.get(source_key="phone")

        self.assertEqual(item.expected_payment_date, datetime.date(2026, 11, 2))
