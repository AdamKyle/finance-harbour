import datetime

from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User
from budget.models import BudgetLineItem, BudgetPayPeriod, BudgetPlan, PaymentReviewStatus, SourceType
from debt_profile.models import ExpensePaymentTiming


class BudgetLineItemTest(TestCase):
    def test_str_returns_period_id_and_source_key(self) -> None:
        user = User.objects.create_user(email="lineitem_str@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )
        item = BudgetLineItem.objects.create(
            pay_period=period,
            source_type=SourceType.STANDARD_EXPENSE,
            source_key="food_cents",
            title="Food",
            amount_cents=20000,
        )
        self.assertEqual(str(item), f"BudgetLineItem({period.pk}, food_cents)")

    def test_paid_line_item_requires_actual_amount(self) -> None:
        user = User.objects.create_user(email="lineitem-paid@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetLineItem.objects.create(
                pay_period=period,
                source_type=SourceType.STANDARD_EXPENSE,
                source_key="food_cents",
                title="Food",
                amount_cents=20000,
                payment_review_status=PaymentReviewStatus.PAID,
                actual_amount_cents=None,
            )

    def test_not_paid_line_item_rejects_non_zero_actual_amount(self) -> None:
        user = User.objects.create_user(email="lineitem-not-paid@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetLineItem.objects.create(
                pay_period=period,
                source_type=SourceType.STANDARD_EXPENSE,
                source_key="food_cents",
                title="Food",
                amount_cents=20000,
                payment_review_status=PaymentReviewStatus.NOT_PAID,
                actual_amount_cents=1,
            )

    def test_scheduled_line_item_requires_a_scheduled_payment_date(self) -> None:
        user = User.objects.create_user(email="lineitem-scheduled@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetLineItem.objects.create(
                pay_period=period,
                source_type=SourceType.STANDARD_EXPENSE,
                source_key="insurance_cents",
                title="Insurance",
                amount_cents=20000,
                payment_review_status=PaymentReviewStatus.SCHEDULED,
                scheduled_amount_cents=1000,
                payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
                expected_payment_date=None,
            )

    def test_scheduled_line_item_requires_a_separate_scheduled_amount(self) -> None:
        user = User.objects.create_user(email="lineitem-scheduled-amount@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        period = BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2025, 8, 1),
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            BudgetLineItem.objects.create(
                pay_period=period,
                source_type=SourceType.STANDARD_EXPENSE,
                source_key="insurance_cents",
                title="Insurance",
                amount_cents=20000,
                payment_review_status=PaymentReviewStatus.SCHEDULED,
                scheduled_amount_cents=None,
                payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
                expected_payment_date=datetime.date(2025, 8, 12),
            )
