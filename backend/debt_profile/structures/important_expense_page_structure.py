from typing import TypedDict

from debt_profile.structures.important_expense_card_structure import ImportantExpenseCardStructure


class ImportantExpensePageStructure(TypedDict):
    cards: list[ImportantExpenseCardStructure]
    page: int
    total: int
    total_pages: int
