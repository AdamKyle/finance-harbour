import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class GenerateBudgetMonthlyNegativeTest(TestCase):
    def test_negative_left_over_sets_flag(self) -> None:
        user = User.objects.create_user(email="negative_monthly@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="rent_or_mortgage",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent or mortgage",
            amount_cents=100000,
        )
        plan = generate_budget(user)
        first = plan.pay_periods.first()
        self.assertTrue(first.has_negative_left_over)

    def test_affects_important_expenses_when_rent_not_coverable(self) -> None:
        user = User.objects.create_user(email="affects_important_monthly@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="rent_or_mortgage",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent or mortgage",
            amount_cents=100000,
        )
        plan = generate_budget(user)
        first = plan.pay_periods.first()
        self.assertTrue(first.affects_important_expenses)
