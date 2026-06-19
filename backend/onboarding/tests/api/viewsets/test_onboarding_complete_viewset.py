from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import DebtProfile, MonthlyExpense
from onboarding.models import OnboardingProgress


class OnboardingCompleteViewTest(APITestCase):
    def test_completion_endpoint_requires_authentication(self) -> None:
        client = APIClient()

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completion_fails_when_no_debt_profile_exists(self) -> None:
        user = User.objects.create_user(
            email="nodata@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_debts_are_required_for_completion(self) -> None:
        user = User.objects.create_user(
            email="nodebts@example.com",
            password="StrongPassword123!",
        )
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[],
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_income_is_required_for_completion(self) -> None:
        user = User.objects.create_user(
            email="noincome@example.com",
            password="StrongPassword123!",
        )
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=0,
            pay_period_type="",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expenses_are_required_for_completion(self) -> None:
        user = User.objects.create_user(
            email="noexpenses@example.com",
            password="StrongPassword123!",
        )
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_step_is_optional_for_completion(self) -> None:
        user = User.objects.create_user(
            email="noprofile@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(debt_profile=debt_profile, rent_or_mortgage_cents=150000)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_completion_does_not_mark_completed_onboarding_true(self) -> None:
        user = User.objects.create_user(
            email="invalidcomplete@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        user.refresh_from_db()
        self.assertFalse(user.completed_onboarding)

    def test_valid_completion_marks_completed_onboarding_true(self) -> None:
        user = User.objects.create_user(
            email="validcomplete@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="WEEKLY",
            debts=[
                {
                    "label": "Loan",
                    "current_balance_cents": 500000,
                    "interest_rate_basis_points": 500,
                    "minimum_payment_cents": 10000,
                    "current_payment_cents": 15000,
                }
            ],
        )
        MonthlyExpense.objects.create(debt_profile=debt_profile, rent_or_mortgage_cents=100000)
        client = APIClient()
        client.force_authenticate(user=user)

        client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        user.refresh_from_db()
        self.assertTrue(user.completed_onboarding)

    def test_valid_completion_marks_progress_is_complete_true(self) -> None:
        user = User.objects.create_user(
            email="progresscomplete@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=300000,
            pay_period_type="MONTHLY",
            debts=[
                {
                    "label": "Mortgage",
                    "current_balance_cents": 2000000,
                    "interest_rate_basis_points": 350,
                    "minimum_payment_cents": 50000,
                    "current_payment_cents": 50000,
                }
            ],
        )
        MonthlyExpense.objects.create(debt_profile=debt_profile, food_cents=50000)
        client = APIClient()
        client.force_authenticate(user=user)

        client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        progress = OnboardingProgress.objects.get(user=user)
        self.assertTrue(progress.is_complete)

    def test_completion_response_does_not_expose_sensitive_extra_fields(self) -> None:
        user = User.objects.create_user(
            email="noextrafields@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=250000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(debt_profile=debt_profile, food_cents=40000)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/onboarding/complete/", {}, format="json", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"detail"})
