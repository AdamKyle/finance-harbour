from django.db import models

from budget.models import BudgetLineItem, BudgetPayPeriod, PaymentReviewStatus
from budget.types import PaydayWarning, PaydayWarningSeverity, PaydayWarningType


def build_recalculation_warnings(periods: list[BudgetPayPeriod]) -> list[PaydayWarning]:
    warnings: list[PaydayWarning] = []
    missed_important_titles: dict[int, list[str]] = {}
    missed_rows = (
        BudgetLineItem.objects.filter(pay_period__in=periods, is_required=True)
        .filter(
            models.Q(payment_review_status=PaymentReviewStatus.NOT_PAID)
            | models.Q(
                payment_review_status=PaymentReviewStatus.PAID,
                actual_amount_cents__lt=models.F("amount_cents"),
            )
        )
        .values_list("pay_period_id", "title")
    )

    for pay_period_id, title in missed_rows:
        missed_important_titles.setdefault(pay_period_id, []).append(title)

    for period in periods:
        if period.has_negative_left_over:
            warnings.append(
                PaydayWarning(
                    warning_type=PaydayWarningType.NEGATIVE_LEFT_OVER,
                    affected_period_id=period.id,
                    affected_pay_date=period.pay_date,
                    amount_cents=period.left_over_cents,
                    important_titles=[],
                    severity=PaydayWarningSeverity.DANGER,
                )
            )

        if period.has_missed_important_expenses:
            important_titles = missed_important_titles.get(period.id, [])
            warnings.append(
                PaydayWarning(
                    warning_type=PaydayWarningType.IMPORTANT_PAYMENT_MISSED_OR_UNDERPAID,
                    affected_period_id=period.id,
                    affected_pay_date=period.pay_date,
                    amount_cents=None,
                    important_titles=important_titles,
                    severity=PaydayWarningSeverity.DANGER,
                )
            )

        if period.affects_important_expenses and not period.has_missed_important_expenses:
            warnings.append(
                PaydayWarning(
                    warning_type=PaydayWarningType.IMPORTANT_EXPENSE_AFFECTED,
                    affected_period_id=period.id,
                    affected_pay_date=period.pay_date,
                    amount_cents=None,
                    important_titles=[],
                    severity=PaydayWarningSeverity.DANGER,
                )
            )

        if period.is_below_warning_threshold:
            warnings.append(
                PaydayWarning(
                    warning_type=PaydayWarningType.WARNING_THRESHOLD_CROSSED,
                    affected_period_id=period.id,
                    affected_pay_date=period.pay_date,
                    amount_cents=period.left_over_cents,
                    important_titles=[],
                    severity=PaydayWarningSeverity.WARNING,
                )
            )

    return warnings
