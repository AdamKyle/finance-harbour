from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from onboarding.models import OnboardingProgress
from onboarding.structure_serializers.onboarding_progress_serializer import OnboardingProgressSerializer
from onboarding.views.request_validators import OnboardingProgressPartialUpdateRequest


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
        progress_request = OnboardingProgressPartialUpdateRequest(request.data)
        progress_request.validate()

        validated_data = progress_request.validated_data

        if "current_step" in validated_data:
            progress.current_step = validated_data["current_step"]

        if "completed_steps" in validated_data:
            progress.completed_steps = validated_data["completed_steps"]

        if "form_data" in validated_data:
            progress.form_data = validated_data["form_data"]

        if validated_data:
            progress.save()

        read_serializer = OnboardingProgressSerializer(progress)

        return Response(read_serializer.data, status=status.HTTP_200_OK)
