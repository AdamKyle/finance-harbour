from django.db import models


class RequiredExpense(models.Model):
    debt_profile = models.ForeignKey(
        "debt_profile.DebtProfile",
        on_delete=models.CASCADE,
        related_name="required_expenses",
    )
    source_key = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    amount_cents = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["debt_profile", "source_key"],
                name="unique_required_expense_source_per_debt_profile",
            ),
        ]

    def __str__(self) -> str:
        return f"RequiredExpense({self.debt_profile_id}, {self.source_key})"
