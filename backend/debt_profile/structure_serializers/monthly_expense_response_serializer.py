from rest_framework import serializers

from debt_profile.models import DebtProfile
from debt_profile.serializers.expense_payment_schedule_serializer import ExpensePaymentScheduleSerializer
from debt_profile.structure_serializers.recurring_expense_serializer import RecurringExpenseSerializer


class MonthlyExpenseResponseSerializer(serializers.Serializer):
    recurring_expenses = serializers.SerializerMethodField()
    payment_schedules = serializers.SerializerMethodField()

    def get_recurring_expenses(self, instance: DebtProfile) -> list[dict[str, object]]:
        expenses = instance.recurring_expenses.order_by("id")

        return RecurringExpenseSerializer(expenses, many=True).data

    def get_payment_schedules(self, instance: DebtProfile) -> list[dict[str, str | int | bool | None]]:
        schedules = instance.expense_payment_schedules.exclude(source_key__startswith="debt:").order_by("source_key")

        return ExpensePaymentScheduleSerializer(schedules, many=True).data
