from django.urls import include, path

urlpatterns = [
    path("api/", include("authentication.urls")),
    path("api/", include("onboarding.urls")),
    path("api/", include("debt_profile.urls")),
    path("api/", include("budget.urls")),
]
