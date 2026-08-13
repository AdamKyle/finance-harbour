from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from budget.enums import BudgetValueField
from budget.models import BudgetLineItem, BudgetPayPeriod
from budget.services import regenerate_budget_from_pay_period, update_budget_value
from budget.structure_serializers.budget_pay_period_serializer import BudgetPayPeriodSerializer
from budget.views.request_validators import BudgetValueUpdateRequest


class BudgetValueUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, period_id: int) -> Response:
        update_request = BudgetValueUpdateRequest(request.data)
        update_request.validate()
        validated_data = update_request.validated_data

        try:
            if validated_data["field"] == BudgetValueField.PAY_DATE:
                period = regenerate_budget_from_pay_period(
                    user=request.user,
                    period_id=period_id,
                    new_pay_date=validated_data["pay_date"],
                )
            else:
                period = update_budget_value(
                    user=request.user,
                    period_id=period_id,
                    field=validated_data["field"],
                    amount_cents=validated_data["amount_cents"],
                    going_forward=validated_data["going_forward"],
                    source_key=validated_data.get("source_key"),
                )
        except (BudgetPayPeriod.DoesNotExist, BudgetLineItem.DoesNotExist) as error:
            raise Http404 from error

        period.refresh_from_db()
        previous_pay_date = (
            BudgetPayPeriod.objects.filter(plan=period.plan, sequence__lt=period.sequence)
            .order_by("-sequence")
            .values_list("pay_date", flat=True)
            .first()
        )
        period._previous_pay_date = previous_pay_date
        serializer = BudgetPayPeriodSerializer(period)

        return Response(serializer.data, status=status.HTTP_200_OK)
