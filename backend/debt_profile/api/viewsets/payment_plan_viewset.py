from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.models import DebtProfile, PaymentPlan
from debt_profile.structure_serializers.payment_plan_serializer import PaymentPlanSerializer
from debt_profile.views.request_validators import PaymentPlanPatchRequest


class PaymentPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_debt_profile(self, request: Request) -> DebtProfile:
        debt_profile, _ = DebtProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "income_per_pay_period_cents": 0,
                "pay_period_type": "",
                "debts": [],
            },
        )

        return debt_profile

    def get(self, request: Request) -> Response:
        debt_profile = self._get_debt_profile(request)
        plan, _ = PaymentPlan.objects.get_or_create(
            debt_profile=debt_profile,
            defaults={
                "extra_payment_cents": 0,
                "spending_payment_percentage_basis_points": 0,
                "is_active": True,
            },
        )

        serializer = PaymentPlanSerializer(plan)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        debt_profile = self._get_debt_profile(request)
        plan, _ = PaymentPlan.objects.get_or_create(
            debt_profile=debt_profile,
            defaults={
                "extra_payment_cents": 0,
                "spending_payment_percentage_basis_points": 0,
                "is_active": True,
            },
        )

        payment_plan_request = PaymentPlanPatchRequest(request.data)
        payment_plan_request.validate()
        data = payment_plan_request.validated_data

        update_fields: list[str] = []

        if "extra_payment_cents" in data:
            extra_payment_cents = data["extra_payment_cents"]
            if isinstance(extra_payment_cents, int):
                plan.extra_payment_cents = extra_payment_cents
                update_fields.append("extra_payment_cents")

        if "spending_payment_percentage_basis_points" in data:
            spending_pp = data["spending_payment_percentage_basis_points"]
            if isinstance(spending_pp, int):
                plan.spending_payment_percentage_basis_points = spending_pp
                update_fields.append("spending_payment_percentage_basis_points")

        if update_fields:
            plan.save(update_fields=update_fields)

        read_serializer = PaymentPlanSerializer(plan)

        return Response(read_serializer.data, status=status.HTTP_200_OK)
