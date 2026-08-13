import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class RecurringObligationConfiguration:
    pay_period_type: str
    representative_date: datetime.date
