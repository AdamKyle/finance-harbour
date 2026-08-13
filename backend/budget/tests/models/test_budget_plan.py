import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import BudgetPlan


class BudgetPlanStrTest(TestCase):
    def test_str_returns_user_id(self) -> None:
        user = User.objects.create_user(email="plan_str@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        self.assertEqual(str(plan), f"BudgetPlan({user.pk})")
