from math import ceil

from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from budget.models import BudgetLineItem, BudgetPlan
from budget.services.budget_dashboard_anchor_service import get_budget_dashboard_anchor
from budget.services.debt_balance_projection_service import get_debt_balance_projections_for_periods
from budget.services.payday_development_date_service import resolve_payday_effective_date
from budget.structure_serializers.budget_pay_period_serializer import BudgetPayPeriodSerializer


class BudgetView(APIView):
    permission_classes = [IsAuthenticated]
    per_page = 6

    def get(self, request: Request) -> Response:
        try:
            plan = BudgetPlan.objects.get(user=request.user)
        except BudgetPlan.DoesNotExist:
            return Response(
                {
                    "data": [],
                    "meta": {
                        "can_load_more": False,
                        "can_load_previous": False,
                        "anchor_period_id": None,
                        "pagination": {
                            "count": 0,
                            "current_page": 1,
                            "links": {},
                            "per_page": self.per_page,
                            "total": 0,
                            "total_pages": 1,
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )

        periods_qs = plan.pay_periods.order_by("sequence", "pay_date")
        submitted_anchor_period_id = request.query_params.get("anchor_period_id")
        requested_anchor_period_id = None

        if submitted_anchor_period_id is not None:
            try:
                requested_anchor_period_id = int(submitted_anchor_period_id)
            except ValueError:
                requested_anchor_period_id = None

        anchor = get_budget_dashboard_anchor(
            periods_qs,
            resolve_payday_effective_date(request.user),
            self.per_page,
            requested_anchor_period_id,
        )
        submitted_page = request.query_params.get("page")

        if submitted_page is None:
            page = anchor.page
        else:
            try:
                page = max(int(submitted_page), 1)
            except ValueError:
                page = anchor.page

        line_items_prefetch = Prefetch(
            "line_items",
            queryset=BudgetLineItem.objects.order_by("display_order", "id"),
        )
        periods_qs = periods_qs.prefetch_related(line_items_prefetch)
        total = periods_qs.count()
        total_pages = ceil(total / self.per_page) if total > 0 else 1
        start = (page - 1) * self.per_page
        page_periods = list(periods_qs[start : start + self.per_page])
        previous_sequences = {period.sequence - 1 for period in page_periods if period.sequence > 0}
        previous_dates_by_sequence = dict(
            plan.pay_periods.filter(sequence__in=previous_sequences).values_list("sequence", "pay_date")
        )

        for period in page_periods:
            period._previous_pay_date = previous_dates_by_sequence.get(period.sequence - 1)

        debt_checks_by_period = get_debt_balance_projections_for_periods(page_periods)

        for period in page_periods:
            period._debt_balance_checks = debt_checks_by_period[period.id]

        serializer = BudgetPayPeriodSerializer(page_periods, many=True)

        return Response(
            {
                "data": serializer.data,
                "meta": {
                    "can_load_more": page < total_pages,
                    "can_load_previous": page > 1,
                    "anchor_period_id": anchor.period_id,
                    "pagination": {
                        "count": len(page_periods),
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
