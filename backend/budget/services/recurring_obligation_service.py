from uuid import uuid4

from django.db import transaction
from rest_framework.exceptions import ValidationError

from authentication.models import User
from budget.models import BudgetPayPeriod
from budget.services.budget_forward_regeneration_service import regenerate_budget_from_pay_period
from budget.services.payday_development_date_service import resolve_payday_effective_date
from budget.structures import RecurringObligationResult
from debt_profile.models import (
    DebtProfile,
    ExpensePaymentSchedule,
    RecurringExpense,
    RecurringExpenseCategory,
    RequiredExpense,
)


@transaction.atomic
def create_recurring_obligation(user: User, validated_data: dict[str, object]) -> RecurringObligationResult:
    debt_profile = DebtProfile.objects.select_for_update().get(user=user)
    effective_date = resolve_payday_effective_date(user)
    first_period = (
        BudgetPayPeriod.objects.select_for_update()
        .filter(plan__user=user, pay_date__gte=effective_date)
        .order_by("sequence")
        .first()
    )

    if first_period is None:
        raise ValidationError({"budget": ["No future budget period is available for this payment."]})

    kind = str(validated_data["kind"])
    label = str(validated_data["label"]).strip()

    if kind == "BILL":
        source_key = f"misc:{uuid4()}"
        amount_cents = int(validated_data["amount_cents"])
        RecurringExpense.objects.create(
            debt_profile=debt_profile,
            source_key=source_key,
            category=RecurringExpenseCategory.MISC,
            label=label,
            amount_cents=amount_cents,
        )
    else:
        source_key = f"debt:{len(debt_profile.debts)}"
        amount_cents = int(validated_data["current_payment_cents"])
        debt_profile.debts = [
            *debt_profile.debts,
            {
                "label": label,
                "current_balance_cents": int(validated_data["current_balance_cents"]),
                "minimum_payment_cents": int(validated_data["minimum_payment_cents"]),
                "current_payment_cents": amount_cents,
            },
        ]
        debt_profile.save(update_fields=["debts", "updated_at"])

    schedule = validated_data["payment_schedule"]
    ExpensePaymentSchedule.objects.create(
        debt_profile=debt_profile,
        source_key=source_key,
        timing=schedule["timing"],
        paycheck_position=schedule["paycheck_position"] or "",
        day_of_month=schedule["day_of_month"],
        auto_deducted=schedule["auto_deducted"],
    )

    if validated_data["is_required"] is True:
        RequiredExpense.objects.create(
            debt_profile=debt_profile,
            source_key=source_key,
            title=label,
            amount_cents=amount_cents,
        )

    regenerated_period = regenerate_budget_from_pay_period(
        user,
        first_period.id,
        first_period.pay_date,
        cadence_anchor=debt_profile.next_pay_date,
    )

    return RecurringObligationResult(
        kind=kind,
        source_key=source_key,
        first_effective_budget_period_id=regenerated_period.id,
    )
