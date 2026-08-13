from dataclasses import dataclass
from enum import StrEnum

from budget.models import BudgetLineItem, BudgetPayPeriod, PaydayReconciliationStatus, PaymentReviewStatus


class PaymentCompletionStatus(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    NO_BILLS = "NO_BILLS"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class PaymentCompletion:
    bill_count: int
    paid_bill_count: int
    scheduled_bill_count: int
    missed_bill_count: int
    percentage: float | None
    status: PaymentCompletionStatus


def calculate_payment_completion(
    period: BudgetPayPeriod,
    line_items: list[BudgetLineItem],
) -> PaymentCompletion:
    bill_count = len(line_items)
    paid_bill_count = sum(line_item.payment_review_status == PaymentReviewStatus.PAID for line_item in line_items)
    scheduled_bill_count = sum(
        line_item.payment_review_status == PaymentReviewStatus.SCHEDULED for line_item in line_items
    )
    missed_bill_count = sum(line_item.payment_review_status == PaymentReviewStatus.NOT_PAID for line_item in line_items)

    if period.payday_reconciliation_status != PaydayReconciliationStatus.REVIEWED:
        return PaymentCompletion(
            bill_count=bill_count,
            paid_bill_count=paid_bill_count,
            scheduled_bill_count=scheduled_bill_count,
            missed_bill_count=missed_bill_count,
            percentage=None,
            status=PaymentCompletionStatus.NOT_APPLICABLE,
        )

    if bill_count == 0:
        return PaymentCompletion(
            bill_count=0,
            paid_bill_count=0,
            scheduled_bill_count=0,
            missed_bill_count=0,
            percentage=None,
            status=PaymentCompletionStatus.NO_BILLS,
        )

    percentage = paid_bill_count / bill_count * 100

    if percentage >= 75:
        completion_status = PaymentCompletionStatus.GREEN
    elif percentage > 25:
        completion_status = PaymentCompletionStatus.YELLOW
    else:
        completion_status = PaymentCompletionStatus.RED

    return PaymentCompletion(
        bill_count=bill_count,
        paid_bill_count=paid_bill_count,
        scheduled_bill_count=scheduled_bill_count,
        missed_bill_count=missed_bill_count,
        percentage=percentage,
        status=completion_status,
    )


def get_payment_completion(period: BudgetPayPeriod) -> PaymentCompletion:
    cached_completion = getattr(period, "_payment_completion", None)

    if cached_completion is not None:
        return cached_completion

    completion = calculate_payment_completion(period, list(period.line_items.all()))
    period._payment_completion = completion

    return completion
