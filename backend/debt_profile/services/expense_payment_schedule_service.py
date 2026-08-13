from django.db import transaction

from debt_profile.models import DebtProfile, ExpensePaymentSchedule
from debt_profile.types import ExpensePaymentScheduleDefinition


@transaction.atomic
def replace_monthly_expense_payment_schedules(
    debt_profile: DebtProfile,
    schedules: list[ExpensePaymentScheduleDefinition],
) -> None:
    ExpensePaymentSchedule.objects.filter(debt_profile=debt_profile).exclude(source_key__startswith="debt:").delete()
    _create_schedules(debt_profile, schedules)


@transaction.atomic
def replace_debt_payment_schedules(
    debt_profile: DebtProfile,
    schedules: list[ExpensePaymentScheduleDefinition],
) -> None:
    ExpensePaymentSchedule.objects.filter(
        debt_profile=debt_profile,
        source_key__startswith="debt:",
    ).delete()
    _create_schedules(debt_profile, schedules)


def _create_schedules(
    debt_profile: DebtProfile,
    schedules: list[ExpensePaymentScheduleDefinition],
) -> None:
    ExpensePaymentSchedule.objects.bulk_create(
        [
            ExpensePaymentSchedule(
                debt_profile=debt_profile,
                source_key=schedule["source_key"],
                timing=schedule["timing"],
                paycheck_position=schedule["paycheck_position"] or "",
                day_of_month=schedule["day_of_month"],
                auto_deducted=schedule["auto_deducted"],
            )
            for schedule in schedules
        ]
    )
