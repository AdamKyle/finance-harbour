from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, MonthlyExpense, PaymentPlan


class DebtProfileStrTest(TestCase):
    def test_str_returns_user_id(self) -> None:
        user = User.objects.create_user(
            email="dpstr@example.com",
            password="StrongPassword123!",
        )
        profile = DebtProfile.objects.create(user=user)

        self.assertEqual(str(profile), f"DebtProfile({user.id})")


class MonthlyExpenseStrTest(TestCase):
    def test_str_returns_debt_profile_id(self) -> None:
        user = User.objects.create_user(
            email="mestr@example.com",
            password="StrongPassword123!",
        )
        profile = DebtProfile.objects.create(user=user)
        expense = MonthlyExpense.objects.create(debt_profile=profile)

        self.assertEqual(str(expense), f"MonthlyExpense({profile.id})")


class PaymentPlanStrTest(TestCase):
    def test_str_returns_debt_profile_id(self) -> None:
        user = User.objects.create_user(
            email="ppstr@example.com",
            password="StrongPassword123!",
        )
        profile = DebtProfile.objects.create(user=user)
        plan = PaymentPlan.objects.create(debt_profile=profile)

        self.assertEqual(str(plan), f"PaymentPlan({profile.id})")
