from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    RecurringExpense,
    RecurringExpenseCategory,
    RequiredExpense,
)


class ImportantExpensesViewTest(APITestCase):
    secure_origin = "https://testserver"

    def test_lists_normalized_recurring_expenses(self) -> None:
        user = User.objects.create_user(email="important-list@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Hydro",
            amount_cents=18000,
            utility_type="CUSTOM",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/?page=1", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"data", "meta"})
        self.assertEqual(response.data["data"][0]["key"], "utilities")
        self.assertEqual(response.data["data"][0]["title"], "Hydro")

    def test_rent_is_excluded_from_candidates(self) -> None:
        user = User.objects.create_user(email="rent-important@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="rent_or_mortgage",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent",
            amount_cents=150000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"], [])

    def test_auto_deducted_expense_is_excluded_from_candidates(self) -> None:
        user = User.objects.create_user(email="auto-important@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
            auto_deducted=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"], [])

    def test_manually_selected_expense_remains_a_selected_candidate(self) -> None:
        user = User.objects.create_user(email="saved-important@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        RequiredExpense.objects.create(debt_profile=profile, source_key="phone", title="Phone", amount_cents=10000)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"][0]["key"], "phone")
        self.assertTrue(response.data["data"][0]["selected"])

    def test_ordinary_food_is_included_as_undecided(self) -> None:
        user = User.objects.create_user(email="food-undecided@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"][0]["key"], "food")
        self.assertFalse(response.data["data"][0]["selected"])

    def test_invalid_page_preserves_first_page_semantics(self) -> None:
        user = User.objects.create_user(email="invalid-page@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/?page=invalid", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["pagination"]["current_page"], 1)

    def test_anonymous_request_is_denied(self) -> None:
        client = APIClient()

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ordinary_internet_is_included_as_undecided(self) -> None:
        user = User.objects.create_user(email="internet-undecided@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=10000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"][0]["key"], "internet")

    def test_manually_selected_internet_remains_a_selected_candidate(self) -> None:
        user = User.objects.create_user(email="internet-selected@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=10000,
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            title="Internet",
            amount_cents=10000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"][0]["key"], "internet")
        self.assertTrue(response.data["data"][0]["selected"])

    def test_other_users_expenses_are_not_returned(self) -> None:
        jane = User.objects.create_user(email="jane-candidates@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="bob-candidates@example.com", password="StrongPassword123!")
        jane_profile = DebtProfile.objects.create(user=jane)
        DebtProfile.objects.create(user=bob)
        RecurringExpense.objects.create(
            debt_profile=jane_profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=10000,
        )
        client = APIClient()
        client.force_authenticate(user=bob)

        response = client.get("/api/debt-profile/important-expenses/", secure=True)

        self.assertEqual(response.data["data"], [])

    @override_settings(DEBUG=True)
    def test_owner_can_replace_important_selection_through_cookie_auth_and_csrf(self) -> None:
        cache.clear()

        owner = User.objects.create_user(email="owner-important@example.com", password="StrongPassword123!")
        owner_profile = DebtProfile.objects.create(user=owner)
        RecurringExpense.objects.create(
            debt_profile=owner_profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        client = APIClient(enforce_csrf_checks=True)
        pre_login_csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "owner-important@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=pre_login_csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])

        self.assertNotEqual(pre_login_csrf_token, post_login_csrf_token)

        response = client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["food"]},
            format="json",
            HTTP_X_CSRFTOKEN=post_login_csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"selected_keys": ["food"]})
        self.assertEqual(
            list(owner_profile.required_expenses.values_list("source_key", flat=True)),
            ["food"],
        )

    @override_settings(DEBUG=True)
    def test_selection_is_scoped_to_cookie_authenticated_owner(self) -> None:
        cache.clear()

        jane = User.objects.create_user(email="jane-important@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="bob-important@example.com", password="StrongPassword123!")
        jane_profile = DebtProfile.objects.create(user=jane)
        bob_profile = DebtProfile.objects.create(user=bob)
        RecurringExpense.objects.create(
            debt_profile=jane_profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        RecurringExpense.objects.create(
            debt_profile=bob_profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=50000,
        )
        RequiredExpense.objects.create(
            debt_profile=jane_profile,
            source_key="food",
            title="Food",
            amount_cents=40000,
        )
        client = APIClient(enforce_csrf_checks=True)
        pre_login_csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "bob-important@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=pre_login_csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        post_login_csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])

        self.assertNotEqual(pre_login_csrf_token, post_login_csrf_token)

        response = client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["food"]},
            format="json",
            HTTP_X_CSRFTOKEN=post_login_csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"selected_keys": ["food"]})
        self.assertTrue(RequiredExpense.objects.filter(debt_profile=jane_profile, source_key="food").exists())
        self.assertTrue(RequiredExpense.objects.filter(debt_profile=bob_profile, source_key="food").exists())

    def test_anonymous_patch_is_denied_without_mutation(self) -> None:
        user = User.objects.create_user(email="anonymous-important@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        client = APIClient(enforce_csrf_checks=True)

        response = client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["food"]},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(profile.required_expenses.exists())

    @override_settings(DEBUG=True)
    def test_authenticated_patch_without_csrf_is_rejected_without_mutation(self) -> None:
        cache.clear()

        owner = User.objects.create_user(email="csrf-important@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=owner)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = str(client.get("/api/auth/csrf/", secure=True).data["csrfToken"])
        login_response = client.post(
            "/api/auth/login/",
            {"email": "csrf-important@example.com", "password": "StrongPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.patch(
            "/api/debt-profile/important-expenses/",
            {"selected_keys": ["food"]},
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(profile.required_expenses.exists())
