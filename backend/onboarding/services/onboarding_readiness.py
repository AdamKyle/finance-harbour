from dataclasses import dataclass

from authentication.models import User
from debt_profile.models import DebtProfile, MonthlyExpense


@dataclass
class OnboardingReadinessResult:
    ready: bool
    reason: str | None = None


def _has_real_expenses(expense: MonthlyExpense) -> bool:
    common_values = [
        expense.rent_or_mortgage_cents,
        expense.water_cents,
        expense.electricity_cents,
        expense.food_cents,
        expense.internet_cents,
        expense.phone_cents,
        expense.car_payment_cents,
        expense.insurance_cents,
    ]
    if any(v > 0 for v in common_values):
        return True
    return any(entry.get("amount_cents", 0) > 0 for entry in expense.misc_expenses)


def check_onboarding_readiness(user: User) -> OnboardingReadinessResult:
    try:
        debt_profile = DebtProfile.objects.get(user=user)
    except DebtProfile.DoesNotExist:
        return OnboardingReadinessResult(ready=False, reason="Debt profile is required.")

    if not debt_profile.debts:
        return OnboardingReadinessResult(ready=False, reason="At least one debt is required.")

    if not debt_profile.income_per_pay_period_cents or not debt_profile.pay_period_type:
        return OnboardingReadinessResult(ready=False, reason="Income information is required.")

    try:
        expense = MonthlyExpense.objects.get(debt_profile=debt_profile)
    except MonthlyExpense.DoesNotExist:
        return OnboardingReadinessResult(ready=False, reason="Monthly expenses are required.")

    if not _has_real_expenses(expense):
        return OnboardingReadinessResult(ready=False, reason="At least one monthly expense is required.")

    return OnboardingReadinessResult(ready=True)
