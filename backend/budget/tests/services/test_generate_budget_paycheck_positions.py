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
)


class GenerateBudgetPaycheckPositionsTest(TestCase):
    def test_biweekly_timeline_start_preserves_calendar_positions(self) -> None:
        user = User.objects.create_user(email="biweekly-cadence@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 21),
        )

        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="first",
            category=RecurringExpenseCategory.PHONE,
            label="First",
            amount_cents=10000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="second",
            category=RecurringExpenseCategory.PHONE,
            label="Second",
            amount_cents=10000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="last",
            category=RecurringExpenseCategory.PHONE,
            label="Last",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="first",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="second",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.SECOND,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="last",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.LAST,
        )

        plan = generate_budget(user)
        august_twenty_first = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21))
        september_fourth = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))

        self.assertFalse(august_twenty_first.line_items.filter(source_key="first").exists())
        self.assertTrue(august_twenty_first.line_items.filter(source_key="second").exists())
        self.assertTrue(august_twenty_first.line_items.filter(source_key="last").exists())
        self.assertTrue(september_fourth.line_items.filter(source_key="first").exists())
        self.assertFalse(september_fourth.line_items.filter(source_key="second").exists())
        self.assertFalse(september_fourth.line_items.filter(source_key="last").exists())

    def test_weekly_timeline_start_preserves_fourth_calendar_position(self) -> None:
        user = User.objects.create_user(email="weekly-cadence@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 28),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="fourth",
            category=RecurringExpenseCategory.PHONE,
            label="Fourth",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="fourth",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FOURTH,
        )

        plan = generate_budget(user)

        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 28)).line_items.filter(source_key="fourth").exists()
        )

    def test_biweekly_first_appears_only_on_first_paycheck(self) -> None:
        user = User.objects.create_user(email="biweekly-first@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )

        plan = generate_budget(user)

        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 7)).line_items.filter(source_key="phone").exists()
        )
        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21)).line_items.filter(source_key="phone").exists()
        )

    def test_biweekly_second_does_not_repeat_on_extra_paycheck(self) -> None:
        user = User.objects.create_user(email="biweekly-second@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 10, 2),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.SECOND,
        )

        plan = generate_budget(user)

        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 10, 16)).line_items.filter(source_key="phone").exists()
        )
        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 10, 30)).line_items.filter(source_key="phone").exists()
        )

    def test_biweekly_last_uses_third_paycheck_in_extra_paycheck_month(self) -> None:
        user = User.objects.create_user(email="biweekly-last@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 10, 2),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.LAST,
        )

        plan = generate_budget(user)

        october_items = plan.pay_periods.filter(pay_date__month=10, line_items__source_key="phone")
        self.assertEqual(october_items.count(), 1)
        self.assertEqual(october_items.get().pay_date, datetime.date(2026, 10, 30))

    def test_weekly_fourth_and_last_share_fourth_paycheck_without_duplicates(self) -> None:
        user = User.objects.create_user(email="weekly-four@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 2, 6),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.LAST,
        )

        plan = generate_budget(user)

        february_items = plan.pay_periods.filter(pay_date__month=2, line_items__source_key="phone")
        self.assertEqual(february_items.count(), 1)
        self.assertEqual(february_items.get().pay_date, datetime.date(2026, 2, 27))

    def test_weekly_last_uses_fifth_paycheck(self) -> None:
        user = User.objects.create_user(email="weekly-five@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 5, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.LAST,
        )

        plan = generate_budget(user)

        self.assertEqual(
            plan.pay_periods.get(line_items__source_key="phone", pay_date__month=5).pay_date,
            datetime.date(2026, 5, 29),
        )

    def test_monthly_position_appears_once(self) -> None:
        user = User.objects.create_user(email="monthly-position@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )

        plan = generate_budget(user)

        self.assertEqual(plan.pay_periods.filter(pay_date__month=8, line_items__source_key="phone").count(), 1)
