from django.conf import settings
from django.db import models


class DebtProfile(models.Model):
    class PayPeriodType(models.TextChoices):
        WEEKLY = "WEEKLY", "Weekly"
        BIWEEKLY = "BIWEEKLY", "Bi-weekly"
        MONTHLY = "MONTHLY", "Monthly"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="debt_profile",
    )
    income_per_pay_period_cents = models.PositiveIntegerField(default=0)
    pay_period_type = models.CharField(
        max_length=20,
        choices=PayPeriodType.choices,
        blank=True,
        default="",
    )
    debts = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"DebtProfile({self.user_id})"
