from django.test import TestCase
from rest_framework.exceptions import ValidationError

from authentication.models import User
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory
from debt_profile.views.request_validators.important_expenses_save_request import ImportantExpensesSaveRequest


class ImportantExpensesSaveRequestTest(TestCase):
    def test_rejects_a_source_outside_the_owners_recurring_expenses(self) -> None:
        user = User.objects.create_user(email="important-validator@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        request = ImportantExpensesSaveRequest({"selected_keys": ["utilities"]}, profile)

        with self.assertRaises(ValidationError):
            request.validate()
