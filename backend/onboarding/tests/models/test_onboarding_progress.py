from django.test import TestCase

from authentication.models import User
from onboarding.models import OnboardingProgress


class OnboardingProgressStrTest(TestCase):
    def test_str_returns_user_id(self) -> None:
        user = User.objects.create_user(
            email="strtest@example.com",
            password="StrongPassword123!",
        )
        progress = OnboardingProgress.objects.create(user=user)

        self.assertEqual(str(progress), f"OnboardingProgress({user.id})")
