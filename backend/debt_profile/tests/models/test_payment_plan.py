from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, PaymentPlan


class PaymentPlanStrTest(TestCase):
    def test_str_returns_debt_profile_id(self) -> None:
        user = User.objects.create_user(
            email="ppstr@example.com",
            password="StrongPassword123!",
        )
        profile = DebtProfile.objects.create(user=user)
        plan = PaymentPlan.objects.create(debt_profile=profile)

        self.assertEqual(str(plan), f"PaymentPlan({profile.id})")
