import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class GenerateBudgetNoObligationsTest(TestCase):
    def test_empty_obligations_all_income_is_left_over(self) -> None:
        user = User.objects.create_user(email="budget_no_obligations@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=200000,
            next_pay_date=anchor,
        )
        plan = generate_budget(user)
        first = plan.pay_periods.first()
        self.assertEqual(first.left_over_cents, 200000)
        self.assertEqual(first.line_items.count(), 0)
        self.assertFalse(first.has_negative_left_over)

    def test_no_deferred_items_when_all_fit(self) -> None:
        user = User.objects.create_user(email="budget_no_deferred@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=50000,
        )
        plan = generate_budget(user)
        any_deferred = plan.pay_periods.filter(has_deferred_items=True).exists()
        self.assertFalse(any_deferred)
