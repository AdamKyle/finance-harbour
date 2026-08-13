from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory, UtilityType


class RecurringExpenseModelTest(TestCase):
    def test_source_key_is_unique_per_profile(self) -> None:
        user = User.objects.create_user(email="expense-model@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water + electricity",
            amount_cents=18000,
            utility_type=UtilityType.WATER_AND_ELECTRICITY,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            RecurringExpense.objects.create(
                debt_profile=profile,
                source_key="utilities",
                category=RecurringExpenseCategory.UTILITIES,
                label="Hydro",
                amount_cents=20000,
                utility_type=UtilityType.CUSTOM,
            )

    def test_included_services_require_utilities_category(self) -> None:
        user = User.objects.create_user(email="included-model@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)

        with self.assertRaises(IntegrityError), transaction.atomic():
            RecurringExpense.objects.create(
                debt_profile=profile,
                source_key="internet",
                category=RecurringExpenseCategory.INTERNET,
                label="Internet",
                amount_cents=9000,
                includes_internet=True,
            )
