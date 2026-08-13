import datetime

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetDebtBalanceRecord, BudgetLineItem, BudgetPayPeriod, BudgetPlan, SourceType


class PaydayDebtBalanceUpdateViewTest(APITestCase):
    secure_origin = "https://testserver"

    @override_settings(DEBUG=True)
    def test_confirmed_balance_is_recorded_independently_from_payment(self) -> None:
        owner = User.objects.create_user(email="debt-owner@example.com", password="StrongPassword123!")
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
        payment = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=50000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        client.post(
            "/api/auth/login/",
            {"email": "debt-owner@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/debt-balance/",
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": 910000,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"pay_period", "warnings", "affected_pay_period_ids"},
        )
        self.assertEqual(response.data["affected_pay_period_ids"], [period.id])
        record = BudgetDebtBalanceRecord.objects.get(pay_period=period, source_key="debt:0")
        payment.refresh_from_db()
        self.assertEqual(record.actual_balance_cents, 910000)
        self.assertIsNone(payment.actual_amount_cents)

    @override_settings(DEBUG=True)
    def test_unknown_balance_stores_null(self) -> None:
        owner = User.objects.create_user(email="debt-unknown@example.com", password="StrongPassword123!")
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
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=50000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        client.post(
            "/api/auth/login/",
            {"email": "debt-unknown@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/debt-balance/",
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "UNKNOWN",
                "actual_balance_cents": 910000,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record = BudgetDebtBalanceRecord.objects.get(pay_period=period, source_key="debt:0")
        self.assertIsNone(record.actual_balance_cents)

    @override_settings(DEBUG=True)
    def test_bob_cannot_add_balance_to_janes_period(self) -> None:
        jane = User.objects.create_user(email="debt-jane@example.com", password="StrongPassword123!")
        User.objects.create_user(email="debt-bob@example.com", password="StrongPassword123!")
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
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=50000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        client.post(
            "/api/auth/login/",
            {"email": "debt-bob@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/debt-balance/",
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": 910000,
                "user_id": jane.id,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(BudgetDebtBalanceRecord.objects.filter(pay_period=period).exists())

    @override_settings(DEBUG=True)
    def test_negative_balance_is_rejected(self) -> None:
        owner = User.objects.create_user(email="debt-negative@example.com", password="StrongPassword123!")
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
            source_type=SourceType.DEBT,
            source_key="debt:negative",
            title="Visa",
            amount_cents=50000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        client.post(
            "/api/auth/login/",
            {"email": "debt-negative@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/debt-balance/",
            {
                "source_key": "debt:negative",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": -1,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(BudgetDebtBalanceRecord.objects.filter(pay_period=period).exists())

    def test_anonymous_debt_balance_update_is_denied(self) -> None:
        response = APIClient().patch(
            "/api/budget/payday/pay-periods/1/debt-balance/",
            {
                "source_key": "debt:0",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": 100000,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DEBUG=True)
    def test_another_users_source_key_cannot_be_added_to_owned_period(self) -> None:
        jane = User.objects.create_user(email="debt-source-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="debt-source-bob@example.com", password="StrongPassword123!")
        jane_plan = BudgetPlan.objects.create(
            user=jane,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        bob_plan = BudgetPlan.objects.create(
            user=bob,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        jane_period = BudgetPayPeriod.objects.create(
            plan=jane_plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        bob_period = BudgetPayPeriod.objects.create(
            plan=bob_plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        BudgetLineItem.objects.create(
            pay_period=jane_period,
            source_type=SourceType.DEBT,
            source_key="debt:jane-only",
            title="Jane Visa",
            amount_cents=50000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        client.post(
            "/api/auth/login/",
            {"email": "debt-source-bob@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        client.credentials(HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN=self.secure_origin)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{bob_period.id}/debt-balance/",
            {
                "source_key": "debt:jane-only",
                "title": "Jane Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": 900000,
                "user_id": jane.id,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(BudgetDebtBalanceRecord.objects.filter(pay_period=bob_period).exists())
        self.assertFalse(BudgetDebtBalanceRecord.objects.filter(pay_period=jane_period).exists())

    @override_settings(DEBUG=True)
    def test_cookie_authenticated_debt_balance_update_requires_csrf(self) -> None:
        owner = User.objects.create_user(email="debt-csrf@example.com", password="StrongPassword123!")
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
            source_type=SourceType.DEBT,
            source_key="debt:csrf",
            title="Visa",
            amount_cents=50000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "debt-csrf@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/debt-balance/",
            {
                "source_key": "debt:csrf",
                "title": "Visa",
                "review_status": "CONFIRMED",
                "actual_balance_cents": 900000,
            },
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
