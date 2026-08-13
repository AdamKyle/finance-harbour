from budget.models import BudgetLineItem, PaymentReviewStatus, SourceType


def apply_line_item_funding(
    line_items: list[BudgetLineItem],
    available_cents: int,
) -> None:
    remaining_cents = max(available_cents, 0)

    for line_item in sorted(line_items, key=_funding_priority):
        required_cents = _get_effective_amount(line_item)
        funded_cents = min(required_cents, remaining_cents)
        line_item.funded_amount_cents = funded_cents
        line_item.shortfall_cents = required_cents - funded_cents
        remaining_cents -= funded_cents


def _get_effective_amount(line_item: BudgetLineItem) -> int:
    if line_item.payment_review_status == PaymentReviewStatus.PAID:
        return line_item.actual_amount_cents or 0

    if line_item.payment_review_status == PaymentReviewStatus.NOT_PAID:
        return 0

    if line_item.payment_review_status == PaymentReviewStatus.SCHEDULED:
        return line_item.scheduled_amount_cents or 0

    return line_item.amount_cents


def _funding_priority(line_item: BudgetLineItem) -> tuple[int, int, str]:
    if line_item.is_required:
        return (0, line_item.display_order, line_item.source_key)

    if line_item.source_type == SourceType.DEBT:
        return (1, line_item.display_order, line_item.source_key)

    if line_item.source_type == SourceType.MISC_EXPENSE:
        return (3, line_item.display_order, line_item.source_key)

    return (2, line_item.display_order, line_item.source_key)
