from django.db import models


class RecurringExpenseCategory(models.TextChoices):
    RENT_OR_MORTGAGE = "RENT_OR_MORTGAGE", "Rent or mortgage"
    UTILITIES = "UTILITIES", "Utilities"
    FOOD = "FOOD", "Food"
    INTERNET = "INTERNET", "Internet"
    PHONE = "PHONE", "Phone"
    CAR_PAYMENT = "CAR_PAYMENT", "Car payment"
    INSURANCE = "INSURANCE", "Insurance"
    MISC = "MISC", "Other"


class UtilityType(models.TextChoices):
    ELECTRICITY = "ELECTRICITY", "Electricity"
    WATER = "WATER", "Water"
    WATER_AND_ELECTRICITY = "WATER_AND_ELECTRICITY", "Water + electricity"
    UTILITIES = "UTILITIES", "Utilities"
    CUSTOM = "CUSTOM", "Custom"


class RecurringExpense(models.Model):
    debt_profile = models.ForeignKey(
        "debt_profile.DebtProfile",
        on_delete=models.CASCADE,
        related_name="recurring_expenses",
    )
    source_key = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=RecurringExpenseCategory.choices)
    label = models.CharField(max_length=150)
    amount_cents = models.PositiveIntegerField()
    utility_type = models.CharField(max_length=30, choices=UtilityType.choices, blank=True, default="")
    includes_internet = models.BooleanField(default=False)
    includes_cable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["debt_profile", "source_key"],
                name="unique_recurring_expense_source_per_profile",
            ),
            models.CheckConstraint(
                condition=models.Q(amount_cents__gte=0),
                name="recurring_expense_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(category=RecurringExpenseCategory.UTILITIES, utility_type__gt="")
                    | ~models.Q(category=RecurringExpenseCategory.UTILITIES)
                ),
                name="utility_expense_requires_type",
            ),
            models.CheckConstraint(
                condition=(~models.Q(utility_type=UtilityType.CUSTOM) | models.Q(label__gt="")),
                name="custom_utility_requires_label",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(category=RecurringExpenseCategory.UTILITIES)
                    | models.Q(utility_type="", includes_internet=False, includes_cable=False)
                ),
                name="included_services_belong_to_utilities",
            ),
        ]

    def __str__(self) -> str:
        return f"RecurringExpense({self.debt_profile_id}, {self.source_key})"
