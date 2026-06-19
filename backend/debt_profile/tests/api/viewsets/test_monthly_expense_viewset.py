from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import DebtProfile, MonthlyExpense


class MonthlyExpenseViewTest(APITestCase):
    def test_authenticated_user_can_save_monthly_expenses(self) -> None:
        user = User.objects.create_user(
            email="saveexpense@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/monthly-expense/",
            {"rent_or_mortgage_cents": 150000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rent_or_mortgage_cents"], 150000)

    def test_common_monthly_expense_fields_save_as_cents(self) -> None:
        user = User.objects.create_user(
            email="expensecents@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/monthly-expense/",
            {
                "water_cents": 5000,
                "electricity_cents": 12000,
                "food_cents": 60000,
                "internet_cents": 8000,
                "phone_cents": 7500,
                "car_payment_cents": 35000,
                "insurance_cents": 15000,
            },
            format="json",
            secure=True,
        )

        debt_profile = DebtProfile.objects.get(user=user)
        expense = MonthlyExpense.objects.get(debt_profile=debt_profile)
        self.assertEqual(expense.water_cents, 5000)
        self.assertEqual(expense.electricity_cents, 12000)
        self.assertEqual(expense.food_cents, 60000)
        self.assertEqual(expense.internet_cents, 8000)
        self.assertEqual(expense.phone_cents, 7500)
        self.assertEqual(expense.car_payment_cents, 35000)
        self.assertEqual(expense.insurance_cents, 15000)

    def test_misc_expenses_save_as_label_value_rows(self) -> None:
        user = User.objects.create_user(
            email="miscexpense@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/monthly-expense/",
            {
                "misc_expenses": [
                    {"label": "Gym", "amount_cents": 4500},
                    {"label": "Streaming", "amount_cents": 2000},
                ]
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["misc_expenses"]), 2)
        self.assertEqual(response.data["misc_expenses"][0]["label"], "Gym")
        self.assertEqual(response.data["misc_expenses"][0]["amount_cents"], 4500)

    def test_negative_values_are_rejected(self) -> None:
        user = User.objects.create_user(
            email="negexpense@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/monthly-expense/",
            {"rent_or_mortgage_cents": -1000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_misc_expense_rows_are_rejected(self) -> None:
        user = User.objects.create_user(
            email="invalidmisc@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/monthly-expense/",
            {"misc_expenses": [{"label": "Gym", "amount_cents": -500}]},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_access_rejected(self) -> None:
        client = APIClient()

        response = client.patch(
            "/api/debt-profile/monthly-expense/",
            {"food_cents": 50000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cross_user_access_rejected(self) -> None:
        user1 = User.objects.create_user(
            email="expowner@example.com",
            password="StrongPassword123!",
        )
        user2 = User.objects.create_user(
            email="expother@example.com",
            password="StrongPassword123!",
        )
        debt_profile1 = DebtProfile.objects.create(user=user1)
        MonthlyExpense.objects.create(debt_profile=debt_profile1, food_cents=40000)

        client = APIClient()
        client.force_authenticate(user=user2)
        client.patch(
            "/api/debt-profile/monthly-expense/",
            {"food_cents": 99999},
            format="json",
            secure=True,
        )

        expense = MonthlyExpense.objects.get(debt_profile=debt_profile1)
        self.assertNotEqual(expense.food_cents, 99999)

    def test_response_returns_only_expected_fields(self) -> None:
        user = User.objects.create_user(
            email="expfields@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/monthly-expense/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = {
            "rent_or_mortgage_cents",
            "water_cents",
            "electricity_cents",
            "food_cents",
            "internet_cents",
            "phone_cents",
            "car_payment_cents",
            "insurance_cents",
            "misc_expenses",
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
