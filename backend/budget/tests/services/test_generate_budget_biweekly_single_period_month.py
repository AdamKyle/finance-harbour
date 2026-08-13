import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class GenerateBudgetBiweeklySinglePeriodMonthTest(TestCase):
    def test_single_biweekly_period_in_month_gets_all_obligations(self) -> None:
        # anchor 2025-08-25: next biweekly is 2025-09-08, so August has exactly 1 period
        user = User.objects.create_user(email="biweekly_single@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 25)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=200000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="rent_or_mortgage",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent or mortgage",
            amount_cents=80000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=30000,
        )
        plan = generate_budget(user)
        all_periods = list(plan.pay_periods.all())
        august_periods = [p for p in all_periods if p.pay_date.month == 8 and p.pay_date.year == 2025]
        self.assertEqual(len(august_periods), 1)
        single = august_periods[0]
        rent_items = single.line_items.filter(source_type=SourceType.RENT_OR_MORTGAGE)
        self.assertEqual(rent_items.count(), 1)
