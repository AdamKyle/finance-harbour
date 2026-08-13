from rest_framework import serializers

from debt_profile.models import ExpensePaymentTiming, PaycheckPosition
from debt_profile.types import ExpensePaymentScheduleDefinition


class ExpensePaymentScheduleSerializer(serializers.Serializer):
    source_key = serializers.CharField(max_length=150)
    timing = serializers.ChoiceField(choices=ExpensePaymentTiming.choices)
    paycheck_position = serializers.ChoiceField(
        choices=PaycheckPosition.choices,
        allow_null=True,
    )
    day_of_month = serializers.IntegerField(min_value=1, max_value=31, allow_null=True)
    auto_deducted = serializers.BooleanField()

    def to_representation(self, instance: object) -> dict[str, str | int | bool | None]:
        representation = super().to_representation(instance)

        if representation["paycheck_position"] == "":
            representation["paycheck_position"] = None

        return representation

    def validate(
        self,
        attributes: ExpensePaymentScheduleDefinition,
    ) -> ExpensePaymentScheduleDefinition:
        timing = ExpensePaymentTiming(attributes["timing"])
        attributes["timing"] = timing
        paycheck_position = attributes["paycheck_position"]
        day_of_month = attributes["day_of_month"]

        if timing == ExpensePaymentTiming.EVERY_PAYCHECK:
            if paycheck_position is not None:
                raise serializers.ValidationError(
                    {"paycheck_position": "Every-paycheck schedules do not use a position."}
                )
            if day_of_month is not None:
                raise serializers.ValidationError({"day_of_month": "Every-paycheck schedules do not use a day."})
            if attributes["auto_deducted"]:
                raise serializers.ValidationError(
                    {"auto_deducted": "Auto-deducted is available only for date-based payments."}
                )

        if timing == ExpensePaymentTiming.PAYCHECK_POSITION:
            if paycheck_position is None:
                raise serializers.ValidationError({"paycheck_position": "Select a paycheck."})
            if day_of_month is not None:
                raise serializers.ValidationError({"day_of_month": "Paycheck schedules do not use a day."})
            if attributes["auto_deducted"]:
                raise serializers.ValidationError(
                    {"auto_deducted": "Auto-deducted is available only for date-based payments."}
                )
            attributes["paycheck_position"] = PaycheckPosition(paycheck_position)

        if timing == ExpensePaymentTiming.DAY_OF_MONTH:
            if day_of_month is None:
                raise serializers.ValidationError({"day_of_month": "Enter a day from 1 to 31."})
            if paycheck_position is not None:
                attributes["paycheck_position"] = PaycheckPosition(paycheck_position)

        return attributes
