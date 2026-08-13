import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    RecurringExpense,
    RecurringExpenseCategory,
    RequiredExpense,
    UtilityType,
)


class GenerateBudgetObligationsTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="generated-obligations@example.com", password="StrongPassword123!")
        self.profile = DebtProfile.objects.create(
            user=self.user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 1),
        )

    def test_recurring_expense_generates_expected_line_item(self) -> None:
        RecurringExpense.objects.create(
            debt_profile=self.profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Mobile phone",
            amount_cents=12000,
        )

        item = generate_budget(self.user).pay_periods.first().line_items.get(source_key="phone")

        self.assertEqual(item.title, "Mobile phone")
        self.assertEqual(item.amount_cents, 12000)
        self.assertEqual(item.source_type, SourceType.STANDARD_EXPENSE)

    def test_debt_payment_generates_expected_line_item(self) -> None:
        self.profile.debts = [
            {
                "label": "Visa",
                "current_balance_cents": 500000,
                "minimum_payment_cents": 5000,
                "current_payment_cents": 7500,
            }
        ]
        self.profile.save(update_fields=["debts"])

        item = generate_budget(self.user).pay_periods.first().line_items.get(source_key="debt:0")

        self.assertEqual(item.title, "Visa")
        self.assertEqual(item.amount_cents, 7500)
        self.assertEqual(item.source_type, SourceType.DEBT)

    def test_required_expense_generates_important_line_item(self) -> None:
        RecurringExpense.objects.create(
            debt_profile=self.profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=15000,
        )
        RequiredExpense.objects.create(
            debt_profile=self.profile,
            source_key="insurance",
            title="Insurance",
            amount_cents=15000,
        )

        item = generate_budget(self.user).pay_periods.first().line_items.get(source_key="insurance")

        self.assertTrue(item.is_required)

    def test_misc_expense_generates_misc_line_item(self) -> None:
        RecurringExpense.objects.create(
            debt_profile=self.profile,
            source_key="misc:0",
            category=RecurringExpenseCategory.MISC,
            label="Streaming",
            amount_cents=2500,
        )

        item = generate_budget(self.user).pay_periods.first().line_items.get(source_key="misc:0")

        self.assertEqual(item.source_type, SourceType.MISC_EXPENSE)

    def test_combined_utilities_generate_once_without_separate_internet(self) -> None:
        RecurringExpense.objects.create(
            debt_profile=self.profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water + electricity",
            amount_cents=18000,
            utility_type=UtilityType.WATER_AND_ELECTRICITY,
            includes_internet=True,
        )

        plan = generate_budget(self.user)
        utility_items = plan.pay_periods.first().line_items.filter(source_key="utilities")

        self.assertEqual(utility_items.count(), 1)
        self.assertFalse(plan.pay_periods.filter(line_items__source_key="internet").exists())
