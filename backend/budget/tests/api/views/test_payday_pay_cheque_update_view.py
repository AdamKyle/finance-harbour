import datetime

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan, PayChequeReviewStatus


class PaydayPayChequeUpdateViewTest(APITestCase):
    secure_origin = "https://testserver"

    @override_settings(DEBUG=True)
    def test_owner_confirms_actual_pay_without_replacing_planned_pay(self) -> None:
        owner = User.objects.create_user(email="pay-owner@example.com", password="StrongPassword123!")
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
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "pay-owner@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/pay-cheque/",
            {"review_status": "CONFIRMED", "actual_amount_cents": 125000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"pay_period", "warnings", "affected_pay_period_ids"},
        )
        self.assertEqual(response.data["affected_pay_period_ids"], [period.id])
        period.refresh_from_db()
        self.assertEqual(period.pay_cheque_cents, 100000)
        self.assertEqual(period.actual_pay_cheque_cents, 125000)
        self.assertEqual(period.total_available_cents, 125000)

    @override_settings(DEBUG=True)
    def test_owner_can_confirm_exact_planned_pay(self) -> None:
        owner = User.objects.create_user(email="pay-exact@example.com", password="StrongPassword123!")
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
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "pay-exact@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/pay-cheque/",
            {"review_status": "CONFIRMED", "actual_amount_cents": 100000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        period.refresh_from_db()
        self.assertEqual(period.actual_pay_cheque_cents, period.pay_cheque_cents)

    @override_settings(DEBUG=True)
    def test_unknown_pay_stores_null_actual(self) -> None:
        owner = User.objects.create_user(email="pay-unknown@example.com", password="StrongPassword123!")
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
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "pay-unknown@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/pay-cheque/",
            {"review_status": "UNKNOWN", "actual_amount_cents": 999999},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        period.refresh_from_db()
        self.assertEqual(period.pay_cheque_review_status, PayChequeReviewStatus.UNKNOWN)
        self.assertIsNone(period.actual_pay_cheque_cents)
        self.assertEqual(period.total_available_cents, 100000)

    @override_settings(DEBUG=True)
    def test_negative_actual_pay_is_rejected(self) -> None:
        owner = User.objects.create_user(email="pay-negative@example.com", password="StrongPassword123!")
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
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "pay-negative@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/pay-cheque/",
            {"review_status": "CONFIRMED", "actual_amount_cents": -1},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        period.refresh_from_db()
        self.assertIsNone(period.actual_pay_cheque_cents)

    @override_settings(DEBUG=True)
    def test_bob_cannot_change_janes_pay_cheque_using_user_id(self) -> None:
        jane = User.objects.create_user(email="pay-jane@example.com", password="StrongPassword123!")
        User.objects.create_user(email="pay-bob@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=jane,
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
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "pay-bob@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/pay-cheque/",
            {"review_status": "CONFIRMED", "actual_amount_cents": 200000, "user_id": jane.id},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        period.refresh_from_db()
        self.assertIsNone(period.actual_pay_cheque_cents)

    def test_anonymous_pay_cheque_update_is_denied(self) -> None:
        response = APIClient().patch(
            "/api/budget/payday/pay-periods/1/pay-cheque/",
            {"review_status": "CONFIRMED", "actual_amount_cents": 100000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DEBUG=True)
    def test_cookie_authenticated_pay_cheque_update_requires_csrf(self) -> None:
        owner = User.objects.create_user(email="pay-csrf@example.com", password="StrongPassword123!")
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
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "pay-csrf@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/pay-cheque/",
            {"review_status": "CONFIRMED", "actual_amount_cents": 100000},
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
