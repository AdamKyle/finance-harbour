import datetime

from django.test import TestCase

from authentication.models import User
from budget.models import SourceType
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile


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
