import datetime

from rest_framework import serializers

from budget.models import BudgetPlan


class OnboardingCompletionResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    budget_plan_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    @classmethod
    def from_plan(cls, plan: BudgetPlan) -> dict[str, str | int | datetime.date]:
        return {
            "detail": "Onboarding complete.",
            "budget_plan_id": plan.pk,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
        }
