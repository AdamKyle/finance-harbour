from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User


class DjRestAuthCookieAuthTest(APITestCase):
    secure_origin = "https://testserver"

    def test_registration_sets_jwt_cookies_and_returns_user_with_completed_onboarding(self) -> None:
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = self._get_csrf_token(client)

        response = client.post(
            "/api/auth/registration/",
            {
                "email": "registered@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(settings.REST_AUTH["JWT_AUTH_COOKIE"], response.cookies)
        self.assertIn(settings.REST_AUTH["JWT_AUTH_REFRESH_COOKIE"], response.cookies)
        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertNotIn("messages", response.cookies)
        self.assertEqual(response.data["user"]["email"], "registered@example.com")
        self.assertFalse(response.data["user"]["completed_onboarding"])
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

        user_response = client.get("/api/auth/user/", secure=True)

        self.assertEqual(user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_response.data["email"], "registered@example.com")
        self.assertFalse(user_response.data["completed_onboarding"])

    def test_login_sets_jwt_cookies_and_user_endpoint_returns_completed_onboarding(self) -> None:
        User.objects.create_user(
            email="logged-in@example.com",
            password="StrongPassword123!",
            completed_onboarding=True,
        )

        client = APIClient(enforce_csrf_checks=True)
        csrf_token = self._get_csrf_token(client)

        response = client.post(
            "/api/auth/login/",
            {
                "email": "logged-in@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.REST_AUTH["JWT_AUTH_COOKIE"], response.cookies)
        self.assertIn(settings.REST_AUTH["JWT_AUTH_REFRESH_COOKIE"], response.cookies)
        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertNotIn("messages", response.cookies)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

        user_response = client.get("/api/auth/user/", secure=True)

        self.assertEqual(user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_response.data["email"], "logged-in@example.com")
        self.assertTrue(user_response.data["completed_onboarding"])

    def test_login_rotates_csrf_token_and_requires_fresh_token_for_profile_update(self) -> None:
        user = User.objects.create_user(
            email="csrf-rotation@example.com",
            password="StrongPassword123!",
        )

        client = APIClient(enforce_csrf_checks=True)
        stale_csrf_token = self._get_csrf_token(client)

        login_response = client.post(
            "/api/auth/login/",
            {
                "email": "csrf-rotation@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=stale_csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        fresh_csrf_token = self._get_csrf_token(client)

        self.assertNotEqual(stale_csrf_token, fresh_csrf_token)

        stale_update_response = client.patch(
            "/api/profile/onboarding/",
            {"nickname": "FreshNick"},
            format="json",
            HTTP_X_CSRFTOKEN=stale_csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(stale_update_response.status_code, status.HTTP_403_FORBIDDEN)

        fresh_update_response = client.patch(
            "/api/profile/onboarding/",
            {"nickname": "FreshNick"},
            format="json",
            HTTP_X_CSRFTOKEN=fresh_csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(fresh_update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(fresh_update_response.data["nickname"], "FreshNick")

        user.refresh_from_db()

        self.assertEqual(user.nickname, "FreshNick")

    def test_logout_deletes_jwt_cookies(self) -> None:
        User.objects.create_user(
            email="logout@example.com",
            password="StrongPassword123!",
        )

        client = APIClient(enforce_csrf_checks=True)
        csrf_token = self._get_csrf_token(client)

        login_response = client.post(
            "/api/auth/login/",
            {
                "email": "logout@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        csrf_token = self._get_csrf_token(client)

        response = client.post(
            "/api/auth/logout/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies[settings.REST_AUTH["JWT_AUTH_COOKIE"]].value, "")
        self.assertEqual(response.cookies[settings.REST_AUTH["JWT_AUTH_REFRESH_COOKIE"]].value, "")

        user_response = client.get("/api/auth/user/", secure=True)

        self.assertEqual(user_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registration_requires_csrf_token(self) -> None:
        client = APIClient(enforce_csrf_checks=True)

        response = client.post(
            "/api/auth/registration/",
            {
                "email": "missing-csrf@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_requires_csrf_token(self) -> None:
        User.objects.create_user(
            email="missing-login-csrf@example.com",
            password="StrongPassword123!",
        )

        client = APIClient(enforce_csrf_checks=True)

        response = client.post(
            "/api/auth/login/",
            {
                "email": "missing-login-csrf@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_requires_csrf_token(self) -> None:
        User.objects.create_user(
            email="missing-logout-csrf@example.com",
            password="StrongPassword123!",
        )

        client = APIClient(enforce_csrf_checks=True)
        csrf_token = self._get_csrf_token(client)

        login_response = client.post(
            "/api/auth/login/",
            {
                "email": "missing-logout-csrf@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = client.post(
            "/api/auth/logout/",
            {},
            format="json",
            HTTP_ORIGIN=self.secure_origin,
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _get_csrf_token(self, client: APIClient) -> str:
        response = client.get("/api/auth/csrf/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.CSRF_COOKIE_NAME, response.cookies)

        return str(response.data["csrfToken"])
