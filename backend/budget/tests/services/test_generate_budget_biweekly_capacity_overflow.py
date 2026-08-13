import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory, UtilityType


class GenerateBudgetBiweeklyCapacityOverflowTest(TestCase):
    def test_biweekly_first_period_capacity_exhaustion_skips_obligation(self) -> None:
        # income=50000, debt=30000, food=30000, water=30000 — first period fills up forcing skip
        user = User.objects.create_user(email="biweekly_overflow@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
            debts=[
                {
                    "label": "Visa",
                    "current_balance_cents": 50000,
                    "minimum_payment_cents": 30000,
                    "current_payment_cents": 30000,
                }
            ],
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=30000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water",
            amount_cents=30000,
            utility_type=UtilityType.WATER,
        )
        plan = generate_budget(user)
        self.assertIsNotNone(plan.pk)
        has_deferred = plan.pay_periods.filter(has_deferred_items=True).exists()
        self.assertTrue(has_deferred)

    def test_biweekly_split_obligation_carries_to_final_period(self) -> None:
        # income=50000, debt=30000, food=40000 — food splits across periods
        user = User.objects.create_user(email="biweekly_split_carry@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=50000,
            next_pay_date=anchor,
            debts=[
                {
                    "label": "Visa",
                    "current_balance_cents": 50000,
                    "minimum_payment_cents": 30000,
                    "current_payment_cents": 30000,
                }
            ],
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        plan = generate_budget(user)
        august_periods = [p for p in plan.pay_periods.all() if p.pay_date.month == 8 and p.pay_date.year == 2025]
        total_food = sum(li.amount_cents for p in august_periods for li in p.line_items.filter(source_key="food"))
        self.assertEqual(total_food, 40000)
        split_items = [li for p in august_periods for li in p.line_items.filter(source_key="food", is_split=True)]
        self.assertTrue(len(split_items) > 0)
