import datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.models import User
from budget.services.budget_forward_regeneration_service import regenerate_budget_from_pay_period
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile


class BudgetForwardRegenerationValidationServiceTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="forward-validation@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=self.user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        self.plan = generate_budget(self.user)
        self.periods = list(self.plan.pay_periods.order_by("sequence")[:4])

    def test_date_equal_to_previous_period_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            regenerate_budget_from_pay_period(
                self.user,
                self.periods[1].id,
                self.periods[0].pay_date,
            )

        self.assertEqual(self.plan.pay_periods.get(id=self.periods[1].id).pay_date, self.periods[1].pay_date)

    def test_date_before_previous_period_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            regenerate_budget_from_pay_period(
                self.user,
                self.periods[1].id,
                datetime.date(2026, 8, 20),
            )

        self.assertEqual(self.plan.pay_periods.get(id=self.periods[1].id).pay_date, self.periods[1].pay_date)

    def test_duplicate_later_period_date_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            regenerate_budget_from_pay_period(
                self.user,
                self.periods[1].id,
                self.periods[2].pay_date,
            )

        self.assertEqual(self.plan.pay_periods.get(id=self.periods[1].id).pay_date, self.periods[1].pay_date)

    def test_first_period_date_before_today_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            regenerate_budget_from_pay_period(
                self.user,
                self.periods[0].id,
                timezone.localdate() - datetime.timedelta(days=1),
            )

        self.assertEqual(self.plan.pay_periods.get(id=self.periods[0].id).pay_date, self.periods[0].pay_date)
