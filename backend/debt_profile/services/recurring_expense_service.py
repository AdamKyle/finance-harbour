from django.db import transaction

from debt_profile.models import DebtProfile, RecurringExpense
from debt_profile.types import RecurringExpenseInput


@transaction.atomic
def replace_recurring_expenses(
    debt_profile: DebtProfile,
    entries: list[RecurringExpenseInput],
) -> list[RecurringExpense]:
    submitted_source_keys = {entry["source_key"] for entry in entries}

    debt_profile.recurring_expenses.all().delete()
    debt_profile.required_expenses.exclude(source_key__in=submitted_source_keys).delete()
    debt_profile.expense_payment_schedules.exclude(source_key__startswith="debt:").exclude(
        source_key__in=submitted_source_keys
    ).delete()

    recurring_expenses = [
        RecurringExpense(
            debt_profile=debt_profile,
            source_key=entry["source_key"],
            category=entry["category"],
            label=entry["label"],
            amount_cents=entry["amount_cents"],
            utility_type=entry["utility_type"],
            includes_internet=entry["includes_internet"],
            includes_cable=entry["includes_cable"],
        )
        for entry in entries
    ]

    return RecurringExpense.objects.bulk_create(recurring_expenses)
