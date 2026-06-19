from rest_framework import serializers

from authentication.models import User


class ProfileOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nickname", "profile_photo", "completed_onboarding"]
        read_only_fields = ["nickname", "profile_photo", "completed_onboarding"]
