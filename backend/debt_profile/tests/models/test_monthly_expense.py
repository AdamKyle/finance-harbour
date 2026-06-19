from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, MonthlyExpense


class MonthlyExpenseStrTest(TestCase):
    def test_str_returns_debt_profile_id(self) -> None:
        user = User.objects.create_user(
            email="mestr@example.com",
            password="StrongPassword123!",
        )
        profile = DebtProfile.objects.create(user=user)
        expense = MonthlyExpense.objects.create(debt_profile=profile)

        self.assertEqual(str(expense), f"MonthlyExpense({profile.id})")
