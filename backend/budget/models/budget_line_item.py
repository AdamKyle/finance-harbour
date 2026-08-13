from django.db import models

from debt_profile.models.expense_payment_schedule import ExpensePaymentTiming, PaycheckPosition


class SourceType(models.TextChoices):
    RENT_OR_MORTGAGE = "rent_or_mortgage", "Rent or Mortgage"
    DEBT = "debt", "Debt"
    STANDARD_EXPENSE = "standard_expense", "Standard Monthly Expense"
    MISC_EXPENSE = "misc_expense", "Miscellaneous Monthly Expense"
    MANUAL_EXPENSE = "manual_expense", "Manual Expense"


class PaymentReviewStatus(models.TextChoices):
    UNREVIEWED = "UNREVIEWED", "Unreviewed"
    PAID = "PAID", "Paid"
    NOT_PAID = "NOT_PAID", "Not paid"
    UNKNOWN = "UNKNOWN", "Unknown"
    SCHEDULED = "SCHEDULED", "Scheduled"


class BudgetLineItem(models.Model):
    pay_period = models.ForeignKey(
        "budget.BudgetPayPeriod",
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
    )
    source_key = models.CharField(max_length=150)
    title = models.CharField(max_length=200)
    amount_cents = models.IntegerField()
    display_order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    is_split = models.BooleanField(default=False)
    is_manual_override = models.BooleanField(default=False)
    is_auto_deducted = models.BooleanField(default=False)
    funded_amount_cents = models.PositiveIntegerField(default=0)
    shortfall_cents = models.PositiveIntegerField(default=0)
    payment_review_status = models.CharField(
        max_length=20,
        choices=PaymentReviewStatus.choices,
        default=PaymentReviewStatus.UNREVIEWED,
    )
    actual_amount_cents = models.PositiveIntegerField(null=True, blank=True)
    scheduled_amount_cents = models.PositiveIntegerField(null=True, blank=True)
    payment_reconciled_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    expected_payment_date = models.DateField(null=True, blank=True)
    payment_timing = models.CharField(
        max_length=20,
        choices=ExpensePaymentTiming.choices,
        blank=True,
        default="",
    )
    paycheck_position = models.CharField(
        max_length=10,
        choices=PaycheckPosition.choices,
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pay_period", "source_key"],
                name="unique_budget_line_item_source_per_period",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        payment_review_status=PaymentReviewStatus.PAID,
                        actual_amount_cents__isnull=False,
                        scheduled_amount_cents__isnull=True,
                    )
                    | models.Q(
                        payment_review_status=PaymentReviewStatus.NOT_PAID,
                        actual_amount_cents=0,
                        scheduled_amount_cents__isnull=True,
                    )
                    | models.Q(
                        payment_review_status__in=[
                            PaymentReviewStatus.UNKNOWN,
                            PaymentReviewStatus.UNREVIEWED,
                        ],
                        actual_amount_cents__isnull=True,
                        scheduled_amount_cents__isnull=True,
                    )
                    | models.Q(
                        payment_review_status=PaymentReviewStatus.SCHEDULED,
                        actual_amount_cents__isnull=True,
                        scheduled_amount_cents__isnull=False,
                        payment_timing=ExpensePaymentTiming.DAY_OF_MONTH,
                        expected_payment_date__isnull=False,
                    )
                ),
                name="budget_line_item_actual_matches_review_status",
            ),
            models.CheckConstraint(
                condition=models.Q(actual_amount_cents__isnull=True) | models.Q(actual_amount_cents__gte=0),
                name="budget_line_item_actual_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(scheduled_amount_cents__isnull=True) | models.Q(scheduled_amount_cents__gte=0),
                name="budget_line_item_scheduled_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(funded_amount_cents__gte=0),
                name="budget_line_item_funded_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(shortfall_cents__gte=0),
                name="budget_line_item_shortfall_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["pay_period", "display_order"]),
        ]

    def __str__(self) -> str:
        return f"BudgetLineItem({self.pay_period_id}, {self.source_key})"
