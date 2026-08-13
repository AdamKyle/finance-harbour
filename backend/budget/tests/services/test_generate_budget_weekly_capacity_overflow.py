import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory, UtilityType


class GenerateBudgetWeeklyCapacityOverflowTest(TestCase):
    def test_weekly_first_period_capacity_exhaustion_skips_obligation(self) -> None:
        # income=50000, food=30000, water=30000, electricity=30000 — periods fill up forcing skip
        user = User.objects.create_user(email="weekly_overflow@example.com", password="StrongPassword123!")
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
            amount_cents=30000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water + electricity",
            amount_cents=60000,
            utility_type=UtilityType.WATER_AND_ELECTRICITY,
        )
        plan = generate_budget(user)
        self.assertIsNotNone(plan.pk)
        has_deferred = plan.pay_periods.filter(has_deferred_items=True).exists()
        self.assertTrue(has_deferred)
