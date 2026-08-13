import datetime
from dataclasses import dataclass

from debt_profile.models import DebtProfile, PaycheckPosition


@dataclass(frozen=True)
class PayCadencePosition:
    ordinal: PaycheckPosition | None
    is_last: bool

    def matches(self, position: PaycheckPosition) -> bool:
        if position == PaycheckPosition.LAST:
            return self.is_last

        return position == self.ordinal


def get_payday_position(
    payday: datetime.date,
    cadence_anchor: datetime.date,
    pay_period_type: str,
) -> PayCadencePosition:
    if pay_period_type == DebtProfile.PayPeriodType.MONTHLY:
        return PayCadencePosition(ordinal=PaycheckPosition.FIRST, is_last=True)

    cadence_days = 7

    if pay_period_type == DebtProfile.PayPeriodType.BIWEEKLY:
        cadence_days = 14

    cadence_interval = datetime.timedelta(days=cadence_days)
    month_start = payday.replace(day=1)
    current = cadence_anchor

    while current > month_start:
        current -= cadence_interval

    while current < month_start:
        current += cadence_interval

    monthly_paydays: list[datetime.date] = []

    while current.month == payday.month and current.year == payday.year:
        monthly_paydays.append(current)
        current += cadence_interval

    payday_index = monthly_paydays.index(payday)
    ordinals = [
        PaycheckPosition.FIRST,
        PaycheckPosition.SECOND,
        PaycheckPosition.THIRD,
        PaycheckPosition.FOURTH,
    ]
    ordinal = None

    if payday_index < len(ordinals):
        ordinal = ordinals[payday_index]

    return PayCadencePosition(ordinal=ordinal, is_last=payday_index == len(monthly_paydays) - 1)
