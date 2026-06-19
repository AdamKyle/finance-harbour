from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import DebtProfile, PaymentPlan


class PaymentPlanViewTest(APITestCase):
    def test_authenticated_user_can_save_extra_payment_cents(self) -> None:
        user = User.objects.create_user(
            email="extraplan@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/payment-plan/",
            {"extra_payment_cents": 25000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["extra_payment_cents"], 25000)

    def test_authenticated_user_can_save_spending_payment_percentage_basis_points(self) -> None:
        user = User.objects.create_user(
            email="spendingbp@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/payment-plan/",
            {"spending_payment_percentage_basis_points": 1500},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["spending_payment_percentage_basis_points"], 1500)

    def test_money_is_stored_as_cents(self) -> None:
        user = User.objects.create_user(
            email="planmoneycents@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/payment-plan/",
            {"extra_payment_cents": 50000},
            format="json",
            secure=True,
        )

        debt_profile = DebtProfile.objects.get(user=user)
        plan = PaymentPlan.objects.get(debt_profile=debt_profile)
        self.assertEqual(plan.extra_payment_cents, 50000)

    def test_percentage_is_stored_as_basis_points(self) -> None:
        user = User.objects.create_user(
            email="percentageBP@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/payment-plan/",
            {"spending_payment_percentage_basis_points": 2000},
            format="json",
            secure=True,
        )

        debt_profile = DebtProfile.objects.get(user=user)
        plan = PaymentPlan.objects.get(debt_profile=debt_profile)
        self.assertEqual(plan.spending_payment_percentage_basis_points, 2000)

    def test_negative_extra_payment_cents_is_rejected(self) -> None:
        user = User.objects.create_user(
            email="negplan@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/payment-plan/",
            {"extra_payment_cents": -100},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_access_rejected(self) -> None:
        client = APIClient()

        response = client.patch(
            "/api/debt-profile/payment-plan/",
            {"extra_payment_cents": 10000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cross_user_access_rejected(self) -> None:
        user1 = User.objects.create_user(
            email="planowner@example.com",
            password="StrongPassword123!",
        )
        user2 = User.objects.create_user(
            email="planother@example.com",
            password="StrongPassword123!",
        )
        debt_profile1 = DebtProfile.objects.create(user=user1)
        PaymentPlan.objects.create(debt_profile=debt_profile1, extra_payment_cents=10000)

        client = APIClient()
        client.force_authenticate(user=user2)
        client.patch(
            "/api/debt-profile/payment-plan/",
            {"extra_payment_cents": 99999},
            format="json",
            secure=True,
        )

        plan = PaymentPlan.objects.get(debt_profile=debt_profile1)
        self.assertNotEqual(plan.extra_payment_cents, 99999)

    def test_response_returns_only_expected_fields(self) -> None:
        user = User.objects.create_user(
            email="planfields@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/payment-plan/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {"extra_payment_cents", "spending_payment_percentage_basis_points", "plan_data", "is_active"},
        )

    def test_no_fake_plan_generation_logic(self) -> None:
        user = User.objects.create_user(
            email="nofake@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/payment-plan/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["plan_data"], {})
