from django.test import TestCase
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.views.request_validators import RegisterRequest


class RegisterRequestTest(TestCase):
    def test_valid_registration_data_passes_validation(self) -> None:
        register_request = RegisterRequest(
            {
                "email": "valid-register-request@example.com",
                "password": "StrongPassword123!",
            }
        )

        register_request.validate()

        self.assertEqual(
            register_request.validated_data,
            {
                "email": "valid-register-request@example.com",
                "password": "StrongPassword123!",
            },
        )

    def test_duplicate_email_fails_validation(self) -> None:
        User.objects.create_user(
            email="duplicate-register-request@example.com",
            password="StrongPassword123!",
        )
        register_request = RegisterRequest(
            {
                "email": "duplicate-register-request@example.com",
                "password": "StrongPassword123!",
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            register_request.validate()

        self.assertIn("email", raised_error.exception.detail)

    def test_case_variant_duplicate_email_fails_validation(self) -> None:
        User.objects.create_user(
            email="case-register-request@example.com",
            password="StrongPassword123!",
        )
        register_request = RegisterRequest(
            {
                "email": "CASE-register-request@example.com",
                "password": "StrongPassword123!",
            }
        )

        with self.assertRaises(ValidationError) as raised_error:
            register_request.validate()

        self.assertIn("email", raised_error.exception.detail)
