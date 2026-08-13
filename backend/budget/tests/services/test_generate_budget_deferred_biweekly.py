import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    RecurringExpense,
    RecurringExpenseCategory,
    RequiredExpense,
    UtilityType,
)


class GenerateBudgetDeferredBiweeklyTest(TestCase):
    def test_biweekly_item_wholly_on_middle_card_is_deferred(self) -> None:
        # anchor 2025-08-01: biweekly produces Aug 1, Aug 15, Aug 29 (3 periods, middle = Aug 15)
        # income=50000, water=50000 (fills first), electricity=40000 (fits wholly on second/middle)
        # electricity must land on Aug 15 (second, non-final) and be deferred
        user = User.objects.create_user(email="biweekly_middle_deferred@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water + electricity",
            amount_cents=90000,
            utility_type=UtilityType.WATER_AND_ELECTRICITY,
        )
        plan = generate_budget(user)
        august_periods = sorted(
            [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025],
            key=lambda p: p.sequence,
        )
        self.assertEqual(len(august_periods), 3)
        middle_period = august_periods[1]
        electricity_on_middle = middle_period.line_items.filter(source_key="utilities")
        self.assertTrue(electricity_on_middle.exists())
        # Middle card received electricity wholly (not split), so has_deferred_items must be True
        self.assertTrue(middle_period.has_deferred_items)

    def test_biweekly_deferred_required_expense_marks_affects_important_on_non_negative_card(self) -> None:
        # income=10000 biweekly, electricity(required)=15000, food=10000 per month
        # First period: electricity fills 10000, remaining 5000. Food: 0 capacity, skip.
        # Second/middle period: electricity remainder=5000 placed (deferred), food=5000 placed
        # Second period left_over=10000-5000-5000=0, NOT negative but has deferred required item
        user = User.objects.create_user(
            email="biweekly_deferred_affects_important@example.com", password="StrongPassword123!"
        )
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=10000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Electricity",
            amount_cents=15000,
            utility_type=UtilityType.ELECTRICITY,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=10000,
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            title="Electricity",
            amount_cents=15000,
        )
        plan = generate_budget(user)
        affected_non_negative = [
            p for p in plan.pay_periods.all() if p.affects_important_expenses and not p.has_negative_left_over
        ]
        self.assertTrue(len(affected_non_negative) > 0)

    def test_biweekly_non_required_deferred_does_not_mark_affects_important(self) -> None:
        # water (non-required) wholly deferred to middle card should NOT affect important
        user = User.objects.create_user(
            email="biweekly_nonrequired_deferred@example.com", password="StrongPassword123!"
        )
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water + electricity",
            amount_cents=70000,
            utility_type=UtilityType.WATER_AND_ELECTRICITY,
        )
        plan = generate_budget(user)
        august_periods = sorted(
            [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025],
            key=lambda p: p.sequence,
        )
        middle_period = august_periods[1]
        self.assertTrue(middle_period.has_deferred_items)
        self.assertFalse(middle_period.affects_important_expenses)
