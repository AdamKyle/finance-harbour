import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from budget.models import BudgetPlan
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory


class OnboardingCompleteViewTest(APITestCase):
    def test_completion_requires_authentication(self) -> None:
        response = APIClient().post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completion_generates_from_the_authenticated_owners_recurring_expenses(self) -> None:
        user = User.objects.create_user(email="complete-owner@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
            next_pay_date=timezone.localdate() + datetime.timedelta(days=7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(BudgetPlan.objects.filter(user=user).exists())

    def test_completion_rejects_missing_expenses(self) -> None:
        user = User.objects.create_user(email="complete-no-expense@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
            next_pay_date=timezone.localdate() + datetime.timedelta(days=7),
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
