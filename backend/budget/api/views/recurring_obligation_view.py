from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from budget.services.recurring_obligation_service import create_recurring_obligation
from budget.structure_serializers.recurring_obligation_configuration_serializer import (
    RecurringObligationConfigurationSerializer,
)
from budget.structure_serializers.recurring_obligation_result_serializer import RecurringObligationResultSerializer
from budget.structures import RecurringObligationConfiguration
from budget.views.request_validators.recurring_obligation_create_request import RecurringObligationCreateRequest
from debt_profile.models import DebtProfile


class RecurringObligationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        debt_profile = self._get_profile(request)
        self._validate_profile_configuration(debt_profile)

        configuration = RecurringObligationConfiguration(
            pay_period_type=debt_profile.pay_period_type,
            representative_date=debt_profile.next_pay_date,
        )

        return Response(RecurringObligationConfigurationSerializer(configuration).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        debt_profile = self._get_profile(request)
        self._validate_profile_configuration(debt_profile)
        create_request = RecurringObligationCreateRequest(request.data)
        create_request.validate()
        create_request.validate_schedule_position(debt_profile.pay_period_type)
        result = create_recurring_obligation(request.user, create_request.validated_data)

        return Response(RecurringObligationResultSerializer(result).data, status=status.HTTP_201_CREATED)

    def _get_profile(self, request: Request) -> DebtProfile:
        try:
            return DebtProfile.objects.get(user=request.user)
        except DebtProfile.DoesNotExist as error:
            raise ValidationError(
                {"profile": ["Complete your financial profile before adding a recurring payment."]}
            ) from error

    def _validate_profile_configuration(self, debt_profile: DebtProfile) -> None:
        valid_pay_period_types = set(DebtProfile.PayPeriodType.values)

        if debt_profile.pay_period_type not in valid_pay_period_types or debt_profile.next_pay_date is None:
            raise ValidationError({"profile": ["Complete your pay schedule before adding a recurring payment."]})
