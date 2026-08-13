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
    UtilityType,
)


class GenerateBudgetWithPaymentScheduleTest(TestCase):
    def test_combined_utilities_generate_once_on_the_responsible_pay_period(self) -> None:
        user = User.objects.create_user(email="scheduled-utility@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water + electricity",
            amount_cents=18000,
            utility_type=UtilityType.WATER_AND_ELECTRICITY,
            includes_internet=True,
            includes_cable=True,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="utilities",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
        )

        plan = generate_budget(user)
        utility_items = plan.pay_periods.filter(line_items__source_key="utilities")

        self.assertEqual(utility_items.count(), 12)
        self.assertFalse(plan.pay_periods.filter(line_items__source_key="internet").exists())

    def test_shorter_month_clamps_then_moves_weekend_to_monday(self) -> None:
        user = User.objects.create_user(email="short-month@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 1, 31),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=18750,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=31,
        )

        plan = generate_budget(user)
        february_item = plan.pay_periods.get(pay_date=datetime.date(2026, 2, 28)).line_items.get(source_key="insurance")

        self.assertEqual(february_item.expected_payment_date, datetime.date(2026, 3, 2))

    def test_auto_deducted_date_obligation_is_important(self) -> None:
        user = User.objects.create_user(email="auto-deducted@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=18750,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=17,
            auto_deducted=True,
        )

        plan = generate_budget(user)
        insurance = plan.pay_periods.first().line_items.get(source_key="insurance")

        self.assertTrue(insurance.is_auto_deducted)
        self.assertTrue(insurance.is_required)
