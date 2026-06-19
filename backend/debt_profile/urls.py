from django.urls import path

from debt_profile.api.viewsets.debt_profile_viewset import DebtProfileView
from debt_profile.api.viewsets.monthly_expense_viewset import MonthlyExpenseView
from debt_profile.api.viewsets.payment_plan_viewset import PaymentPlanView

urlpatterns = [
    path("debt-profile/", DebtProfileView.as_view()),
    path("debt-profile/monthly-expense/", MonthlyExpenseView.as_view()),
    path("debt-profile/payment-plan/", PaymentPlanView.as_view()),
]
