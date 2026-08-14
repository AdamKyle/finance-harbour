from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, RequiredExpense


class RequiredExpenseTest(TestCase):
    def test_str_representation(self) -> None:
        user = User.objects.create_user(
            email="required-expense-str@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        expense = RequiredExpense.objects.create(
            debt_profile=debt_profile,
            source_key="food",
            title="Food",
            amount_cents=50000,
        )

        self.assertEqual(str(expense), f"RequiredExpense({debt_profile.pk}, food)")

    def test_source_key_is_unique_per_debt_profile(self) -> None:
        user = User.objects.create_user(
            email="required-expense-model@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        RequiredExpense.objects.create(
            debt_profile=debt_profile,
            source_key="food",
            title="Food",
            amount_cents=50000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            RequiredExpense.objects.create(
                debt_profile=debt_profile,
                source_key="food",
                title="Food",
                amount_cents=60000,
            )
