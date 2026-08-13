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
    UtilityType,
)


class GenerateBudgetWithPaymentScheduleTest(TestCase):
    def test_combined_utilities_generate_once_on_the_responsible_pay_period(self) -> None:
        user = User.objects.create_user(email="scheduled-utility@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="utilities",
            category=RecurringExpenseCategory.UTILITIES,
            label="Water + electricity",
            amount_cents=18000,
            utility_type=UtilityType.WATER_AND_ELECTRICITY,
            includes_internet=True,
            includes_cable=True,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="utilities",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
        )

        plan = generate_budget(user)
        utility_items = plan.pay_periods.filter(line_items__source_key="utilities")

        self.assertEqual(utility_items.count(), 12)
        self.assertFalse(plan.pay_periods.filter(line_items__source_key="internet").exists())

    def test_shorter_month_clamps_then_moves_weekend_to_monday(self) -> None:
        user = User.objects.create_user(email="short-month@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 1, 31),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=18750,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=31,
        )

        plan = generate_budget(user)
        february_item = plan.pay_periods.get(pay_date=datetime.date(2026, 2, 28)).line_items.get(source_key="insurance")

        self.assertEqual(february_item.expected_payment_date, datetime.date(2026, 3, 2))

    def test_auto_deducted_date_obligation_is_important(self) -> None:
        user = User.objects.create_user(email="auto-deducted@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 1),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=18750,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=17,
            auto_deducted=True,
        )

        plan = generate_budget(user)
        insurance = plan.pay_periods.first().line_items.get(source_key="insurance")

        self.assertTrue(insurance.is_auto_deducted)
        self.assertTrue(insurance.is_required)

    def test_biweekly_date_schedule_uses_calendar_month_first_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-first@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=9000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="internet",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="FIRST",
            day_of_month=10,
        )

        plan = generate_budget(user)
        august_period = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21))
        september_period = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))

        self.assertFalse(august_period.line_items.filter(source_key="internet").exists())
        september_item = september_period.line_items.get(source_key="internet")
        self.assertEqual(september_item.expected_payment_date, datetime.date(2026, 9, 10))

    def test_weekly_date_schedule_uses_fourth_calendar_month_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-fourth@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=150000,
            next_pay_date=datetime.date(2026, 8, 28),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=8500,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="FOURTH",
            day_of_month=22,
        )

        plan = generate_budget(user)
        august_period = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 28))
        august_item = august_period.line_items.get(source_key="phone")

        self.assertEqual(august_item.expected_payment_date, datetime.date(2026, 8, 24))

    def test_monthly_date_schedule_funds_monthly_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-monthly@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=11679,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="FIRST",
            day_of_month=22,
        )

        plan = generate_budget(user)
        august_period = plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21))
        item = august_period.line_items.get(source_key="insurance")

        self.assertEqual(item.expected_payment_date, datetime.date(2026, 8, 24))

    def test_biweekly_date_schedule_funds_second_calendar_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-second@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=9000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="internet",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="SECOND",
            day_of_month=10,
        )

        plan = generate_budget(user)

        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 7)).line_items.filter(source_key="internet").exists()
        )
        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21)).line_items.filter(source_key="internet").exists()
        )

    def test_biweekly_date_schedule_funds_actual_last_calendar_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-biweekly-last@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=11679,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="LAST",
            day_of_month=22,
        )

        plan = generate_budget(user)

        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 10, 16))
            .line_items.filter(source_key="insurance")
            .exists()
        )
        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 10, 30))
            .line_items.filter(source_key="insurance")
            .exists()
        )

    def test_weekly_date_schedule_funds_first_calendar_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-weekly-first@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=150000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=8500,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="FIRST",
            day_of_month=22,
        )

        plan = generate_budget(user)

        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 7)).line_items.filter(source_key="phone").exists()
        )
        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 14)).line_items.filter(source_key="phone").exists()
        )

    def test_weekly_date_schedule_funds_second_calendar_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-weekly-second@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=150000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=8500,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="SECOND",
            day_of_month=22,
        )

        plan = generate_budget(user)

        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 14)).line_items.filter(source_key="phone").exists()
        )
        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21)).line_items.filter(source_key="phone").exists()
        )

    def test_weekly_date_schedule_funds_third_calendar_paycheck(self) -> None:
        user = User.objects.create_user(email="funded-weekly-third@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=150000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=8500,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="THIRD",
            day_of_month=22,
        )

        plan = generate_budget(user)

        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21)).line_items.filter(source_key="phone").exists()
        )
        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 28)).line_items.filter(source_key="phone").exists()
        )

    def test_weekly_date_schedule_last_uses_fifth_paycheck_when_present(self) -> None:
        user = User.objects.create_user(email="funded-weekly-last@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="WEEKLY",
            income_per_pay_period_cents=150000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=8500,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            paycheck_position="LAST",
            day_of_month=22,
        )

        plan = generate_budget(user)

        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 10, 23)).line_items.filter(source_key="phone").exists()
        )
        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 10, 30)).line_items.filter(source_key="phone").exists()
        )

    def test_legacy_date_schedule_uses_responsible_period_fallback(self) -> None:
        user = User.objects.create_user(email="legacy-date-funding@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=300000,
            next_pay_date=datetime.date(2026, 8, 7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=9000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="internet",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=10,
        )

        plan = generate_budget(user)

        self.assertTrue(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 7)).line_items.filter(source_key="internet").exists()
        )
        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 8, 21)).line_items.filter(source_key="internet").exists()
        )
