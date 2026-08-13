import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import (
    BudgetDebtBalanceRecord,
    BudgetLineItem,
    BudgetPayPeriod,
    BudgetPlan,
    DebtBalanceReviewStatus,
    PaymentReviewStatus,
    SourceType,
)
from budget.services.debt_balance_projection_service import get_debt_balance_projections, resolve_baseline_balance
from budget.services.payday_reconciliation_service import update_line_item
from debt_profile.models import DebtProfile, ExpensePaymentTiming


class DebtBalanceProjectionServiceTest(TestCase):
    def test_recurring_debts_produce_one_projection_per_logical_source_key(self) -> None:
        owner = User.objects.create_user(email="projection-dedupe@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=owner,
            debts=[
                {"label": "Visa", "current_balance_cents": 100000},
                {"label": "LOC", "current_balance_cents": 200000},
                {"label": "Mastercard", "current_balance_cents": 300000},
            ],
        )
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=40000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=40000,
        )
        BudgetLineItem.objects.create(
            pay_period=first, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetLineItem.objects.create(
            pay_period=first, source_type=SourceType.DEBT, source_key="debt:1", title="LOC", amount_cents=20000
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.DEBT,
            source_key="debt:2",
            title="Mastercard",
            amount_cents=30000,
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:1", title="LOC", amount_cents=20000
        )
        BudgetLineItem.objects.create(
            pay_period=later,
            source_type=SourceType.DEBT,
            source_key="debt:2",
            title="Mastercard",
            amount_cents=30000,
        )

        projections = get_debt_balance_projections(later)

        self.assertEqual([projection.title for projection in projections], ["Visa", "LOC", "Mastercard"])
        self.assertEqual(len(projections), 3)

    def test_debt_first_persisted_in_later_period_is_not_applicable_to_earlier_payday(self) -> None:
        owner = User.objects.create_user(email="projection-applicability@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=owner,
            debts=[
                {"label": "Visa", "current_balance_cents": 100000},
                {"label": "Amex", "current_balance_cents": 200000},
            ],
        )
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=70000,
        )
        BudgetLineItem.objects.create(
            pay_period=first, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:1", title="Amex", amount_cents=20000
        )

        projections = get_debt_balance_projections(first)

        self.assertEqual([projection.source_key for projection in projections], ["debt:0"])
        self.assertEqual([projection.title for projection in projections], ["Visa"])

    def test_matching_index_resolves_expected_baseline(self) -> None:
        debts = [{"label": "Visa", "current_balance_cents": 845000}]

        balance = resolve_baseline_balance("debt:0", "Visa", debts)

        self.assertEqual(balance, 845000)

    def test_unique_title_fallback_resolves_moved_debt(self) -> None:
        debts = [
            {"label": "Mastercard", "current_balance_cents": 500000},
            {"label": "Visa", "current_balance_cents": 845000},
        ]

        balance = resolve_baseline_balance("debt:0", "Visa", debts)

        self.assertEqual(balance, 845000)

    def test_ambiguous_title_does_not_guess(self) -> None:
        debts = [
            {"label": "Visa", "current_balance_cents": 845000},
            {"label": "Visa", "current_balance_cents": 910000},
        ]

        balance = resolve_baseline_balance("debt:9", "Visa", debts)

        self.assertIsNone(balance)

    def test_confirmed_actual_balance_becomes_future_projection_baseline(self) -> None:
        owner = User.objects.create_user(email="projection-baseline@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=owner, debts=[{"label": "Visa", "current_balance_cents": 100000, "current_payment_cents": 10000}]
        )
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        BudgetLineItem.objects.create(
            pay_period=first, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetDebtBalanceRecord.objects.create(
            pay_period=first,
            source_key="debt:0",
            title="Visa",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=80000,
            reconciled_at=datetime.datetime(2026, 8, 1, tzinfo=datetime.UTC),
        )

        projection = get_debt_balance_projections(later)[0]

        self.assertEqual(projection.expected_balance_cents, 70000)

    def test_balance_update_does_not_modify_payment_amount(self) -> None:
        owner = User.objects.create_user(email="projection-balance-payment@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=owner, debts=[{"label": "Visa", "current_balance_cents": 100000}])
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
            left_over_cents=90000,
        )
        payment = BudgetLineItem.objects.create(
            pay_period=period, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetDebtBalanceRecord.objects.create(
            pay_period=period,
            source_key="debt:0",
            title="Visa",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=80000,
            reconciled_at=datetime.datetime(2026, 8, 1, tzinfo=datetime.UTC),
        )

        get_debt_balance_projections(period)

        payment.refresh_from_db()
        self.assertEqual(payment.amount_cents, 10000)

    def test_paid_uses_actual_payment_and_projection_never_becomes_negative(self) -> None:
        owner = User.objects.create_user(email="projection-paid@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=owner, debts=[{"label": "Visa", "current_balance_cents": 10000}])
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=5000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=20000,
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=5000
        )

        projection = get_debt_balance_projections(later)[0]

        self.assertEqual(projection.expected_balance_cents, 0)

    def test_not_paid_reduces_balance_by_zero(self) -> None:
        owner = User.objects.create_user(email="projection-not-paid@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=owner, debts=[{"label": "Visa", "current_balance_cents": 100000}])
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.NOT_PAID,
            actual_amount_cents=0,
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )

        projection = get_debt_balance_projections(later)[0]

        self.assertEqual(projection.expected_balance_cents, 100000)

    def test_unknown_payment_uses_planned_payment_and_marks_projection_uncertain(self) -> None:
        owner = User.objects.create_user(email="projection-unknown-payment@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=owner, debts=[{"label": "Visa", "current_balance_cents": 100000}])
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.UNKNOWN,
        )
        BudgetLineItem.objects.create(
            pay_period=later, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )

        projection = get_debt_balance_projections(later)[0]

        self.assertEqual(projection.expected_balance_cents, 80000)
        self.assertTrue(projection.is_uncertain)

    def test_scheduled_payment_uses_planned_payment_and_marks_projection_uncertain(self) -> None:
        owner = User.objects.create_user(email="projection-scheduled@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=owner, debts=[{"label": "Visa", "current_balance_cents": 100000}])
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.SCHEDULED,
            scheduled_amount_cents=20000,
            payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
            expected_payment_date=datetime.date(2026, 8, 12),
        )
        BudgetLineItem.objects.create(
            pay_period=later,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
        )

        projection = get_debt_balance_projections(later)[0]

        self.assertEqual(projection.expected_balance_cents, 90000)
        self.assertTrue(projection.is_uncertain)

    def test_unknown_balance_marks_projection_uncertain(self) -> None:
        owner = User.objects.create_user(email="projection-unknown-balance@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=owner, debts=[{"label": "Visa", "current_balance_cents": 100000}])
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
            left_over_cents=90000,
        )
        BudgetLineItem.objects.create(
            pay_period=period, source_type=SourceType.DEBT, source_key="debt:0", title="Visa", amount_cents=10000
        )
        BudgetDebtBalanceRecord.objects.create(
            pay_period=period,
            source_key="debt:0",
            title="Visa",
            review_status=DebtBalanceReviewStatus.UNKNOWN,
            actual_balance_cents=None,
            reconciled_at=datetime.datetime(2026, 8, 1, tzinfo=datetime.UTC),
        )

        projection = get_debt_balance_projections(period)[0]

        self.assertTrue(projection.is_uncertain)
        self.assertIsNone(projection.actual_balance_cents)

    def test_payment_update_does_not_modify_balance_record(self) -> None:
        owner = User.objects.create_user(email="projection-payment-balance@example.com", password="StrongPassword123!")
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
            left_over_cents=90000,
        )
        payment = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
        )
        balance_record = BudgetDebtBalanceRecord.objects.create(
            pay_period=period,
            source_key="debt:0",
            title="Visa",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=80000,
            reconciled_at=datetime.datetime(2026, 8, 1, tzinfo=datetime.UTC),
        )

        update_line_item(
            owner,
            period.id,
            payment.id,
            PaymentReviewStatus.PAID,
            12000,
            None,
            datetime.date(2026, 8, 9),
        )

        balance_record.refresh_from_db()
        self.assertEqual(balance_record.actual_balance_cents, 80000)

    def test_later_confirmed_balance_resets_future_factual_baseline(self) -> None:
        owner = User.objects.create_user(email="projection-reset@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=owner, debts=[{"label": "Visa", "current_balance_cents": 100000}])
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        reset_period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        future = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=2,
            pay_date=datetime.date(2026, 10, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=90000,
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
        )
        BudgetLineItem.objects.create(
            pay_period=reset_period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
        )
        BudgetLineItem.objects.create(
            pay_period=future,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=10000,
        )
        BudgetDebtBalanceRecord.objects.create(
            pay_period=reset_period,
            source_key="debt:0",
            title="Visa",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=50000,
            reconciled_at=datetime.datetime(2026, 9, 1, tzinfo=datetime.UTC),
        )

        projection = get_debt_balance_projections(future)[0]

        self.assertEqual(projection.expected_balance_cents, 40000)
