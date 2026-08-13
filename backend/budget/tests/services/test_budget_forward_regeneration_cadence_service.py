import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_forward_regeneration_service import regenerate_budget_from_pay_period
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile


class BudgetForwardRegenerationCadenceServiceTest(TestCase):
    def test_weekly_regeneration_keeps_earlier_period_and_anchors_forward_dates(self) -> None:
        user = User.objects.create_user(email="weekly-forward@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 14),
        )
        plan = generate_budget(user)
        original_periods = list(plan.pay_periods.order_by("sequence")[:4])

        regenerated = regenerate_budget_from_pay_period(user, original_periods[1].id, datetime.date(2026, 8, 22))
        dates = list(plan.pay_periods.order_by("sequence").values_list("pay_date", flat=True)[:4])

        self.assertEqual(regenerated.id, original_periods[1].id)
        self.assertEqual(
            dates,
            [
                datetime.date(2026, 8, 14),
                datetime.date(2026, 8, 22),
                datetime.date(2026, 8, 29),
                datetime.date(2026, 9, 5),
            ],
        )
        self.assertEqual(plan.pay_periods.get(sequence=0).id, original_periods[0].id)

    def test_biweekly_regeneration_keeps_earlier_period_and_anchors_forward_dates(self) -> None:
        user = User.objects.create_user(email="biweekly-forward@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        plan = generate_budget(user)
        original_periods = list(plan.pay_periods.order_by("sequence")[:4])

        regenerate_budget_from_pay_period(user, original_periods[1].id, datetime.date(2026, 9, 5))
        dates = list(plan.pay_periods.order_by("sequence").values_list("pay_date", flat=True)[:4])

        self.assertEqual(
            dates,
            [
                datetime.date(2026, 8, 21),
                datetime.date(2026, 9, 5),
                datetime.date(2026, 9, 19),
                datetime.date(2026, 10, 3),
            ],
        )
        self.assertEqual(plan.pay_periods.get(sequence=0).id, original_periods[0].id)

    def test_monthly_regeneration_preserves_month_end_advancement(self) -> None:
        user = User.objects.create_user(email="monthly-forward@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 12, 30),
        )
        plan = generate_budget(user)
        original_periods = list(plan.pay_periods.order_by("sequence")[:4])

        regenerate_budget_from_pay_period(user, original_periods[1].id, datetime.date(2027, 1, 31))
        dates = list(plan.pay_periods.order_by("sequence").values_list("pay_date", flat=True)[:4])

        self.assertEqual(
            dates,
            [
                datetime.date(2026, 12, 30),
                datetime.date(2027, 1, 31),
                datetime.date(2027, 2, 28),
                datetime.date(2027, 3, 31),
            ],
        )

    def test_monthly_regeneration_anchors_normal_calendar_day(self) -> None:
        user = User.objects.create_user(email="monthly-normal-forward@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 9, 15),
        )
        plan = generate_budget(user)
        original_periods = list(plan.pay_periods.order_by("sequence")[:4])

        regenerate_budget_from_pay_period(user, original_periods[1].id, datetime.date(2026, 10, 16))
        dates = list(plan.pay_periods.order_by("sequence").values_list("pay_date", flat=True)[:4])

        self.assertEqual(
            dates,
            [
                datetime.date(2026, 9, 15),
                datetime.date(2026, 10, 16),
                datetime.date(2026, 11, 16),
                datetime.date(2026, 12, 16),
            ],
        )

    def test_first_period_change_updates_plan_and_profile_anchors(self) -> None:
        user = User.objects.create_user(email="first-forward@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        plan = generate_budget(user)
        first_period = plan.pay_periods.order_by("sequence").first()

        regenerate_budget_from_pay_period(user, first_period.id, datetime.date(2026, 8, 22))
        profile.refresh_from_db()
        plan.refresh_from_db()

        self.assertEqual(profile.next_pay_date, datetime.date(2026, 8, 22))
        self.assertEqual(plan.start_date, datetime.date(2026, 8, 22))
        self.assertEqual(plan.pay_periods.order_by("sequence").first().pay_date, datetime.date(2026, 8, 22))
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2026, 8, 22)).exists())
