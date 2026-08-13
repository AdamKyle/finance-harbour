from authentication.models import User
from debt_profile.models import DebtProfile


def get_or_create_debt_profile(user: User) -> DebtProfile:
    debt_profile, _ = DebtProfile.objects.get_or_create(
        user=user,
        defaults={
            "income_per_pay_period_cents": 0,
            "pay_period_type": "",
            "debts": [],
        },
    )

    return debt_profile
