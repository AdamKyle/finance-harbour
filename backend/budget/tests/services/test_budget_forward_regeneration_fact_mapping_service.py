import datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.models import User
from budget.models import BudgetDebtBalanceRecord, DebtBalanceReviewStatus, PaymentReviewStatus
from budget.services.budget_forward_regeneration_service import regenerate_budget_from_pay_period
from budget.services.budget_generator import generate_budget
from budget.services.budget_mutation_service import add_budget_bill
from budget.services.debt_balance_projection_service import get_debt_balance_projections
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    PaycheckPosition,
    RecurringExpense,
    RecurringExpenseCategory,
)


class BudgetForwardRegenerationFactMappingServiceTest(TestCase):
    def test_day_of_month_fact_moves_with_same_effective_payment_date(self) -> None:
        user = User.objects.create_user(email="day-moves@example.com", password="StrongPassword123!")
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
            amount_cents=20000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=17,
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        original_item = selected.line_items.get(
            source_key="insurance",
            expected_payment_date=datetime.date(2026, 9, 17),
        )
        original_item.payment_review_status = PaymentReviewStatus.PAID
        original_item.actual_amount_cents = 17500
        original_item.payment_reconciled_at = timezone.now()
        original_item.paid_at = timezone.now()
        original_item.save()

        regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 8, 30))

        mapped_period = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 13))
        mapped_item = mapped_period.line_items.get(
            source_key="insurance",
            expected_payment_date=datetime.date(2026, 9, 17),
        )
        self.assertEqual(mapped_item.payment_review_status, PaymentReviewStatus.PAID)
        self.assertEqual(mapped_item.actual_amount_cents, 17500)
        self.assertEqual(
            plan.pay_periods.filter(
                line_items__source_key="insurance",
                line_items__payment_review_status=PaymentReviewStatus.PAID,
            ).count(),
            1,
        )

    def test_day_of_month_fact_stays_with_unchanged_semantic_occurrence(self) -> None:
        user = User.objects.create_user(email="day-stays@example.com", password="StrongPassword123!")
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
            amount_cents=20000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="insurance",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=17,
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        original_item = selected.line_items.get(source_key="insurance")
        original_item.payment_review_status = PaymentReviewStatus.NOT_PAID
        original_item.actual_amount_cents = 0
        original_item.payment_reconciled_at = timezone.now()
        original_item.save()

        regenerated = regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 9, 5))

        mapped_item = regenerated.line_items.get(
            source_key="insurance",
            expected_payment_date=datetime.date(2026, 9, 17),
        )
        self.assertEqual(mapped_item.payment_review_status, PaymentReviewStatus.NOT_PAID)
        self.assertEqual(mapped_item.actual_amount_cents, 0)

    def test_every_paycheck_fact_maps_only_to_edited_effective_occurrence(self) -> None:
        user = User.objects.create_user(email="every-fact@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=10000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="food",
            timing=ExpensePaymentTiming.EVERY_PAYCHECK,
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        original_item = selected.line_items.get(source_key="food")
        original_item.payment_review_status = PaymentReviewStatus.PAID
        original_item.actual_amount_cents = 9000
        original_item.payment_reconciled_at = timezone.now()
        original_item.paid_at = timezone.now()
        original_item.save()

        regenerated = regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 9, 5))

        mapped_item = regenerated.line_items.get(source_key="food")
        self.assertEqual(mapped_item.payment_review_status, PaymentReviewStatus.PAID)
        self.assertEqual(mapped_item.actual_amount_cents, 9000)
        self.assertEqual(
            plan.pay_periods.filter(
                sequence__gte=regenerated.sequence,
                line_items__source_key="food",
                line_items__payment_review_status=PaymentReviewStatus.PAID,
            ).count(),
            1,
        )

    def test_paycheck_position_fact_maps_by_month_and_position(self) -> None:
        user = User.objects.create_user(email="position-fact@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="phone",
            category=RecurringExpenseCategory.PHONE,
            label="Phone",
            amount_cents=15000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="phone",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.SECOND,
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        original_occurrence = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 18)).line_items.get(
            source_key="phone"
        )
        original_occurrence.payment_review_status = PaymentReviewStatus.PAID
        original_occurrence.actual_amount_cents = 14000
        original_occurrence.payment_reconciled_at = timezone.now()
        original_occurrence.paid_at = timezone.now()
        original_occurrence.save()

        regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 8, 30))

        mapped_item = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 27)).line_items.get(source_key="phone")
        self.assertEqual(mapped_item.payment_review_status, PaymentReviewStatus.PAID)
        self.assertEqual(mapped_item.actual_amount_cents, 14000)
        self.assertFalse(
            plan.pay_periods.get(pay_date=datetime.date(2026, 9, 13)).line_items.filter(source_key="phone").exists()
        )

    def test_one_period_manual_override_stays_on_edited_effective_period_only(self) -> None:
        user = User.objects.create_user(email="manual-fact@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        add_budget_bill(
            user=user,
            period_id=selected.id,
            title="One-off repair",
            amount_cents=12500,
            is_required=False,
            going_forward=False,
        )
        source_key = selected.line_items.get(title="One-off repair").source_key

        regenerated = regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 9, 5))

        self.assertEqual(regenerated.line_items.get(source_key=source_key).amount_cents, 12500)
        self.assertEqual(
            plan.pay_periods.filter(sequence__gt=regenerated.sequence, line_items__source_key=source_key).count(),
            0,
        )

    def test_confirmed_debt_fact_on_effective_period_remains_projection_baseline(self) -> None:
        user = User.objects.create_user(email="debt-effective-fact@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
            debts=[{"label": "Loan", "current_balance_cents": 500000, "current_payment_cents": 20000}],
        )
        profile = DebtProfile.objects.get(user=user)
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.EVERY_PAYCHECK,
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        BudgetDebtBalanceRecord.objects.create(
            pay_period=selected,
            source_key="debt:0",
            title="Loan",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=450000,
            reconciled_at=timezone.now(),
        )

        regenerated = regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 9, 5))
        future_period = plan.pay_periods.get(sequence=regenerated.sequence + 1)
        mapped_record = regenerated.debt_balance_records.get(source_key="debt:0")
        future_projection = get_debt_balance_projections(future_period)[0]

        self.assertEqual(mapped_record.actual_balance_cents, 450000)
        self.assertEqual(regenerated.pay_date, datetime.date(2026, 9, 5))
        self.assertEqual(future_projection.expected_balance_cents, 430000)

    def test_unmappable_later_debt_fact_rejects_and_rolls_back_regeneration(self) -> None:
        user = User.objects.create_user(email="debt-unmappable@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            pay_period_type="BIWEEKLY",
            income_per_pay_period_cents=100000,
            next_pay_date=datetime.date(2026, 8, 21),
            debts=[{"label": "Loan", "current_balance_cents": 500000, "current_payment_cents": 20000}],
        )
        plan = generate_budget(user)
        selected = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 4))
        later_period = plan.pay_periods.get(pay_date=datetime.date(2026, 9, 18))
        record = BudgetDebtBalanceRecord.objects.create(
            pay_period=later_period,
            source_key="debt:0",
            title="Loan",
            review_status=DebtBalanceReviewStatus.CONFIRMED,
            actual_balance_cents=440000,
            reconciled_at=timezone.now(),
        )
        original_dates = list(plan.pay_periods.order_by("sequence").values_list("pay_date", flat=True))

        with self.assertRaises(ValidationError):
            regenerate_budget_from_pay_period(user, selected.id, datetime.date(2026, 9, 5))

        self.assertEqual(
            list(plan.pay_periods.order_by("sequence").values_list("pay_date", flat=True)),
            original_dates,
        )
        record.refresh_from_db()
        self.assertEqual(record.pay_period_id, later_period.id)
        self.assertEqual(record.actual_balance_cents, 440000)
