import datetime
from dataclasses import dataclass
from math import ceil

from django.db.models import QuerySet

from budget.models import BudgetPayPeriod, PaydayReconciliationStatus


@dataclass(frozen=True)
class BudgetDashboardAnchor:
    period_id: int | None
    page: int


def get_budget_dashboard_anchor(
    periods: QuerySet[BudgetPayPeriod],
    effective_date: datetime.date,
    per_page: int,
    requested_period_id: int | None = None,
) -> BudgetDashboardAnchor:
    requested_period = None

    if requested_period_id is not None:
        requested_period = periods.filter(id=requested_period_id).only("id", "sequence").first()

    anchor_period = requested_period or _get_default_anchor_period(periods, effective_date)

    if anchor_period is None:
        return BudgetDashboardAnchor(period_id=None, page=1)

    preceding_count = periods.filter(sequence__lt=anchor_period.sequence).count()

    return BudgetDashboardAnchor(
        period_id=anchor_period.id,
        page=ceil((preceding_count + 1) / per_page),
    )


def _get_default_anchor_period(
    periods: QuerySet[BudgetPayPeriod],
    effective_date: datetime.date,
) -> BudgetPayPeriod | None:
    unresolved_period = (
        periods.filter(
            pay_date__lte=effective_date,
            payday_reconciliation_status__in=[
                PaydayReconciliationStatus.NOT_STARTED,
                PaydayReconciliationStatus.IN_PROGRESS,
            ],
        )
        .order_by("sequence")
        .only("id", "sequence")
        .first()
    )

    if unresolved_period is not None:
        return unresolved_period

    current_period = (
        periods.filter(pay_date__lte=effective_date).order_by("-pay_date", "-sequence").only("id", "sequence").first()
    )

    if current_period is not None:
        return current_period

    return periods.filter(pay_date__gt=effective_date).order_by("pay_date", "sequence").only("id", "sequence").first()
