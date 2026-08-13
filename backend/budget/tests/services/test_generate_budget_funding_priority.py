import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    PaycheckPosition,
    RecurringExpense,
    RecurringExpenseCategory,
    RequiredExpense,
)


class GenerateBudgetFundingPriorityTest(TestCase):
    def test_important_obligation_is_funded_before_debt(self) -> None:
        user = User.objects.create_user(email="important-before-debt@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=150000,
            next_pay_date=datetime.date(2026, 8, 1),
            debts=[{"label": "Visa", "current_balance_cents": 500000, "current_payment_cents": 50000}],
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="rent",
            category=RecurringExpenseCategory.RENT_OR_MORTGAGE,
            label="Rent",
            amount_cents=147500,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="rent",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )

        period = generate_budget(user).pay_periods.first()
        rent = period.line_items.get(source_key="rent")
        debt = period.line_items.get(source_key="debt:0")

        self.assertEqual(rent.funded_amount_cents, 147500)
        self.assertEqual(rent.shortfall_cents, 0)
        self.assertEqual(debt.funded_amount_cents, 2500)
        self.assertEqual(debt.shortfall_cents, 47500)
        self.assertEqual(period.total_bills_cents, 197500)

    def test_important_debt_uses_important_priority(self) -> None:
        user = User.objects.create_user(email="important-debt@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=12000,
            next_pay_date=datetime.date(2026, 8, 1),
            debts=[
                {"label": "Normal debt", "current_balance_cents": 100000, "current_payment_cents": 10000},
                {"label": "Automatic debt", "current_balance_cents": 100000, "current_payment_cents": 10000},
            ],
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:1",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=1,
            auto_deducted=True,
        )

        period = generate_budget(user).pay_periods.first()
        important_debt = period.line_items.get(source_key="debt:1")
        normal_debt = period.line_items.get(source_key="debt:0")

        self.assertEqual(important_debt.funded_amount_cents, 10000)
        self.assertEqual(normal_debt.funded_amount_cents, 2000)
        self.assertEqual(normal_debt.shortfall_cents, 8000)

    def test_debt_is_funded_before_standard_expense(self) -> None:
        user = User.objects.create_user(email="debt-before-standard@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=10000,
            next_pay_date=datetime.date(2026, 8, 1),
            debts=[{"label": "Visa", "current_balance_cents": 100000, "current_payment_cents": 8000}],
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=8000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )

        period = generate_budget(user).pay_periods.first()

        self.assertEqual(period.line_items.get(source_key="debt:0").funded_amount_cents, 8000)
        self.assertEqual(period.line_items.get(source_key="phone").funded_amount_cents, 2000)

    def test_standard_expense_is_funded_before_misc(self) -> None:
        user = User.objects.create_user(email="standard-before-misc@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=10000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=8000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="misc:0",
            category=RecurringExpenseCategory.MISC,
            label="Streaming",
            amount_cents=8000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="misc:0",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )

        period = generate_budget(user).pay_periods.first()

        self.assertEqual(period.line_items.get(source_key="phone").funded_amount_cents, 8000)
        self.assertEqual(period.line_items.get(source_key="misc:0").funded_amount_cents, 2000)

    def test_important_obligations_keep_deterministic_order(self) -> None:
        user = User.objects.create_user(email="important-order@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=10000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance-one",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance one",
            amount_cents=8000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance-two",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance two",
            amount_cents=8000,
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="insurance-one",
            title="Insurance one",
            amount_cents=8000,
        )
        RequiredExpense.objects.create(
            debt_profile=profile,
            source_key="insurance-two",
            title="Insurance two",
            amount_cents=8000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance-one",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance-two",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )

        period = generate_budget(user).pay_periods.first()

        self.assertEqual(period.line_items.get(source_key="insurance-one").funded_amount_cents, 8000)
        self.assertEqual(period.line_items.get(source_key="insurance-two").funded_amount_cents, 2000)
        self.assertEqual(period.line_items.get(source_key="insurance-two").shortfall_cents, 6000)
