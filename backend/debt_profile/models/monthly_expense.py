from django.db import models


class MonthlyExpense(models.Model):
    debt_profile = models.OneToOneField(
        "debt_profile.DebtProfile",
        on_delete=models.CASCADE,
        related_name="monthly_expense",
    )
    rent_or_mortgage_cents = models.PositiveIntegerField(default=0)
    water_cents = models.PositiveIntegerField(default=0)
    electricity_cents = models.PositiveIntegerField(default=0)
    food_cents = models.PositiveIntegerField(default=0)
    internet_cents = models.PositiveIntegerField(default=0)
    phone_cents = models.PositiveIntegerField(default=0)
    car_payment_cents = models.PositiveIntegerField(default=0)
    insurance_cents = models.PositiveIntegerField(default=0)
    misc_expenses = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"MonthlyExpense({self.debt_profile_id})"
