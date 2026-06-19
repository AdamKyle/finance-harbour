from django.urls import path

from onboarding.api.viewsets.onboarding_complete_viewset import OnboardingCompleteView
from onboarding.api.viewsets.onboarding_progress_viewset import OnboardingProgressViewSet

urlpatterns = [
    path(
        "onboarding/progress/",
        OnboardingProgressViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
    ),
    path("onboarding/complete/", OnboardingCompleteView.as_view()),
]
