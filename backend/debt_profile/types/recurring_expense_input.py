from typing import Literal, TypedDict

from debt_profile.models import RecurringExpenseCategory, UtilityType


class RecurringExpenseInput(TypedDict):
    source_key: str
    category: RecurringExpenseCategory
    label: str
    amount_cents: int
    utility_type: UtilityType | Literal[""]
    includes_internet: bool
    includes_cable: bool
