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


class GenerateBudgetDeferredWeeklyTest(TestCase):
    def test_weekly_item_wholly_on_second_card_is_deferred(self) -> None:
        user = User.objects.create_user(email="weekly_second_card_deferred@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 4)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=30000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water",
            amount_cents=30000,
            utility_type=UtilityType.WATER,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=30000,
        )
        plan = generate_budget(user)
        august_periods = sorted(
            [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025],
            key=lambda p: p.sequence,
        )
        food_on_second = august_periods[1].line_items.filter(source_key="food")
        self.assertTrue(food_on_second.exists())
        self.assertTrue(august_periods[1].has_deferred_items)

    def test_weekly_item_on_first_card_is_not_deferred(self) -> None:
        user = User.objects.create_user(
            email="weekly_first_card_not_deferred@example.com", password="StrongPassword123!"
        )
        anchor = datetime.date(2025, 8, 4)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=20000,
        )
        plan = generate_budget(user)
        august_periods = sorted(
            [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025],
            key=lambda p: p.sequence,
        )
        first_period = august_periods[0]
        self.assertFalse(first_period.has_deferred_items)

    def test_debt_is_deferred_after_required_expense_uses_first_period_funds(self) -> None:
        user = User.objects.create_user(email="weekly_deferred_debt@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 4)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=30000,
            next_pay_date=anchor,
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "minimum_payment_cents": 15000,
                    "current_payment_cents": 15000,
                }
            ],
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Electricity",
            amount_cents=30000,
            utility_type=UtilityType.ELECTRICITY,
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            title="Electricity",
            amount_cents=30000,
        )
        plan = generate_budget(user)
        august_periods = sorted(
            [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025],
            key=lambda p: p.sequence,
        )

        first_electricity = august_periods[0].line_items.get(source_key="utilities")
        deferred_debt_periods = [
            period for period in august_periods if period.line_items.filter(source_key="debt:0").exists()
        ]

        self.assertEqual(first_electricity.amount_cents, 30000)
        self.assertEqual(len(deferred_debt_periods), 1)
        self.assertEqual(deferred_debt_periods[0].sequence, august_periods[1].sequence)
        self.assertTrue(deferred_debt_periods[0].has_deferred_items)
        self.assertFalse(deferred_debt_periods[0].has_deferred_important_expenses)

    def test_non_required_deferred_item_does_not_mark_affects_important(self) -> None:
        user = User.objects.create_user(email="weekly_nonrequired_deferred@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 4)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=30000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water",
            amount_cents=10000,
            utility_type=UtilityType.WATER,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=30000,
        )
        plan = generate_budget(user)
        august_periods = sorted(
            [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025],
            key=lambda p: p.sequence,
        )
        second_period = august_periods[1]
        food_on_second = second_period.line_items.filter(source_key="food")
        self.assertTrue(food_on_second.exists())
        self.assertFalse(second_period.affects_important_expenses)
        self.assertFalse(second_period.has_deferred_important_expenses)

    def test_split_first_fragment_is_not_deferred(self) -> None:
        user = User.objects.create_user(
            email="weekly_split_first_not_deferred@example.com", password="StrongPassword123!"
        )
        anchor = datetime.date(2025, 8, 4)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Electricity",
            amount_cents=60000,
            utility_type=UtilityType.ELECTRICITY,
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            title="Electricity",
            amount_cents=60000,
        )
        plan = generate_budget(user)
        august_periods = sorted(
            [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025],
            key=lambda p: p.sequence,
        )
        first_elec = list(august_periods[0].line_items.filter(source_key="utilities"))
        self.assertEqual(len(first_elec), 1)
        self.assertTrue(first_elec[0].is_split)
        self.assertFalse(august_periods[0].affects_important_expenses)
        second_elec = list(august_periods[1].line_items.filter(source_key="utilities"))
        self.assertEqual(len(second_elec), 1)
        self.assertTrue(second_elec[0].is_split)
        self.assertTrue(august_periods[1].affects_important_expenses)
