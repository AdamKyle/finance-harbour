from __future__ import annotations

from typing import TYPE_CHECKING

from debt_profile.models import (
    DebtProfile,
    ExpensePaymentTiming,
    PaycheckPosition,
)

if TYPE_CHECKING:
    from debt_profile.types import ExpensePaymentScheduleDefinition


VALID_POSITIONS_BY_PAY_PERIOD = {
    DebtProfile.PayPeriodType.MONTHLY: {PaycheckPosition.FIRST},
    DebtProfile.PayPeriodType.BIWEEKLY: {
        PaycheckPosition.FIRST,
        PaycheckPosition.SECOND,
        PaycheckPosition.LAST,
    },
    DebtProfile.PayPeriodType.WEEKLY: set(PaycheckPosition.values),
}


def validate_schedule_positions(
    schedules: list[ExpensePaymentScheduleDefinition],
    pay_period_type: str,
) -> bool:
    valid_positions = VALID_POSITIONS_BY_PAY_PERIOD.get(pay_period_type, set())

    for schedule in schedules:
        if schedule["timing"] != ExpensePaymentTiming.PAYCHECK_POSITION:
            continue

        if schedule["paycheck_position"] not in valid_positions:
            return False

    return True
