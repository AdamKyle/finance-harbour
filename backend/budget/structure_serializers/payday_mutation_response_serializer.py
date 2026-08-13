from rest_framework import serializers

from budget.structure_serializers.budget_pay_period_serializer import BudgetPayPeriodSerializer
from budget.structure_serializers.payday_warning_serializer import PaydayWarningSerializer


class PaydayMutationResponseSerializer(serializers.Serializer):
    pay_period = BudgetPayPeriodSerializer()
    warnings = PaydayWarningSerializer(many=True)
    affected_pay_period_ids = serializers.ListField(child=serializers.IntegerField())
