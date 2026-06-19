from rest_framework import serializers

from debt_profile.models import DebtProfile


class LeftOverWarningThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtProfile
        fields = ["left_over_warning_amount_cents"]
        read_only_fields = ["left_over_warning_amount_cents"]
