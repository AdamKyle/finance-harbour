import datetime

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from budget.models import (
    BudgetPayPeriod,
    DebtBalanceReviewStatus,
    PayChequeReviewStatus,
    PaymentReviewStatus,
)
from budget.services.payday_reconciliation_service import validate_unknown_eligibility


class PaydayUnknownEligibilityServiceTest(SimpleTestCase):
    def test_past_pay_cheque_unknown_is_allowed(self) -> None:
        period = BudgetPayPeriod(pay_date=datetime.date(2026, 8, 1))

        validate_unknown_eligibility(
            period,
            PayChequeReviewStatus.UNKNOWN,
            datetime.date(2026, 8, 2),
        )

    def test_current_pay_cheque_unknown_is_rejected(self) -> None:
        period = BudgetPayPeriod(pay_date=datetime.date(2026, 8, 1))

        with self.assertRaises(ValidationError):
            validate_unknown_eligibility(
                period,
                PayChequeReviewStatus.UNKNOWN,
                datetime.date(2026, 8, 1),
            )

    def test_current_line_item_unknown_is_rejected(self) -> None:
        period = BudgetPayPeriod(pay_date=datetime.date(2026, 8, 1))

        with self.assertRaises(ValidationError):
            validate_unknown_eligibility(
                period,
                PaymentReviewStatus.UNKNOWN,
                datetime.date(2026, 8, 1),
            )

    def test_current_debt_balance_unknown_is_rejected(self) -> None:
        period = BudgetPayPeriod(pay_date=datetime.date(2026, 8, 1))

        with self.assertRaises(ValidationError):
            validate_unknown_eligibility(
                period,
                DebtBalanceReviewStatus.UNKNOWN,
                datetime.date(2026, 8, 1),
            )

    def test_known_current_facts_are_allowed(self) -> None:
        period = BudgetPayPeriod(pay_date=datetime.date(2026, 8, 1))

        validate_unknown_eligibility(
            period,
            PayChequeReviewStatus.CONFIRMED,
            datetime.date(2026, 8, 1),
        )
