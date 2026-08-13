from math import ceil

from django.db import transaction

from debt_profile.models import DebtProfile, RecurringExpenseCategory, RequiredExpense
from debt_profile.structures import ImportantExpenseCardStructure, ImportantExpensePageStructure


def build_important_expense_cards(
    debt_profile: DebtProfile,
) -> list[ImportantExpenseCardStructure]:
    selected_keys = set(debt_profile.required_expenses.values_list("source_key", flat=True))
    auto_deducted_keys = set(
        debt_profile.expense_payment_schedules.filter(auto_deducted=True).values_list("source_key", flat=True)
    )
    cards: list[ImportantExpenseCardStructure] = []

    for recurring_expense in debt_profile.recurring_expenses.order_by("id"):
        if recurring_expense.amount_cents <= 0:
            continue

        if recurring_expense.category == RecurringExpenseCategory.RENT_OR_MORTGAGE:
            continue

        if recurring_expense.source_key in auto_deducted_keys:
            continue

        cards.append(
            {
                "key": recurring_expense.source_key,
                "title": recurring_expense.label,
                "amount_cents": recurring_expense.amount_cents,
                "selected": recurring_expense.source_key in selected_keys,
            }
        )

    for index, debt in enumerate(debt_profile.debts):
        amount_cents = int(debt.get("current_payment_cents", 0))
        source_key = f"debt:{index}"

        if amount_cents <= 0 or source_key in auto_deducted_keys:
            continue

        cards.append(
            {
                "key": source_key,
                "title": str(debt.get("label", f"Debt {index + 1}")),
                "amount_cents": amount_cents,
                "selected": source_key in selected_keys,
            }
        )

    return cards


def build_important_expense_page(
    debt_profile: DebtProfile,
    page: int,
    per_page: int,
) -> ImportantExpensePageStructure:
    cards = build_important_expense_cards(debt_profile)
    total = len(cards)
    total_pages = ceil(total / per_page) if total > 0 else 1
    start_index = (page - 1) * per_page

    return {
        "cards": cards[start_index : start_index + per_page],
        "page": page,
        "total": total,
        "total_pages": total_pages,
    }


@transaction.atomic
def replace_required_expenses(
    debt_profile: DebtProfile,
    selected_keys: list[str],
) -> list[RequiredExpense]:
    available_cards = {card["key"]: card for card in build_important_expense_cards(debt_profile)}

    debt_profile.required_expenses.all().delete()

    required_expenses = [
        RequiredExpense(
            debt_profile=debt_profile,
            source_key=source_key,
            title=available_cards[source_key]["title"],
            amount_cents=available_cards[source_key]["amount_cents"],
        )
        for source_key in selected_keys
    ]

    return RequiredExpense.objects.bulk_create(required_expenses)
