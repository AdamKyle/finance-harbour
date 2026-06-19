from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from authentication.structure_serializers.profile_onboarding_serializer import ProfileOnboardingSerializer
from authentication.views.request_validators import ProfileOnboardingPartialUpdateRequest


class ProfileOnboardingViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request: Request, **kwargs: object) -> Response:
        serializer = ProfileOnboardingSerializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request: Request, **kwargs: object) -> Response:
        profile_onboarding_request = ProfileOnboardingPartialUpdateRequest(
            request.data,
            instance=request.user,
        )
        profile_onboarding_request.validate()

        validated_data = profile_onboarding_request.validated_data

        for field_name, field_value in validated_data.items():
            setattr(request.user, field_name, field_value)

        if validated_data:
            request.user.save(update_fields=list(validated_data))

        read_serializer = ProfileOnboardingSerializer(request.user)

        return Response(read_serializer.data, status=status.HTTP_200_OK)
