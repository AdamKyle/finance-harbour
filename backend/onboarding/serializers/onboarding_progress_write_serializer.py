from rest_framework import serializers


class OnboardingProgressWriteSerializer(serializers.Serializer):
    current_step = serializers.CharField(required=False, allow_blank=True, max_length=50)
    completed_steps = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
    )
    form_data = serializers.JSONField(required=False)
