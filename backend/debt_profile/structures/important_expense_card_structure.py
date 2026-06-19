from typing import TypedDict


class ImportantExpenseCardStructure(TypedDict):
    key: str
    title: str
    amount_cents: int
    selected: bool
