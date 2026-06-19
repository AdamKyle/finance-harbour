from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from onboarding.models import OnboardingProgress
from onboarding.serializers.onboarding_progress_write_serializer import OnboardingProgressWriteSerializer
from onboarding.structure_serializers.onboarding_progress_serializer import OnboardingProgressSerializer


class OnboardingProgressViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request: Request, **kwargs: object) -> Response:
        progress, _ = OnboardingProgress.objects.get_or_create(
            user=request.user,
            defaults={"current_step": "profile", "completed_steps": [], "form_data": {}},
        )
        serializer = OnboardingProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request: Request, **kwargs: object) -> Response:
        progress, _ = OnboardingProgress.objects.get_or_create(
            user=request.user,
            defaults={"current_step": "profile", "completed_steps": [], "form_data": {}},
        )
        write_serializer = OnboardingProgressWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        data = write_serializer.validated_data

        if "current_step" in data:
            progress.current_step = data["current_step"]
        if "completed_steps" in data:
            progress.completed_steps = data["completed_steps"]
        if "form_data" in data:
            progress.form_data = data["form_data"]
        progress.save()

        read_serializer = OnboardingProgressSerializer(progress)
        return Response(read_serializer.data, status=status.HTTP_200_OK)
