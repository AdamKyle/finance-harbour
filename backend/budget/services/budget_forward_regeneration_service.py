import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.models import User
from budget import models
from budget.services.budget_forward_fact_mapping_service import restore_forward_facts, snapshot_forward_facts
from budget.services.budget_generator import build_budget_period_states, create_budget_periods
from budget.services.budget_mutation_service import recalculate_periods
from budget.services.pay_date_generation_service import generate_pay_dates
from debt_profile.models import DebtProfile


@transaction.atomic
def regenerate_budget_from_pay_period(
    user: User,
    period_id: int,
    new_pay_date: datetime.date,
) -> models.BudgetPayPeriod:
    selected_period = (
        models.BudgetPayPeriod.objects.select_for_update()
        .select_related("plan")
        .get(
            id=period_id,
            plan__user=user,
        )
    )
    plan = selected_period.plan
    debt_profile = DebtProfile.objects.select_for_update().get(user=user)
    previous_period = (
        models.BudgetPayPeriod.objects.select_for_update()
        .filter(plan=plan, sequence__lt=selected_period.sequence)
        .order_by("-sequence")
        .first()
    )

    if previous_period is not None and new_pay_date <= previous_period.pay_date:
        raise ValidationError({"pay_date": ["Pay date must be after the previous pay period."]})

    if previous_period is None and new_pay_date < timezone.localdate():
        raise ValidationError({"pay_date": ["Pay date cannot be in the past."]})

    if new_pay_date >= plan.end_date:
        raise ValidationError({"pay_date": ["Pay date must be before the plan end date."]})

    duplicate_exists = (
        models.BudgetPayPeriod.objects.filter(plan=plan, pay_date=new_pay_date).exclude(id=period_id).exists()
    )

    if duplicate_exists:
        raise ValidationError({"pay_date": ["A pay period already exists on this date."]})

    forward_periods = list(
        models.BudgetPayPeriod.objects.select_for_update()
        .filter(plan=plan, sequence__gte=selected_period.sequence)
        .order_by("sequence")
    )
    forward_line_items = list(
        models.BudgetLineItem.objects.filter(pay_period__in=forward_periods).order_by(
            "pay_period__sequence",
            "display_order",
            "id",
        )
    )
    forward_debt_records = list(
        models.BudgetDebtBalanceRecord.objects.filter(pay_period__in=forward_periods).order_by(
            "pay_period__sequence",
            "source_key",
        )
    )
    fact_snapshot = snapshot_forward_facts(
        effective_period=selected_period,
        forward_periods=forward_periods,
        forward_line_items=forward_line_items,
        forward_debt_records=forward_debt_records,
    )

    generated_dates = generate_pay_dates(new_pay_date, plan.pay_period_type, plan.end_date)
    previous_left_over = previous_period.left_over_cents if previous_period is not None else 0

    models.BudgetPayPeriod.objects.filter(plan=plan, sequence__gte=selected_period.sequence).delete()

    if previous_period is None:
        plan.start_date = new_pay_date
        plan.save(update_fields=["start_date", "updated_at"])
        debt_profile.next_pay_date = new_pay_date
        debt_profile.save(update_fields=["next_pay_date", "updated_at"])

    planning_date = new_pay_date

    if previous_period is None:
        planning_date = min(timezone.localdate(), new_pay_date)

    period_states = build_budget_period_states(
        debt_profile=debt_profile,
        pay_dates=generated_dates,
        cadence_anchor=new_pay_date,
        planning_date=planning_date,
    )
    regenerated_periods = create_budget_periods(
        plan=plan,
        debt_profile=debt_profile,
        period_states=period_states,
        starting_sequence=selected_period.sequence,
        carried_left_over_cents=previous_left_over,
        first_period_id=selected_period.id,
    )

    restore_forward_facts(regenerated_periods, fact_snapshot)
    recalculate_periods(regenerated_periods)

    return regenerated_periods[0]
