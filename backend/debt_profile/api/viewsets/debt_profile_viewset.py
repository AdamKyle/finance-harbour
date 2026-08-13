from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.services.debt_profile_service import get_or_create_debt_profile
from debt_profile.services.expense_payment_schedule_service import replace_debt_payment_schedules
from debt_profile.structure_serializers.debt_profile_serializer import DebtProfileSerializer
from debt_profile.views.request_validators import DebtProfilePatchRequest


class DebtProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        debt_profile = get_or_create_debt_profile(request.user)

        serializer = DebtProfileSerializer(debt_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request: Request) -> Response:
        debt_profile = get_or_create_debt_profile(request.user)

        debt_profile_request = DebtProfilePatchRequest(request.data)
        debt_profile_request.validate()
        debt_profile_request.validate_schedule_positions(debt_profile.pay_period_type)
        data = debt_profile_request.validated_data

        update_fields: list[str] = []

        if "income_per_pay_period_cents" in data:
            income = data["income_per_pay_period_cents"]
            if isinstance(income, int):
                debt_profile.income_per_pay_period_cents = income
                update_fields.append("income_per_pay_period_cents")

        if "pay_period_type" in data:
            pay_period_type = data["pay_period_type"]
            if isinstance(pay_period_type, str):
                debt_profile.pay_period_type = pay_period_type
                update_fields.append("pay_period_type")

        if "debts" in data:
            debts = data["debts"]
            if isinstance(debts, list):
                debt_profile.debts = [dict(entry) for entry in debts]
                update_fields.append("debts")

        if "next_pay_date" in data:
            debt_profile.next_pay_date = data["next_pay_date"]
            update_fields.append("next_pay_date")

        if update_fields:
            debt_profile.save(update_fields=update_fields)

        payment_schedules = data.get("payment_schedules")

        if isinstance(payment_schedules, list):
            replace_debt_payment_schedules(debt_profile, payment_schedules)

        read_serializer = DebtProfileSerializer(debt_profile)

        return Response(read_serializer.data, status=status.HTTP_200_OK)
