import datetime

from django.test import TestCase

from authentication.models import User
from budget.services.budget_generator import generate_budget
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    RecurringExpense,
    RecurringExpenseCategory,
)


class GenerateBudgetInitialPartialCycleTest(TestCase):
    def test_bill_before_first_payday_is_allocated_to_first_generated_period(self) -> None:
        user = User.objects.create_user(email="partial-cycle@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 22),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="insurance", timing=ExpensePaymentTiming.DAY_OF_MONTH, day_of_month=17
        )

        plan = generate_budget(user)
        first_period = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 22))

        self.assertTrue(
            first_period.line_items.filter(
                source_key="insurance", expected_payment_date=datetime.date(2026, 8, 17)
            ).exists()
        )
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2026, 8, 22)).exists())

    def test_bill_before_planning_date_is_not_injected_historically(self) -> None:
        user = User.objects.create_user(email="outside-cycle@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 22),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="insurance", timing=ExpensePaymentTiming.DAY_OF_MONTH, day_of_month=10
        )

        plan = generate_budget(user)
        first_period = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 22))
        september_period = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 5))

        self.assertFalse(first_period.line_items.filter(source_key="insurance").exists())
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2026, 8, 22)).exists())
        september_insurance = september_period.line_items.get(source_key="insurance")
        self.assertEqual(september_insurance.expected_payment_date, datetime.date(2026, 9, 10))

    def test_weekend_adjusted_bill_is_allocated_to_first_generated_period(self) -> None:
        user = User.objects.create_user(email="partial-weekend@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 22),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile, source_key="insurance", timing=ExpensePaymentTiming.DAY_OF_MONTH, day_of_month=15
        )

        plan = generate_budget(user)
        first_period = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 22))

        self.assertTrue(
            first_period.line_items.filter(
                source_key="insurance", expected_payment_date=datetime.date(2026, 8, 17)
            ).exists()
        )
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2026, 8, 22)).exists())
