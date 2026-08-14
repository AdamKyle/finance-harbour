import datetime

from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetLineItem, BudgetPayPeriod, BudgetPlan, PaymentReviewStatus, SourceType
from debt_profile.models import ExpensePaymentTiming


class PaydayLineItemUpdateViewTest(APITestCase):
    secure_origin = "https://testserver"

    @override_settings(DEBUG=True)
    def test_owner_can_save_changed_scheduled_amount_separately_from_plan(self) -> None:
        owner = User.objects.create_user(email="scheduled-owner@example.com", password="StrongPassword123!")
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
            left_over_cents=81250,
        )
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="insurance_cents",
            title="Insurance",
            amount_cents=18750,
            payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
            expected_payment_date=datetime.date(2026, 8, 12),
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {
                "review_status": "SCHEDULED",
                "actual_amount_cents": None,
                "scheduled_amount_cents": 21500,
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_item.refresh_from_db()
        self.assertEqual(line_item.payment_review_status, PaymentReviewStatus.SCHEDULED)
        self.assertEqual(line_item.amount_cents, 18750)
        self.assertIsNone(line_item.actual_amount_cents)
        self.assertEqual(line_item.scheduled_amount_cents, 21500)

    @override_settings(DEBUG=True)
    def test_paid_payment_records_actual_and_paid_timestamp_without_replacing_plan(self) -> None:
        owner = User.objects.create_user(email="line-owner@example.com", password="StrongPassword123!")
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
            total_bills_cents=50000,
            left_over_cents=50000,
        )
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {"review_status": "PAID", "actual_amount_cents": 60000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"pay_period", "warnings", "affected_pay_period_ids"},
        )
        self.assertEqual(response.data["affected_pay_period_ids"], [period.id])
        line_item.refresh_from_db()
        self.assertEqual(line_item.amount_cents, 50000)
        self.assertEqual(line_item.actual_amount_cents, 60000)
        self.assertIsNone(line_item.paid_at)
        self.assertIsNotNone(line_item.payment_reconciled_at)

    @override_settings(DEBUG=True)
    def test_paid_payment_lower_than_planned_is_stored_separately(self) -> None:
        owner = User.objects.create_user(email="line-lower@example.com", password="StrongPassword123!")
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
            total_bills_cents=50000,
            left_over_cents=50000,
        )
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:lower",
            title="Power",
            amount_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {"review_status": "PAID", "actual_amount_cents": 40000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_item.refresh_from_db()
        self.assertEqual(line_item.amount_cents, 50000)
        self.assertEqual(line_item.actual_amount_cents, 40000)

    @override_settings(DEBUG=True)
    def test_not_paid_stores_zero_and_releases_planned_amount(self) -> None:
        owner = User.objects.create_user(email="line-not-paid@example.com", password="StrongPassword123!")
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
            total_bills_cents=50000,
            left_over_cents=50000,
        )
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {"review_status": "NOT_PAID", "actual_amount_cents": 99999},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_item.refresh_from_db()
        period.refresh_from_db()
        self.assertEqual(line_item.actual_amount_cents, 0)
        self.assertIsNone(line_item.paid_at)
        self.assertEqual(period.left_over_cents, 100000)

    @override_settings(DEBUG=True)
    def test_unknown_stores_null_and_keeps_planned_amount_reserved(self) -> None:
        owner = User.objects.create_user(email="line-unknown@example.com", password="StrongPassword123!")
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
            total_bills_cents=50000,
            left_over_cents=50000,
        )
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {"review_status": "UNKNOWN", "actual_amount_cents": 12345},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_item.refresh_from_db()
        period.refresh_from_db()
        self.assertIsNone(line_item.actual_amount_cents)
        self.assertEqual(period.left_over_cents, 50000)

    @override_settings(DEBUG=True)
    def test_bob_cannot_mutate_janes_line_item(self) -> None:
        jane = User.objects.create_user(email="line-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="line-bob@example.com", password="StrongPassword123!")
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
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:1",
            title="Power",
            amount_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=bob)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {"review_status": "PAID", "actual_amount_cents": 50000, "user_id": jane.id},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        line_item.refresh_from_db()
        self.assertEqual(line_item.payment_review_status, PaymentReviewStatus.UNREVIEWED)

    @override_settings(DEBUG=True)
    def test_line_item_from_another_period_cannot_be_mutated(self) -> None:
        owner = User.objects.create_user(email="line-period-owner@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        selected_period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        other_period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 8),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        other_line_item = BudgetLineItem.objects.create(
            pay_period=other_period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:other",
            title="Water",
            amount_cents=25000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{selected_period.id}/line-items/{other_line_item.id}/",
            {"review_status": "PAID", "actual_amount_cents": 25000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_line_item.refresh_from_db()
        self.assertEqual(other_line_item.payment_review_status, PaymentReviewStatus.UNREVIEWED)

    @override_settings(DEBUG=True)
    def test_negative_actual_amount_is_rejected(self) -> None:
        owner = User.objects.create_user(email="line-negative@example.com", password="StrongPassword123!")
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
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:negative",
            title="Power",
            amount_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {"review_status": "PAID", "actual_amount_cents": -1},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        line_item.refresh_from_db()
        self.assertEqual(line_item.payment_review_status, PaymentReviewStatus.UNREVIEWED)

    def test_anonymous_line_item_update_is_denied(self) -> None:
        response = APIClient().patch(
            "/api/budget/payday/pay-periods/1/line-items/1/",
            {"review_status": "PAID", "actual_amount_cents": 10000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DEBUG=True)
    def test_cookie_authenticated_line_item_update_requires_csrf(self) -> None:
        cache.clear()

        owner = User.objects.create_user(email="line-csrf@example.com", password="StrongPassword123!")
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
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:csrf",
            title="Power",
            amount_cents=50000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "line-csrf@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.patch(
            f"/api/budget/payday/pay-periods/{period.id}/line-items/{line_item.id}/",
            {"review_status": "PAID", "actual_amount_cents": 50000},
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
