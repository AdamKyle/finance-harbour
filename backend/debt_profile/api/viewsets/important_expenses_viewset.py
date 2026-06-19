from math import ceil

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from debt_profile.models import DebtProfile
from debt_profile.services import (
    build_important_expense_cards,
    replace_required_expenses,
)
from debt_profile.structure_serializers.important_expense_card_serializer import (
    ImportantExpenseCardSerializer,
)
from debt_profile.views.request_validators import ImportantExpensesSaveRequest


class ImportantExpensesView(APIView):
    permission_classes = [IsAuthenticated]
    per_page = 8

    def get(self, request: Request) -> Response:
        debt_profile = self._get_debt_profile(request)
        cards = build_important_expense_cards(debt_profile)

        page = self._get_page(request)
        total = len(cards)
        total_pages = ceil(total / self.per_page) if total > 0 else 1
        start_index = (page - 1) * self.per_page
        page_cards = cards[start_index : start_index + self.per_page]

        serializer = ImportantExpenseCardSerializer(page_cards, many=True)

        return Response(
            {
                "data": serializer.data,
                "meta": {
                    "can_load_more": page < total_pages,
                    "pagination": {
                        "count": len(page_cards),
                        "current_page": page,
                        "links": {},
                        "per_page": self.per_page,
                        "total": total,
                        "total_pages": total_pages,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request) -> Response:
        debt_profile = self._get_debt_profile(request)

        important_expenses_request = ImportantExpensesSaveRequest(
            request.data,
            debt_profile,
        )
        important_expenses_request.validate()

        selected_keys = important_expenses_request.validated_data["selected_keys"]

        if not isinstance(selected_keys, list):
            selected_keys = []

        replace_required_expenses(debt_profile, selected_keys)

        return Response({"selected_keys": selected_keys}, status=status.HTTP_200_OK)

    def _get_debt_profile(self, request: Request) -> DebtProfile:
        debt_profile, _ = DebtProfile.objects.get_or_create(user=request.user)

        return debt_profile

    def _get_page(self, request: Request) -> int:
        submitted_page = request.query_params.get("page", "1")

        try:
            page = int(submitted_page)
        except ValueError:
            return 1

        return max(page, 1)
