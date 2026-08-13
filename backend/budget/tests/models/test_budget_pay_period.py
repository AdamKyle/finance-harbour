import datetime

from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan, PayChequeReviewStatus


class BudgetPayPeriodTest(TestCase):
    def test_str_returns_plan_id_and_sequence(self) -> None:
        user = User.objects.create_user(email="period_str@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )
        self.assertEqual(str(period), f"BudgetPayPeriod({plan.pk}, seq=0)")

    def test_confirmed_pay_cheque_requires_actual_amount(self) -> None:
        user = User.objects.create_user(email="period-confirmed@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=0,
                pay_date=datetime.date(2025, 8, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=300000,
                pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
                actual_pay_cheque_cents=None,
            )

    def test_unknown_pay_cheque_requires_null_actual_amount(self) -> None:
        user = User.objects.create_user(email="period-unknown@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=0,
                pay_date=datetime.date(2025, 8, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=300000,
                pay_cheque_review_status=PayChequeReviewStatus.UNKNOWN,
                actual_pay_cheque_cents=300000,
            )
