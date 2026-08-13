import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    RequiredExpense,
)


class GenerateBudgetWithDebtsTest(TestCase):
    def test_debt_line_items_appear_in_budget(self) -> None:
        user = User.objects.create_user(email="budget_debts@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=400000,
            next_pay_date=anchor,
            debts=[
                {
                    "label": "Visa",
                    "current_balance_cents": 500000,
                    "minimum_payment_cents": 10000,
                    "current_payment_cents": 15000,
                }
            ],
        )
        plan = generate_budget(user)
        first = plan.pay_periods.first()
        debt_items = first.line_items.filter(source_type=SourceType.DEBT)
        self.assertEqual(debt_items.count(), 1)
        self.assertEqual(debt_items.first().title, "Visa")
        self.assertEqual(debt_items.first().amount_cents, 15000)

    def test_debt_with_default_label(self) -> None:
        user = User.objects.create_user(email="budget_debt_nolabel@example.com", password="StrongPassword123!")
        anchor = datetime.date(2025, 8, 1)
        DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=400000,
            next_pay_date=anchor,
            debts=[
                {
                    "current_balance_cents": 500000,
                    "minimum_payment_cents": 10000,
                    "current_payment_cents": 15000,
                }
            ],
        )
        plan = generate_budget(user)
        first = plan.pay_periods.first()
        debt_items = first.line_items.filter(source_type=SourceType.DEBT)
        self.assertEqual(debt_items.first().title, "Debt 1")

    def test_manually_important_debt_is_required_without_auto_deduction(self) -> None:
        user = User.objects.create_user(email="manual-important-debt@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=400000,
            next_pay_date=datetime.date(2026, 8, 1),
            debts=[
                {
                    "label": "Student Loan",
                    "current_balance_cents": 500000,
                    "minimum_payment_cents": 10000,
                    "current_payment_cents": 15000,
                }
            ],
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            title="Student Loan",
            amount_cents=15000,
        )

        item = generate_budget(user).pay_periods.first().line_items.get(source_key="debt:0")

        self.assertTrue(item.is_required)
        self.assertFalse(item.is_auto_deducted)

    def test_auto_deducted_debt_is_required_without_manual_importance(self) -> None:
        user = User.objects.create_user(email="automatic-important-debt@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=400000,
            next_pay_date=datetime.date(2026, 8, 1),
            debts=[
                {
                    "label": "Student Loan",
                    "current_balance_cents": 500000,
                    "minimum_payment_cents": 10000,
                    "current_payment_cents": 15000,
                }
            ],
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=10,
            auto_deducted=True,
        )

        item = generate_budget(user).pay_periods.first().line_items.get(source_key="debt:0")

        self.assertTrue(item.is_required)
        self.assertTrue(item.is_auto_deducted)
