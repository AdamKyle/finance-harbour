from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.models import DebtProfile, MonthlyExpense
from debt_profile.structure_serializers.monthly_expense_serializer import MonthlyExpenseSerializer
from debt_profile.views.request_validators import MonthlyExpensePatchRequest


class MonthlyExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_debt_profile(self, request: Request) -> DebtProfile:
        debt_profile, _ = DebtProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "income_per_pay_period_cents": 0,
                "pay_period_type": "",
                "debts": [],
            },
        )

        return debt_profile

    def get(self, request: Request) -> Response:
        debt_profile = self._get_debt_profile(request)
        expense, _ = MonthlyExpense.objects.get_or_create(debt_profile=debt_profile)

        serializer = MonthlyExpenseSerializer(expense)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        debt_profile = self._get_debt_profile(request)
        expense, _ = MonthlyExpense.objects.get_or_create(debt_profile=debt_profile)

        monthly_expense_request = MonthlyExpensePatchRequest(request.data)
        monthly_expense_request.validate()
        data = monthly_expense_request.validated_data

        money_fields = [
            "rent_or_mortgage_cents",
            "water_cents",
            "electricity_cents",
            "food_cents",
            "internet_cents",
            "phone_cents",
            "car_payment_cents",
            "insurance_cents",
        ]
        update_fields: list[str] = []

        for field in money_fields:
            if field in data:
                value = data[field]
                if isinstance(value, int):
                    setattr(expense, field, value)
                    update_fields.append(field)

        if "misc_expenses" in data:
            misc_expenses = data["misc_expenses"]
            if isinstance(misc_expenses, list):
                expense.misc_expenses = [dict(entry) for entry in misc_expenses]
                update_fields.append("misc_expenses")

        if update_fields:
            expense.save(update_fields=update_fields)

        read_serializer = MonthlyExpenseSerializer(expense)

        return Response(read_serializer.data, status=status.HTTP_200_OK)
