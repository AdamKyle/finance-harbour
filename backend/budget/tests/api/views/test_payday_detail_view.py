import datetime

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetLineItem, BudgetPayPeriod, BudgetPlan, SourceType
from debt_profile.models import DebtProfile


class PaydayDetailViewTest(APITestCase):
    @override_settings(DEBUG=True)
    def test_owner_receives_owned_period_line_items_and_debt_checks(self) -> None:
        owner = User.objects.create_user(email="detail-owner@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=owner,
            income_per_pay_period_cents=200000,
            pay_period_type="MONTHLY",
            next_pay_date=datetime.date(2026, 8, 1),
            debts=[{"label": "Visa", "current_balance_cents": 500000, "current_payment_cents": 20000}],
        )
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=200000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=200000,
            total_available_cents=200000,
            total_bills_cents=20000,
            left_over_cents=180000,
        )
        line_item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Visa",
            amount_cents=20000,
        )
        client = APIClient()
        client.force_authenticate(owner)

        response = client.get(
            f"/api/budget/payday/pay-periods/{period.id}/",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"pay_period", "debt_balance_checks", "progress"})
        self.assertEqual(
            set(response.data["debt_balance_checks"][0]),
            {
                "source_key",
                "title",
                "expected_balance_cents",
                "actual_balance_cents",
                "review_status",
                "variance_cents",
                "variance_percentage",
                "previous_confirmed_balance_cents",
                "movement_from_previous_percentage",
                "is_uncertain",
            },
        )
        self.assertEqual(
            set(response.data["progress"]),
            {
                "bill_count",
                "reviewed_bill_count",
                "paid_bill_count",
                "scheduled_bill_count",
                "missed_bill_count",
                "payment_completion_percentage",
                "payment_completion_status",
                "overall_reconciliation_status",
            },
        )
        self.assertEqual(response.data["pay_period"]["id"], period.id)
        self.assertEqual(response.data["pay_period"]["line_items"][0]["id"], line_item.id)
        self.assertEqual(response.data["pay_period"]["line_items"][0]["amount_cents"], 20000)
        self.assertIsNone(response.data["pay_period"]["line_items"][0]["actual_amount_cents"])
        self.assertEqual(response.data["debt_balance_checks"][0]["source_key"], "debt:0")
        self.assertEqual(response.data["debt_balance_checks"][0]["expected_balance_cents"], 500000)
        self.assertEqual(response.data["progress"]["bill_count"], 1)
        self.assertEqual(response.data["progress"]["reviewed_bill_count"], 0)
        self.assertEqual(response.data["progress"]["paid_bill_count"], 0)

    def test_anonymous_request_is_denied(self) -> None:
        response = APIClient().get("/api/budget/payday/pay-periods/1/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DEBUG=True)
    def test_bob_cannot_read_janes_payday_or_line_items(self) -> None:
        jane = User.objects.create_user(email="detail-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="detail-bob@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=jane,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=200000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=200000,
            total_available_cents=200000,
            left_over_cents=200000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="food_cents",
            title="Food",
            amount_cents=20000,
        )
        client = APIClient()
        client.force_authenticate(bob)

        response = client.get(
            f"/api/budget/payday/pay-periods/{period.id}/",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(DEBUG=True)
    def test_bob_cannot_read_janes_debt_balance_data(self) -> None:
        jane = User.objects.create_user(email="detail-debt-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="detail-debt-bob@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=jane,
            debts=[{"label": "Jane Visa", "current_balance_cents": 900000, "current_payment_cents": 20000}],
        )
        plan = BudgetPlan.objects.create(
            user=jane,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=200000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 1),
            pay_cheque_cents=200000,
            total_available_cents=200000,
            left_over_cents=200000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.DEBT,
            source_key="debt:0",
            title="Jane Visa",
            amount_cents=20000,
        )
        client = APIClient()
        client.force_authenticate(bob)

        response = client.get(
            f"/api/budget/payday/pay-periods/{period.id}/",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
