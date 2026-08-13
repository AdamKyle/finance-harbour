import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import BudgetPlan, SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class GenerateBudgetMonthlyTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="budget_monthly@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        self.debt_profile = DebtProfile.objects.create(
            user=self.user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=anchor,
            left_over_warning_amount_cents=10000,
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
            amount_cents=50000,
        )

    def test_creates_budget_plan_for_user(self) -> None:
        plan = generate_budget(self.user)
        self.assertIsNotNone(plan.pk)
        self.assertEqual(plan.user, self.user)
        self.assertEqual(plan.pay_period_type, "MONTHLY")

    def test_creates_12_pay_periods(self) -> None:
        plan = generate_budget(self.user)
        self.assertEqual(plan.pay_periods.count(), 12)

    def test_line_items_created_for_each_period(self) -> None:
        plan = generate_budget(self.user)
        for period in plan.pay_periods.all():
            self.assertGreater(period.line_items.count(), 0)

    def test_monthly_puts_full_rent_on_every_period(self) -> None:
        plan = generate_budget(self.user)
        for period in plan.pay_periods.all():
            rent_items = period.line_items.filter(source_type=SourceType.RENT_OR_MORTGAGE)
            self.assertEqual(rent_items.count(), 1)
            self.assertEqual(rent_items.first().amount_cents, 100000)

    def test_left_over_calculation_is_correct(self) -> None:
        plan = generate_budget(self.user)
        first = plan.pay_periods.first()
        expected_left_over = 300000 - 100000 - 50000
        self.assertEqual(first.left_over_cents, expected_left_over)

    def test_carried_left_over_propagates(self) -> None:
        plan = generate_budget(self.user)
        periods = list(plan.pay_periods.all())
        expected_carry = 300000 - 100000 - 50000
        self.assertEqual(periods[1].carried_left_over_cents, expected_carry)

    def test_period_is_below_warning_threshold(self) -> None:
        user = User.objects.create_user(email="monthly_below_warn@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=105000,
            next_pay_date=anchor,
            left_over_warning_amount_cents=20000,
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
        self.assertTrue(first.is_below_warning_threshold)

    def test_period_not_below_threshold_when_threshold_is_zero(self) -> None:
        plan = generate_budget(self.user)
        first = plan.pay_periods.first()
        self.assertFalse(first.is_below_warning_threshold)

    def test_regenerating_deletes_old_plan(self) -> None:
        generate_budget(self.user)
        generate_budget(self.user)
        self.assertEqual(BudgetPlan.objects.filter(user=self.user).count(), 1)

    def test_plan_start_date_equals_anchor(self) -> None:
        plan = generate_budget(self.user)
        self.assertEqual(plan.start_date, datetime.date(2025, 8, 1))

    def test_total_bills_cents_equals_sum_of_line_items(self) -> None:
        plan = generate_budget(self.user)
        for period in plan.pay_periods.all():
            expected = sum(li.amount_cents for li in period.line_items.all())
            self.assertEqual(period.total_bills_cents, expected)

    def test_total_available_equals_income_plus_carry(self) -> None:
        plan = generate_budget(self.user)
        for period in plan.pay_periods.all():
            self.assertEqual(
                period.total_available_cents,
                period.pay_cheque_cents + period.carried_left_over_cents,
            )
