from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile


class DebtProfileStrTest(TestCase):
    def test_str_returns_user_id(self) -> None:
        user = User.objects.create_user(
            email="dpstr@example.com",
            password="StrongPassword123!",
        )
        profile = DebtProfile.objects.create(user=user)

        self.assertEqual(str(profile), f"DebtProfile({user.id})")
