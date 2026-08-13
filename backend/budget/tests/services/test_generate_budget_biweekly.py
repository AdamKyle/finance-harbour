import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class GenerateBudgetBiweeklyTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="budget_biweekly@example.com", password="StrongPassword123!")
        self.anchor = datetime.date(2025, 8, 1)
        self.debt_profile = DebtProfile.objects.create(
            user=self.user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=150000,
            next_pay_date=self.anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=self.debt_profile,
            source_key="rent_or_mortgage",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent or mortgage",
            amount_cents=100000,
        )
        RecurringExpense.objects.create(
            debt_profile=self.debt_profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=30000,
        )

    def test_creates_27_pay_periods(self) -> None:
        plan = generate_budget(self.user)
        self.assertEqual(plan.pay_periods.count(), 27)

    def test_rent_appears_on_last_biweekly_in_month(self) -> None:
        plan = generate_budget(self.user)
        august_periods = [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025]
        last_august = max(august_periods, key=lambda p: p.pay_date)
        rent_items = last_august.line_items.filter(source_type=SourceType.RENT_OR_MORTGAGE)
        self.assertEqual(rent_items.count(), 1)

    def test_non_rent_distributed_across_biweekly_periods(self) -> None:
        plan = generate_budget(self.user)
        total_food = sum(
            li.amount_cents for period in plan.pay_periods.all() for li in period.line_items.filter(source_key="food")
        )
        august_months = 12
        self.assertEqual(total_food, 30000 * august_months)

    def test_income_per_period_stored_correctly(self) -> None:
        plan = generate_budget(self.user)
        self.assertEqual(plan.income_per_pay_period_cents, 150000)
