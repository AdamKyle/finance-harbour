import datetime

from django.test import TestCase

from authentication.models import User
from budget.enums import BudgetValueField
from budget.models import BudgetLineItem, BudgetPayPeriod, BudgetPlan, SourceType
from budget.services import update_budget_value


class BudgetMutationServiceTest(TestCase):
    def test_period_only_left_over_remains_authoritative_for_future_carry(self) -> None:
        user = User.objects.create_user(email="budget-mutation@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        periods = [
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=sequence,
                pay_date=datetime.date(2026, sequence + 1, 1),
                pay_cheque_cents=100000,
                total_available_cents=100000,
                total_bills_cents=10000,
                left_over_cents=90000,
            )
            for sequence in range(3)
        ]

        update_budget_value(user, periods[1].id, BudgetValueField.LEFT_OVER, 40000, False, None)
        for period in periods:
            period.refresh_from_db()

        self.assertEqual(periods[0].pay_cheque_cents, 100000)
        self.assertEqual(periods[1].left_over_cents, 40000)
        self.assertTrue(periods[1].left_over_is_manual)
        self.assertEqual(periods[2].carried_left_over_cents, 40000)

    def test_line_item_going_forward_updates_selected_and_future_periods(self) -> None:
        user = User.objects.create_user(email="budget-bills@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        periods = [
            BudgetPayPeriod.objects.create(
                plan=plan,
                sequence=sequence,
                pay_date=datetime.date(2026, sequence + 1, 1),
                pay_cheque_cents=100000,
                total_available_cents=100000,
                left_over_cents=100000,
            )
            for sequence in range(3)
        ]
        for period in periods:
            BudgetLineItem.objects.create(
                pay_period=period,
                source_type=SourceType.STANDARD_EXPENSE,
                source_key="food",
                title="Food",
                amount_cents=10000,
            )

        update_budget_value(user, periods[1].id, BudgetValueField.LINE_ITEM, 15000, True, "food")

        self.assertEqual(periods[0].line_items.get(source_key="food").amount_cents, 10000)
        self.assertEqual(periods[1].line_items.get(source_key="food").amount_cents, 15000)
        self.assertEqual(periods[2].line_items.get(source_key="food").amount_cents, 15000)

    def test_deferred_important_warning_remains_after_non_negative_mutation(self) -> None:
        user = User.objects.create_user(email="budget-warning@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            total_bills_cents=20000,
            left_over_cents=80000,
            has_deferred_items=True,
            has_deferred_important_expenses=True,
            affects_important_expenses=True,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="utilities",
            title="Electricity",
            amount_cents=20000,
            is_required=True,
        )

        update_budget_value(user, period.id, BudgetValueField.LEFT_OVER, 50000, False, None)
        period.refresh_from_db()

        self.assertFalse(period.has_negative_left_over)
        self.assertTrue(period.affects_important_expenses)

    def test_deferred_non_important_expense_does_not_preserve_important_warning(self) -> None:
        user = User.objects.create_user(email="budget-non-important-warning@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2027, 1, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 1, 1),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            total_bills_cents=120000,
            left_over_cents=-20000,
            has_negative_left_over=True,
            has_deferred_items=True,
            has_deferred_important_expenses=False,
            affects_important_expenses=True,
        )
        BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="utilities",
            title="Electricity",
            amount_cents=20000,
            is_required=True,
        )

        update_budget_value(user, period.id, BudgetValueField.LEFT_OVER, 50000, False, None)
        period.refresh_from_db()

        self.assertFalse(period.has_negative_left_over)
        self.assertFalse(period.affects_important_expenses)
