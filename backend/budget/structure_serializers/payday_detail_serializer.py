from rest_framework import serializers

from budget.structure_serializers.budget_pay_period_serializer import BudgetPayPeriodSerializer
from budget.structure_serializers.payday_debt_balance_check_serializer import (
    PaydayDebtBalanceCheckSerializer,
)
from budget.structure_serializers.payday_progress_serializer import PaydayProgressSerializer


class PaydayDetailSerializer(serializers.Serializer):
    pay_period = BudgetPayPeriodSerializer()
    debt_balance_checks = PaydayDebtBalanceCheckSerializer(many=True)
    progress = PaydayProgressSerializer()
