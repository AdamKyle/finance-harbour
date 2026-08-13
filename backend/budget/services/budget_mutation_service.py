from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from authentication.models import User
from budget.enums import BudgetValueField
from budget.models import BudgetLineItem, BudgetPayPeriod, PayChequeReviewStatus, PaymentReviewStatus, SourceType
from budget.services.important_expense_warning_service import calculate_affects_important_expenses
from budget.services.line_item_funding_service import apply_line_item_funding
from debt_profile.models import DebtProfile

PERIOD_FIELDS = {
    BudgetValueField.PAY_CHEQUE: "pay_cheque_is_manual",
    BudgetValueField.CARRIED_LEFT_OVER: "carried_left_over_is_manual",
    BudgetValueField.TOTAL_AVAILABLE: "total_available_is_manual",
    BudgetValueField.TOTAL_BILLS: "total_bills_is_manual",
    BudgetValueField.LEFT_OVER: "left_over_is_manual",
}


@transaction.atomic
def update_budget_value(
    user: User,
    period_id: int,
    field: BudgetValueField,
    amount_cents: int,
    going_forward: bool,
    source_key: str | None,
) -> BudgetPayPeriod:
    selected_period = BudgetPayPeriod.objects.select_for_update().get(id=period_id, plan__user=user)
    affected_periods = list(
        BudgetPayPeriod.objects.select_for_update()
        .filter(plan=selected_period.plan, sequence__gte=selected_period.sequence)
        .order_by("sequence")
    )
    selected_period = affected_periods[0]
    target_periods = affected_periods if going_forward else [selected_period]

    if field == BudgetValueField.LINE_ITEM:
        update_line_items(target_periods, selected_period, source_key, amount_cents)
    else:
        update_period_fields(target_periods, field, amount_cents)

    recalculate_periods(affected_periods)

    return selected_period


def update_period_fields(periods: list[BudgetPayPeriod], field: BudgetValueField, amount_cents: int) -> None:
    manual_field = PERIOD_FIELDS[field]
    updated_at = timezone.now()

    for period in periods:
        setattr(period, field, amount_cents)
        setattr(period, manual_field, True)
        period.updated_at = updated_at

    BudgetPayPeriod.objects.bulk_update(periods, [field, manual_field, "updated_at"])


def update_line_items(
    periods: list[BudgetPayPeriod],
    selected_period: BudgetPayPeriod,
    source_key: str | None,
    amount_cents: int,
) -> None:
    if source_key is None:
        raise BudgetLineItem.DoesNotExist

    source_item = BudgetLineItem.objects.filter(
        pay_period__plan=selected_period.plan,
        source_key=source_key,
    ).first()

    if source_item is None:
        raise BudgetLineItem.DoesNotExist

    existing_items = {
        line_item.pay_period_id: line_item
        for line_item in BudgetLineItem.objects.filter(
            pay_period__in=periods,
            source_key=source_key,
        )
    }
    updated_items = []
    missing_items = []
    updated_at = timezone.now()

    for period in periods:
        line_item = existing_items.get(period.id)

        if line_item is None:
            missing_items.append(
                BudgetLineItem(
                    pay_period=period,
                    source_type=source_item.source_type,
                    source_key=source_item.source_key,
                    title=source_item.title,
                    amount_cents=amount_cents,
                    display_order=source_item.display_order,
                    is_required=source_item.is_required,
                    is_split=False,
                    is_manual_override=True,
                )
            )

            continue

        line_item.amount_cents = amount_cents
        line_item.is_manual_override = True
        line_item.updated_at = updated_at
        updated_items.append(line_item)

    if updated_items:
        BudgetLineItem.objects.bulk_update(
            updated_items,
            ["amount_cents", "is_manual_override", "updated_at"],
        )

    if missing_items:
        BudgetLineItem.objects.bulk_create(missing_items)


@transaction.atomic
def add_budget_bill(
    user: User,
    period_id: int,
    title: str,
    amount_cents: int,
    is_required: bool,
    going_forward: bool,
) -> BudgetPayPeriod:
    selected_period = BudgetPayPeriod.objects.select_for_update().get(id=period_id, plan__user=user)
    affected_periods = list(
        BudgetPayPeriod.objects.select_for_update()
        .filter(plan=selected_period.plan, sequence__gte=selected_period.sequence)
        .order_by("sequence")
    )
    selected_period = affected_periods[0]
    target_periods = affected_periods if going_forward else [selected_period]
    source_key = f"manual:{uuid4()}"
    display_order = (
        BudgetLineItem.objects.filter(pay_period=selected_period)
        .order_by("-display_order")
        .values_list("display_order", flat=True)
        .first()
        or 0
    ) + 1

    BudgetLineItem.objects.bulk_create(
        [
            BudgetLineItem(
                pay_period=period,
                source_type=SourceType.MANUAL_EXPENSE,
                source_key=source_key,
                title=title.strip(),
                amount_cents=amount_cents,
                display_order=display_order,
                is_required=is_required,
                is_manual_override=True,
            )
            for period in target_periods
        ]
    )

    recalculate_periods(affected_periods)

    return selected_period


def recalculate_periods(periods: list[BudgetPayPeriod]) -> None:
    if not periods:
        return

    plan_id = periods[0].plan_id
    first_sequence = periods[0].sequence
    previous_left_over = (
        BudgetPayPeriod.objects.filter(plan_id=plan_id, sequence__lt=first_sequence)
        .order_by("-sequence")
        .values_list("left_over_cents", flat=True)
        .first()
    )
    bill_totals: dict[int, int] = {}
    missed_important_period_ids: set[int] = set()
    line_items = list(
        BudgetLineItem.objects.filter(pay_period__in=periods).only(
            "id",
            "pay_period_id",
            "source_type",
            "source_key",
            "display_order",
            "amount_cents",
            "actual_amount_cents",
            "scheduled_amount_cents",
            "payment_review_status",
            "is_required",
            "funded_amount_cents",
            "shortfall_cents",
        )
    )

    for line_item in line_items:
        effective_amount = line_item.amount_cents

        if line_item.payment_review_status == PaymentReviewStatus.PAID:
            effective_amount = line_item.actual_amount_cents or 0

        if line_item.payment_review_status == PaymentReviewStatus.NOT_PAID:
            effective_amount = 0

        if line_item.payment_review_status == PaymentReviewStatus.SCHEDULED:
            effective_amount = line_item.scheduled_amount_cents or 0

        bill_totals[line_item.pay_period_id] = bill_totals.get(line_item.pay_period_id, 0) + effective_amount

        is_missed_important = line_item.is_required and (
            line_item.payment_review_status == PaymentReviewStatus.NOT_PAID
            or (
                line_item.payment_review_status == PaymentReviewStatus.PAID
                and effective_amount < line_item.amount_cents
            )
        )

        if is_missed_important:
            missed_important_period_ids.add(line_item.pay_period_id)
    important_period_ids = set(
        BudgetLineItem.objects.filter(pay_period__in=periods, is_required=True).values_list("pay_period_id", flat=True)
    )
    warning_threshold = (
        DebtProfile.objects.filter(user__budget_plan__id=plan_id)
        .values_list("left_over_warning_amount_cents", flat=True)
        .first()
        or 0
    )
    updated_at = timezone.now()

    for period in periods:
        if previous_left_over is not None and not period.carried_left_over_is_manual:
            period.carried_left_over_cents = previous_left_over

        if not period.total_available_is_manual:
            effective_pay_cheque = period.pay_cheque_cents

            if period.pay_cheque_review_status == PayChequeReviewStatus.CONFIRMED:
                effective_pay_cheque = period.actual_pay_cheque_cents or 0

            period.total_available_cents = effective_pay_cheque + period.carried_left_over_cents

        if not period.total_bills_is_manual:
            period.total_bills_cents = bill_totals.get(period.id, 0)

        if not period.left_over_is_manual:
            period.left_over_cents = period.total_available_cents - period.total_bills_cents

        period.has_negative_left_over = period.left_over_cents < 0
        period.has_missed_important_expenses = period.id in missed_important_period_ids
        period.is_below_warning_threshold = warning_threshold > 0 and period.left_over_cents < warning_threshold
        period.affects_important_expenses = (
            calculate_affects_important_expenses(
                has_negative_left_over=period.has_negative_left_over,
                has_important_on_card=period.id in important_period_ids,
                has_deferred_important=period.has_deferred_important_expenses,
            )
            or period.has_missed_important_expenses
        )
        period.updated_at = updated_at
        period_line_items = [line_item for line_item in line_items if line_item.pay_period_id == period.id]
        apply_line_item_funding(period_line_items, period.total_available_cents)
        previous_left_over = period.left_over_cents

    BudgetLineItem.objects.bulk_update(
        line_items,
        ["funded_amount_cents", "shortfall_cents"],
    )

    BudgetPayPeriod.objects.bulk_update(
        periods,
        [
            "carried_left_over_cents",
            "total_available_cents",
            "total_bills_cents",
            "left_over_cents",
            "has_negative_left_over",
            "has_missed_important_expenses",
            "is_below_warning_threshold",
            "affects_important_expenses",
            "updated_at",
        ],
    )
