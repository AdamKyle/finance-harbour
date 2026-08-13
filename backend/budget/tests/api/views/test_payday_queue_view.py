import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan, PaydayReconciliationStatus
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile


class PaydayQueueViewTest(APITestCase):
    def test_generated_plan_has_no_payday_backlog_before_selected_first_payday(self) -> None:
        owner = User.objects.create_user(email="queue-not-started@example.com", password="StrongPassword123!")
        selected_payday = timezone.localdate() + datetime.timedelta(days=7)
        DebtProfile.objects.create(
            user=owner,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=selected_payday,
        )
        plan = generate_budget(owner)
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unresolved_count"], 0)
        self.assertEqual(response.data["unresolved_periods"], [])
        self.assertEqual(response.data["next_future_pay_date"], selected_payday.isoformat())
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=selected_payday).exists())

    def test_selected_first_payday_is_reviewable_on_its_pay_date(self) -> None:
        owner = User.objects.create_user(email="queue-first-today@example.com", password="StrongPassword123!")
        selected_payday = timezone.localdate()
        DebtProfile.objects.create(
            user=owner,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=selected_payday,
        )
        plan = generate_budget(owner)
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unresolved_count"], 1)
        self.assertEqual(response.data["oldest_unresolved_period"]["pay_date"], selected_payday.isoformat())
        self.assertEqual(plan.pay_periods.order_by("sequence").first().pay_date, selected_payday)

    def test_unresolved_first_payday_becomes_catch_up_after_its_pay_date(self) -> None:
        owner = User.objects.create_user(email="queue-first-past@example.com", password="StrongPassword123!")
        selected_payday = timezone.localdate() - datetime.timedelta(days=1)
        DebtProfile.objects.create(
            user=owner,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
            next_pay_date=selected_payday,
        )
        plan = generate_budget(owner)
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unresolved_count"], 1)
        self.assertEqual(response.data["oldest_unresolved_period"]["pay_date"], selected_payday.isoformat())
        self.assertEqual(plan.pay_periods.count(), 12)

    def test_owner_receives_own_unresolved_periods_oldest_first(self) -> None:
        owner = User.objects.create_user(email="queue-owner@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 7, 1),
            end_date=datetime.date(2027, 7, 1),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        newer = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 7),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        older = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 7, 24),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {
                "effective_date",
                "unresolved_count",
                "unresolved_periods",
                "oldest_unresolved_period",
                "next_future_pay_date",
            },
        )
        self.assertEqual(
            [period["id"] for period in response.data["unresolved_periods"]],
            [older.id, newer.id],
        )
        self.assertEqual(
            set(response.data["unresolved_periods"][0]),
            {
                "id",
                "pay_date",
                "payday_reconciliation_status",
                "pay_cheque_review_status",
            },
        )
        self.assertEqual(response.data["oldest_unresolved_period"]["id"], older.id)

    def test_future_period_is_excluded_and_returned_as_next_future_date(self) -> None:
        owner = User.objects.create_user(email="queue-future@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 21),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.data["unresolved_count"], 0)
        self.assertEqual(response.data["next_future_pay_date"], "2026-08-21")

    def test_reviewed_period_is_excluded(self) -> None:
        owner = User.objects.create_user(email="queue-reviewed@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED,
        )
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.data["unresolved_count"], 0)

    def test_incomplete_period_is_excluded(self) -> None:
        owner = User.objects.create_user(email="queue-incomplete@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
            payday_reconciliation_status=PaydayReconciliationStatus.INCOMPLETE,
        )
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.data["unresolved_count"], 0)

    def test_anonymous_request_is_denied(self) -> None:
        response = APIClient().get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_receives_none_of_another_users_periods(self) -> None:
        jane = User.objects.create_user(email="queue-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="queue-bob@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=jane,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        client = APIClient()
        client.force_authenticate(bob)

        response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(response.data["unresolved_count"], 0)
        self.assertEqual(response.data["unresolved_periods"], [])
