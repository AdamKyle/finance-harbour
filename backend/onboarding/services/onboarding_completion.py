import contextlib
from dataclasses import dataclass

from django.db import transaction

from authentication.models import User
from budget.models import BudgetPlan
from budget.services.budget_generator import generate_budget
from debt_profile.models import DebtProfile
from onboarding.models import OnboardingProgress
from onboarding.services.onboarding_readiness import check_onboarding_readiness


@dataclass
class OnboardingCompletionResult:
    success: bool
    plan: BudgetPlan | None = None
    reason: str | None = None


@transaction.atomic
def complete_onboarding(user: User) -> OnboardingCompletionResult:
    locked_user = User.objects.select_for_update().get(pk=user.pk)

    with contextlib.suppress(DebtProfile.DoesNotExist):
        DebtProfile.objects.select_for_update().get(user=locked_user)

    if locked_user.completed_onboarding:
        existing_plan = BudgetPlan.objects.filter(user=locked_user).first()

        if existing_plan:
            return OnboardingCompletionResult(success=True, plan=existing_plan)

        readiness = check_onboarding_readiness(locked_user)

        if not readiness.ready:
            return OnboardingCompletionResult(success=False, reason=readiness.reason)

        plan = generate_budget(locked_user)

        return OnboardingCompletionResult(success=True, plan=plan)

    readiness = check_onboarding_readiness(locked_user)

    if not readiness.ready:
        return OnboardingCompletionResult(success=False, reason=readiness.reason)

    plan = generate_budget(locked_user)

    locked_user.completed_onboarding = True
    locked_user.save(update_fields=["completed_onboarding"])

    progress, _ = OnboardingProgress.objects.get_or_create(user=locked_user)
    progress.is_complete = True
    progress.save(update_fields=["is_complete"])

    return OnboardingCompletionResult(success=True, plan=plan)
