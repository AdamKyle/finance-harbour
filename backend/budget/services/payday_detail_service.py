import datetime

from authentication.models import User
from budget.models import BudgetPayPeriod, PaydayReconciliationStatus, PaymentReviewStatus
from budget.services.debt_balance_projection_service import get_debt_balance_projections
from budget.services.payment_completion_service import calculate_payment_completion
from budget.types import PaydayDetail, PaydayProgress


def get_payday_detail(user: User, period_id: int, effective_date: datetime.date) -> PaydayDetail:
    period = (
        BudgetPayPeriod.objects.filter(id=period_id, plan__user=user, pay_date__lte=effective_date)
        .select_related("plan", "plan__user")
        .prefetch_related("line_items", "debt_balance_records")
        .get()
    )
    line_items = list(period.line_items.all())
    payment_completion = calculate_payment_completion(period, line_items)
    bill_count = payment_completion.bill_count
    reviewed_bill_count = sum(entry.payment_review_status != PaymentReviewStatus.UNREVIEWED for entry in line_items)
    paid_bill_count = payment_completion.paid_bill_count

    return PaydayDetail(
        pay_period=period,
        debt_balance_checks=get_debt_balance_projections(period),
        progress=PaydayProgress(
            bill_count=bill_count,
            reviewed_bill_count=reviewed_bill_count,
            paid_bill_count=paid_bill_count,
            scheduled_bill_count=payment_completion.scheduled_bill_count,
            missed_bill_count=payment_completion.missed_bill_count,
            payment_completion_percentage=payment_completion.percentage,
            payment_completion_status=payment_completion.status,
            overall_reconciliation_status=PaydayReconciliationStatus(period.payday_reconciliation_status),
        ),
    )
