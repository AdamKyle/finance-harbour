import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class GenerateBudgetWeeklyTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="budget_weekly@example.com", password="StrongPassword123!")
        self.anchor = datetime.date(2025, 8, 4)
        self.debt_profile = DebtProfile.objects.create(
            user=self.user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=self.anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=self.debt_profile,
            source_key="rent_or_mortgage",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent or mortgage",
            amount_cents=80000,
        )
        RecurringExpense.objects.create(
            debt_profile=self.debt_profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=20000,
        )

    def test_creates_53_pay_periods(self) -> None:
        plan = generate_budget(self.user)
        self.assertEqual(plan.pay_periods.count(), 53)

    def test_rent_appears_on_last_weekly_in_month(self) -> None:
        plan = generate_budget(self.user)
        august_periods = [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025]
        last_august = max(august_periods, key=lambda p: p.pay_date)
        rent_items = last_august.line_items.filter(source_type=SourceType.RENT_OR_MORTGAGE)
        self.assertEqual(rent_items.count(), 1)

    def test_rent_does_not_appear_on_non_final_weekly_in_month(self) -> None:
        plan = generate_budget(self.user)
        august_periods = [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025]
        last_august = max(august_periods, key=lambda p: p.pay_date)
        for period in august_periods:
            if period.pay_date == last_august.pay_date:
                continue
            rent_items = period.line_items.filter(source_type=SourceType.RENT_OR_MORTGAGE)
            self.assertEqual(rent_items.count(), 0)

    def test_has_deferred_items_when_split_occurs(self) -> None:
        user = User.objects.create_user(email="weekly_split@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 4)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=80000,
        )
        plan = generate_budget(user)
        has_deferred = plan.pay_periods.filter(has_deferred_items=True).exists()
        self.assertTrue(has_deferred)

    def test_sequences_are_unique_within_plan(self) -> None:
        plan = generate_budget(self.user)
        sequences = list(plan.pay_periods.values_list("sequence", flat=True))
        self.assertEqual(len(sequences), len(set(sequences)))

    def test_periods_sorted_by_sequence(self) -> None:
        plan = generate_budget(self.user)
        sequences = list(plan.pay_periods.values_list("sequence", flat=True))
        self.assertEqual(sequences, sorted(sequences))
