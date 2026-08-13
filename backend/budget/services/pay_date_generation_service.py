import calendar
import datetime

from debt_profile.models import DebtProfile


def generate_pay_dates(
    anchor: datetime.date,
    pay_period_type: str,
    end_date: datetime.date,
) -> list[datetime.date]:
    dates: list[datetime.date] = []
    current = anchor

    while current < end_date:
        dates.append(current)

        if pay_period_type == DebtProfile.PayPeriodType.WEEKLY:
            current += datetime.timedelta(days=7)
        elif pay_period_type == DebtProfile.PayPeriodType.BIWEEKLY:
            current += datetime.timedelta(days=14)
        else:
            current = advance_monthly_pay_date(current, anchor.day)

    return dates


def advance_monthly_pay_date(date: datetime.date, anchor_day: int) -> datetime.date:
    month = date.month + 1
    year = date.year

    if month > 12:
        month = 1
        year += 1

    maximum_day = calendar.monthrange(year, month)[1]

    return datetime.date(year, month, min(anchor_day, maximum_day))
