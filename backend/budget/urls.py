from django.urls import path

from budget.api.views import BudgetBillCreateView, BudgetValueUpdateView
from budget.api.views.payday_views import (
    PaydayDebtBalanceUpdateView,
    PaydayDetailView,
    PaydayLineItemUpdateView,
    PaydayMarkIncompleteView,
    PaydayPayChequeUpdateView,
    PaydayQueueView,
)
from budget.api.viewsets.budget_viewset import BudgetView

urlpatterns = [
    path("budget/pay-periods/", BudgetView.as_view()),
    path("budget/pay-periods/<int:period_id>/values/", BudgetValueUpdateView.as_view()),
    path("budget/pay-periods/<int:period_id>/bills/", BudgetBillCreateView.as_view()),
    path("budget/payday/queue/", PaydayQueueView.as_view()),
    path("budget/payday/pay-periods/<int:period_id>/", PaydayDetailView.as_view()),
    path("budget/payday/pay-periods/<int:period_id>/pay-cheque/", PaydayPayChequeUpdateView.as_view()),
    path(
        "budget/payday/pay-periods/<int:period_id>/line-items/<int:line_item_id>/",
        PaydayLineItemUpdateView.as_view(),
    ),
    path("budget/payday/pay-periods/<int:period_id>/debt-balance/", PaydayDebtBalanceUpdateView.as_view()),
    path("budget/payday/pay-periods/<int:period_id>/mark-incomplete/", PaydayMarkIncompleteView.as_view()),
]
