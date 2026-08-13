import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import (
    BudgetLineItem,
    BudgetPayPeriod,
    BudgetPlan,
    PayChequeReviewStatus,
    PaydayReconciliationStatus,
    PaymentReviewStatus,
    SourceType,
)
from budget.services.payday_reconciliation_service import (
    mark_payday_incomplete,
    recalculate_reconciliation_status,
)
from debt_profile.models import ExpensePaymentTiming


class PaydayReconciliationStatusServiceTest(TestCase):
    def test_untouched_period_is_not_started(self) -> None:
        owner = User.objects.create_user(email="status-new@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=10000,
        )

        recalculate_reconciliation_status(period)

        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.NOT_STARTED)
        self.assertIsNone(period.payday_reconciliation_started_at)
        self.assertIsNone(period.payday_reconciliation_completed_at)

    def test_partially_reviewed_period_is_in_progress(self) -> None:
        owner = User.objects.create_user(email="status-partial@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=100000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=10000,
        )

        recalculate_reconciliation_status(period)

        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.IN_PROGRESS)
        self.assertIsNotNone(period.payday_reconciliation_started_at)
        self.assertIsNone(period.payday_reconciliation_completed_at)

    def test_all_known_facts_make_period_reviewed(self) -> None:
        owner = User.objects.create_user(email="status-reviewed@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=100000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=10000,
        )

        recalculate_reconciliation_status(period)

        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.REVIEWED)
        self.assertIsNotNone(period.payday_reconciliation_completed_at)

    def test_unknown_fact_makes_addressed_period_incomplete(self) -> None:
        owner = User.objects.create_user(email="status-unknown@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            pay_cheque_review_status=PayChequeReviewStatus.UNKNOWN,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.NOT_PAID,
            actual_amount_cents=0,
        )

        recalculate_reconciliation_status(period)

        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.INCOMPLETE)
        self.assertIsNotNone(period.payday_reconciliation_completed_at)

    def test_scheduled_fact_is_addressed_and_period_can_be_reviewed(self) -> None:
        owner = User.objects.create_user(email="status-scheduled@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=100000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="insurance",
            title="Insurance",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.SCHEDULED,
            scheduled_amount_cents=10000,
            payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
            expected_payment_date=datetime.date(2026, 8, 12),
        )

        recalculate_reconciliation_status(period)

        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.REVIEWED)

    def test_correcting_unknown_fact_changes_incomplete_to_reviewed(self) -> None:
        owner = User.objects.create_user(email="status-repair@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            payday_reconciliation_status=PaydayReconciliationStatus.INCOMPLETE,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=100000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=10000,
        )

        recalculate_reconciliation_status(period)

        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.REVIEWED)

    def test_mark_incomplete_preserves_known_values_and_marks_unresolved_unknown(self) -> None:
        owner = User.objects.create_user(email="status-mark@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=110000,
        )
        known = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=9000,
        )
        unresolved = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:2",
            title="Water",
            amount_cents=5000,
        )

        mark_payday_incomplete(owner, period.id, datetime.date(2026, 8, 9))

        period.refresh_from_db()
        known.refresh_from_db()
        unresolved.refresh_from_db()
        self.assertEqual(period.actual_pay_cheque_cents, 110000)
        self.assertEqual(known.actual_amount_cents, 9000)
        self.assertEqual(unresolved.payment_review_status, PaymentReviewStatus.UNKNOWN)
