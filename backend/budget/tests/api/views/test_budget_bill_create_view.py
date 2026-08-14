import datetime

from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan


class BudgetBillCreateViewTest(APITestCase):
    secure_origin = "https://testserver"

    def test_authenticated_owner_can_add_important_bill_to_selected_and_future_periods(self) -> None:
        owner = User.objects.create_user(email="bill-owner@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        selected_period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        future_period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 2, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            f"/api/budget/pay-periods/{selected_period.id}/bills/",
            {
                "title": "Child care",
                "amount_cents": 20000,
                "is_required": True,
                "going_forward": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], selected_period.id)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "sequence",
                "pay_date",
                "previous_pay_date",
                "pay_cheque_cents",
                "pay_cheque_is_manual",
                "carried_left_over_cents",
                "carried_left_over_is_manual",
                "total_available_cents",
                "total_available_is_manual",
                "total_bills_cents",
                "total_bills_is_manual",
                "left_over_cents",
                "left_over_is_manual",
                "has_negative_left_over",
                "is_below_warning_threshold",
                "has_deferred_items",
                "affects_important_expenses",
                "has_missed_important_expenses",
                "payday_reconciliation_status",
                "actual_pay_cheque_cents",
                "pay_cheque_review_status",
                "pay_cheque_reconciled_at",
                "payday_reconciliation_started_at",
                "payday_reconciliation_completed_at",
                "line_items",
                "bill_count",
                "paid_bill_count",
                "scheduled_bill_count",
                "missed_bill_count",
                "payment_completion_percentage",
                "payment_completion_status",
                "debt_balance_checks",
            },
        )
        selected_bill = selected_period.line_items.get(title="Child care")
        future_bill = future_period.line_items.get(title="Child care")
        self.assertEqual(selected_bill.source_key, future_bill.source_key)
        self.assertTrue(selected_bill.is_required)

    def test_anonymous_bill_request_is_rejected(self) -> None:
        response = APIClient(enforce_csrf_checks=True).post(
            "/api/budget/pay-periods/1/bills/",
            {
                "title": "Child care",
                "amount_cents": 20000,
                "is_required": False,
                "going_forward": False,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_cannot_add_bill_to_another_users_period(self) -> None:
        owner = User.objects.create_user(email="bill-owner-denied@example.com", password="StrongPassword123!")
        other = User.objects.create_user(email="bill-other@example.com", password="StrongPassword123!")
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
        client = APIClient()
        client.force_authenticate(user=other)

        response = client.post(
            f"/api/budget/pay-periods/{period.id}/bills/",
            {
                "title": "Child care",
                "amount_cents": 20000,
                "is_required": False,
                "going_forward": False,
                "user_id": owner.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(period.line_items.exists())

    def test_blank_bill_name_is_rejected_without_creation(self) -> None:
        owner = User.objects.create_user(email="blank-bill-owner@example.com", password="StrongPassword123!")
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
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            f"/api/budget/pay-periods/{period.id}/bills/",
            {
                "title": "   ",
                "amount_cents": 20000,
                "is_required": False,
                "going_forward": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(period.line_items.exists())

    def test_cookie_authenticated_bill_request_requires_csrf_header(self) -> None:
        cache.clear()

        owner = User.objects.create_user(email="bill-csrf-owner@example.com", password="StrongPassword123!")
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
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "bill-csrf-owner@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.post(
            f"/api/budget/pay-periods/{period.id}/bills/",
            {
                "title": "Child care",
                "amount_cents": 20000,
                "is_required": False,
                "going_forward": False,
            },
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(period.line_items.exists())
