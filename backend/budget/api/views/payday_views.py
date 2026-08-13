from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from budget.models import BudgetLineItem, BudgetPayPeriod
from budget.services.payday_detail_service import get_payday_detail
from budget.services.payday_development_date_service import resolve_payday_effective_date
from budget.services.payday_queue_service import get_payday_queue
from budget.services.payday_reconciliation_service import (
    mark_payday_incomplete,
    update_debt_balance,
    update_line_item,
    update_pay_cheque,
)
from budget.structure_serializers.payday_detail_serializer import PaydayDetailSerializer
from budget.structure_serializers.payday_mutation_response_serializer import PaydayMutationResponseSerializer
from budget.structure_serializers.payday_queue_serializer import PaydayQueueSerializer
from budget.views.request_validators import (
    PaydayDebtBalanceUpdateRequest,
    PaydayLineItemUpdateRequest,
    PaydayPayChequeUpdateRequest,
)


class PaydayQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        queue = get_payday_queue(request.user)
        serializer = PaydayQueueSerializer(queue)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PaydayDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, period_id: int) -> Response:
        effective_date = resolve_payday_effective_date(request.user)

        try:
            detail = get_payday_detail(request.user, period_id, effective_date)
        except BudgetPayPeriod.DoesNotExist as error:
            raise Http404 from error

        serializer = PaydayDetailSerializer(detail)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PaydayPayChequeUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, period_id: int) -> Response:
        update_request = PaydayPayChequeUpdateRequest(request.data)
        update_request.validate()
        effective_date = resolve_payday_effective_date(request.user)

        try:
            period, warnings, affected_pay_period_ids = update_pay_cheque(
                request.user,
                period_id,
                effective_date=effective_date,
                **update_request.validated_data,
            )
        except BudgetPayPeriod.DoesNotExist as error:
            raise Http404 from error

        serializer = PaydayMutationResponseSerializer(
            {
                "pay_period": period,
                "warnings": warnings,
                "affected_pay_period_ids": affected_pay_period_ids,
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class PaydayLineItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, period_id: int, line_item_id: int) -> Response:
        update_request = PaydayLineItemUpdateRequest(request.data)
        update_request.validate()
        effective_date = resolve_payday_effective_date(request.user)

        try:
            period, warnings, affected_pay_period_ids = update_line_item(
                request.user,
                period_id,
                line_item_id,
                effective_date=effective_date,
                **update_request.validated_data,
            )
        except (BudgetPayPeriod.DoesNotExist, BudgetLineItem.DoesNotExist) as error:
            raise Http404 from error

        serializer = PaydayMutationResponseSerializer(
            {
                "pay_period": period,
                "warnings": warnings,
                "affected_pay_period_ids": affected_pay_period_ids,
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class PaydayDebtBalanceUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, period_id: int) -> Response:
        update_request = PaydayDebtBalanceUpdateRequest(request.data)
        update_request.validate()
        effective_date = resolve_payday_effective_date(request.user)

        try:
            period, affected_pay_period_ids = update_debt_balance(
                request.user,
                period_id,
                effective_date=effective_date,
                **update_request.validated_data,
            )
        except (BudgetPayPeriod.DoesNotExist, BudgetLineItem.DoesNotExist) as error:
            raise Http404 from error

        serializer = PaydayMutationResponseSerializer(
            {
                "pay_period": period,
                "warnings": [],
                "affected_pay_period_ids": affected_pay_period_ids,
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class PaydayMarkIncompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, period_id: int) -> Response:
        effective_date = resolve_payday_effective_date(request.user)

        try:
            period, affected_pay_period_ids = mark_payday_incomplete(
                request.user,
                period_id,
                effective_date,
            )
        except BudgetPayPeriod.DoesNotExist as error:
            raise Http404 from error
        except ValueError:
            return Response(
                {"detail": "Only unresolved past paydays can be marked incomplete."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PaydayMutationResponseSerializer(
            {
                "pay_period": period,
                "warnings": [],
                "affected_pay_period_ids": affected_pay_period_ids,
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
