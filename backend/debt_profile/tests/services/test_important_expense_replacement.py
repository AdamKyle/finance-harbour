from django.test import TestCase

from authentication.models import User
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    RecurringExpense,
    RecurringExpenseCategory,
    RequiredExpense,
)
from debt_profile.services.important_expenses import build_important_expense_cards, replace_required_expenses


class ImportantExpenseReplacementTest(TestCase):
    def test_initial_selection_persists_exact_manual_set(self) -> None:
        user = User.objects.create_user(email="important-initial@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=10000,
        )

        replace_required_expenses(profile, ["food", "internet"])

        self.assertEqual(set(profile.required_expenses.values_list("source_key", flat=True)), {"food", "internet"})

    def test_resubmission_removes_deselected_manual_expense(self) -> None:
        user = User.objects.create_user(email="important-remove@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=10000,
        )
        RequiredExpense.objects.create(debt_profile=profile, source_key="food", title="Food", amount_cents=40000)
        RequiredExpense.objects.create(
            debt_profile=profile, source_key="internet", title="Internet", amount_cents=10000
        )

        replace_required_expenses(profile, ["food"])

        self.assertEqual(list(profile.required_expenses.values_list("source_key", flat=True)), ["food"])

    def test_resubmission_replaces_manual_selection(self) -> None:
        user = User.objects.create_user(email="important-replace@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        RequiredExpense.objects.create(debt_profile=profile, source_key="food", title="Food", amount_cents=40000)

        replace_required_expenses(profile, ["phone"])

        self.assertEqual(list(profile.required_expenses.values_list("source_key", flat=True)), ["phone"])

    def test_empty_submission_clears_manual_selection(self) -> None:
        user = User.objects.create_user(email="important-clear@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=10000,
        )
        RequiredExpense.objects.create(debt_profile=profile, source_key="food", title="Food", amount_cents=40000)
        RequiredExpense.objects.create(
            debt_profile=profile, source_key="internet", title="Internet", amount_cents=10000
        )

        replace_required_expenses(profile, [])

        self.assertFalse(profile.required_expenses.exists())

    def test_rent_remains_system_important_without_required_expense_row(self) -> None:
        user = User.objects.create_user(email="important-rent-system@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="rent_or_mortgage",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent",
            amount_cents=150000,
        )
        RequiredExpense.objects.create(
            debt_profile=profile, source_key="rent_or_mortgage", title="Rent", amount_cents=150000
        )

        replace_required_expenses(profile, [])

        self.assertFalse(profile.required_expenses.exists())
        self.assertEqual(build_important_expense_cards(profile), [])

    def test_auto_deducted_remains_system_important_without_required_expense_row(self) -> None:
        user = User.objects.create_user(email="important-auto-system@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
            auto_deducted=True,
        )
        RequiredExpense.objects.create(
            debt_profile=profile, source_key="insurance", title="Insurance", amount_cents=10000
        )

        replace_required_expenses(profile, [])

        self.assertFalse(profile.required_expenses.exists())
        self.assertEqual(build_important_expense_cards(profile), [])

    def test_manual_removal_does_not_expose_system_important_expense(self) -> None:
        user = User.objects.create_user(email="important-combined@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(user=user)
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
            auto_deducted=True,
        )
        RequiredExpense.objects.create(debt_profile=profile, source_key="food", title="Food", amount_cents=40000)

        replace_required_expenses(profile, [])

        self.assertFalse(profile.required_expenses.exists())
        self.assertEqual(build_important_expense_cards(profile)[0]["key"], "food")

    def test_manual_debt_selection_uses_required_expense_workflow(self) -> None:
        user = User.objects.create_user(email="important-debt@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            debts=[
                {
                    "label": "Student Loan",
                    "current_balance_cents": 1200000,
                    "minimum_payment_cents": 10000,
                    "current_payment_cents": 15000,
                }
            ],
        )

        cards = build_important_expense_cards(profile)
        replace_required_expenses(profile, ["debt:0"])

        self.assertEqual(cards[0]["key"], "debt:0")
        self.assertEqual(cards[0]["amount_cents"], 15000)
        self.assertTrue(profile.required_expenses.filter(source_key="debt:0").exists())
