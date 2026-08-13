import datetime

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile


class BudgetValueUpdateViewTest(APITestCase):
    secure_origin = "https://testserver"

    def test_authenticated_owner_can_update_manual_value_with_exact_response_fields(self) -> None:
        User.objects.create_user(email="owner-success@example.com", password="StrongPassword123!")
        owner = User.objects.get(email="owner-success@example.com")
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
            {"email": "owner-success@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_response = client.get("/api/auth/csrf/", secure=True)
        post_login_token = str(post_login_response.data["csrfToken"])
        response = client.patch(
            f"/api/budget/pay-periods/{period.id}/values/",
            {
                "field": "left_over_cents",
                "amount_cents": 40000,
                "going_forward": False,
            },
            format="json",
            HTTP_X_CSRFTOKEN=post_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["left_over_cents"], 40000)
        self.assertTrue(response.data["left_over_is_manual"])
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

    def test_anonymous_update_is_rejected(self) -> None:
        response = APIClient(enforce_csrf_checks=True).patch(
            "/api/budget/pay-periods/1/values/",
            {
                "field": "left_over_cents",
                "amount_cents": 40000,
                "going_forward": False,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_update_another_users_period(self) -> None:
        owner = User.objects.create_user(email="owner@example.com", password="StrongPassword123!")
        User.objects.create_user(email="other@example.com", password="StrongPassword123!")
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
            {"email": "other@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_response = client.get("/api/auth/csrf/", secure=True)
        post_login_token = str(post_login_response.data["csrfToken"])
        response = client.patch(
            f"/api/budget/pay-periods/{period.id}/values/",
            {
                "field": "left_over_cents",
                "amount_cents": 40000,
                "going_forward": False,
                "user_id": owner.id,
            },
            format="json",
            HTTP_X_CSRFTOKEN=post_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        period.refresh_from_db()
        self.assertEqual(period.left_over_cents, 100000)

    def test_invalid_value_is_rejected_without_mutation(self) -> None:
        owner = User.objects.create_user(email="invalid-owner@example.com", password="StrongPassword123!")
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
            {"email": "invalid-owner@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_response = client.get("/api/auth/csrf/", secure=True)
        post_login_token = str(post_login_response.data["csrfToken"])
        response = client.patch(
            f"/api/budget/pay-periods/{period.id}/values/",
            {"field": "pay_cheque_cents", "amount_cents": -1, "going_forward": False},
            format="json",
            HTTP_X_CSRFTOKEN=post_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        period.refresh_from_db()
        self.assertEqual(period.pay_cheque_cents, 100000)

    def test_cookie_authenticated_update_requires_csrf_header(self) -> None:
        owner = User.objects.create_user(email="csrf-owner@example.com", password="StrongPassword123!")
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
            {"email": "csrf-owner@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.patch(
            f"/api/budget/pay-periods/{period.id}/values/",
            {"field": "left_over_cents", "amount_cents": 40000, "going_forward": False},
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        period.refresh_from_db()
        self.assertEqual(period.left_over_cents, 100000)

    def test_cookie_authenticated_user_cannot_regenerate_another_users_timeline(self) -> None:
        jane = User.objects.create_user(email="jane-forward@example.com", password="StrongPassword123!")
        User.objects.create_user(email="bob-forward@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=jane,
            start_date=datetime.date(2026, 8, 21),
            end_date=datetime.date(2027, 8, 21),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        first = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 21),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        selected = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 9, 4),
            pay_cheque_cents=100000,
            total_available_cents=200000,
            left_over_cents=200000,
        )
        client = APIClient(enforce_csrf_checks=True)
        pre_login_response = client.get("/api/auth/csrf/", secure=True)
        pre_login_token = str(pre_login_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "bob-forward@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=pre_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_response = client.get("/api/auth/csrf/", secure=True)
        post_login_token = str(post_login_response.data["csrfToken"])
        response = client.patch(
            f"/api/budget/pay-periods/{selected.id}/values/",
            {"field": "pay_date", "pay_date": "2026-09-05"},
            format="json",
            HTTP_X_CSRFTOKEN=post_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        first.refresh_from_db()
        selected.refresh_from_db()
        self.assertEqual(first.pay_date, datetime.date(2026, 8, 21))
        self.assertEqual(selected.pay_date, datetime.date(2026, 9, 4))

    def test_cookie_authenticated_owner_can_regenerate_timeline_from_selected_period(self) -> None:
        owner = User.objects.create_user(email="owner-forward@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=owner,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        plan = generate_budget(owner)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        client = APIClient(enforce_csrf_checks=True)
        pre_login_response = client.get("/api/auth/csrf/", secure=True)
        pre_login_token = str(pre_login_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "owner-forward@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=pre_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_response = client.get("/api/auth/csrf/", secure=True)
        post_login_token = str(post_login_response.data["csrfToken"])
        response = client.patch(
            f"/api/budget/pay-periods/{selected.id}/values/",
            {"field": "pay_date", "pay_date": "2026-09-05"},
            format="json",
            HTTP_X_CSRFTOKEN=post_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], selected.id)
        self.assertEqual(response.data["pay_date"], "2026-09-05")
        self.assertEqual(response.data["previous_pay_date"], "2026-08-21")
        self.assertEqual(
            list(plan.pay_periods.order_by("sequence").values_list("pay_date", flat=True)[:4]),
            [
                datetime.date(2026, 8, 21),
                datetime.date(2026, 9, 5),
                datetime.date(2026, 9, 19),
                datetime.date(2026, 10, 3),
            ],
        )

    def test_invalid_pay_date_format_is_rejected_without_mutation(self) -> None:
        owner = User.objects.create_user(email="invalid-date@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 21),
            end_date=datetime.date(2027, 8, 21),
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 21),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        client = APIClient(enforce_csrf_checks=True)
        pre_login_response = client.get("/api/auth/csrf/", secure=True)
        pre_login_token = str(pre_login_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "invalid-date@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=pre_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_response = client.get("/api/auth/csrf/", secure=True)
        post_login_token = str(post_login_response.data["csrfToken"])

        response = client.patch(
            f"/api/budget/pay-periods/{period.id}/values/",
            {"field": "pay_date", "pay_date": "not-a-date"},
            format="json",
            HTTP_X_CSRFTOKEN=post_login_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        period.refresh_from_db()
        self.assertEqual(period.pay_date, datetime.date(2026, 8, 21))
