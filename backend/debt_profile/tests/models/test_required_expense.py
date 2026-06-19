from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, RequiredExpense


class RequiredExpenseTest(TestCase):
    def test_source_key_is_unique_per_debt_profile(self) -> None:
        user = User.objects.create_user(
            email="required-expense-model@example.com",
            password="StrongPassword123!",
        )
        debt_profile = DebtProfile.objects.create(user=user)
        RequiredExpense.objects.create(
            debt_profile=debt_profile,
            source_key="food_cents",
            title="Food",
            amount_cents=50000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            RequiredExpense.objects.create(
                debt_profile=debt_profile,
                source_key="food_cents",
                title="Food",
                amount_cents=60000,
            )
