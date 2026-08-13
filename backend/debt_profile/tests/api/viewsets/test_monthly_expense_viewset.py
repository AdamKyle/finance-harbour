from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import DebtProfile, RecurringExpense


class MonthlyExpenseViewTest(APITestCase):
    def test_saves_one_combined_utility_without_standalone_internet(self) -> None:
        user = User.objects.create_user(email="utilities-api@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(user=user)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/monthly-expense/",
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "Hydro",
                        "amount_cents": 18000,
                        "utility_type": "CUSTOM",
                        "includes_internet": True,
                        "includes_cable": True,
                    }
                ],
                "payment_schedules": [
                    {
                        "source_key": "utilities",
                        "timing": "DAY_OF_MONTH",
                        "paycheck_position": None,
                        "day_of_month": 12,
                        "auto_deducted": True,
                    }
                ],
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RecurringExpense.objects.filter(debt_profile__user=user).count(), 1)
        self.assertFalse(RecurringExpense.objects.filter(debt_profile__user=user, source_key="internet").exists())

    def test_cannot_replace_another_users_expenses(self) -> None:
        jane = User.objects.create_user(email="jane-utility@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="bob-utility@example.com", password="StrongPassword123!")
        jane_profile = DebtProfile.objects.create(user=jane)
        DebtProfile.objects.create(user=bob)
        RecurringExpense.objects.create(
            debt_profile=jane_profile,
            source_key="internet",
            category="INTERNET",
            label="Internet",
            amount_cents=8000,
        )
        client = APIClient()
        client.force_authenticate(user=bob)

        client.patch(
            "/api/debt-profile/monthly-expense/",
            {"recurring_expenses": []},
            format="json",
            secure=True,
        )

        self.assertTrue(RecurringExpense.objects.filter(debt_profile=jane_profile, source_key="internet").exists())
