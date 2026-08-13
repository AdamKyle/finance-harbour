from authentication.models import User
from budget.models import BudgetPayPeriod, PayChequeReviewStatus, PaydayReconciliationStatus
from budget.services.payday_development_date_service import resolve_payday_effective_date
from budget.types import PaydayQueue, PaydayQueuePeriod


def get_payday_queue(user: User) -> PaydayQueue:
    effective_date = resolve_payday_effective_date(user)
    owned_periods = BudgetPayPeriod.objects.filter(plan__user=user)
    unresolved_rows = list(
        owned_periods.filter(
            pay_date__lte=effective_date,
            payday_reconciliation_status__in=[
                PaydayReconciliationStatus.NOT_STARTED,
                PaydayReconciliationStatus.IN_PROGRESS,
            ],
        )
        .order_by("pay_date", "sequence")
        .values("id", "pay_date", "payday_reconciliation_status", "pay_cheque_review_status")
    )
    unresolved = [
        PaydayQueuePeriod(
            id=row["id"],
            pay_date=row["pay_date"],
            payday_reconciliation_status=PaydayReconciliationStatus(row["payday_reconciliation_status"]),
            pay_cheque_review_status=PayChequeReviewStatus(row["pay_cheque_review_status"]),
        )
        for row in unresolved_rows
    ]
    next_future_pay_date = (
        owned_periods.filter(pay_date__gt=effective_date)
        .order_by("pay_date")
        .values_list("pay_date", flat=True)
        .first()
    )

    return PaydayQueue(
        effective_date=effective_date,
        unresolved_count=len(unresolved),
        unresolved_periods=unresolved,
        oldest_unresolved_period=unresolved[0] if unresolved else None,
        next_future_pay_date=next_future_pay_date,
    )
