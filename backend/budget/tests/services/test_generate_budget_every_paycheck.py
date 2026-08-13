import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    RecurringExpense,
    RecurringExpenseCategory,
)


class GenerateBudgetEveryPaycheckTest(TestCase):
    def test_monthly_schedule_appears_once(self) -> None:
        user = User.objects.create_user(email="every-monthly@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type=DebtProfile.PayPeriodType.MONTHLY,
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 9, 4),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=20000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="food",
            timing=ExpensePaymentTiming.EVERY_PAYCHECK,
        )

        plan = generate_budget(user)

        self.assertEqual(plan.pay_periods.filter(pay_date__month=9, line_items__source_key="food").count(), 1)

    def test_biweekly_two_paycheck_month_appears_twice(self) -> None:
        user = User.objects.create_user(email="every-biweekly-two@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type=DebtProfile.PayPeriodType.BIWEEKLY,
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 9, 4),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=20000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="food", timing=ExpensePaymentTiming.EVERY_PAYCHECK
        )

        plan = generate_budget(user)

        self.assertEqual(plan.pay_periods.filter(pay_date__month=9, line_items__source_key="food").count(), 2)

    def test_biweekly_three_paycheck_month_appears_three_times(self) -> None:
        user = User.objects.create_user(email="every-biweekly-three@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type=DebtProfile.PayPeriodType.BIWEEKLY,
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 10, 2),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=20000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="food", timing=ExpensePaymentTiming.EVERY_PAYCHECK
        )

        plan = generate_budget(user)

        self.assertEqual(plan.pay_periods.filter(pay_date__month=10, line_items__source_key="food").count(), 3)

    def test_weekly_four_paycheck_month_appears_four_times(self) -> None:
        user = User.objects.create_user(email="every-weekly-four@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type=DebtProfile.PayPeriodType.WEEKLY,
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 2, 6),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=20000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="food", timing=ExpensePaymentTiming.EVERY_PAYCHECK
        )

        plan = generate_budget(user)

        self.assertEqual(plan.pay_periods.filter(pay_date__month=2, line_items__source_key="food").count(), 4)

    def test_weekly_five_paycheck_month_appears_five_times(self) -> None:
        user = User.objects.create_user(email="every-weekly-five@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type=DebtProfile.PayPeriodType.WEEKLY,
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 5, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=20000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="food", timing=ExpensePaymentTiming.EVERY_PAYCHECK
        )

        plan = generate_budget(user)

        self.assertEqual(plan.pay_periods.filter(pay_date__month=5, line_items__source_key="food").count(), 5)
