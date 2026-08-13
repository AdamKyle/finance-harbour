import datetime

from django.test import TestCase
from django.utils import timezone

from authentication.models import User
from debt_profile.models import DebtProfile, RecurringExpense, RecurringExpenseCategory
from onboarding.services.onboarding_readiness import check_onboarding_readiness


class OnboardingReadinessServiceTest(TestCase):
    def test_requires_a_positive_normalized_recurring_expense(self) -> None:
        user = User.objects.create_user(email="readiness-empty@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
            next_pay_date=timezone.localdate() + datetime.timedelta(days=7),
        )

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "At least one monthly expense is required.")

    def test_is_ready_with_complete_context_and_a_recurring_expense(self) -> None:
        user = User.objects.create_user(email="readiness-ready@example.com", password="StrongPassword123!")
        profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
            next_pay_date=timezone.localdate() + datetime.timedelta(days=7),
        )
        RecurringExpense.objects.create(
            debt_profile=profile,
            source_key="food",
            category=RecurringExpenseCategory.FOOD,
            label="Food",
            amount_cents=40000,
        )

        result = check_onboarding_readiness(user)

        self.assertTrue(result.ready)
        self.assertIsNone(result.reason)
