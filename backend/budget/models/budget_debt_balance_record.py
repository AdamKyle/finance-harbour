from django.db import models


class DebtBalanceReviewStatus(models.TextChoices):
    UNREVIEWED = "UNREVIEWED", "Unreviewed"
    CONFIRMED = "CONFIRMED", "Confirmed"
    UNKNOWN = "UNKNOWN", "Unknown"


class BudgetDebtBalanceRecord(models.Model):
    pay_period = models.ForeignKey(
        "budget.BudgetPayPeriod",
        on_delete=models.CASCADE,
        related_name="debt_balance_records",
    )
    source_key = models.CharField(max_length=150)
    title = models.CharField(max_length=200)
    review_status = models.CharField(max_length=20, choices=DebtBalanceReviewStatus.choices)
    actual_balance_cents = models.PositiveIntegerField(null=True, blank=True)
    reconciled_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pay_period", "source_key"],
                name="unique_budget_debt_balance_per_period_source",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        review_status=DebtBalanceReviewStatus.CONFIRMED,
                        actual_balance_cents__isnull=False,
                    )
                    | models.Q(
                        review_status=DebtBalanceReviewStatus.UNKNOWN,
                        actual_balance_cents__isnull=True,
                    )
                ),
                name="budget_debt_balance_actual_matches_review_status",
            ),
            models.CheckConstraint(
                condition=models.Q(actual_balance_cents__isnull=True) | models.Q(actual_balance_cents__gte=0),
                name="budget_debt_balance_actual_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"BudgetDebtBalanceRecord({self.pay_period_id}, {self.source_key})"
