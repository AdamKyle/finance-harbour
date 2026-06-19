from django.urls import path

from debt_profile.api.viewsets.debt_profile_viewset import DebtProfileView
from debt_profile.api.viewsets.important_expenses_viewset import ImportantExpensesView
from debt_profile.api.viewsets.left_over_warning_threshold_viewset import LeftOverWarningThresholdView
from debt_profile.api.viewsets.monthly_expense_viewset import MonthlyExpenseView
from debt_profile.api.viewsets.payment_plan_viewset import PaymentPlanView

urlpatterns = [
    path("debt-profile/", DebtProfileView.as_view()),
    path("debt-profile/monthly-expense/", MonthlyExpenseView.as_view()),
    path("debt-profile/payment-plan/", PaymentPlanView.as_view()),
    path("debt-profile/important-expenses/", ImportantExpensesView.as_view()),
    path(
        "debt-profile/left-over-warning-threshold/",
        LeftOverWarningThresholdView.as_view(),
    ),
]
