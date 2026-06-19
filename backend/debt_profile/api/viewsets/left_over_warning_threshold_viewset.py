from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.models import DebtProfile
from debt_profile.structure_serializers.left_over_warning_threshold_serializer import (
    LeftOverWarningThresholdSerializer,
)
from debt_profile.views.request_validators import LeftOverWarningThresholdRequest


class LeftOverWarningThresholdView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request) -> Response:
        threshold_request = LeftOverWarningThresholdRequest(request.data)
        threshold_request.validate()

        debt_profile, _ = DebtProfile.objects.get_or_create(user=request.user)
        threshold_value = threshold_request.validated_data["left_over_warning_amount_cents"]

        if isinstance(threshold_value, int):
            debt_profile.left_over_warning_amount_cents = threshold_value
            debt_profile.save(update_fields=["left_over_warning_amount_cents"])

        serializer = LeftOverWarningThresholdSerializer(debt_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)
