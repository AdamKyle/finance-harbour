import datetime

from django.test import SimpleTestCase

from budget.models import BudgetLineItem, BudgetPayPeriod, PaydayReconciliationStatus, PaymentReviewStatus
from budget.services.payment_completion_service import PaymentCompletionStatus, calculate_payment_completion


class PaymentCompletionServiceTest(SimpleTestCase):
    def test_seventy_five_percent_is_green(self) -> None:
        period = BudgetPayPeriod(
            pay_date=datetime.date(2026, 8, 1), payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED
        )
        line_items = [
            BudgetLineItem(payment_review_status=PaymentReviewStatus.PAID),
            BudgetLineItem(payment_review_status=PaymentReviewStatus.PAID),
            BudgetLineItem(payment_review_status=PaymentReviewStatus.PAID),
            BudgetLineItem(payment_review_status=PaymentReviewStatus.NOT_PAID),
        ]

        completion = calculate_payment_completion(period, line_items)

        self.assertEqual(completion.percentage, 75)
        self.assertEqual(completion.status, PaymentCompletionStatus.GREEN)

    def test_middle_percentage_is_yellow(self) -> None:
        period = BudgetPayPeriod(
            pay_date=datetime.date(2026, 8, 1), payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED
        )
        line_items = [BudgetLineItem(payment_review_status=PaymentReviewStatus.PAID)]
        line_items.append(BudgetLineItem(payment_review_status=PaymentReviewStatus.NOT_PAID))

        completion = calculate_payment_completion(period, line_items)

        self.assertEqual(completion.percentage, 50)
        self.assertEqual(completion.status, PaymentCompletionStatus.YELLOW)

    def test_twenty_five_percent_is_red(self) -> None:
        period = BudgetPayPeriod(
            pay_date=datetime.date(2026, 8, 1), payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED
        )
        line_items = [BudgetLineItem(payment_review_status=PaymentReviewStatus.PAID)]
        line_items.extend(
            [
                BudgetLineItem(payment_review_status=PaymentReviewStatus.NOT_PAID),
                BudgetLineItem(payment_review_status=PaymentReviewStatus.NOT_PAID),
                BudgetLineItem(payment_review_status=PaymentReviewStatus.NOT_PAID),
            ]
        )

        completion = calculate_payment_completion(period, line_items)

        self.assertEqual(completion.percentage, 25)
        self.assertEqual(completion.status, PaymentCompletionStatus.RED)

    def test_reviewed_period_with_no_bills_is_not_a_zero_percent_failure(self) -> None:
        period = BudgetPayPeriod(
            pay_date=datetime.date(2026, 8, 1), payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED
        )

        completion = calculate_payment_completion(period, [])

        self.assertIsNone(completion.percentage)
        self.assertEqual(completion.status, PaymentCompletionStatus.NO_BILLS)

    def test_scheduled_bill_is_not_counted_as_paid_or_missed(self) -> None:
        period = BudgetPayPeriod(
            pay_date=datetime.date(2026, 8, 1),
            payday_reconciliation_status=PaydayReconciliationStatus.REVIEWED,
        )
        line_items = [BudgetLineItem(payment_review_status=PaymentReviewStatus.SCHEDULED)]

        completion = calculate_payment_completion(period, line_items)

        self.assertEqual(completion.paid_bill_count, 0)
        self.assertEqual(completion.scheduled_bill_count, 1)
        self.assertEqual(completion.missed_bill_count, 0)
