from django.db import transaction

from debt_profile.models import DebtProfile, MonthlyExpense, RequiredExpense
from debt_profile.structures import ImportantExpenseCardStructure

STANDARD_EXPENSE_FIELDS = (
    ("rent_or_mortgage_cents", "Rent or mortgage"),
    ("water_cents", "Water"),
    ("electricity_cents", "Electricity"),
    ("food_cents", "Food"),
    ("internet_cents", "Internet"),
    ("phone_cents", "Phone"),
    ("car_payment_cents", "Car payment"),
    ("insurance_cents", "Insurance"),
)


def build_important_expense_cards(
    debt_profile: DebtProfile,
) -> list[ImportantExpenseCardStructure]:
    try:
        monthly_expense = debt_profile.monthly_expense
    except MonthlyExpense.DoesNotExist:
        return []

    selected_keys = set(debt_profile.required_expenses.values_list("source_key", flat=True))
    cards: list[ImportantExpenseCardStructure] = []

    for field_name, title in STANDARD_EXPENSE_FIELDS:
        amount_cents = getattr(monthly_expense, field_name)

        if amount_cents <= 0:
            continue

        cards.append(
            {
                "key": field_name,
                "title": title,
                "amount_cents": amount_cents,
                "selected": field_name in selected_keys,
            }
        )

    for expense_index, misc_expense in enumerate(monthly_expense.misc_expenses):
        title = misc_expense.get("label")
        amount_cents = misc_expense.get("amount_cents")

        if not isinstance(title, str) or not isinstance(amount_cents, int):
            continue

        if title == "" or amount_cents <= 0:
            continue

        source_key = f"misc:{expense_index}"

        cards.append(
            {
                "key": source_key,
                "title": title,
                "amount_cents": amount_cents,
                "selected": source_key in selected_keys,
            }
        )

    return cards


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
