from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import DebtProfile, MonthlyExpense, RequiredExpense


class ImportantExpensesViewTest(APITestCase):
    def test_list_requires_authentication(self) -> None:
        client = APIClient()

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_eight_expenses_per_page(self) -> None:
        user = User.objects.create_user(
            email="important-page@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            rent_or_mortgage_cents=100000,
            water_cents=5000,
            electricity_cents=8000,
            food_cents=50000,
            internet_cents=7000,
            phone_cents=6000,
            car_payment_cents=30000,
            insurance_cents=15000,
            misc_expenses=[{"label": "Gym", "amount_cents": 4000}],
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            "/api/debt-profile/important-expenses/?page=1",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 8)
        self.assertEqual(response.data["meta"]["pagination"]["per_page"], 8)
        self.assertTrue(response.data["meta"]["can_load_more"])

    def test_list_includes_standard_monthly_expenses(self) -> None:
        user = User.objects.create_user(
            email="important-standard@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            food_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(
            response.data["data"][0],
            {
                "key": "food_cents",
                "title": "Food",
                "amount_cents": 50000,
                "selected": False,
            },
        )

    def test_list_includes_misc_monthly_expenses(self) -> None:
        user = User.objects.create_user(
            email="important-misc@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            misc_expenses=[{"label": "Gym", "amount_cents": 4500}],
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"][0]["key"], "misc:0")
        self.assertEqual(response.data["data"][0]["title"], "Gym")
        self.assertEqual(response.data["data"][0]["amount_cents"], 4500)

    def test_save_requires_authentication(self) -> None:
        client = APIClient()

        response = client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": []},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_save_creates_required_expense_rows(self) -> None:
        user = User.objects.create_user(
            email="important-save@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            food_cents=50000,
            internet_cents=8000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["food_cents", "internet_cents"]},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(RequiredExpense.objects.filter(debt_profile=debt_profile).values_list("source_key", flat=True)),
            {"food_cents", "internet_cents"},
        )

    def test_save_replaces_previous_required_expenses(self) -> None:
        user = User.objects.create_user(
            email="important-replace@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            food_cents=50000,
            internet_cents=8000,
        )
        RequiredExpense.objects.create(
            debt_profile=debt_profile,
            source_key="food_cents",
            title="Food",
            amount_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["internet_cents"]},
            format="json",
            secure=True,
        )

        self.assertEqual(
            list(RequiredExpense.objects.filter(debt_profile=debt_profile).values_list("source_key", flat=True)),
            ["internet_cents"],
        )

    def test_save_rejects_another_users_expense_key(self) -> None:
        owner = User.objects.create_user(
            email="important-owner@example.com",
            password="StrongPassword123!",
        )
        owner_profile = DebtProfile.objects.create(user=owner)
        MonthlyExpense.objects.create(
            debt_profile=owner_profile,
            food_cents=50000,
        )
        other_user = User.objects.create_user(
            email="important-other@example.com",
            password="StrongPassword123!",
        )
        DebtProfile.objects.create(user=other_user)
        client = APIClient()
        client.force_authenticate(user=other_user)

        response = client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["food_cents"]},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(RequiredExpense.objects.filter(debt_profile=owner_profile).exists())

    def test_save_does_not_mark_onboarding_complete(self) -> None:
        user = User.objects.create_user(
            email="important-incomplete@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            food_cents=50000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["food_cents"]},
            format="json",
            secure=True,
        )

        user.refresh_from_db()

        self.assertFalse(user.completed_onboarding)
