from rest_framework import serializers

from onboarding.models import OnboardingProgress


class OnboardingProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingProgress
        fields = ["current_step", "completed_steps", "form_data", "is_complete"]
        read_only_fields = ["current_step", "completed_steps", "form_data", "is_complete"]
