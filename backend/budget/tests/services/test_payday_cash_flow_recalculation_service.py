import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import (
    BudgetLineItem,
    BudgetPayPeriod,
    BudgetPlan,
    PayChequeReviewStatus,
    PaymentReviewStatus,
    SourceType,
)
from budget.services.budget_mutation_service import recalculate_periods
from debt_profile.models import ExpensePaymentTiming


class PaydayCashFlowRecalculationServiceTest(TestCase):
    def test_paid_actual_higher_than_planned_decreases_left_over(self) -> None:
        owner = User.objects.create_user(email="cash-higher@example.com", password="StrongPassword123!")
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
            left_over_cents=50000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:higher",
            title="Power",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=60000,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertEqual(period.left_over_cents, 40000)

    def test_paid_actual_lower_than_planned_increases_left_over(self) -> None:
        owner = User.objects.create_user(email="cash-lower@example.com", password="StrongPassword123!")
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
            left_over_cents=50000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:lower",
            title="Power",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=40000,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertEqual(period.left_over_cents, 60000)

    def test_not_paid_uses_zero_outflow_and_increases_left_over(self) -> None:
        owner = User.objects.create_user(email="cash-not-paid@example.com", password="StrongPassword123!")
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
            left_over_cents=50000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:not-paid",
            title="Power",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.NOT_PAID,
            actual_amount_cents=0,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertEqual(period.total_bills_cents, 0)
        self.assertEqual(period.left_over_cents, 100000)

    def test_scheduled_keeps_planned_obligation_reserved(self) -> None:
        owner = User.objects.create_user(email="cash-scheduled@example.com", password="StrongPassword123!")
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
            left_over_cents=50000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:scheduled",
            title="Insurance",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.SCHEDULED,
            scheduled_amount_cents=50000,
            payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
            expected_payment_date=datetime.date(2026, 8, 12),
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertEqual(period.total_bills_cents, 50000)
        self.assertEqual(period.left_over_cents, 50000)

    def test_changed_scheduled_amount_is_reserved_and_carries_forward(self) -> None:
        owner = User.objects.create_user(email="cash-scheduled-change@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=50000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 15),
            pay_cheque_cents=100000,
            total_available_cents=150000,
            left_over_cents=150000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:scheduled-change",
            title="Insurance",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.SCHEDULED,
            scheduled_amount_cents=60000,
            payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
            expected_payment_date=datetime.date(2026, 8, 12),
        )

        recalculate_periods([period, later])

        period.refresh_from_db()
        later.refresh_from_db()
        self.assertEqual(period.total_bills_cents, 60000)
        self.assertEqual(period.left_over_cents, 40000)
        self.assertEqual(later.carried_left_over_cents, 40000)

    def test_unknown_keeps_planned_obligation_reserved(self) -> None:
        owner = User.objects.create_user(email="cash-unknown@example.com", password="StrongPassword123!")
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
            left_over_cents=50000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:unknown",
            title="Power",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.UNKNOWN,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertEqual(period.total_bills_cents, 50000)

    def test_actual_pay_cheque_updates_effective_available_funds(self) -> None:
        owner = User.objects.create_user(email="cash-pay@example.com", password="StrongPassword123!")
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
            actual_pay_cheque_cents=120000,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertEqual(period.total_available_cents, 120000)
        self.assertEqual(period.left_over_cents, 120000)

    def test_actual_pay_change_propagates_into_later_period_carry(self) -> None:
        owner = User.objects.create_user(email="cash-pay-carry@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=120000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 15),
            pay_cheque_cents=100000,
            total_available_cents=200000,
            left_over_cents=200000,
        )

        recalculate_periods([first, later])

        later.refresh_from_db()
        self.assertEqual(later.carried_left_over_cents, 120000)
        self.assertEqual(later.total_available_cents, 220000)

    def test_actual_line_item_change_propagates_into_later_period_carry(self) -> None:
        owner = User.objects.create_user(email="cash-item-carry@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=50000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 15),
            pay_cheque_cents=100000,
            total_available_cents=150000,
            left_over_cents=150000,
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:carry",
            title="Power",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=40000,
        )

        recalculate_periods([first, later])

        later.refresh_from_db()
        self.assertEqual(later.carried_left_over_cents, 60000)

    def test_manual_total_override_remains_authoritative(self) -> None:
        owner = User.objects.create_user(email="cash-manual@example.com", password="StrongPassword123!")
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
            total_available_cents=777000,
            total_available_is_manual=True,
            left_over_cents=777000,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=120000,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertEqual(period.total_available_cents, 777000)

    def test_future_planned_history_does_not_overwrite_historical_actuals(self) -> None:
        owner = User.objects.create_user(email="cash-history@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        historical = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=90000,
            left_over_cents=90000,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=90000,
        )
        future = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 15),
            pay_cheque_cents=150000,
            total_available_cents=240000,
            left_over_cents=240000,
        )

        recalculate_periods([historical, future])

        historical.refresh_from_db()
        self.assertEqual(historical.actual_pay_cheque_cents, 90000)
        self.assertEqual(historical.total_available_cents, 90000)
