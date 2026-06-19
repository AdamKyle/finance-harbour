from django.test import TestCase

from authentication.models import User
from debt_profile.models import DebtProfile, MonthlyExpense
from onboarding.services.onboarding_readiness import check_onboarding_readiness


class OnboardingReadinessServiceTest(TestCase):
    def test_returns_not_ready_when_no_debt_profile(self) -> None:
        user = User.objects.create_user(email="noready_noprofile@example.com", password="StrongPassword123!")

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "Debt profile is required.")

    def test_returns_not_ready_when_no_debts(self) -> None:
        user = User.objects.create_user(email="noready_nodebts@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[],
        )

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "At least one debt is required.")

    def test_returns_not_ready_when_income_amount_is_zero(self) -> None:
        user = User.objects.create_user(email="noready_zeroincome@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=0,
            pay_period_type="WEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "Income information is required.")

    def test_returns_not_ready_when_pay_period_type_is_blank(self) -> None:
        user = User.objects.create_user(email="noready_nopayperiod@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "Income information is required.")

    def test_returns_not_ready_when_no_monthly_expense_record(self) -> None:
        user = User.objects.create_user(email="noready_noexpenses@example.com", password="StrongPassword123!")
        DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "Monthly expenses are required.")

    def test_returns_not_ready_when_expense_record_has_all_zero_common_fields_and_no_misc(self) -> None:
        user = User.objects.create_user(email="noready_zeroexpenses@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            rent_or_mortgage_cents=0,
            water_cents=0,
            electricity_cents=0,
            food_cents=0,
            internet_cents=0,
            phone_cents=0,
            car_payment_cents=0,
            insurance_cents=0,
            misc_expenses=[],
        )

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)

    def test_not_ready_reason_is_at_least_one_monthly_expense_required_when_no_real_expense(self) -> None:
        user = User.objects.create_user(email="noready_reasonexpenses@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="MONTHLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(debt_profile=debt_profile, misc_expenses=[])

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "At least one monthly expense is required.")

    def test_returns_not_ready_when_misc_expenses_contains_only_zero_amount(self) -> None:
        user = User.objects.create_user(email="noready_zeromisc@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="WEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            misc_expenses=[{"label": "Gym", "amount_cents": 0}],
        )

        result = check_onboarding_readiness(user)

        self.assertFalse(result.ready)

    def test_returns_ready_when_one_common_expense_field_is_greater_than_zero(self) -> None:
        user = User.objects.create_user(email="ready_commonexpense@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=300000,
            pay_period_type="MONTHLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(debt_profile=debt_profile, rent_or_mortgage_cents=150000)

        result = check_onboarding_readiness(user)

        self.assertTrue(result.ready)
        self.assertIsNone(result.reason)

    def test_returns_ready_when_one_misc_expense_has_amount_cents_greater_than_zero(self) -> None:
        user = User.objects.create_user(email="ready_miscexpense@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(
            debt_profile=debt_profile,
            misc_expenses=[{"label": "Gym", "amount_cents": 5000}],
        )

        result = check_onboarding_readiness(user)

        self.assertTrue(result.ready)
        self.assertIsNone(result.reason)

    def test_profile_step_is_not_required_for_readiness(self) -> None:
        user = User.objects.create_user(email="ready_noprofile@example.com", password="StrongPassword123!")
        debt_profile = DebtProfile.objects.create(
            user=user,
            income_per_pay_period_cents=150000,
            pay_period_type="WEEKLY",
            debts=[
                {
                    "label": "Card",
                    "current_balance_cents": 100000,
                    "interest_rate_basis_points": 2000,
                    "minimum_payment_cents": 5000,
                    "current_payment_cents": 5000,
                }
            ],
        )
        MonthlyExpense.objects.create(debt_profile=debt_profile, food_cents=60000)

        result = check_onboarding_readiness(user)

        self.assertTrue(result.ready)
