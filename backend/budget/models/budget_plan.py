from django.conf import settings
from django.db import models


class BudgetPlan(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budget_plan",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    pay_period_type = models.CharField(max_length=20)
    income_per_pay_period_cents = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"BudgetPlan({self.user_id})"
