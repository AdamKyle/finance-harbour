from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.services import (
    build_important_expense_page,
    replace_required_expenses,
)
from debt_profile.services.debt_profile_service import get_or_create_debt_profile
from debt_profile.structure_serializers.important_expense_card_serializer import (
    ImportantExpenseCardSerializer,
)
from debt_profile.views.request_validators import ImportantExpensesIndexRequest, ImportantExpensesSaveRequest


class ImportantExpensesView(APIView):
    permission_classes = [IsAuthenticated]
    per_page = 8

    def get(self, request: Request) -> Response:
        index_request = ImportantExpensesIndexRequest(request.query_params)
        index_request.validate()
        debt_profile = get_or_create_debt_profile(request.user)
        expense_page = build_important_expense_page(debt_profile, index_request.page, self.per_page)

        serializer = ImportantExpenseCardSerializer(expense_page["cards"], many=True)

        return Response(
            {
                "data": serializer.data,
                "meta": {
                    "can_load_more": expense_page["page"] < expense_page["total_pages"],
                    "pagination": {
                        "count": len(expense_page["cards"]),
                        "current_page": expense_page["page"],
                        "links": {},
                        "per_page": self.per_page,
                        "total": expense_page["total"],
                        "total_pages": expense_page["total_pages"],
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request) -> Response:
        debt_profile = get_or_create_debt_profile(request.user)

        important_expenses_request = ImportantExpensesSaveRequest(
            request.data,
            debt_profile,
        )
        important_expenses_request.validate()

        selected_keys = important_expenses_request.validated_data["selected_keys"]

        replace_required_expenses(debt_profile, selected_keys)

        return Response({"selected_keys": selected_keys}, status=status.HTTP_200_OK)
