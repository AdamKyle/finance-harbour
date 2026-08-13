from typing import TypedDict

from debt_profile.models import ExpensePaymentTiming, PaycheckPosition


class ExpensePaymentScheduleDefinition(TypedDict):
    source_key: str
    timing: ExpensePaymentTiming
    paycheck_position: PaycheckPosition | None
    day_of_month: int | None
    auto_deducted: bool
