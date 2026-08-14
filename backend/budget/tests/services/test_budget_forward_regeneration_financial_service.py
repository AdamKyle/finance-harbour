import datetime

from django.test import TestCase
from django.utils import timezone

from authentication.models import User
from budget.models import (
    BudgetDebtBalanceRecord,
    DebtBalanceReviewStatus,
    PayChequeReviewStatus,
    PaydayReconciliationStatus,
    PaymentReviewStatus,
)
from budget.services.budget_forward_regeneration_service import regenerate_budget_from_pay_period
from budget.services.budget_generator import generate_budget
from budget.services.debt_balance_projection_service import get_debt_balance_projections
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    PaycheckPosition,
    RecurringExpense,
    RecurringExpenseCategory,
)


class BudgetForwardRegenerationFinancialServiceTest(TestCase):
    def test_first_period_regeneration_keeps_prospective_date_bill_before_new_payday(self) -> None:
        user = User.objects.create_user(email="first-period-bill-forward@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=15000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=17,
        )
        plan = generate_budget(user)
        first_period = plan.pay_periods.order_by("sequence").first()

        regenerated = regenerate_budget_from_pay_period(user, first_period.id, datetime.date(2026, 8, 22))

        self.assertEqual(regenerated.pay_date, datetime.date(2026, 8, 22))
        self.assertTrue(
            regenerated.line_items.filter(
                source_key="insurance",
                expected_payment_date=datetime.date(2026, 8, 17),
            ).exists()
        )
        self.assertFalse(plan.pay_periods.filter(pay_date__lt=datetime.date(2026, 8, 22)).exists())

    def test_period_before_boundary_keeps_factual_and_reconciliation_state(self) -> None:
        user = User.objects.create_user(email="history-forward@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
            debts=[{"label": "Loan", "current_balance_cents": 500000, "current_payment_cents": 20000}],
        )
        plan = generate_budget(user)
        periods = list(plan.pay_periods.order_by("sequence")[:3])
        historical = periods[0]
        historical.payday_reconciliation_status = PaydayReconciliationStatus.REVIEWED
        historical.actual_pay_cheque_cents = 95000
        historical.pay_cheque_review_status = PayChequeReviewStatus.CONFIRMED
        historical.save()
        debt_item = historical.line_items.get(source_key="debt:0")
        debt_item.payment_review_status = PaymentReviewStatus.PAID
        debt_item.actual_amount_cents = 18000
        debt_item.save()
        debt_record = BudgetDebtBalanceRecord.objects.create(
            pay_period=historical,
            source_key="debt:0",
            title="Loan",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=482000,
            reconciled_at=timezone.now(),
        )

        regenerate_budget_from_pay_period(user, periods[1].id, datetime.date(2026, 9, 5))
        historical.refresh_from_db()
        debt_item.refresh_from_db()
        debt_record.refresh_from_db()

        self.assertEqual(historical.id, periods[0].id)
        self.assertEqual(historical.pay_date, datetime.date(2026, 8, 21))
        self.assertEqual(historical.payday_reconciliation_status, PaydayReconciliationStatus.REVIEWED)
        self.assertEqual(historical.actual_pay_cheque_cents, 95000)
        self.assertEqual(debt_item.actual_amount_cents, 18000)
        self.assertEqual(debt_record.actual_balance_cents, 482000)

    def test_regeneration_rebuilds_every_paycheck_position_and_day_schedules(self) -> None:
        user = User.objects.create_user(email="schedule-forward@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=47500,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=10000,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="internet",
            category=RecurringExpenseCategory.INTERNET,
            label="Internet",
            amount_cents=37500,
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="insurance",
            category=RecurringExpenseCategory.INSURANCE,
            label="Insurance",
            amount_cents=40000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="food",
            timing=ExpensePaymentTiming.EVERY_PAYCHECK,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="internet",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=19,
            paycheck_position=PaycheckPosition.SECOND,
            auto_deducted=True,
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))

        regenerated = regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 9, 5))
        next_period = plan.pay_periods.get(sequence=regenerated.sequence + 1)

        self.assertTrue(regenerated.line_items.filter(source_key="food").exists())
        self.assertTrue(next_period.line_items.filter(source_key="food").exists())
        self.assertTrue(regenerated.line_items.filter(source_key="internet").exists())
        self.assertFalse(next_period.line_items.filter(source_key="internet").exists())
        self.assertTrue(
            next_period.line_items.filter(
                source_key="insurance",
                expected_payment_date=datetime.date(2026, 9, 21),
            ).exists()
        )
        insurance = next_period.line_items.get(source_key="insurance")
        food = next_period.line_items.get(source_key="food")
        self.assertEqual(insurance.funded_amount_cents, 40000)
        self.assertEqual(insurance.shortfall_cents, 0)
        self.assertEqual(food.funded_amount_cents, 5000)
        self.assertEqual(food.shortfall_cents, 5000)

    def test_regeneration_recalculates_future_debt_projection_from_confirmed_history(self) -> None:
        user = User.objects.create_user(email="debt-projection-forward@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
            debts=[{"label": "Loan", "current_balance_cents": 500000, "current_payment_cents": 20000}],
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.EVERY_PAYCHECK,
        )
        plan = generate_budget(user)
        periods = list(plan.pay_periods.order_by("sequence")[:3])
        historical_record = BudgetDebtBalanceRecord.objects.create(
            pay_period=periods[0],
            source_key="debt:0",
            title="Loan",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=480000,
            reconciled_at=timezone.now(),
        )

        regenerated = regenerate_budget_from_pay_period(user, periods[1].id, datetime.date(2026, 9, 5))
        future_period = plan.pay_periods.get(sequence=regenerated.sequence + 1)
        historical_projection = get_debt_balance_projections(periods[0])[0]
        regenerated_projection = get_debt_balance_projections(regenerated)[0]
        future_projection = get_debt_balance_projections(future_period)[0]
        historical_record.refresh_from_db()

        self.assertEqual(historical_record.actual_balance_cents, 480000)
        self.assertEqual(historical_projection.actual_balance_cents, 480000)
        self.assertEqual(regenerated.pay_date, datetime.date(2026, 9, 5))
        self.assertEqual(regenerated_projection.expected_balance_cents, 460000)
        self.assertEqual(future_period.pay_date, datetime.date(2026, 9, 19))
        self.assertEqual(future_projection.expected_balance_cents, 440000)
