from django.urls import include, path
from rest_framework.routers import DefaultRouter

from authentication.api.views.google_login_view import GoogleLoginView
from authentication.api.views.login_view import LoginView
from authentication.api.views.register_view import RegisterView
from authentication.api.viewsets.csrf_cookie_viewset import CsrfCookieViewSet
from authentication.api.viewsets.profile_onboarding_viewset import ProfileOnboardingViewSet

router = DefaultRouter()
router.register("auth/csrf", CsrfCookieViewSet, basename="csrf")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", LoginView.as_view()),
    path("auth/social/google/", GoogleLoginView.as_view()),
    path("auth/registration/", RegisterView.as_view()),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "profile/onboarding/",
        ProfileOnboardingViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
    ),
]
