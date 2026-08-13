import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.models import User
from budget.models import (
    BudgetDebtBalanceRecord,
    BudgetLineItem,
    BudgetPayPeriod,
    DebtBalanceReviewStatus,
    PayChequeReviewStatus,
    PaydayReconciliationStatus,
    PaymentReviewStatus,
)
from budget.services.budget_mutation_service import recalculate_periods
from budget.services.debt_balance_projection_service import (
    get_applicable_debt_definitions,
    get_plan_debt_definitions,
)
from budget.services.payday_warning_service import build_recalculation_warnings
from budget.types import PaydayWarning
from debt_profile.models import ExpensePaymentTiming


def recalculate_reconciliation_status(period: BudgetPayPeriod) -> None:
    payment_statuses = list(period.line_items.values_list("payment_review_status", flat=True))
    debt_definitions = get_applicable_debt_definitions(
        get_plan_debt_definitions(period.plan),
        period.sequence,
    )
    debt_statuses = dict(period.debt_balance_records.values_list("source_key", "review_status"))
    facts = [period.pay_cheque_review_status, *payment_statuses]
    facts.extend(
        debt_statuses.get(definition.source_key, DebtBalanceReviewStatus.UNREVIEWED) for definition in debt_definitions
    )
    now = timezone.now()

    unreviewed_statuses = {
        PayChequeReviewStatus.UNREVIEWED,
        PaymentReviewStatus.UNREVIEWED,
        DebtBalanceReviewStatus.UNREVIEWED,
    }
    unknown_statuses = {
        PayChequeReviewStatus.UNKNOWN,
        PaymentReviewStatus.UNKNOWN,
        DebtBalanceReviewStatus.UNKNOWN,
    }

    if all(status in unreviewed_statuses for status in facts):
        status = PaydayReconciliationStatus.NOT_STARTED
    elif any(status in unreviewed_statuses for status in facts):
        status = PaydayReconciliationStatus.IN_PROGRESS
    elif any(status in unknown_statuses for status in facts):
        status = PaydayReconciliationStatus.INCOMPLETE
    else:
        status = PaydayReconciliationStatus.REVIEWED

    if status != PaydayReconciliationStatus.NOT_STARTED and period.payday_reconciliation_started_at is None:
        period.payday_reconciliation_started_at = now

    period.payday_reconciliation_status = status
    period.payday_reconciliation_completed_at = (
        now if status in {PaydayReconciliationStatus.REVIEWED, PaydayReconciliationStatus.INCOMPLETE} else None
    )
    period.save(
        update_fields=[
            "payday_reconciliation_status",
            "payday_reconciliation_started_at",
            "payday_reconciliation_completed_at",
            "updated_at",
        ]
    )


def lock_owned_recalculation_periods(
    user: User,
    period_id: int,
    effective_date: datetime.date,
) -> tuple[BudgetPayPeriod, list[BudgetPayPeriod]]:
    selected = BudgetPayPeriod.objects.select_for_update().get(
        id=period_id,
        plan__user=user,
        pay_date__lte=effective_date,
    )
    periods = list(
        BudgetPayPeriod.objects.select_for_update()
        .filter(plan=selected.plan, sequence__gte=selected.sequence)
        .order_by("sequence")
    )

    return periods[0], periods


def validate_unknown_eligibility(
    period: BudgetPayPeriod,
    review_status: PayChequeReviewStatus | PaymentReviewStatus | DebtBalanceReviewStatus,
    effective_date: datetime.date,
) -> None:
    if review_status not in {
        PayChequeReviewStatus.UNKNOWN,
        PaymentReviewStatus.UNKNOWN,
        DebtBalanceReviewStatus.UNKNOWN,
    }:
        return

    if period.pay_date >= effective_date:
        raise ValidationError({"review_status": ["Unknown is available only for a past payday."]})


@transaction.atomic
def update_pay_cheque(
    user: User,
    period_id: int,
    review_status: PayChequeReviewStatus,
    actual_amount_cents: int | None,
    effective_date: datetime.date,
) -> tuple[BudgetPayPeriod, list[PaydayWarning], list[int]]:
    period, affected_periods = lock_owned_recalculation_periods(user, period_id, effective_date)
    validate_unknown_eligibility(period, review_status, effective_date)

    if review_status == PayChequeReviewStatus.UNKNOWN:
        actual_amount_cents = None
    period.pay_cheque_review_status = review_status
    period.actual_pay_cheque_cents = actual_amount_cents
    period.pay_cheque_reconciled_at = timezone.now()
    period.save(update_fields=["pay_cheque_review_status", "actual_pay_cheque_cents", "pay_cheque_reconciled_at"])
    recalculate_reconciliation_status(period)
    recalculate_periods(affected_periods)

    return period, build_recalculation_warnings(affected_periods), [entry.id for entry in affected_periods]


@transaction.atomic
def update_line_item(
    user: User,
    period_id: int,
    line_item_id: int,
    review_status: PaymentReviewStatus,
    actual_amount_cents: int | None,
    scheduled_amount_cents: int | None,
    effective_date: datetime.date,
) -> tuple[BudgetPayPeriod, list[PaydayWarning], list[int]]:
    period, affected_periods = lock_owned_recalculation_periods(user, period_id, effective_date)
    validate_unknown_eligibility(period, review_status, effective_date)
    line_item = BudgetLineItem.objects.select_for_update().get(
        id=line_item_id, pay_period=period, pay_period__plan__user=user
    )

    if review_status == PaymentReviewStatus.SCHEDULED and line_item.payment_timing != ExpensePaymentTiming.DAY_OF_MONTH:
        raise ValidationError({"review_status": ["Only a scheduled-date bill can remain scheduled."]})

    line_item.payment_review_status = review_status
    line_item.actual_amount_cents = actual_amount_cents
    line_item.scheduled_amount_cents = scheduled_amount_cents
    line_item.payment_reconciled_at = timezone.now()
    line_item.save(
        update_fields=[
            "payment_review_status",
            "actual_amount_cents",
            "scheduled_amount_cents",
            "payment_reconciled_at",
            "updated_at",
        ]
    )
    recalculate_reconciliation_status(period)
    recalculate_periods(affected_periods)

    return period, build_recalculation_warnings(affected_periods), [entry.id for entry in affected_periods]


@transaction.atomic
def update_debt_balance(
    user: User,
    period_id: int,
    source_key: str,
    title: str,
    review_status: DebtBalanceReviewStatus,
    actual_balance_cents: int | None,
    effective_date: datetime.date,
) -> tuple[BudgetPayPeriod, list[int]]:
    period, affected_periods = lock_owned_recalculation_periods(user, period_id, effective_date)
    validate_unknown_eligibility(period, review_status, effective_date)

    if review_status == DebtBalanceReviewStatus.UNKNOWN:
        actual_balance_cents = None
    applicable_debt_definitions = get_applicable_debt_definitions(
        get_plan_debt_definitions(period.plan),
        period.sequence,
    )
    if not any(
        definition.source_key == source_key and definition.title == title for definition in applicable_debt_definitions
    ):
        raise BudgetLineItem.DoesNotExist

    BudgetDebtBalanceRecord.objects.update_or_create(
        pay_period=period,
        source_key=source_key,
        defaults={
            "title": title,
            "review_status": review_status,
            "actual_balance_cents": actual_balance_cents,
            "reconciled_at": timezone.now(),
        },
    )
    recalculate_reconciliation_status(period)

    return period, [entry.id for entry in affected_periods]


@transaction.atomic
def mark_payday_incomplete(
    user: User,
    period_id: int,
    effective_date: datetime.date,
) -> tuple[BudgetPayPeriod, list[int]]:
    period, affected_periods = lock_owned_recalculation_periods(user, period_id, effective_date)
    if period.pay_date >= effective_date:
        raise ValueError("Only unresolved past paydays can be marked incomplete.")

    if period.payday_reconciliation_status not in {
        PaydayReconciliationStatus.NOT_STARTED,
        PaydayReconciliationStatus.IN_PROGRESS,
    }:
        raise ValueError("Only unresolved past paydays can be marked incomplete.")

    debt_definitions = get_applicable_debt_definitions(
        get_plan_debt_definitions(period.plan),
        period.sequence,
    )

    existing_keys = set(period.debt_balance_records.values_list("source_key", flat=True))
    has_unresolved_fact = (
        period.pay_cheque_review_status == PayChequeReviewStatus.UNREVIEWED
        or period.line_items.filter(payment_review_status=PaymentReviewStatus.UNREVIEWED).exists()
        or any(definition.source_key not in existing_keys for definition in debt_definitions)
    )

    if not has_unresolved_fact:
        raise ValueError("Only unresolved past paydays can be marked incomplete.")

    now = timezone.now()
    if period.pay_cheque_review_status == PayChequeReviewStatus.UNREVIEWED:
        period.pay_cheque_review_status = PayChequeReviewStatus.UNKNOWN
        period.actual_pay_cheque_cents = None
        period.pay_cheque_reconciled_at = now
        period.save(update_fields=["pay_cheque_review_status", "actual_pay_cheque_cents", "pay_cheque_reconciled_at"])

    period.line_items.filter(payment_review_status=PaymentReviewStatus.UNREVIEWED).update(
        payment_review_status=PaymentReviewStatus.UNKNOWN,
        actual_amount_cents=None,
        scheduled_amount_cents=None,
        payment_reconciled_at=now,
    )
    BudgetDebtBalanceRecord.objects.bulk_create(
        [
            BudgetDebtBalanceRecord(
                pay_period=period,
                source_key=definition.source_key,
                title=definition.title,
                review_status=DebtBalanceReviewStatus.UNKNOWN,
                actual_balance_cents=None,
                reconciled_at=now,
            )
            for definition in debt_definitions
            if definition.source_key not in existing_keys
        ]
    )
    recalculate_reconciliation_status(period)

    return period, [entry.id for entry in affected_periods]
