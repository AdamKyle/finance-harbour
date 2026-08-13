import datetime

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan
from budget.services.recurring_obligation_service import create_recurring_obligation
from debt_profile.models import DebtProfile, ExpensePaymentSchedule, ExpensePaymentTiming


class RecurringObligationServiceTest(TestCase):
    def test_schedule_constraint_failure_rolls_back_appended_debt(self) -> None:
        user = User.objects.create_user(email="rollback-debt@example.com", password="StrongPassword123!")
        future_pay_date = timezone.localdate() + datetime.timedelta(days=7)
        profile = DebtProfile.objects.create(
            user=user,
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
            next_pay_date=future_pay_date,
            debts=[],
        )
        plan = BudgetPlan.objects.create(
            user=user,
            start_date=future_pay_date,
            end_date=future_pay_date + datetime.timedelta(days=365),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=300000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=future_pay_date,
            pay_cheque_cents=300000,
            total_available_cents=300000,
            left_over_cents=300000,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position="FIRST",
        )

        with self.assertRaises(IntegrityError):
            create_recurring_obligation(
                user,
                {
                    "kind": "DEBT",
                    "label": "Student Loan",
                    "is_required": False,
                    "current_balance_cents": 1200000,
                    "minimum_payment_cents": 10000,
                    "current_payment_cents": 15000,
                    "payment_schedule": {
                        "timing": ExpensePaymentTiming.PAYCHECK_POSITION,
                        "paycheck_position": "FIRST",
                        "day_of_month": None,
                        "auto_deducted": False,
                    },
                },
            )

        profile.refresh_from_db()

        self.assertEqual(profile.debts, [])
