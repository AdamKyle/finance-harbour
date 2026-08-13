from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User


class TokenRefreshViewTest(APITestCase):
    def test_valid_refresh_cookie_sets_access_cookie_without_returning_raw_tokens(self) -> None:
        user = User.objects.create_user(email="refresh@example.com", password="StrongPassword123!")
        refresh_token = RefreshToken.for_user(user)
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])
        client.cookies["refresh"] = str(refresh_token)

        response = client.post(
            "/api/auth/token/refresh/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN="https://testserver",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.cookies)
        self.assertTrue(response.cookies["access"]["httponly"])
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_missing_refresh_cookie_is_rejected_without_setting_access_cookie(self) -> None:
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/", secure=True)
        csrf_token = str(csrf_response.data["csrfToken"])

        response = client.post(
            "/api/auth/token/refresh/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN="https://testserver",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.cookies)

    def test_missing_csrf_is_rejected_with_valid_refresh_cookie(self) -> None:
        user = User.objects.create_user(email="refresh-csrf@example.com", password="StrongPassword123!")
        refresh_token = RefreshToken.for_user(user)
        client = APIClient(enforce_csrf_checks=True)
        client.cookies["refresh"] = str(refresh_token)

        response = client.post(
            "/api/auth/token/refresh/",
            {},
            format="json",
            HTTP_ORIGIN="https://testserver",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("access", response.cookies)
