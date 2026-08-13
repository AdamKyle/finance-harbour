import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile


class GenerateBudgetPayDatesTest(TestCase):
    def test_weekly_budget_generates_seven_day_pay_periods(self) -> None:
        user = User.objects.create_user(email="weekly-dates@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2025, 1, 6),
        )

        plan = generate_budget(user)
        periods = list(plan.pay_periods.order_by("sequence")[:2])

        self.assertEqual(periods[0].pay_date, datetime.date(2025, 1, 6))
        self.assertEqual(periods[1].pay_date, datetime.date(2025, 1, 13))
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2025, 1, 6)).exists())

    def test_biweekly_budget_generates_fourteen_day_pay_periods(self) -> None:
        user = User.objects.create_user(email="biweekly-dates@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2025, 1, 1),
        )

        plan = generate_budget(user)
        periods = list(plan.pay_periods.order_by("sequence")[:2])

        self.assertEqual(periods[0].pay_date, datetime.date(2025, 1, 1))
        self.assertEqual(periods[1].pay_date, datetime.date(2025, 1, 15))
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2025, 1, 1)).exists())

    def test_monthly_budget_preserves_month_end_anchor(self) -> None:
        user = User.objects.create_user(email="monthly-dates@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2025, 1, 31),
        )

        plan = generate_budget(user)
        periods = list(plan.pay_periods.order_by("sequence")[:3])

        self.assertEqual(periods[0].pay_date, datetime.date(2025, 1, 31))
        self.assertEqual(periods[1].pay_date, datetime.date(2025, 2, 28))
        self.assertEqual(periods[2].pay_date, datetime.date(2025, 3, 31))
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2025, 1, 31)).exists())
