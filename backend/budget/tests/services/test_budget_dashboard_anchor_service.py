import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan, PaydayReconciliationStatus
from budget.services.budget_dashboard_anchor_service import get_budget_dashboard_anchor


class BudgetDashboardAnchorServiceTest(TestCase):
    def test_oldest_eligible_unresolved_period_is_default_anchor(self) -> None:
        owner = User.objects.create_user(email="anchor-unresolved@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED,
        )
        unresolved = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 2, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )

        anchor = get_budget_dashboard_anchor(
            plan.pay_periods.all(),
            datetime.date(2026, 3, 1),
            6,
        )

        self.assertEqual(anchor.period_id, unresolved.id)
        self.assertEqual(anchor.page, 1)

    def test_current_historical_period_is_used_when_no_unresolved_exists(self) -> None:
        owner = User.objects.create_user(email="anchor-current@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        current = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 2, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED,
        )

        anchor = get_budget_dashboard_anchor(
            plan.pay_periods.all(),
            datetime.date(2026, 2, 15),
            6,
        )

        self.assertEqual(anchor.period_id, current.id)

    def test_nearest_future_period_is_used_when_history_does_not_exist(self) -> None:
        owner = User.objects.create_user(email="anchor-future@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 3, 1),
            end_date=datetime.date(2027, 3, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        future = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 3, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )

        anchor = get_budget_dashboard_anchor(
            plan.pay_periods.all(),
            datetime.date(2026, 2, 15),
            6,
        )

        self.assertEqual(anchor.period_id, future.id)

    def test_latest_historical_period_is_used_when_plan_has_ended(self) -> None:
        owner = User.objects.create_user(email="anchor-history@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2026, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 11, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED,
        )
        latest = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2025, 12, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED,
        )

        anchor = get_budget_dashboard_anchor(
            plan.pay_periods.all(),
            datetime.date(2026, 8, 10),
            6,
        )

        self.assertEqual(anchor.period_id, latest.id)

    def test_unowned_requested_anchor_falls_back_without_disclosure(self) -> None:
        jane = User.objects.create_user(email="anchor-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="anchor-bob@example.com", password="StrongPassword123!")
        jane_plan = BudgetPlan.objects.create(
            user=jane,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        bob_plan = BudgetPlan.objects.create(
            user=bob,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        jane_period = BudgetPayPeriod.objects.create(
            plan=jane_plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        bob_period = BudgetPayPeriod.objects.create(
            plan=bob_plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )

        anchor = get_budget_dashboard_anchor(
            bob_plan.pay_periods.all(),
            datetime.date(2026, 1, 2),
            6,
            jane_period.id,
        )

        self.assertEqual(anchor.period_id, bob_period.id)
