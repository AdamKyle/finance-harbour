from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User
from core.middleware.ownership_middleware import OwnershipMiddleware


class OwnershipMiddlewareTest(TestCase):
    def test_anonymous_user_rejected_for_protected_endpoint(self) -> None:
        client = APIClient()

        response = client.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_matching_route_user_id_succeeds(self) -> None:
        user = User.objects.create_user(
            email="match@example.com",
            password="StrongPassword123!",
        )
        request: HttpRequest = RequestFactory().get("/")
        request.user = user
        middleware = OwnershipMiddleware(get_response=lambda r: HttpResponse())

        result = middleware.process_view(request, lambda r: HttpResponse(), [], {"user_id": user.id})

        self.assertIsNone(result)

    def test_mismatched_route_user_id_fails(self) -> None:
        user1 = User.objects.create_user(
            email="user1@example.com",
            password="StrongPassword123!",
        )
        user2 = User.objects.create_user(
            email="user2@example.com",
            password="StrongPassword123!",
        )
        request: HttpRequest = RequestFactory().get("/")
        request.user = user1
        middleware = OwnershipMiddleware(get_response=lambda r: HttpResponse())

        result = middleware.process_view(request, lambda r: HttpResponse(), [], {"user_id": user2.id})

        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)  # type: ignore[union-attr]

    def test_middleware_blocks_cross_user_route_access(self) -> None:
        target_user = User.objects.create_user(
            email="target@example.com",
            password="StrongPassword123!",
        )
        request: HttpRequest = RequestFactory().get("/")
        request.user = AnonymousUser()  # type: ignore[assignment]
        middleware = OwnershipMiddleware(get_response=lambda r: HttpResponse())

        result = middleware.process_view(request, lambda r: HttpResponse(), [], {"user_id": target_user.id})

        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)  # type: ignore[union-attr]

    def test_routes_without_user_id_rely_on_request_user_filtering(self) -> None:
        user1 = User.objects.create_user(
            email="filter1@example.com",
            password="StrongPassword123!",
        )
        user2 = User.objects.create_user(
            email="filter2@example.com",
            password="StrongPassword123!",
        )
        client1 = APIClient()
        client1.force_authenticate(user=user1)
        client1.patch(
            "/api/onboarding/progress/",
            {"current_step": "debts"},
            format="json",
            secure=True,
        )

        client2 = APIClient()
        client2.force_authenticate(user=user2)
        response = client2.get("/api/onboarding/progress/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_step"], "profile")
