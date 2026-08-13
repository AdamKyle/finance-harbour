import datetime
from dataclasses import dataclass
from enum import StrEnum

from rest_framework.exceptions import ValidationError

from budget import models
from debt_profile.models import ExpensePaymentTiming, PaycheckPosition


class LineItemOccurrenceKind(StrEnum):
    DAY_OF_MONTH = "DAY_OF_MONTH"
    PAYCHECK_POSITION = "PAYCHECK_POSITION"
    PAY_DATE = "PAY_DATE"
    EFFECTIVE_PERIOD = "EFFECTIVE_PERIOD"


@dataclass(frozen=True)
class LineItemOccurrenceKey:
    source_key: str
    kind: LineItemOccurrenceKind
    occurrence_date: datetime.date
    paycheck_position: PaycheckPosition | None


@dataclass(frozen=True)
class LineItemState:
    occurrence_key: LineItemOccurrenceKey
    source_type: models.SourceType
    source_key: str
    title: str
    amount_cents: int
    display_order: int
    is_required: bool
    is_split: bool
    is_manual_override: bool
    is_auto_deducted: bool
    payment_review_status: models.PaymentReviewStatus
    actual_amount_cents: int | None
    scheduled_amount_cents: int | None
    payment_reconciled_at: datetime.datetime | None
    paid_at: datetime.datetime | None
    expected_payment_date: datetime.date | None
    payment_timing: ExpensePaymentTiming | None
    paycheck_position: PaycheckPosition | None


@dataclass(frozen=True)
class PeriodState:
    original_pay_date: datetime.date
    is_effective_period: bool
    pay_cheque_cents: int
    pay_cheque_is_manual: bool
    carried_left_over_cents: int
    carried_left_over_is_manual: bool
    total_available_cents: int
    total_available_is_manual: bool
    total_bills_cents: int
    total_bills_is_manual: bool
    left_over_cents: int
    left_over_is_manual: bool
    payday_reconciliation_status: models.PaydayReconciliationStatus
    actual_pay_cheque_cents: int | None
    pay_cheque_review_status: models.PayChequeReviewStatus
    pay_cheque_reconciled_at: datetime.datetime | None
    payday_reconciliation_started_at: datetime.datetime | None
    payday_reconciliation_completed_at: datetime.datetime | None


@dataclass(frozen=True)
class DebtBalanceState:
    source_key: str
    title: str
    original_pay_date: datetime.date
    is_effective_period: bool
    review_status: models.DebtBalanceReviewStatus
    actual_balance_cents: int | None
    reconciled_at: datetime.datetime


@dataclass(frozen=True)
class ForwardFactSnapshot:
    period_states: list[PeriodState]
    line_item_states: list[LineItemState]
    debt_balance_states: list[DebtBalanceState]


def snapshot_forward_facts(
    effective_period: models.BudgetPayPeriod,
    forward_periods: list[models.BudgetPayPeriod],
    forward_line_items: list[models.BudgetLineItem],
    forward_debt_records: list[models.BudgetDebtBalanceRecord],
) -> ForwardFactSnapshot:
    pay_dates_by_period_id = {period.id: period.pay_date for period in forward_periods}
    period_states = [
        _snapshot_period(period, period.id == effective_period.id)
        for period in forward_periods
        if _period_has_preserved_state(period)
    ]
    line_item_states = [
        _snapshot_line_item(
            line_item,
            pay_dates_by_period_id[line_item.pay_period_id],
            line_item.pay_period_id == effective_period.id,
        )
        for line_item in forward_line_items
        if _line_item_has_preserved_state(line_item)
    ]
    debt_balance_states = [
        DebtBalanceState(
            source_key=record.source_key,
            title=record.title,
            original_pay_date=pay_dates_by_period_id[record.pay_period_id],
            is_effective_period=record.pay_period_id == effective_period.id,
            review_status=models.DebtBalanceReviewStatus(record.review_status),
            actual_balance_cents=record.actual_balance_cents,
            reconciled_at=record.reconciled_at,
        )
        for record in forward_debt_records
    ]

    return ForwardFactSnapshot(
        period_states=period_states,
        line_item_states=line_item_states,
        debt_balance_states=debt_balance_states,
    )


def restore_forward_facts(
    regenerated_periods: list[models.BudgetPayPeriod],
    snapshot: ForwardFactSnapshot,
) -> None:
    _restore_period_states(regenerated_periods, snapshot.period_states)
    _restore_line_item_states(regenerated_periods, snapshot.line_item_states)
    _restore_debt_balance_states(regenerated_periods, snapshot.debt_balance_states)


def _period_has_preserved_state(period: models.BudgetPayPeriod) -> bool:
    return (
        period.pay_cheque_is_manual
        or period.carried_left_over_is_manual
        or period.total_available_is_manual
        or period.total_bills_is_manual
        or period.left_over_is_manual
        or period.payday_reconciliation_status != models.PaydayReconciliationStatus.NOT_STARTED
        or period.pay_cheque_review_status != models.PayChequeReviewStatus.UNREVIEWED
    )


def _line_item_has_preserved_state(line_item: models.BudgetLineItem) -> bool:
    return (
        line_item.is_manual_override
        or line_item.source_type == models.SourceType.MANUAL_EXPENSE
        or line_item.payment_review_status != models.PaymentReviewStatus.UNREVIEWED
    )


def _snapshot_period(period: models.BudgetPayPeriod, is_effective_period: bool) -> PeriodState:
    return PeriodState(
        original_pay_date=period.pay_date,
        is_effective_period=is_effective_period,
        pay_cheque_cents=period.pay_cheque_cents,
        pay_cheque_is_manual=period.pay_cheque_is_manual,
        carried_left_over_cents=period.carried_left_over_cents,
        carried_left_over_is_manual=period.carried_left_over_is_manual,
        total_available_cents=period.total_available_cents,
        total_available_is_manual=period.total_available_is_manual,
        total_bills_cents=period.total_bills_cents,
        total_bills_is_manual=period.total_bills_is_manual,
        left_over_cents=period.left_over_cents,
        left_over_is_manual=period.left_over_is_manual,
        payday_reconciliation_status=models.PaydayReconciliationStatus(period.payday_reconciliation_status),
        actual_pay_cheque_cents=period.actual_pay_cheque_cents,
        pay_cheque_review_status=models.PayChequeReviewStatus(period.pay_cheque_review_status),
        pay_cheque_reconciled_at=period.pay_cheque_reconciled_at,
        payday_reconciliation_started_at=period.payday_reconciliation_started_at,
        payday_reconciliation_completed_at=period.payday_reconciliation_completed_at,
    )


def _snapshot_line_item(
    line_item: models.BudgetLineItem,
    period_pay_date: datetime.date,
    is_effective_period: bool,
) -> LineItemState:
    return LineItemState(
        occurrence_key=_get_line_item_occurrence_key(line_item, period_pay_date, is_effective_period),
        source_type=models.SourceType(line_item.source_type),
        source_key=line_item.source_key,
        title=line_item.title,
        amount_cents=line_item.amount_cents,
        display_order=line_item.display_order,
        is_required=line_item.is_required,
        is_split=line_item.is_split,
        is_manual_override=line_item.is_manual_override,
        is_auto_deducted=line_item.is_auto_deducted,
        payment_review_status=models.PaymentReviewStatus(line_item.payment_review_status),
        actual_amount_cents=line_item.actual_amount_cents,
        scheduled_amount_cents=line_item.scheduled_amount_cents,
        payment_reconciled_at=line_item.payment_reconciled_at,
        paid_at=line_item.paid_at,
        expected_payment_date=line_item.expected_payment_date,
        payment_timing=ExpensePaymentTiming(line_item.payment_timing) if line_item.payment_timing else None,
        paycheck_position=PaycheckPosition(line_item.paycheck_position) if line_item.paycheck_position else None,
    )


def _get_line_item_occurrence_key(
    line_item: models.BudgetLineItem,
    period_pay_date: datetime.date,
    is_effective_period: bool,
) -> LineItemOccurrenceKey:
    if line_item.payment_timing == ExpensePaymentTiming.DAY_OF_MONTH and line_item.expected_payment_date is not None:
        return LineItemOccurrenceKey(
            source_key=line_item.source_key,
            kind=LineItemOccurrenceKind.DAY_OF_MONTH,
            occurrence_date=line_item.expected_payment_date,
            paycheck_position=None,
        )

    if line_item.payment_timing == ExpensePaymentTiming.PAYCHECK_POSITION:
        return LineItemOccurrenceKey(
            source_key=line_item.source_key,
            kind=LineItemOccurrenceKind.PAYCHECK_POSITION,
            occurrence_date=period_pay_date.replace(day=1),
            paycheck_position=PaycheckPosition(line_item.paycheck_position),
        )

    occurrence_kind = LineItemOccurrenceKind.PAY_DATE

    if is_effective_period:
        occurrence_kind = LineItemOccurrenceKind.EFFECTIVE_PERIOD

    return LineItemOccurrenceKey(
        source_key=line_item.source_key,
        kind=occurrence_kind,
        occurrence_date=datetime.date.min if is_effective_period else period_pay_date,
        paycheck_position=None,
    )


def _restore_period_states(
    regenerated_periods: list[models.BudgetPayPeriod],
    states: list[PeriodState],
) -> None:
    periods_by_pay_date = {period.pay_date: period for period in regenerated_periods}
    updated_periods: list[models.BudgetPayPeriod] = []

    for state in states:
        target = (
            regenerated_periods[0] if state.is_effective_period else periods_by_pay_date.get(state.original_pay_date)
        )

        if target is None:
            raise ValidationError(
                {"pay_date": ["A reconciled or manually edited future pay period cannot be mapped to the new cadence."]}
            )

        _apply_period_state(target, state)
        updated_periods.append(target)

    if updated_periods:
        models.BudgetPayPeriod.objects.bulk_update(updated_periods, _period_update_fields())


def _apply_period_state(period: models.BudgetPayPeriod, state: PeriodState) -> None:
    manual_fields = [
        ("pay_cheque_cents", "pay_cheque_is_manual"),
        ("carried_left_over_cents", "carried_left_over_is_manual"),
        ("total_available_cents", "total_available_is_manual"),
        ("total_bills_cents", "total_bills_is_manual"),
        ("left_over_cents", "left_over_is_manual"),
    ]

    for value_field, manual_field in manual_fields:
        if getattr(state, manual_field):
            setattr(period, value_field, getattr(state, value_field))
            setattr(period, manual_field, True)

    period.payday_reconciliation_status = state.payday_reconciliation_status
    period.actual_pay_cheque_cents = state.actual_pay_cheque_cents
    period.pay_cheque_review_status = state.pay_cheque_review_status
    period.pay_cheque_reconciled_at = state.pay_cheque_reconciled_at
    period.payday_reconciliation_started_at = state.payday_reconciliation_started_at
    period.payday_reconciliation_completed_at = state.payday_reconciliation_completed_at


def _period_update_fields() -> list[str]:
    return [
        "pay_cheque_cents",
        "pay_cheque_is_manual",
        "carried_left_over_cents",
        "carried_left_over_is_manual",
        "total_available_cents",
        "total_available_is_manual",
        "total_bills_cents",
        "total_bills_is_manual",
        "left_over_cents",
        "left_over_is_manual",
        "payday_reconciliation_status",
        "actual_pay_cheque_cents",
        "pay_cheque_review_status",
        "pay_cheque_reconciled_at",
        "payday_reconciliation_started_at",
        "payday_reconciliation_completed_at",
    ]


def _restore_line_item_states(
    regenerated_periods: list[models.BudgetPayPeriod],
    states: list[LineItemState],
) -> None:
    regenerated_items = list(models.BudgetLineItem.objects.filter(pay_period__in=regenerated_periods))
    pay_dates_by_period_id = {period.id: period.pay_date for period in regenerated_periods}
    targets_by_key = {
        _get_line_item_occurrence_key(
            item,
            pay_dates_by_period_id[item.pay_period_id],
            item.pay_period_id == regenerated_periods[0].id,
        ): item
        for item in regenerated_items
    }
    updated_items: list[models.BudgetLineItem] = []
    missing_items: list[models.BudgetLineItem] = []

    for state in states:
        target = targets_by_key.get(state.occurrence_key)

        if target is None and _can_recreate_manual_item(state):
            target_period = _get_manual_target_period(regenerated_periods, state.occurrence_key)

            if target_period is not None:
                missing_items.append(_build_manual_item(target_period, state))
                continue

        if target is None:
            raise ValidationError(
                {"pay_date": ["A reconciled or manually edited future bill cannot be mapped to the new cadence."]}
            )

        if state.is_manual_override:
            target.amount_cents = state.amount_cents
            target.is_manual_override = True

        if state.payment_review_status != models.PaymentReviewStatus.UNREVIEWED:
            target.payment_review_status = state.payment_review_status
            target.actual_amount_cents = state.actual_amount_cents
            target.scheduled_amount_cents = state.scheduled_amount_cents
            target.payment_reconciled_at = state.payment_reconciled_at
            target.paid_at = state.paid_at

        updated_items.append(target)

    if updated_items:
        models.BudgetLineItem.objects.bulk_update(
            updated_items,
            [
                "amount_cents",
                "is_manual_override",
                "payment_review_status",
                "actual_amount_cents",
                "scheduled_amount_cents",
                "payment_reconciled_at",
                "paid_at",
            ],
        )

    if missing_items:
        models.BudgetLineItem.objects.bulk_create(missing_items)


def _can_recreate_manual_item(state: LineItemState) -> bool:
    return state.is_manual_override or state.source_type == models.SourceType.MANUAL_EXPENSE


def _get_manual_target_period(
    regenerated_periods: list[models.BudgetPayPeriod],
    occurrence_key: LineItemOccurrenceKey,
) -> models.BudgetPayPeriod | None:
    if occurrence_key.kind == LineItemOccurrenceKind.EFFECTIVE_PERIOD:
        return regenerated_periods[0]

    if occurrence_key.kind == LineItemOccurrenceKind.PAY_DATE:
        return next(
            (period for period in regenerated_periods if period.pay_date == occurrence_key.occurrence_date),
            None,
        )

    return None


def _build_manual_item(period: models.BudgetPayPeriod, state: LineItemState) -> models.BudgetLineItem:
    return models.BudgetLineItem(
        pay_period=period,
        source_type=state.source_type,
        source_key=state.source_key,
        title=state.title,
        amount_cents=state.amount_cents,
        display_order=state.display_order,
        is_required=state.is_required,
        is_split=state.is_split,
        is_manual_override=state.is_manual_override,
        is_auto_deducted=state.is_auto_deducted,
        payment_review_status=state.payment_review_status,
        actual_amount_cents=state.actual_amount_cents,
        scheduled_amount_cents=state.scheduled_amount_cents,
        payment_reconciled_at=state.payment_reconciled_at,
        paid_at=state.paid_at,
        expected_payment_date=state.expected_payment_date,
        payment_timing=state.payment_timing or "",
        paycheck_position=state.paycheck_position or "",
    )


def _restore_debt_balance_states(
    regenerated_periods: list[models.BudgetPayPeriod],
    states: list[DebtBalanceState],
) -> None:
    periods_by_pay_date = {period.pay_date: period for period in regenerated_periods}
    restored_records: list[models.BudgetDebtBalanceRecord] = []

    for state in states:
        target = (
            regenerated_periods[0] if state.is_effective_period else periods_by_pay_date.get(state.original_pay_date)
        )

        if target is None:
            raise ValidationError({"pay_date": ["A future debt balance fact cannot be mapped to the new cadence."]})

        restored_records.append(
            models.BudgetDebtBalanceRecord(
                pay_period=target,
                source_key=state.source_key,
                title=state.title,
                review_status=state.review_status,
                actual_balance_cents=state.actual_balance_cents,
                reconciled_at=state.reconciled_at,
            )
        )

    if restored_records:
        models.BudgetDebtBalanceRecord.objects.bulk_create(restored_records)
