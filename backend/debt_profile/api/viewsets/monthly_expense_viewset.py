from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.services.debt_profile_service import get_or_create_debt_profile
from debt_profile.services.expense_payment_schedule_service import replace_monthly_expense_payment_schedules
from debt_profile.services.recurring_expense_service import replace_recurring_expenses
from debt_profile.structure_serializers.monthly_expense_response_serializer import MonthlyExpenseResponseSerializer
from debt_profile.views.request_validators import MonthlyExpensePatchRequest


class MonthlyExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        debt_profile = get_or_create_debt_profile(request.user)
        serializer = MonthlyExpenseResponseSerializer(debt_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request: Request) -> Response:
        debt_profile = get_or_create_debt_profile(request.user)
        monthly_expense_request = MonthlyExpensePatchRequest(request.data)
        monthly_expense_request.validate()
        monthly_expense_request.validate_schedule_sources(debt_profile)
        data = monthly_expense_request.validated_data

        recurring_expenses = monthly_expense_request.recurring_expenses

        if isinstance(recurring_expenses, list):
            replace_recurring_expenses(debt_profile, recurring_expenses)

        payment_schedules = data.get("payment_schedules")

        if isinstance(payment_schedules, list):
            replace_monthly_expense_payment_schedules(debt_profile, payment_schedules)

        read_serializer = MonthlyExpenseResponseSerializer(debt_profile)

        return Response(read_serializer.data, status=status.HTTP_200_OK)
