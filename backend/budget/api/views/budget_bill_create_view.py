from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from budget.models import BudgetPayPeriod
from budget.services import add_budget_bill
from budget.structure_serializers.budget_pay_period_serializer import BudgetPayPeriodSerializer
from budget.views.request_validators import BudgetBillCreateRequest


class BudgetBillCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, period_id: int) -> Response:
        create_request = BudgetBillCreateRequest(request.data)
        create_request.validate()
        validated_data = create_request.validated_data

        try:
            period = add_budget_bill(
                user=request.user,
                period_id=period_id,
                title=validated_data["title"],
                amount_cents=validated_data["amount_cents"],
                is_required=validated_data["is_required"],
                going_forward=validated_data["going_forward"],
            )
        except BudgetPayPeriod.DoesNotExist as error:
            raise Http404 from error

        period.refresh_from_db()
        serializer = BudgetPayPeriodSerializer(period)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
