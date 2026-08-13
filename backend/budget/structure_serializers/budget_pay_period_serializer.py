from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnList

from budget.models import BudgetPayPeriod
from budget.services.payment_completion_service import get_payment_completion
from budget.structure_serializers.budget_line_item_serializer import BudgetLineItemSerializer
from budget.structure_serializers.payday_debt_balance_check_serializer import PaydayDebtBalanceCheckSerializer


class BudgetPayPeriodSerializer(serializers.ModelSerializer):
    line_items = BudgetLineItemSerializer(many=True, read_only=True)
    bill_count = serializers.SerializerMethodField()
    paid_bill_count = serializers.SerializerMethodField()
    scheduled_bill_count = serializers.SerializerMethodField()
    missed_bill_count = serializers.SerializerMethodField()
    payment_completion_percentage = serializers.SerializerMethodField()
    payment_completion_status = serializers.SerializerMethodField()
    debt_balance_checks = serializers.SerializerMethodField()
    previous_pay_date = serializers.DateField(source="_previous_pay_date", read_only=True, allow_null=True)

    def get_bill_count(self, period: BudgetPayPeriod) -> int:
        return get_payment_completion(period).bill_count

    def get_paid_bill_count(self, period: BudgetPayPeriod) -> int:
        return get_payment_completion(period).paid_bill_count

    def get_scheduled_bill_count(self, period: BudgetPayPeriod) -> int:
        return get_payment_completion(period).scheduled_bill_count

    def get_missed_bill_count(self, period: BudgetPayPeriod) -> int:
        return get_payment_completion(period).missed_bill_count

    def get_payment_completion_percentage(self, period: BudgetPayPeriod) -> float | None:
        return get_payment_completion(period).percentage

    def get_payment_completion_status(self, period: BudgetPayPeriod) -> str:
        return get_payment_completion(period).status

    def get_debt_balance_checks(self, period: BudgetPayPeriod) -> ReturnList:
        checks = getattr(period, "_debt_balance_checks", [])

        return PaydayDebtBalanceCheckSerializer(checks, many=True).data

    class Meta:
        model = BudgetPayPeriod
        fields = [
            "id",
            "sequence",
            "pay_date",
            "previous_pay_date",
            "pay_cheque_cents",
            "pay_cheque_is_manual",
            "carried_left_over_cents",
            "carried_left_over_is_manual",
            "total_available_cents",
            "total_available_is_manual",
            "total_bills_cents",
            "total_bills_is_manual",
            "left_over_cents",
            "left_over_is_manual",
            "has_negative_left_over",
            "is_below_warning_threshold",
            "has_deferred_items",
            "affects_important_expenses",
            "has_missed_important_expenses",
            "payday_reconciliation_status",
            "actual_pay_cheque_cents",
            "pay_cheque_review_status",
            "pay_cheque_reconciled_at",
            "payday_reconciliation_started_at",
            "payday_reconciliation_completed_at",
            "line_items",
            "bill_count",
            "paid_bill_count",
            "scheduled_bill_count",
            "missed_bill_count",
            "payment_completion_percentage",
            "payment_completion_status",
            "debt_balance_checks",
        ]
        read_only_fields = fields
