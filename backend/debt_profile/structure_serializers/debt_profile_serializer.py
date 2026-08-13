from rest_framework import serializers

from debt_profile.models import DebtProfile
from debt_profile.serializers.expense_payment_schedule_serializer import ExpensePaymentScheduleSerializer


class DebtProfileSerializer(serializers.ModelSerializer):
    payment_schedules = serializers.SerializerMethodField()

    def get_payment_schedules(self, instance: DebtProfile) -> list[dict[str, str | int | bool | None]]:
        schedules = instance.expense_payment_schedules.filter(source_key__startswith="debt:").order_by("source_key")

        return ExpensePaymentScheduleSerializer(schedules, many=True).data

    class Meta:
        model = DebtProfile
        fields = ["income_per_pay_period_cents", "pay_period_type", "debts", "next_pay_date", "payment_schedules"]
        read_only_fields = fields
