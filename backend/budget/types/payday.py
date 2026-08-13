import datetime
from dataclasses import dataclass
from enum import StrEnum
from typing import NotRequired, TypedDict

from budget.models import (
    BudgetPayPeriod,
    DebtBalanceReviewStatus,
    PayChequeReviewStatus,
    PaydayReconciliationStatus,
)
from budget.services.payment_completion_service import PaymentCompletionStatus


class PaydayWarningType(StrEnum):
    NEGATIVE_LEFT_OVER = "NEGATIVE_LEFT_OVER"
    IMPORTANT_PAYMENT_MISSED_OR_UNDERPAID = "IMPORTANT_PAYMENT_MISSED_OR_UNDERPAID"
    IMPORTANT_EXPENSE_AFFECTED = "IMPORTANT_EXPENSE_AFFECTED"
    WARNING_THRESHOLD_CROSSED = "WARNING_THRESHOLD_CROSSED"


class PaydayWarningSeverity(StrEnum):
    WARNING = "WARNING"
    DANGER = "DANGER"


class DebtProfileDebtDefinition(TypedDict):
    label: NotRequired[str]
    current_balance_cents: NotRequired[int]
    current_payment_cents: NotRequired[int]


@dataclass(frozen=True)
class PaydayWarning:
    warning_type: PaydayWarningType
    affected_period_id: int
    affected_pay_date: datetime.date
    amount_cents: int | None
    important_titles: list[str]
    severity: PaydayWarningSeverity


@dataclass(frozen=True)
class PaydayDebtBalanceCheck:
    source_key: str
    title: str
    expected_balance_cents: int | None
    actual_balance_cents: int | None
    review_status: DebtBalanceReviewStatus
    variance_cents: int | None
    variance_percentage: float | None
    previous_confirmed_balance_cents: int | None
    movement_from_previous_percentage: float | None
    is_uncertain: bool


@dataclass(frozen=True)
class PaydayDebtDefinition:
    source_key: str
    title: str
    first_sequence: int


@dataclass(frozen=True)
class PaydayProgress:
    bill_count: int
    reviewed_bill_count: int
    paid_bill_count: int
    scheduled_bill_count: int
    missed_bill_count: int
    payment_completion_percentage: float | None
    payment_completion_status: PaymentCompletionStatus
    overall_reconciliation_status: PaydayReconciliationStatus


@dataclass(frozen=True)
class PaydayDetail:
    pay_period: BudgetPayPeriod
    debt_balance_checks: list[PaydayDebtBalanceCheck]
    progress: PaydayProgress


@dataclass(frozen=True)
class PaydayQueuePeriod:
    id: int
    pay_date: datetime.date
    payday_reconciliation_status: PaydayReconciliationStatus
    pay_cheque_review_status: PayChequeReviewStatus


@dataclass(frozen=True)
class PaydayQueue:
    effective_date: datetime.date
    unresolved_count: int
    unresolved_periods: list[PaydayQueuePeriod]
    oldest_unresolved_period: PaydayQueuePeriod | None
    next_future_pay_date: datetime.date | None
