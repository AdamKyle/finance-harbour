from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from onboarding.models import OnboardingProgress


class OnboardingProgressViewSetTest(APITestCase):
    def test_get_creates_progress_for_authenticated_user(self) -> None:
        user = User.objects.create_user(
            email="getprogress@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(OnboardingProgress.objects.filter(user=user).exists())

    def test_get_returns_existing_progress(self) -> None:
        user = User.objects.create_user(
            email="existing@example.com",
            password="StrongPassword123!",
        )
        OnboardingProgress.objects.create(
            user=user,
            current_step="income",
            completed_steps=["profile", "debts"],
            form_data={"profile": {"nickname": "Test"}},
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_step"], "income")
        self.assertEqual(response.data["completed_steps"], ["profile", "debts"])

    def test_patch_saves_current_step(self) -> None:
        user = User.objects.create_user(
            email="patchstep@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/onboarding/progress/",
            {"current_step": "debts"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_step"], "debts")
        self.assertEqual(OnboardingProgress.objects.get(user=user).current_step, "debts")

    def test_patch_saves_completed_steps(self) -> None:
        user = User.objects.create_user(
            email="patchcompleted@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/onboarding/progress/",
            {"completed_steps": ["profile"]},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_steps"], ["profile"])
        self.assertEqual(
            OnboardingProgress.objects.get(user=user).completed_steps,
            ["profile"],
        )

    def test_patch_saves_form_data(self) -> None:
        user = User.objects.create_user(
            email="patchformdata@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        form_data = {"profile": {"nickname": "TestUser", "selectedAvatarId": "avatar-1"}}
        response = client.patch(
            "/api/onboarding/progress/",
            {"form_data": form_data},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        saved = OnboardingProgress.objects.get(user=user)
        self.assertEqual(saved.form_data["profile"]["nickname"], "TestUser")

    def test_saved_progress_is_returned_after_refresh_style_reload(self) -> None:
        user = User.objects.create_user(
            email="refresh@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/onboarding/progress/",
            {"current_step": "expenses"},
            format="json",
            secure=True,
        )

        response = client.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_step"], "expenses")

    def test_saved_progress_is_returned_after_logout_login_style_reauthentication(self) -> None:
        user = User.objects.create_user(
            email="reauth@example.com",
            password="StrongPassword123!",
        )
        client1 = APIClient()
        client1.force_authenticate(user=user)
        client1.patch(
            "/api/onboarding/progress/",
            {"current_step": "income"},
            format="json",
            secure=True,
        )

        client2 = APIClient()
        client2.force_authenticate(user=user)
        response = client2.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_step"], "income")

    def test_anonymous_get_rejected(self) -> None:
        client = APIClient()

        response = client.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_rejected(self) -> None:
        client = APIClient()

        response = client.patch(
            "/api/onboarding/progress/",
            {"current_step": "debts"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_read_another_users_progress(self) -> None:
        user1 = User.objects.create_user(
            email="owner@example.com",
            password="StrongPassword123!",
        )
        user2 = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
        )
        OnboardingProgress.objects.create(
            user=user1,
            current_step="expenses",
        )

        client = APIClient()
        client.force_authenticate(user=user2)
        response = client.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["current_step"], "expenses")

    def test_user_cannot_write_another_users_progress(self) -> None:
        user1 = User.objects.create_user(
            email="writeowner@example.com",
            password="StrongPassword123!",
        )
        user2 = User.objects.create_user(
            email="writeother@example.com",
            password="StrongPassword123!",
        )
        OnboardingProgress.objects.create(user=user1, current_step="profile")

        client = APIClient()
        client.force_authenticate(user=user2)
        client.patch(
            "/api/onboarding/progress/",
            {"current_step": "conclude"},
            format="json",
            secure=True,
        )

        user1_progress = OnboardingProgress.objects.get(user=user1)
        self.assertNotEqual(user1_progress.current_step, "conclude")

    def test_response_returns_only_expected_fields(self) -> None:
        user = User.objects.create_user(
            email="responsefields@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {"current_step", "completed_steps", "form_data", "is_complete"},
        )
