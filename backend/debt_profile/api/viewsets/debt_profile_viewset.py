from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.models import DebtProfile
from debt_profile.structure_serializers.debt_profile_serializer import DebtProfileSerializer
from debt_profile.views.request_validators import DebtProfilePatchRequest


class DebtProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        debt_profile, _ = DebtProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "income_per_pay_period_cents": 0,
                "pay_period_type": "",
                "debts": [],
            },
        )

        serializer = DebtProfileSerializer(debt_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        debt_profile, _ = DebtProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "income_per_pay_period_cents": 0,
                "pay_period_type": "",
                "debts": [],
            },
        )

        debt_profile_request = DebtProfilePatchRequest(request.data)
        debt_profile_request.validate()
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

        if update_fields:
            debt_profile.save(update_fields=update_fields)

        read_serializer = DebtProfileSerializer(debt_profile)

        return Response(read_serializer.data, status=status.HTTP_200_OK)
