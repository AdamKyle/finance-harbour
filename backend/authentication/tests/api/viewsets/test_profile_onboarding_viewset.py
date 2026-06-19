from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User


class ProfileOnboardingViewSetTest(APITestCase):
    def test_authenticated_user_can_update_valid_profile_data(self) -> None:
        user = User.objects.create_user(
            email="nick@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/profile/onboarding/",
            {
                "nickname": "MyNick",
                "profile_photo": "avatar-1",
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()

        self.assertEqual(user.nickname, "MyNick")
        self.assertEqual(user.profile_photo, "avatar-1")
        self.assertEqual(response.data["nickname"], "MyNick")
        self.assertEqual(response.data["profile_photo"], "avatar-1")

    def test_profile_onboarding_requires_nickname(self) -> None:
        user = User.objects.create_user(
            email="photo@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/profile/onboarding/",
            {"profile_photo": "avatar-2"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)

    def test_profile_onboarding_rejects_blank_nickname(self) -> None:
        user = User.objects.create_user(
            email="blank-required@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/profile/onboarding/",
            {"nickname": ""},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)

    def test_profile_onboarding_rejects_duplicate_non_empty_nickname(self) -> None:
        User.objects.create_user(
            email="existing-nickname@example.com",
            password="StrongPassword123!",
            nickname="ExistingNick",
        )
        user = User.objects.create_user(
            email="duplicate-nickname@example.com",
            password="StrongPassword123!",
            nickname="OriginalNick",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/profile/onboarding/",
            {"nickname": "existingnick"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)

        user.refresh_from_db()

        self.assertEqual(user.nickname, "OriginalNick")

    def test_invalid_profile_data_does_not_mutate_user(self) -> None:
        user = User.objects.create_user(
            email="invalid-profile@example.com",
            password="StrongPassword123!",
            nickname="OriginalNick",
            profile_photo="avatar-original",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/profile/onboarding/",
            {
                "nickname": "n" * 101,
                "profile_photo": "avatar-updated",
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user.refresh_from_db()

        self.assertEqual(user.nickname, "OriginalNick")
        self.assertEqual(user.profile_photo, "avatar-original")

    def test_anonymous_user_cannot_update_profile_onboarding_data(self) -> None:
        client = APIClient()

        response = client.patch(
            "/api/profile/onboarding/",
            {"nickname": "Hacker"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_update_another_users_profile_data(self) -> None:
        user1 = User.objects.create_user(
            email="user1@example.com",
            password="StrongPassword123!",
            nickname="OriginalNick",
        )
        user2 = User.objects.create_user(
            email="user2@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user2)

        client.patch(
            "/api/profile/onboarding/",
            {"nickname": "HijackedNick"},
            format="json",
            secure=True,
        )

        user1.refresh_from_db()

        self.assertEqual(user1.nickname, "OriginalNick")

    def test_response_returns_only_expected_fields(self) -> None:
        user = User.objects.create_user(
            email="fields@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/profile/onboarding/",
            {"nickname": "FieldTest"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"nickname", "profile_photo", "completed_onboarding"})

    def test_get_returns_profile_onboarding_data(self) -> None:
        user = User.objects.create_user(
            email="getprofile@example.com",
            password="StrongPassword123!",
            nickname="GetNick",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/profile/onboarding/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "GetNick")
