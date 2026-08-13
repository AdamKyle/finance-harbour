from __future__ import annotations

import calendar
import datetime
from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone

from authentication.models import User
from budget.models import BudgetLineItem, BudgetPayPeriod, BudgetPlan, SourceType
from budget.services.important_expense_warning_service import calculate_affects_important_expenses
from budget.services.line_item_funding_service import apply_line_item_funding
from budget.services.pay_cadence_position_service import get_payday_position
from budget.services.pay_date_generation_service import generate_pay_dates
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    ExpensePaymentTiming,
    PaycheckPosition,
    RecurringExpense,
    RecurringExpenseCategory,
    RequiredExpense,
)


@dataclass
class SourceObligation:
    source_type: SourceType
    source_key: str
    title: str
    monthly_amount_cents: int
    is_required: bool
    display_order: int
    is_rent: bool = False
    payment_timing: ExpensePaymentTiming | None = None
    payment_day_of_month: int | None = None
    paycheck_position: PaycheckPosition | None = None
    is_auto_deducted: bool = False


@dataclass
class PeriodAllocation:
    obligation: SourceObligation
    amount_cents: int
    is_split: bool
    is_deferred: bool
    expected_payment_date: datetime.date | None = None


@dataclass
class PeriodState:
    sequence: int
    pay_date: datetime.date
    month_key: tuple[int, int]
    is_final_in_month: bool
    allocations: list[PeriodAllocation] = field(default_factory=list)


def _add_one_year(date: datetime.date) -> datetime.date:
    try:
        return date.replace(year=date.year + 1)
    except ValueError:
        # Feb 29 → Feb 28 of next year
        return date.replace(year=date.year + 1, day=28)


def generate_budget(user: User) -> BudgetPlan:
    debt_profile = DebtProfile.objects.select_for_update().get(user=user)
    recurring_expenses = list(RecurringExpense.objects.filter(debt_profile=debt_profile).order_by("id"))
    required_expenses = list(RequiredExpense.objects.filter(debt_profile=debt_profile))
    payment_schedules = {
        schedule.source_key: schedule for schedule in ExpensePaymentSchedule.objects.filter(debt_profile=debt_profile)
    }

    pay_dates = generate_pay_dates(
        debt_profile.next_pay_date,
        debt_profile.pay_period_type,
        _add_one_year(debt_profile.next_pay_date),
    )
    plan_start = debt_profile.next_pay_date
    plan_end = _add_one_year(debt_profile.next_pay_date)
    planning_date = min(timezone.localdate(), debt_profile.next_pay_date)

    periods = build_budget_period_states(
        debt_profile=debt_profile,
        pay_dates=pay_dates,
        cadence_anchor=debt_profile.next_pay_date,
        planning_date=planning_date,
        recurring_expenses=recurring_expenses,
        required_expenses=required_expenses,
        payment_schedules=payment_schedules,
    )

    return _persist(user, plan_start, plan_end, debt_profile, periods)


def build_budget_period_states(
    debt_profile: DebtProfile,
    pay_dates: list[datetime.date],
    cadence_anchor: datetime.date,
    planning_date: datetime.date,
    recurring_expenses: list[RecurringExpense] | None = None,
    required_expenses: list[RequiredExpense] | None = None,
    payment_schedules: dict[str, ExpensePaymentSchedule] | None = None,
) -> list[PeriodState]:
    if recurring_expenses is None:
        recurring_expenses = list(RecurringExpense.objects.filter(debt_profile=debt_profile).order_by("id"))

    if required_expenses is None:
        required_expenses = list(RequiredExpense.objects.filter(debt_profile=debt_profile))

    if payment_schedules is None:
        payment_schedules = {
            schedule.source_key: schedule
            for schedule in ExpensePaymentSchedule.objects.filter(debt_profile=debt_profile)
        }

    obligations = _build_obligations(debt_profile, recurring_expenses, required_expenses, payment_schedules)
    legacy_allocated_obligations = [obligation for obligation in obligations if obligation.payment_timing is None]
    periods = _allocate(
        pay_dates,
        legacy_allocated_obligations,
        debt_profile.pay_period_type,
        debt_profile.income_per_pay_period_cents,
    )
    _apply_every_paycheck_schedules(periods, obligations)
    _apply_paycheck_position_schedules(periods, obligations, cadence_anchor, debt_profile.pay_period_type)
    _apply_day_of_month_schedules(periods, obligations, planning_date)

    return periods


def _advance_one_month(date: datetime.date, anchor_day: int) -> datetime.date:
    month = date.month + 1
    year = date.year

    if month > 12:
        month = 1
        year += 1

    max_day = calendar.monthrange(year, month)[1]
    day = min(anchor_day, max_day)

    return datetime.date(year, month, day)


def _build_obligations(
    debt_profile: DebtProfile,
    recurring_expenses: list[RecurringExpense],
    required_expenses: list[RequiredExpense],
    payment_schedules: dict[str, ExpensePaymentSchedule] | None = None,
) -> list[SourceObligation]:
    if payment_schedules is None:
        payment_schedules = {}

    required_keys = {r.source_key for r in required_expenses}
    obligations: list[SourceObligation] = []
    order = 0

    for idx, debt in enumerate(debt_profile.debts):
        payment = debt.get("current_payment_cents", 0)
        label = debt.get("label", f"Debt {idx + 1}")

        if payment <= 0:
            continue

        source_key = f"debt:{idx}"
        schedule = payment_schedules.get(source_key)
        obligations.append(
            SourceObligation(
                source_type=SourceType.DEBT,
                source_key=source_key,
                title=label,
                monthly_amount_cents=payment,
                is_required=schedule is not None and schedule.auto_deducted,
                display_order=order,
                payment_timing=schedule.timing if schedule is not None else None,
                payment_day_of_month=schedule.day_of_month if schedule is not None else None,
                paycheck_position=(
                    PaycheckPosition(schedule.paycheck_position)
                    if schedule is not None and schedule.paycheck_position
                    else None
                ),
                is_auto_deducted=schedule.auto_deducted if schedule is not None else False,
            )
        )
        order += 1

    for recurring_expense in recurring_expenses:
        if recurring_expense.amount_cents <= 0:
            continue

        schedule = payment_schedules.get(recurring_expense.source_key)
        is_rent = recurring_expense.category == RecurringExpenseCategory.RENT_OR_MORTGAGE
        source_type = SourceType.STANDARD_EXPENSE

        if is_rent:
            source_type = SourceType.RENT_OR_MORTGAGE
        elif recurring_expense.category == RecurringExpenseCategory.MISC:
            source_type = SourceType.MISC_EXPENSE

        obligations.append(
            SourceObligation(
                source_type=source_type,
                source_key=recurring_expense.source_key,
                title=recurring_expense.label,
                monthly_amount_cents=recurring_expense.amount_cents,
                is_required=(
                    is_rent
                    or recurring_expense.source_key in required_keys
                    or (schedule is not None and schedule.auto_deducted)
                ),
                display_order=order,
                is_rent=is_rent,
                payment_timing=schedule.timing if schedule is not None else None,
                payment_day_of_month=schedule.day_of_month if schedule is not None else None,
                paycheck_position=(
                    PaycheckPosition(schedule.paycheck_position)
                    if schedule is not None and schedule.paycheck_position
                    else None
                ),
                is_auto_deducted=schedule.auto_deducted if schedule is not None else False,
            )
        )
        order += 1

    return obligations


def _apply_day_of_month_schedules(
    period_states: list[PeriodState],
    obligations: list[SourceObligation],
    planning_date: datetime.date,
) -> None:
    scheduled_obligations = [
        obligation
        for obligation in obligations
        if obligation.payment_timing == ExpensePaymentTiming.DAY_OF_MONTH
        and obligation.payment_day_of_month is not None
    ]

    if not period_states or not scheduled_obligations:
        return

    for period in period_states:
        scheduled_keys = {obligation.source_key for obligation in scheduled_obligations}
        period.allocations = [
            allocation for allocation in period.allocations if allocation.obligation.source_key not in scheduled_keys
        ]

    month_cursor = planning_date.replace(day=1)
    final_month = period_states[-1].pay_date.replace(day=1)

    while month_cursor <= final_month:
        for obligation in scheduled_obligations:
            last_day = calendar.monthrange(month_cursor.year, month_cursor.month)[1]
            configured_date = month_cursor.replace(day=min(obligation.payment_day_of_month or 1, last_day))
            payment_date = _move_weekend_to_monday(configured_date)
            responsible_period = _find_responsible_period(period_states, payment_date, planning_date)

            if responsible_period is not None:
                responsible_period.allocations.append(
                    PeriodAllocation(
                        obligation=obligation,
                        amount_cents=obligation.monthly_amount_cents,
                        is_split=False,
                        is_deferred=False,
                        expected_payment_date=payment_date,
                    )
                )

        month_cursor = _advance_one_month(month_cursor, 1)


def _move_weekend_to_monday(payment_date: datetime.date) -> datetime.date:
    if payment_date.weekday() == calendar.SATURDAY:
        return payment_date + datetime.timedelta(days=2)

    if payment_date.weekday() == calendar.SUNDAY:
        return payment_date + datetime.timedelta(days=1)

    return payment_date


def _apply_paycheck_position_schedules(
    period_states: list[PeriodState],
    obligations: list[SourceObligation],
    cadence_anchor: datetime.date,
    pay_period_type: str,
) -> None:
    scheduled_obligations = [
        obligation
        for obligation in obligations
        if obligation.payment_timing == ExpensePaymentTiming.PAYCHECK_POSITION
        and obligation.paycheck_position is not None
    ]

    if not scheduled_obligations:
        return

    for period in period_states:
        for obligation in scheduled_obligations:
            cadence_position = get_payday_position(period.pay_date, cadence_anchor, pay_period_type)

            if not cadence_position.matches(obligation.paycheck_position):
                continue

            period.allocations.append(
                PeriodAllocation(
                    obligation=obligation,
                    amount_cents=obligation.monthly_amount_cents,
                    is_split=False,
                    is_deferred=False,
                    expected_payment_date=period.pay_date,
                )
            )


def _apply_every_paycheck_schedules(
    period_states: list[PeriodState],
    obligations: list[SourceObligation],
) -> None:
    scheduled_obligations = [
        obligation for obligation in obligations if obligation.payment_timing == ExpensePaymentTiming.EVERY_PAYCHECK
    ]

    for period in period_states:
        for obligation in scheduled_obligations:
            period.allocations.append(
                PeriodAllocation(
                    obligation=obligation,
                    amount_cents=obligation.monthly_amount_cents,
                    is_split=False,
                    is_deferred=False,
                    expected_payment_date=period.pay_date,
                )
            )


def _get_position_period(
    ordered_periods: list[PeriodState],
    position: PaycheckPosition,
) -> PeriodState | None:
    if not ordered_periods:
        return None

    if position == PaycheckPosition.LAST:
        return ordered_periods[-1]

    position_indexes = {
        PaycheckPosition.FIRST: 0,
        PaycheckPosition.SECOND: 1,
        PaycheckPosition.THIRD: 2,
        PaycheckPosition.FOURTH: 3,
    }
    position_index = position_indexes[position]

    if position_index >= len(ordered_periods):
        return None

    return ordered_periods[position_index]


def _find_responsible_period(
    period_states: list[PeriodState],
    payment_date: datetime.date,
    planning_date: datetime.date,
) -> PeriodState | None:
    first_period = period_states[0]

    if payment_date < first_period.pay_date:
        if payment_date < planning_date:
            return None

        return first_period

    responsible_period: PeriodState | None = None

    for period in period_states:
        if period.pay_date > payment_date:
            break
        responsible_period = period

    return responsible_period


def _month_key(date: datetime.date) -> tuple[int, int]:
    return (date.year, date.month)


def _group_by_month(
    pay_dates: list[datetime.date],
) -> dict[tuple[int, int], list[datetime.date]]:
    groups: dict[tuple[int, int], list[datetime.date]] = {}

    for d in pay_dates:
        key = _month_key(d)
        groups.setdefault(key, []).append(d)

    return groups


def _allocate(
    pay_dates: list[datetime.date],
    obligations: list[SourceObligation],
    pay_period_type: str,
    income_cents: int,
) -> list[PeriodState]:
    monthly_groups = _group_by_month(pay_dates)
    date_to_seq = {d: i for i, d in enumerate(pay_dates)}
    period_states: list[PeriodState] = []

    for date in pay_dates:
        mk = _month_key(date)
        month_dates = monthly_groups[mk]
        is_final = date == month_dates[-1]
        ps = PeriodState(
            sequence=date_to_seq[date],
            pay_date=date,
            month_key=mk,
            is_final_in_month=is_final,
        )
        period_states.append(ps)

    if pay_period_type == "MONTHLY":
        _allocate_monthly(period_states, obligations)
    elif pay_period_type == "WEEKLY":
        _allocate_weekly(period_states, obligations, income_cents)
    else:
        _allocate_biweekly(period_states, obligations, income_cents)

    return period_states


def _rent_obligation(
    obligations: list[SourceObligation],
) -> SourceObligation | None:
    for ob in obligations:
        if ob.is_rent:
            return ob

    return None


def _non_rent_obligations(
    obligations: list[SourceObligation],
) -> list[SourceObligation]:
    return [ob for ob in obligations if not ob.is_rent]


def _priority_key(ob: SourceObligation) -> tuple[int, int]:
    if ob.is_required:
        return (0, ob.display_order)
    if ob.source_type == SourceType.DEBT:
        return (1, ob.display_order)
    if ob.source_type == SourceType.MISC_EXPENSE:
        return (3, ob.display_order)
    return (2, ob.display_order)


def _sort_obligations_weekly(obligations: list[SourceObligation]) -> list[SourceObligation]:
    return sorted(obligations, key=_priority_key)


def _sort_obligations_biweekly(obligations: list[SourceObligation]) -> list[SourceObligation]:
    return sorted(obligations, key=_priority_key)


def _allocate_monthly(
    period_states: list[PeriodState],
    obligations: list[SourceObligation],
) -> None:
    for ps in period_states:
        for ob in obligations:
            ps.allocations.append(PeriodAllocation(ob, ob.monthly_amount_cents, False, False))


def _allocate_weekly(
    period_states: list[PeriodState],
    obligations: list[SourceObligation],
    income_cents: int,
) -> None:
    seq_to_ps = {ps.sequence: ps for ps in period_states}
    mk_to_sequences: dict[tuple[int, int], list[int]] = {}

    for ps in period_states:
        mk_to_sequences.setdefault(ps.month_key, []).append(ps.sequence)

    sorted_mks = sorted(mk_to_sequences.keys())
    # Only assign obligations for the first 12 calendar months
    active_mks = set(sorted_mks[:12])

    rent_ob = _rent_obligation(obligations)
    non_rent = _non_rent_obligations(obligations)
    sorted_non_rent = _sort_obligations_weekly(non_rent)

    carry = 0

    for mk in sorted_mks:
        seqs = mk_to_sequences[mk]
        seqs_sorted = sorted(seqs)

        if mk not in active_mks:
            # Periods beyond the 12-month obligation window carry income forward with no bills
            continue

        first_seq = seqs_sorted[0]
        final_seq = seqs_sorted[-1]
        remaining: dict[str, int] = {ob.source_key: ob.monthly_amount_cents for ob in non_rent}
        split_keys: set[str] = set()
        attempted_in_nonfinal: set[str] = set()
        period_carry = carry

        for seq in seqs_sorted[:-1]:
            ps = seq_to_ps[seq]
            is_first_period = seq == first_seq
            total_available = income_cents + period_carry

            for ob in sorted_non_rent:
                to_place = remaining.get(ob.source_key, 0)

                if to_place <= 0:
                    continue

                attempted_in_nonfinal.add(ob.source_key)
                allocated_so_far = sum(alloc.amount_cents for alloc in ps.allocations)
                available = total_available - allocated_so_far

                if available <= 0:
                    continue

                place = min(to_place, available)
                already_split = ob.source_key in split_keys

                if place < to_place:
                    split_keys.add(ob.source_key)
                    is_split = True
                else:
                    is_split = already_split

                # Deferred when placed on any card after the first card of the month
                is_deferred = not is_first_period

                ps.allocations.append(PeriodAllocation(ob, place, is_split, is_deferred))
                remaining[ob.source_key] = to_place - place

            total_bills = sum(alloc.amount_cents for alloc in ps.allocations)
            period_carry = total_available - total_bills

        final_ps = seq_to_ps[final_seq]
        total_available_final = income_cents + period_carry

        for ob in sorted_non_rent:
            leftover_amount = remaining.get(ob.source_key, 0)

            if leftover_amount <= 0:
                continue

            is_split = ob.source_key in split_keys
            is_deferred = ob.source_key in attempted_in_nonfinal
            final_ps.allocations.append(PeriodAllocation(ob, leftover_amount, is_split, is_deferred))

        if rent_ob:
            final_ps.allocations.append(PeriodAllocation(rent_ob, rent_ob.monthly_amount_cents, False, False))

        total_bills_final = sum(alloc.amount_cents for alloc in final_ps.allocations)
        carry = total_available_final - total_bills_final


def _allocate_biweekly(
    period_states: list[PeriodState],
    obligations: list[SourceObligation],
    income_cents: int,
) -> None:
    seq_to_ps = {ps.sequence: ps for ps in period_states}
    mk_to_sequences: dict[tuple[int, int], list[int]] = {}

    for ps in period_states:
        mk_to_sequences.setdefault(ps.month_key, []).append(ps.sequence)

    sorted_mks = sorted(mk_to_sequences.keys())
    active_mks = set(sorted_mks[:12])

    rent_ob = _rent_obligation(obligations)
    non_rent = _non_rent_obligations(obligations)

    carry = 0

    for mk in sorted_mks:
        seqs = mk_to_sequences[mk]
        seqs_sorted = sorted(seqs)

        if mk not in active_mks:
            continue

        first_seq = seqs_sorted[0]
        final_seq = seqs_sorted[-1]
        remaining: dict[str, int] = {ob.source_key: ob.monthly_amount_cents for ob in non_rent}
        split_keys: set[str] = set()
        attempted_in_nonfinal: set[str] = set()
        period_carry = carry

        for seq in seqs_sorted[:-1]:
            ps = seq_to_ps[seq]
            is_first_period = seq == first_seq
            total_available = income_cents + period_carry

            for ob in _sort_obligations_biweekly(non_rent):
                to_place = remaining.get(ob.source_key, 0)

                if to_place <= 0:
                    continue

                attempted_in_nonfinal.add(ob.source_key)
                allocated_so_far = sum(alloc.amount_cents for alloc in ps.allocations)
                available = total_available - allocated_so_far

                if available <= 0:
                    continue

                place = min(to_place, available)
                already_split = ob.source_key in split_keys

                if place < to_place:
                    split_keys.add(ob.source_key)
                    is_split = True
                else:
                    is_split = already_split

                # Deferred when placed on any card after the first card of the month
                is_deferred = not is_first_period

                ps.allocations.append(PeriodAllocation(ob, place, is_split, is_deferred))
                remaining[ob.source_key] = to_place - place

            total_bills = sum(alloc.amount_cents for alloc in ps.allocations)
            period_carry = total_available - total_bills

        final_ps = seq_to_ps[final_seq]
        total_available_final = income_cents + period_carry

        if rent_ob:
            final_ps.allocations.append(PeriodAllocation(rent_ob, rent_ob.monthly_amount_cents, False, False))

        for ob in _sort_obligations_biweekly(non_rent):
            leftover_amount = remaining.get(ob.source_key, 0)

            if leftover_amount <= 0:
                continue

            is_split = ob.source_key in split_keys
            is_deferred = ob.source_key in attempted_in_nonfinal
            final_ps.allocations.append(PeriodAllocation(ob, leftover_amount, is_split, is_deferred))

        total_bills_final = sum(alloc.amount_cents for alloc in final_ps.allocations)
        carry = total_available_final - total_bills_final


@transaction.atomic
def _persist(
    user: User,
    plan_start: datetime.date,
    plan_end: datetime.date,
    debt_profile: DebtProfile,
    period_states: list[PeriodState],
) -> BudgetPlan:
    existing = BudgetPlan.objects.filter(user=user).first()

    if existing:
        return existing

    plan = BudgetPlan.objects.create(
        user=user,
        start_date=plan_start,
        end_date=plan_end,
        pay_period_type=debt_profile.pay_period_type,
        income_per_pay_period_cents=debt_profile.income_per_pay_period_cents,
    )

    create_budget_periods(
        plan=plan,
        debt_profile=debt_profile,
        period_states=period_states,
        starting_sequence=0,
        carried_left_over_cents=0,
    )

    return plan


def create_budget_periods(
    plan: BudgetPlan,
    debt_profile: DebtProfile,
    period_states: list[PeriodState],
    starting_sequence: int,
    carried_left_over_cents: int,
    first_period_id: int | None = None,
) -> list[BudgetPayPeriod]:
    carried = carried_left_over_cents
    pay_period_objects: list[tuple[BudgetPayPeriod, list[PeriodAllocation]]] = []

    for index, ps in enumerate(period_states):
        income = debt_profile.income_per_pay_period_cents
        total_available = income + carried
        total_bills = sum(alloc.amount_cents for alloc in ps.allocations)
        left_over = total_available - total_bills

        has_negative = left_over < 0
        is_below_threshold = (
            left_over < debt_profile.left_over_warning_amount_cents and debt_profile.left_over_warning_amount_cents > 0
        )
        has_deferred = any(alloc.is_split or alloc.is_deferred for alloc in ps.allocations)
        has_important_on_card = any(
            alloc.obligation.is_required or alloc.obligation.is_rent for alloc in ps.allocations
        )
        has_deferred_important = any(
            (alloc.obligation.is_required or alloc.obligation.is_rent) and alloc.is_deferred for alloc in ps.allocations
        )
        affects_important = calculate_affects_important_expenses(
            has_negative_left_over=has_negative,
            has_important_on_card=has_important_on_card,
            has_deferred_important=has_deferred_important,
        )

        period_obj = BudgetPayPeriod(
            plan=plan,
            sequence=starting_sequence + ps.sequence,
            pay_date=ps.pay_date,
            pay_cheque_cents=income,
            carried_left_over_cents=carried,
            total_available_cents=total_available,
            total_bills_cents=total_bills,
            left_over_cents=left_over,
            has_negative_left_over=has_negative,
            is_below_warning_threshold=is_below_threshold,
            has_deferred_items=has_deferred,
            has_deferred_important_expenses=has_deferred_important,
            affects_important_expenses=affects_important,
        )

        if index == 0 and first_period_id is not None:
            period_obj.id = first_period_id

        pay_period_objects.append((period_obj, ps.allocations))
        carried = left_over

    created_periods = BudgetPayPeriod.objects.bulk_create([pp for pp, _ in pay_period_objects])

    line_items: list[BudgetLineItem] = []

    for period_obj, allocations in zip(created_periods, [allocs for _, allocs in pay_period_objects], strict=True):
        period_line_items: list[BudgetLineItem] = []

        for alloc in allocations:
            period_line_items.append(
                BudgetLineItem(
                    pay_period=period_obj,
                    source_type=alloc.obligation.source_type,
                    source_key=alloc.obligation.source_key,
                    title=alloc.obligation.title,
                    amount_cents=alloc.amount_cents,
                    display_order=alloc.obligation.display_order,
                    is_required=alloc.obligation.is_required or alloc.obligation.is_rent,
                    is_auto_deducted=alloc.obligation.is_auto_deducted,
                    is_split=alloc.is_split,
                    expected_payment_date=(
                        alloc.expected_payment_date
                        or (
                            period_obj.pay_date
                            if alloc.obligation.payment_timing == ExpensePaymentTiming.PAYCHECK_POSITION
                            else None
                        )
                    ),
                    payment_timing=alloc.obligation.payment_timing or "",
                    paycheck_position=alloc.obligation.paycheck_position or "",
                )
            )

        apply_line_item_funding(period_line_items, period_obj.total_available_cents)
        line_items.extend(period_line_items)

    BudgetLineItem.objects.bulk_create(line_items)

    return created_periods
