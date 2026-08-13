import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory, RequiredExpense


class GenerateBudgetWithRequiredExpensesTest(TestCase):
    def test_required_expense_marks_line_item_is_required(self) -> None:
        user = User.objects.create_user(email="budget_required@example.com", password="StrongPassword123!")
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
            amount_cents=30000,
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            title="Food",
            amount_cents=30000,
        )
        plan = generate_budget(user)
        first = plan.pay_periods.first()
        food_item = first.line_items.filter(source_key="food").first()
        self.assertIsNotNone(food_item)
        self.assertTrue(food_item.is_required)

    def test_rent_line_item_always_is_required(self) -> None:
        user = User.objects.create_user(email="budget_rent_required@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
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
        rent_item = first.line_items.filter(source_type=SourceType.RENT_OR_MORTGAGE).first()
        self.assertTrue(rent_item.is_required)
