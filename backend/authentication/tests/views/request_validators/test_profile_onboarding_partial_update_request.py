from django.test import TestCase
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.views.request_validators import ProfileOnboardingPartialUpdateRequest


class ProfileOnboardingPartialUpdateRequestTest(TestCase):
    def test_valid_profile_data_passes_validation(self) -> None:
        user = User.objects.create_user(
            email="valid-profile-request@example.com",
            password="StrongPassword123!",
        )
        profile_request = ProfileOnboardingPartialUpdateRequest(
            {
                "nickname": "ValidNick",
                "profile_photo": "avatar-1",
            },
            instance=user,
        )

        profile_request.validate()

        self.assertEqual(
            profile_request.validated_data,
            {
                "nickname": "ValidNick",
                "profile_photo": "avatar-1",
            },
        )

    def test_duplicate_nickname_fails_validation(self) -> None:
        User.objects.create_user(
            email="existing-profile-request@example.com",
            password="StrongPassword123!",
            nickname="ExistingNick",
        )
        user = User.objects.create_user(
            email="duplicate-profile-request@example.com",
            password="StrongPassword123!",
        )
        profile_request = ProfileOnboardingPartialUpdateRequest(
            {"nickname": "existingnick"},
            instance=user,
        )

        with self.assertRaises(ValidationError) as raised_error:
            profile_request.validate()

        self.assertIn("nickname", raised_error.exception.detail)

    def test_blank_nickname_fails_validation(self) -> None:
        user = User.objects.create_user(
            email="blank-profile-request@example.com",
            password="StrongPassword123!",
        )
        profile_request = ProfileOnboardingPartialUpdateRequest(
            {"nickname": ""},
            instance=user,
        )

        with self.assertRaises(ValidationError) as raised_error:
            profile_request.validate()

        self.assertIn("nickname", raised_error.exception.detail)

    def test_current_users_nickname_is_excluded_from_unique_validation(self) -> None:
        user = User.objects.create_user(
            email="same-profile-request@example.com",
            password="StrongPassword123!",
            nickname="SameNick",
        )
        profile_request = ProfileOnboardingPartialUpdateRequest(
            {"nickname": "SameNick"},
            instance=user,
        )

        profile_request.validate()

        self.assertEqual(profile_request.validated_data, {"nickname": "SameNick"})

    def test_whitespace_only_nickname_fails_validation(self) -> None:
        user = User.objects.create_user(
            email="whitespace-profile-request@example.com",
            password="StrongPassword123!",
        )
        profile_request = ProfileOnboardingPartialUpdateRequest(
            {"nickname": "   "},
            instance=user,
        )

        with self.assertRaises(ValidationError) as raised_error:
            profile_request.validate()

        self.assertIn("nickname", raised_error.exception.detail)
