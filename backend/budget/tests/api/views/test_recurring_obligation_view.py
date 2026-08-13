import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    RecurringExpense,
    RequiredExpense,
)


class RecurringObligationViewTest(APITestCase):
    def test_get_returns_exact_payment_schedule_configuration(self) -> None:
        user = User.objects.create_user(email="bill-config@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            next_pay_date=datetime.date(2026, 8, 21),
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/budget/recurring-obligations/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"pay_period_type", "representative_date"})
        self.assertEqual(response.data["pay_period_type"], "BIWEEKLY")
        self.assertEqual(response.data["representative_date"], "2026-08-21")

    def test_get_rejects_incomplete_payment_schedule_configuration(self) -> None:
        user = User.objects.create_user(email="incomplete-get@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=user, pay_period_type="BIWEEKLY", next_pay_date=None)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/budget/recurring-obligations/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_rejects_incomplete_profile_before_every_paycheck_mutation(self) -> None:
        user = User.objects.create_user(email="incomplete-post@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user, pay_period_type="", next_pay_date=None, debts=[])
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/budget/recurring-obligations/",
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": True,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "EVERY_PAYCHECK",
                    "paycheck_position": None,
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            },
            format="json",
            secure=True,
        )
        profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(RecurringExpense.objects.filter(debt_profile=profile).exists())
        self.assertEqual(profile.debts, [])
        self.assertFalse(ExpensePaymentSchedule.objects.filter(debt_profile=profile).exists())
        self.assertFalse(RequiredExpense.objects.filter(debt_profile=profile).exists())

    def test_anonymous_access_is_rejected(self) -> None:
        response = APIClient().get("/api/budget/recurring-obligations/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_bill_creation_persists_owned_recurring_source(self) -> None:
        user = User.objects.create_user(email="new-bill@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        generate_budget(user)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/budget/recurring-obligations/",
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": True,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "PAYCHECK_POSITION",
                    "paycheck_position": "FIRST",
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data),
            {"kind", "source_key", "first_effective_budget_period_id"},
        )
        self.assertTrue(
            RecurringExpense.objects.filter(
                debt_profile=profile,
                source_key=response.data["source_key"],
            ).exists()
        )
        self.assertTrue(
            RequiredExpense.objects.filter(
                debt_profile=profile,
                source_key=response.data["source_key"],
            ).exists()
        )

    def test_authenticated_debt_creation_appends_existing_debt_shape(self) -> None:
        user = User.objects.create_user(email="new-debt@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=400000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        generate_budget(user)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/budget/recurring-obligations/",
            {
                "kind": "DEBT",
                "label": "Student Loan",
                "is_required": False,
                "current_balance_cents": 1200000,
                "minimum_payment_cents": 10000,
                "current_payment_cents": 15000,
                "payment_schedule": {
                    "timing": "DAY_OF_MONTH",
                    "paycheck_position": "FIRST",
                    "day_of_month": 10,
                    "auto_deducted": True,
                },
            },
            format="json",
            secure=True,
        )
        profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["source_key"], "debt:0")
        self.assertEqual(
            profile.debts[0],
            {
                "label": "Student Loan",
                "current_balance_cents": 1200000,
                "minimum_payment_cents": 10000,
                "current_payment_cents": 15000,
            },
        )
        self.assertFalse(RequiredExpense.objects.filter(debt_profile=profile).exists())

    def test_no_future_period_rolls_back_bill_creation(self) -> None:
        user = User.objects.create_user(email="no-future-period@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2026, 7, 1),
            end_date=datetime.date(2026, 7, 31),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 7, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/budget/recurring-obligations/",
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "EVERY_PAYCHECK",
                    "paycheck_position": None,
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(RecurringExpense.objects.filter(debt_profile=profile).exists())

    def test_creation_is_scoped_to_authenticated_owner(self) -> None:
        future_pay_date = timezone.localdate() + datetime.timedelta(days=7)
        owner = User.objects.create_user(email="bill-owner@example.com", password="StrongPassword123!")
        other_user = User.objects.create_user(email="bill-other@example.com", password="StrongPassword123!")
        owner_profile = DebtProfile.objects.create(
            user=owner,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=future_pay_date,
            debts=[],
        )
        other_profile = DebtProfile.objects.create(
            user=other_user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=future_pay_date,
            debts=[],
        )
        generate_budget(owner)
        generate_budget(other_user)
        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            "/api/budget/recurring-obligations/",
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": True,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "EVERY_PAYCHECK",
                    "paycheck_position": None,
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            },
            format="json",
            secure=True,
        )
        other_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            RecurringExpense.objects.filter(
                debt_profile=owner_profile,
                source_key=response.data["source_key"],
            ).exists()
        )
        self.assertFalse(RecurringExpense.objects.filter(debt_profile=other_profile).exists())
        self.assertEqual(other_profile.debts, [])
        self.assertFalse(ExpensePaymentSchedule.objects.filter(debt_profile=other_profile).exists())
        self.assertFalse(RequiredExpense.objects.filter(debt_profile=other_profile).exists())

    def test_creation_preserves_historical_period_and_regenerates_forward_only(self) -> None:
        user = User.objects.create_user(email="forward-only-bill@example.com", password="StrongPassword123!")
        first_pay_date = timezone.localdate() - datetime.timedelta(days=28)
        DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=first_pay_date,
        )
        plan = generate_budget(user)
        historical_period = plan.pay_periods.filter(pay_date__lt=timezone.localdate()).first()
        historical_items = list(historical_period.line_items.values_list("source_key", "amount_cents", "is_required"))
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/budget/recurring-obligations/",
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "EVERY_PAYCHECK",
                    "paycheck_position": None,
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            },
            format="json",
            secure=True,
        )
        historical_period.refresh_from_db()
        reloaded_historical_items = list(
            historical_period.line_items.values_list("source_key", "amount_cents", "is_required")
        )
        historical_has_new_source = historical_period.line_items.filter(source_key=response.data["source_key"]).exists()
        forward_has_new_source = plan.pay_periods.filter(
            pay_date__gte=timezone.localdate(),
            line_items__source_key=response.data["source_key"],
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reloaded_historical_items, historical_items)
        self.assertFalse(historical_has_new_source)
        self.assertTrue(forward_has_new_source)

    def test_biweekly_first_position_starts_at_next_actual_first_paycheck(self) -> None:
        user = User.objects.create_user(email="api-first-position@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        plan = generate_budget(user)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/budget/recurring-obligations/",
            {
                "kind": "BILL",
                "label": "Internet",
                "is_required": False,
                "amount_cents": 9000,
                "payment_schedule": {
                    "timing": "PAYCHECK_POSITION",
                    "paycheck_position": "FIRST",
                    "day_of_month": None,
                    "auto_deducted": False,
                },
            },
            format="json",
            secure=True,
        )

        august_period = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21))
        september_period = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(august_period.line_items.filter(source_key=response.data["source_key"]).exists())
        self.assertTrue(september_period.line_items.filter(source_key=response.data["source_key"]).exists())
