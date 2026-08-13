from rest_framework import serializers

from budget.models import BudgetLineItem


class BudgetLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetLineItem
        fields = [
            "id",
            "source_type",
            "source_key",
            "title",
            "amount_cents",
            "display_order",
            "is_required",
            "is_split",
            "is_manual_override",
            "is_auto_deducted",
            "funded_amount_cents",
            "shortfall_cents",
            "payment_review_status",
            "actual_amount_cents",
            "scheduled_amount_cents",
            "payment_reconciled_at",
            "paid_at",
            "expected_payment_date",
            "payment_timing",
            "paycheck_position",
        ]
        read_only_fields = fields
