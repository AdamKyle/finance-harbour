from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import DebtProfile


class LeftOverWarningThresholdViewTest(APITestCase):
    def test_save_requires_authentication(self) -> None:
        client = APIClient()

        response = client.patch(
            "/api/debt-profile/left-over-warning-threshold/",
            {"left_over_warning_amount_cents": 5000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_save_updates_debt_profile_cents(self) -> None:
        user = User.objects.create_user(
            email="threshold-save@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/left-over-warning-threshold/",
            {"left_over_warning_amount_cents": 175600},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            DebtProfile.objects.get(user=user).left_over_warning_amount_cents,
            175600,
        )

    def test_save_rejects_negative_cents(self) -> None:
        user = User.objects.create_user(
            email="threshold-negative@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/left-over-warning-threshold/",
            {"left_over_warning_amount_cents": -1},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_does_not_mark_onboarding_complete(self) -> None:
        user = User.objects.create_user(
            email="threshold-incomplete@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/left-over-warning-threshold/",
            {"left_over_warning_amount_cents": 5000},
            format="json",
            secure=True,
        )

        user.refresh_from_db()

        self.assertFalse(user.completed_onboarding)
