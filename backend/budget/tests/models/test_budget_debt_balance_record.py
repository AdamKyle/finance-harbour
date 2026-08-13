import datetime

from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User
from budget.models import (
    BudgetDebtBalanceRecord,
    BudgetPayPeriod,
    BudgetPlan,
    DebtBalanceReviewStatus,
)


class BudgetDebtBalanceRecordTest(TestCase):
    def test_confirmed_record_creation_and_ownership_relationship(self) -> None:
        owner = User.objects.create_user(email="debt-record@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )

        record = BudgetDebtBalanceRecord.objects.create(
            pay_period=period,
            source_key="debt:0",
            title="Visa",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=500000,
            reconciled_at=datetime.datetime(2026, 1, 2, tzinfo=datetime.UTC),
        )

        self.assertEqual(record.pay_period.plan.user, owner)
        self.assertEqual(str(record), f"BudgetDebtBalanceRecord({period.id}, debt:0)")

    def test_period_and_source_key_are_unique(self) -> None:
        owner = User.objects.create_user(email="debt-unique@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        BudgetDebtBalanceRecord.objects.create(
            pay_period=period,
            source_key="debt:0",
            title="Visa",
            review_status=DebtBalanceReviewStatus.UNKNOWN,
            actual_balance_cents=None,
            reconciled_at=datetime.datetime(2026, 1, 2, tzinfo=datetime.UTC),
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetDebtBalanceRecord.objects.create(
                pay_period=period,
                source_key="debt:0",
                title="Visa",
                review_status=DebtBalanceReviewStatus.UNKNOWN,
                actual_balance_cents=None,
                reconciled_at=datetime.datetime(2026, 1, 3, tzinfo=datetime.UTC),
            )

    def test_confirmed_requires_non_negative_actual_balance(self) -> None:
        owner = User.objects.create_user(email="debt-confirmed@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetDebtBalanceRecord.objects.create(
                pay_period=period,
                source_key="debt:0",
                title="Visa",
                review_status=DebtBalanceReviewStatus.CONFIRMED,
                actual_balance_cents=None,
                reconciled_at=datetime.datetime(2026, 1, 2, tzinfo=datetime.UTC),
            )

    def test_unknown_requires_null_actual_balance(self) -> None:
        owner = User.objects.create_user(email="debt-unknown-model@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetDebtBalanceRecord.objects.create(
                pay_period=period,
                source_key="debt:0",
                title="Visa",
                review_status=DebtBalanceReviewStatus.UNKNOWN,
                actual_balance_cents=500000,
                reconciled_at=datetime.datetime(2026, 1, 2, tzinfo=datetime.UTC),
            )
