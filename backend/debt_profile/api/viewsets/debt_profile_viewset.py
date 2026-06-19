from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.models import DebtProfile
from debt_profile.serializers.debt_profile_write_serializer import DebtProfileWriteSerializer
from debt_profile.structure_serializers.debt_profile_serializer import DebtProfileSerializer


class DebtProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        debt_profile, _ = DebtProfile.objects.get_or_create(
            user=request.user,
            defaults={"income_per_pay_period_cents": 0, "pay_period_type": "", "debts": []},
        )
        serializer = DebtProfileSerializer(debt_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        debt_profile, _ = DebtProfile.objects.get_or_create(
            user=request.user,
            defaults={"income_per_pay_period_cents": 0, "pay_period_type": "", "debts": []},
        )
        write_serializer = DebtProfileWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        data = write_serializer.validated_data

        update_fields: list[str] = []
        if "income_per_pay_period_cents" in data:
            debt_profile.income_per_pay_period_cents = data["income_per_pay_period_cents"]
            update_fields.append("income_per_pay_period_cents")
        if "pay_period_type" in data:
            debt_profile.pay_period_type = data["pay_period_type"]
            update_fields.append("pay_period_type")
        if "debts" in data:
            debt_profile.debts = [dict(entry) for entry in data["debts"]]
            update_fields.append("debts")

        if update_fields:
            debt_profile.save(update_fields=update_fields)

        read_serializer = DebtProfileSerializer(debt_profile)
        return Response(read_serializer.data, status=status.HTTP_200_OK)
