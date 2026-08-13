from django.db import models


class PaydayReconciliationStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not started"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    REVIEWED = "REVIEWED", "Reviewed"
    INCOMPLETE = "INCOMPLETE", "Incomplete"


class PayChequeReviewStatus(models.TextChoices):
    UNREVIEWED = "UNREVIEWED", "Unreviewed"
    CONFIRMED = "CONFIRMED", "Confirmed"
    UNKNOWN = "UNKNOWN", "Unknown"


class BudgetPayPeriod(models.Model):
    plan = models.ForeignKey(
        "budget.BudgetPlan",
        on_delete=models.CASCADE,
        related_name="pay_periods",
    )
    sequence = models.PositiveIntegerField()
    pay_date = models.DateField()
    pay_cheque_cents = models.PositiveIntegerField()
    pay_cheque_is_manual = models.BooleanField(default=False)
    carried_left_over_cents = models.IntegerField(default=0)
    carried_left_over_is_manual = models.BooleanField(default=False)
    total_available_cents = models.IntegerField()
    total_available_is_manual = models.BooleanField(default=False)
    total_bills_cents = models.IntegerField(default=0)
    total_bills_is_manual = models.BooleanField(default=False)
    left_over_cents = models.IntegerField()
    left_over_is_manual = models.BooleanField(default=False)
    has_negative_left_over = models.BooleanField(default=False)
    is_below_warning_threshold = models.BooleanField(default=False)
    has_deferred_items = models.BooleanField(default=False)
    has_deferred_important_expenses = models.BooleanField(default=False)
    affects_important_expenses = models.BooleanField(default=False)
    has_missed_important_expenses = models.BooleanField(default=False)
    payday_reconciliation_status = models.CharField(
        max_length=20,
        choices=PaydayReconciliationStatus.choices,
        default=PaydayReconciliationStatus.NOT_STARTED,
    )
    actual_pay_cheque_cents = models.PositiveIntegerField(null=True, blank=True)
    pay_cheque_review_status = models.CharField(
        max_length=20,
        choices=PayChequeReviewStatus.choices,
        default=PayChequeReviewStatus.UNREVIEWED,
    )
    pay_cheque_reconciled_at = models.DateTimeField(null=True, blank=True)
    payday_reconciliation_started_at = models.DateTimeField(null=True, blank=True)
    payday_reconciliation_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["plan", "sequence"],
                name="unique_budget_pay_period_sequence_per_plan",
            ),
            models.UniqueConstraint(
                fields=["plan", "pay_date"],
                name="unique_budget_pay_period_date_per_plan",
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=0),
                name="budget_pay_period_sequence_non_negative",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        pay_cheque_review_status=PayChequeReviewStatus.CONFIRMED,
                        actual_pay_cheque_cents__isnull=False,
                    )
                    | models.Q(
                        pay_cheque_review_status__in=[
                            PayChequeReviewStatus.UNKNOWN,
                            PayChequeReviewStatus.UNREVIEWED,
                        ],
                        actual_pay_cheque_cents__isnull=True,
                    )
                ),
                name="budget_pay_period_actual_pay_matches_review_status",
            ),
            models.CheckConstraint(
                condition=models.Q(actual_pay_cheque_cents__isnull=True) | models.Q(actual_pay_cheque_cents__gte=0),
                name="budget_pay_period_actual_pay_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["plan", "sequence"]),
        ]
        ordering = ["sequence"]

    def __str__(self) -> str:
        return f"BudgetPayPeriod({self.plan_id}, seq={self.sequence})"
