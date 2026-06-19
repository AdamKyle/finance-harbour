from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from onboarding.models import OnboardingProgress
from onboarding.services.onboarding_readiness import check_onboarding_readiness


class OnboardingCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        result = check_onboarding_readiness(request.user)

        if not result.ready:
            return Response(
                {"detail": result.reason},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.completed_onboarding = True
        user.save(update_fields=["completed_onboarding"])

        progress, _ = OnboardingProgress.objects.get_or_create(user=user)
        progress.is_complete = True
        progress.save(update_fields=["is_complete"])

        return Response({"detail": "Onboarding complete."}, status=status.HTTP_200_OK)
