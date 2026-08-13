from dataclasses import dataclass

from authentication.models import User
from debt_profile.models import DebtProfile


@dataclass
class OnboardingReadinessResult:
    ready: bool
    reason: str | None = None


def check_onboarding_readiness(user: User) -> OnboardingReadinessResult:
    try:
        debt_profile = DebtProfile.objects.get(user=user)
    except DebtProfile.DoesNotExist:
        return OnboardingReadinessResult(ready=False, reason="Debt profile is required.")

    if not debt_profile.debts:
        return OnboardingReadinessResult(ready=False, reason="At least one debt is required.")

    if not debt_profile.income_per_pay_period_cents or not debt_profile.pay_period_type:
        return OnboardingReadinessResult(ready=False, reason="Income information is required.")

    if not debt_profile.next_pay_date:
        return OnboardingReadinessResult(ready=False, reason="Next pay date is required.")

    if not debt_profile.recurring_expenses.filter(amount_cents__gt=0).exists():
        return OnboardingReadinessResult(ready=False, reason="At least one monthly expense is required.")

    return OnboardingReadinessResult(ready=True)
