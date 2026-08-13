from django.db import models


class ExpensePaymentTiming(models.TextChoices):
    EVERY_PAYCHECK = "EVERY_PAYCHECK", "On every paycheck"
    PAYCHECK_POSITION = "PAYCHECK_POSITION", "On a paycheck position"
    DAY_OF_MONTH = "DAY_OF_MONTH", "On a specific day of the month"


class PaycheckPosition(models.TextChoices):
    FIRST = "FIRST", "First paycheck"
    SECOND = "SECOND", "Second paycheck"
    THIRD = "THIRD", "Third paycheck"
    FOURTH = "FOURTH", "Fourth paycheck"
    LAST = "LAST", "Last paycheck"


class ExpensePaymentSchedule(models.Model):
    debt_profile = models.ForeignKey(
        "debt_profile.DebtProfile",
        on_delete=models.CASCADE,
        related_name="expense_payment_schedules",
    )
    source_key = models.CharField(max_length=150)
    timing = models.CharField(max_length=20, choices=ExpensePaymentTiming.choices)
    paycheck_position = models.CharField(
        max_length=10,
        choices=PaycheckPosition.choices,
        blank=True,
        default="",
    )
    day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    auto_deducted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["debt_profile", "source_key"],
                name="unique_expense_payment_schedule_source",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        timing=ExpensePaymentTiming.EVERY_PAYCHECK,
                        paycheck_position="",
                        day_of_month__isnull=True,
                        auto_deducted=False,
                    )
                    | models.Q(
                        timing=ExpensePaymentTiming.PAYCHECK_POSITION,
                        paycheck_position__gt="",
                        day_of_month__isnull=True,
                        auto_deducted=False,
                    )
                    | models.Q(
                        timing=ExpensePaymentTiming.DAY_OF_MONTH,
                        paycheck_position="",
                        day_of_month__isnull=False,
                        day_of_month__gte=1,
                        day_of_month__lte=31,
                    )
                ),
                name="expense_payment_schedule_timing_fields_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"ExpensePaymentSchedule({self.debt_profile_id}, {self.source_key})"
