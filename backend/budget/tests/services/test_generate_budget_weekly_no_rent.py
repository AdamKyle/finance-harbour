import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class GenerateBudgetWeeklyNoRentTest(TestCase):
    def test_weekly_with_no_rent_allocates_all_non_rent_to_first_periods(self) -> None:
        user = User.objects.create_user(email="weekly_norent@example.com", password="StrongPassword123!")
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
            amount_cents=40000,
        )
        plan = generate_budget(user)
        self.assertEqual(plan.pay_periods.count(), 53)
        total_food = sum(
            li.amount_cents for period in plan.pay_periods.all() for li in period.line_items.filter(source_key="food")
        )
        # 53 weekly periods span 13 calendar months but obligations only apply to the first 12
        self.assertEqual(total_food, 40000 * 12)
