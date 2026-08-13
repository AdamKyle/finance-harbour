import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import BudgetLineItem, BudgetPayPeriod, BudgetPlan, PaymentReviewStatus, SourceType
from budget.services.budget_mutation_service import recalculate_periods
from budget.services.payday_warning_service import build_recalculation_warnings


class PaydayImportantRiskServiceTest(TestCase):
    def test_important_not_paid_creates_missed_important_risk(self) -> None:
        owner = User.objects.create_user(email="risk-not-paid@example.com", password="StrongPassword123!")
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
            source_key="bill:important",
            title="Power",
            amount_cents=50000,
            is_required=True,
            payment_review_status=PaymentReviewStatus.NOT_PAID,
            actual_amount_cents=0,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertTrue(period.has_missed_important_expenses)

    def test_important_underpayment_creates_missed_important_risk(self) -> None:
        owner = User.objects.create_user(email="risk-underpaid@example.com", password="StrongPassword123!")
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
            source_key="bill:underpaid",
            title="Power",
            amount_cents=50000,
            is_required=True,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=40000,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertTrue(period.has_missed_important_expenses)

    def test_unknown_does_not_assert_missed_important_payment(self) -> None:
        owner = User.objects.create_user(email="risk-unknown@example.com", password="StrongPassword123!")
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
            source_key="bill:unknown-important",
            title="Power",
            amount_cents=50000,
            is_required=True,
            payment_review_status=PaymentReviewStatus.UNKNOWN,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertFalse(period.has_missed_important_expenses)

    def test_existing_deferred_important_semantics_remain(self) -> None:
        owner = User.objects.create_user(email="risk-deferred@example.com", password="StrongPassword123!")
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
            has_deferred_important_expenses=True,
        )

        recalculate_periods([period])

        period.refresh_from_db()
        self.assertTrue(period.affects_important_expenses)

    def test_earlier_reconciliation_change_can_create_later_financial_risk(self) -> None:
        owner = User.objects.create_user(email="risk-later@example.com", password="StrongPassword123!")
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
        )
        later = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 15),
            pay_cheque_cents=10000,
            total_available_cents=110000,
            left_over_cents=10000,
        )
        BudgetLineItem.objects.create(
            pay_period=first,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:first",
            title="Power",
            amount_cents=50000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=120000,
        )
        BudgetLineItem.objects.create(
            pay_period=later,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:later",
            title="Rent",
            amount_cents=100000,
            is_required=True,
        )

        recalculate_periods([first, later])

        later.refresh_from_db()
        self.assertTrue(later.has_negative_left_over)
        self.assertTrue(later.affects_important_expenses)

    def test_financial_risk_flags_produce_factual_warning_for_card_logic(self) -> None:
        owner = User.objects.create_user(email="risk-warning@example.com", password="StrongPassword123!")
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
            source_key="bill:warning",
            title="Power",
            amount_cents=50000,
            is_required=True,
            payment_review_status=PaymentReviewStatus.NOT_PAID,
            actual_amount_cents=0,
        )
        recalculate_periods([period])
        period.refresh_from_db()

        warnings = build_recalculation_warnings([period])

        self.assertEqual(warnings[0].warning_type, "IMPORTANT_PAYMENT_MISSED_OR_UNDERPAID")
        self.assertEqual(warnings[0].important_titles, ["Power"])
        self.assertIsNone(warnings[0].amount_cents)
