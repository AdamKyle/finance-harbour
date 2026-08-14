import datetime

from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import (
    BudgetDebtBalanceRecord,
    BudgetLineItem,
    BudgetPayPeriod,
    BudgetPlan,
    DebtBalanceReviewStatus,
    PayChequeReviewStatus,
    PaydayReconciliationStatus,
    PaymentReviewStatus,
    SourceType,
)


class PaydayMarkIncompleteViewTest(APITestCase):
    secure_origin = "https://testserver"

    @override_settings(DEBUG=True)
    def test_owner_marks_past_unresolved_payday_incomplete_without_fabricating_actuals(self) -> None:
        owner = User.objects.create_user(email="incomplete-owner@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 7, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        earlier_period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 7, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=80000,
            payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED,
            pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
            actual_pay_cheque_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        future_period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=2,
            pay_date=datetime.date(2026, 9, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        known = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:known",
            title="Power",
            amount_cents=10000,
            payment_review_status=PaymentReviewStatus.PAID,
            actual_amount_cents=9000,
        )
        unresolved_bill = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="bill:unknown",
            title="Water",
            amount_cents=5000,
        )
        BudgetLineItem.objects.create(
            pay_period=earlier_period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=20000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=20000,
        )
        BudgetLineItem.objects.create(
            pay_period=future_period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=20000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.DEBT,
            source_key="debt:1",
            title="LOC",
            amount_cents=10000,
        )
        BudgetLineItem.objects.create(
            pay_period=future_period,
            source_type=SourceType.DEBT,
            source_key="debt:1",
            title="LOC",
            amount_cents=10000,
        )
        BudgetLineItem.objects.create(
            pay_period=future_period,
            source_type=SourceType.DEBT,
            source_key="debt:2",
            title="Amex",
            amount_cents=15000,
        )
        existing_record = BudgetDebtBalanceRecord.objects.create(
            pay_period=period,
            source_key="debt:1",
            title="LOC",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=300000,
            reconciled_at=datetime.datetime(2026, 8, 2, tzinfo=datetime.UTC),
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            f"/api/budget/payday/pay-periods/{period.id}/mark-incomplete/",
            {},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"pay_period", "warnings", "affected_pay_period_ids"},
        )
        self.assertEqual(
            response.data["affected_pay_period_ids"],
            [period.id, future_period.id],
        )
        period.refresh_from_db()
        known.refresh_from_db()
        unresolved_bill.refresh_from_db()
        debt_record = BudgetDebtBalanceRecord.objects.get(pay_period=period, source_key="debt:0")
        existing_record.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.INCOMPLETE)
        self.assertEqual(period.pay_cheque_review_status, PayChequeReviewStatus.UNKNOWN)
        self.assertIsNone(period.actual_pay_cheque_cents)
        self.assertEqual(known.actual_amount_cents, 9000)
        self.assertEqual(known.payment_review_status, PaymentReviewStatus.PAID)
        self.assertEqual(unresolved_bill.payment_review_status, PaymentReviewStatus.UNKNOWN)
        self.assertIsNone(unresolved_bill.actual_amount_cents)
        self.assertEqual(debt_record.review_status, DebtBalanceReviewStatus.UNKNOWN)
        self.assertIsNone(debt_record.actual_balance_cents)
        self.assertEqual(existing_record.review_status, DebtBalanceReviewStatus.CONFIRMED)
        self.assertEqual(existing_record.actual_balance_cents, 300000)
        self.assertEqual(period.debt_balance_records.count(), 2)
        self.assertFalse(period.debt_balance_records.filter(source_key="debt:2").exists())

        queue_response = client.get("/api/budget/payday/queue/", secure=True)

        self.assertEqual(queue_response.data["unresolved_periods"], [])

    def test_anonymous_mark_incomplete_is_denied(self) -> None:
        response = APIClient().post(
            "/api/budget/payday/pay-periods/1/mark-incomplete/",
            {},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DEBUG=True)
    def test_cookie_authenticated_mark_incomplete_requires_csrf(self) -> None:
        cache.clear()

        owner = User.objects.create_user(email="incomplete-csrf@example.com", password="StrongPassword123!")
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
            {"email": "incomplete-csrf@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.post(
            f"/api/budget/payday/pay-periods/{period.id}/mark-incomplete/",
            {},
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(DEBUG=True)
    def test_bob_cannot_mark_janes_payday_incomplete_using_user_id(self) -> None:
        jane = User.objects.create_user(email="incomplete-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="incomplete-bob@example.com", password="StrongPassword123!")
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
        client = APIClient()
        client.force_authenticate(user=bob)

        response = client.post(
            f"/api/budget/payday/pay-periods/{period.id}/mark-incomplete/",
            {"user_id": jane.id},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.NOT_STARTED)

    @override_settings(DEBUG=True)
    def test_current_payday_cannot_be_marked_incomplete(self) -> None:
        owner = User.objects.create_user(email="incomplete-current@example.com", password="StrongPassword123!")
        current_date = timezone.localdate()
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=current_date,
            end_date=current_date + datetime.timedelta(days=365),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=current_date,
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            f"/api/budget/payday/pay-periods/{period.id}/mark-incomplete/",
            {},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.NOT_STARTED)

    @override_settings(DEBUG=True)
    def test_future_payday_cannot_be_marked_incomplete(self) -> None:
        owner = User.objects.create_user(email="incomplete-future@example.com", password="StrongPassword123!")
        future_date = timezone.localdate() + datetime.timedelta(days=1)
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=future_date,
            end_date=future_date + datetime.timedelta(days=365),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=future_date,
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            f"/api/budget/payday/pay-periods/{period.id}/mark-incomplete/",
            {},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        period.refresh_from_db()
        self.assertEqual(period.payday_reconciliation_status, PaydayReconciliationStatus.NOT_STARTED)
