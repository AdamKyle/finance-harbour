from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from onboarding.services.onboarding_completion import complete_onboarding
from onboarding.structure_serializers.onboarding_completion_response_serializer import (
    OnboardingCompletionResponseSerializer,
)


class OnboardingCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        result = complete_onboarding(request.user)

        if not result.success:
            return Response(
                {"detail": result.reason},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = OnboardingCompletionResponseSerializer.from_plan(result.plan)

        return Response(data, status=status.HTTP_200_OK)
