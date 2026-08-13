import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetLineItem, BudgetPayPeriod, BudgetPlan, SourceType


class BudgetViewTest(APITestCase):
    def test_unauthenticated_request_returns_401(self) -> None:
        client = APIClient()
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_budget_plan_returns_empty_data(self) -> None:
        user = User.objects.create_user(email="budget_empty@example.com", password="StrongPassword123!")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], [])
        self.assertFalse(response.data["meta"]["can_load_more"])
        self.assertEqual(response.data["meta"]["pagination"]["total"], 0)

    def test_budget_plan_returns_paginated_periods(self) -> None:
        user = User.objects.create_user(email="budget_paged@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        for period_index in range(3):
            period = BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(2025, 8 + period_index, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )
            BudgetLineItem.objects.create(
                pay_period=period,
                source_type=SourceType.STANDARD_EXPENSE,
                source_key="food_cents",
                title="Food",
                amount_cents=150000,
            )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 3)
        self.assertFalse(response.data["meta"]["can_load_more"])

    def test_budget_view_returns_line_items_in_response(self) -> None:
        user = User.objects.create_user(email="budget_lineitems@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=150000,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="food_cents",
            title="Food",
            amount_cents=150000,
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        period_data = response.data["data"][0]
        self.assertIn("line_items", period_data)
        self.assertEqual(len(period_data["line_items"]), 1)
        self.assertEqual(period_data["line_items"][0]["title"], "Food")

    def test_can_load_more_true_when_more_pages_exist(self) -> None:
        user = User.objects.create_user(email="budget_loadmore@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        for period_index in range(7):
            month = ((7 + period_index) % 12) + 1
            year = 2025 + ((7 + period_index) // 12)
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(year, month, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/?page=1", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["meta"]["can_load_more"])
        self.assertFalse(response.data["meta"]["can_load_previous"])
        self.assertEqual(len(response.data["data"]), 6)

    def test_page_2_returns_remaining_items(self) -> None:
        user = User.objects.create_user(email="budget_page2@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        for period_index in range(7):
            month = ((7 + period_index) % 12) + 1
            year = 2025 + ((7 + period_index) // 12)
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(year, month, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/?page=2", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertFalse(response.data["meta"]["can_load_more"])
        self.assertTrue(response.data["meta"]["can_load_previous"])

    def test_invalid_page_param_defaults_to_page_one(self) -> None:
        user = User.objects.create_user(email="budget_badpage@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        for period_index in range(2):
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(2025, 8 + period_index, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/?page=abc", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["pagination"]["current_page"], 1)

    def test_owned_anchor_returns_the_page_containing_the_period(self) -> None:
        user = User.objects.create_user(email="budget-anchor-page@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        anchor_period = None

        for period_index in range(7):
            period = BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(2026, period_index + 1, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )

            if period_index == 6:
                anchor_period = period

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            f"/api/budget/pay-periods/?anchor_period_id={anchor_period.id}",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["pagination"]["current_page"], 2)
        self.assertEqual(response.data["meta"]["anchor_period_id"], anchor_period.id)
        self.assertEqual([entry["id"] for entry in response.data["data"]], [anchor_period.id])

    def test_negative_page_param_defaults_to_page_one(self) -> None:
        user = User.objects.create_user(email="budget_negpage@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        for period_index in range(2):
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(2025, 8 + period_index, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/?page=-1", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["pagination"]["current_page"], 1)

    def test_response_includes_expected_pagination_fields(self) -> None:
        user = User.objects.create_user(email="budget_pagmeta@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        for period_index in range(3):
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(2025, 8 + period_index, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(
            set(response.data["meta"]),
            {
                "can_load_previous",
                "can_load_more",
                "anchor_period_id",
                "pagination",
            },
        )
        pagination = response.data["meta"]["pagination"]
        self.assertIn("count", pagination)
        self.assertIn("current_page", pagination)
        self.assertIn("per_page", pagination)
        self.assertIn("total", pagination)
        self.assertIn("total_pages", pagination)

    def test_response_does_not_expose_unexpected_period_fields(self) -> None:
        user = User.objects.create_user(email="budget_fields@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=150000,
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/", secure=True)
        period = response.data["data"][0]
        expected_fields = {
            "id",
            "sequence",
            "pay_date",
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
        }
        self.assertEqual(set(period.keys()), expected_fields)

    def test_user_only_sees_own_budget(self) -> None:
        user_a = User.objects.create_user(email="budget_usera@example.com", password="StrongPassword123!")
        user_b = User.objects.create_user(email="budget_userb@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user_a,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        for period_index in range(5):
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=period_index,
                pay_date=datetime.date(2025, 8 + period_index, 1),
                pay_cheque_cents=300000,
                total_available_cents=300000,
                left_over_cents=150000,
            )
        client = APIClient()
        client.force_authenticate(user=user_b)
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], [])

    def test_periods_are_ordered_by_sequence_then_pay_date(self) -> None:
        user = User.objects.create_user(email="budget_order@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=2,
            pay_date=datetime.date(2025, 10, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=1,
            pay_date=datetime.date(2025, 9, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sequences = [p["sequence"] for p in response.data["data"]]
        self.assertEqual(sequences, [0, 1, 2])

    def test_line_items_are_ordered_by_display_order_then_id(self) -> None:
        user = User.objects.create_user(email="budget_li_order@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=150000,
        )
        item_b = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="rent_or_mortgage_cents",
            title="Rent",
            amount_cents=100000,
            display_order=2,
        )
        item_a = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="food_cents",
            title="Food",
            amount_cents=50000,
            display_order=1,
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/budget/pay-periods/", secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_items = response.data["data"][0]["line_items"]
        self.assertEqual(len(line_items), 2)
        self.assertEqual(line_items[0]["id"], item_a.pk)
        self.assertEqual(line_items[1]["id"], item_b.pk)

    def test_list_endpoint_query_count_does_not_scale_with_line_item_volume(self) -> None:
        user = User.objects.create_user(email="budget_queries@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=500000,
        )
        for i in range(6):
            month = ((7 + i) % 12) + 1
            pay_date = datetime.date(2025 + ((7 + i) // 12), month, 1)
            period = BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=i,
                pay_date=pay_date,
                pay_cheque_cents=500000,
                total_available_cents=500000,
                left_over_cents=200000,
            )
            for j in range(4):
                BudgetLineItem.objects.create(
                    pay_period=period,
                    source_type=SourceType.STANDARD_EXPENSE,
                    source_key=f"expense_{j}_cents",
                    title=f"Expense {j}",
                    amount_cents=50000,
                    display_order=j,
                )
        client = APIClient()
        client.force_authenticate(user=user)
        with CaptureQueriesContext(connection) as initial_queries:
            response = client.get("/api/budget/pay-periods/", secure=True)

        initial_query_count = len(initial_queries)

        for period in plan.pay_periods.all():
            for item_index in range(4, 12):
                BudgetLineItem.objects.create(
                    pay_period=period,
                    source_type=SourceType.STANDARD_EXPENSE,
                    source_key=f"additional_expense_{item_index}_cents",
                    title=f"Additional expense {item_index}",
                    amount_cents=1000,
                    display_order=item_index,
                )

        with CaptureQueriesContext(connection) as expanded_queries:
            expanded_response = client.get("/api/budget/pay-periods/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expanded_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(expanded_queries), initial_query_count)
        self.assertEqual(len(response.data["data"]), 6)
        self.assertEqual(len(expanded_response.data["data"][0]["line_items"]), 12)
