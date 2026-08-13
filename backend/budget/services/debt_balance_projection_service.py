from budget.models import (
    BudgetLineItem,
    BudgetPayPeriod,
    BudgetPlan,
    DebtBalanceReviewStatus,
    PaymentReviewStatus,
    SourceType,
)
from budget.types import DebtProfileDebtDefinition, PaydayDebtBalanceCheck, PaydayDebtDefinition
from debt_profile.models import DebtProfile


def get_debt_balance_projections(period: BudgetPayPeriod) -> list[PaydayDebtBalanceCheck]:
    return get_debt_balance_projections_for_periods([period])[period.id]


def get_plan_debt_definitions(plan: BudgetPlan) -> list[PaydayDebtDefinition]:
    debt_rows = BudgetLineItem.objects.filter(pay_period__plan=plan, source_type=SourceType.DEBT).order_by(
        "pay_period__sequence", "display_order", "source_key", "id"
    )
    definitions_by_source_key: dict[str, PaydayDebtDefinition] = {}

    for source_key, title, first_sequence in debt_rows.values_list("source_key", "title", "pay_period__sequence"):
        definitions_by_source_key.setdefault(
            source_key,
            PaydayDebtDefinition(source_key=source_key, title=title, first_sequence=first_sequence),
        )

    return list(definitions_by_source_key.values())


def get_applicable_debt_definitions(
    debt_definitions: list[PaydayDebtDefinition],
    selected_sequence: int,
) -> list[PaydayDebtDefinition]:
    return [definition for definition in debt_definitions if definition.first_sequence <= selected_sequence]


def get_debt_balance_projections_for_periods(
    selected_periods: list[BudgetPayPeriod],
) -> dict[int, list[PaydayDebtBalanceCheck]]:
    if not selected_periods:
        return {}

    plan = selected_periods[0].plan
    periods = list(
        BudgetPayPeriod.objects.filter(plan=plan)
        .order_by("sequence")
        .prefetch_related("line_items", "debt_balance_records")
    )
    debt_profile = DebtProfile.objects.filter(user=plan.user).only("debts").first()
    debts: list[DebtProfileDebtDefinition] = debt_profile.debts if debt_profile is not None else []
    debt_definitions = get_plan_debt_definitions(plan)

    results_by_period: dict[int, list[PaydayDebtBalanceCheck]] = {}

    for selected_period in selected_periods:
        results_by_period[selected_period.id] = [
            project_debt(periods, selected_period, definition.source_key, definition.title, debts)
            for definition in get_applicable_debt_definitions(debt_definitions, selected_period.sequence)
        ]

    return results_by_period


def project_debt(
    periods: list[BudgetPayPeriod],
    selected_period: BudgetPayPeriod,
    source_key: str,
    title: str,
    debts: list[DebtProfileDebtDefinition],
) -> PaydayDebtBalanceCheck:
    opening_balance = resolve_baseline_balance(source_key, title, debts)
    uncertain = opening_balance is None
    selected_result: PaydayDebtBalanceCheck | None = None
    previous_confirmed_balance: int | None = None

    for period in periods:
        payment = next((entry for entry in period.line_items.all() if entry.source_key == source_key), None)
        balance_record = next(
            (entry for entry in period.debt_balance_records.all() if entry.source_key == source_key),
            None,
        )
        expected_balance = opening_balance
        actual_balance = None
        review_status = DebtBalanceReviewStatus.UNREVIEWED

        if balance_record is not None:
            actual_balance = balance_record.actual_balance_cents
            review_status = DebtBalanceReviewStatus(balance_record.review_status)

            if balance_record.review_status == DebtBalanceReviewStatus.CONFIRMED:
                opening_balance = actual_balance

            if balance_record.review_status == DebtBalanceReviewStatus.UNKNOWN:
                uncertain = True

        if period.id == selected_period.id:
            variance = None
            variance_percentage = None
            movement_percentage = None

            if expected_balance is not None and actual_balance is not None:
                variance = actual_balance - expected_balance

                if expected_balance > 0:
                    variance_percentage = variance / expected_balance * 100

            if previous_confirmed_balance is not None and previous_confirmed_balance > 0 and actual_balance is not None:
                movement_percentage = (actual_balance - previous_confirmed_balance) / previous_confirmed_balance * 100

            selected_result = PaydayDebtBalanceCheck(
                source_key=source_key,
                title=title,
                expected_balance_cents=expected_balance,
                actual_balance_cents=actual_balance,
                review_status=review_status,
                variance_cents=variance,
                variance_percentage=variance_percentage,
                previous_confirmed_balance_cents=previous_confirmed_balance,
                movement_from_previous_percentage=movement_percentage,
                is_uncertain=uncertain,
            )

        if (
            balance_record is not None
            and balance_record.review_status == DebtBalanceReviewStatus.CONFIRMED
            and actual_balance is not None
        ):
            previous_confirmed_balance = actual_balance

        if opening_balance is None:
            continue

        payment_cents = 0

        if payment is not None:
            payment_cents = payment.amount_cents

            if payment.payment_review_status == PaymentReviewStatus.PAID:
                payment_cents = payment.actual_amount_cents or 0

            if payment.payment_review_status == PaymentReviewStatus.NOT_PAID:
                payment_cents = 0

            if payment.payment_review_status == PaymentReviewStatus.UNKNOWN:
                uncertain = True

            if payment.payment_review_status == PaymentReviewStatus.SCHEDULED:
                payment_cents = payment.scheduled_amount_cents or 0
                uncertain = True

        opening_balance = max(opening_balance - payment_cents, 0)

    if selected_result is None:
        raise BudgetPayPeriod.DoesNotExist

    return selected_result


def resolve_baseline_balance(source_key: str, title: str, debts: list[DebtProfileDebtDefinition]) -> int | None:
    source_parts = source_key.split(":", maxsplit=1)

    if len(source_parts) == 2 and source_parts[0] == "debt" and source_parts[1].isdigit():
        debt_index = int(source_parts[1])

        if debt_index < len(debts):
            indexed_debt = debts[debt_index]

            if indexed_debt.get("label") == title:
                balance = indexed_debt.get("current_balance_cents")

                return balance if isinstance(balance, int) else None

    title_matches = [debt for debt in debts if debt.get("label") == title]

    if len(title_matches) != 1:
        return None

    balance = title_matches[0].get("current_balance_cents")

    return balance if isinstance(balance, int) else None
