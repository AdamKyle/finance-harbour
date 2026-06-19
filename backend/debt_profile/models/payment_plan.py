from django.db import models


class PaymentPlan(models.Model):
    debt_profile = models.OneToOneField(
        "debt_profile.DebtProfile",
        on_delete=models.CASCADE,
        related_name="payment_plan",
    )
    extra_payment_cents = models.PositiveIntegerField(default=0)
    spending_payment_percentage_basis_points = models.PositiveIntegerField(default=0)
    plan_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"PaymentPlan({self.debt_profile_id})"
