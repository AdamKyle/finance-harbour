from django.test import TestCase
from rest_framework.exceptions import ValidationError

from authentication.models import User
from core.request_validator_engine import RequestValidatorEngine
from core.request_validator_engine.definitions import UniqueRuleOptions


class RequiredRequest(RequestValidatorEngine):
    rules = {
        "name": (
            "required",
            "string",
        ),
    }


class NullableRequest(RequestValidatorEngine):
    rules = {
        "name": (
            "nullable",
            "string",
        ),
    }


class EmailRequest(RequestValidatorEngine):
    rules = {
        "email": (
            "email",
            ("max_length", 20),
        ),
    }


class BaselineRulesRequest(RequestValidatorEngine):
    rules = {
        "integer_value": ("integer",),
        "boolean_value": ("boolean",),
        "list_value": ("list",),
        "dict_value": ("dict",),
        "short_string": (
            "string",
            ("min_length", 2),
        ),
        "choice": (("choices", ("one", "two")),),
    }


class UniqueEmailRequest(RequestValidatorEngine):
    rules = {
        "email": (
            (
                "unique",
                UniqueRuleOptions(
                    model=User,
                    field="email",
                    case_insensitive=True,
                ),
            ),
        ),
    }


class RequestValidatorEngineTest(TestCase):
    def test_required_rule_rejects_a_missing_field(self) -> None:
        request_validator = RequiredRequest({})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertEqual(
            str(raised_error.exception.detail["name"][0]),
            "This field is required.",
        )

    def test_nullable_rule_accepts_null(self) -> None:
        request_validator = NullableRequest({"name": None})

        request_validator.validate()

        self.assertEqual(request_validator.validated_data, {"name": None})

    def test_string_rule_rejects_a_non_string_value(self) -> None:
        request_validator = RequiredRequest({"name": 10})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("name", raised_error.exception.detail)

    def test_email_rule_rejects_an_invalid_email(self) -> None:
        request_validator = EmailRequest({"email": "invalid-email"})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("email", raised_error.exception.detail)

    def test_email_rule_rejects_a_non_string_value(self) -> None:
        request_validator = EmailRequest({"email": 10})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("email", raised_error.exception.detail)

    def test_max_length_rule_rejects_a_long_value(self) -> None:
        request_validator = EmailRequest({"email": "long-email@example.com"})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("email", raised_error.exception.detail)

    def test_baseline_type_and_value_rules_accept_valid_data(self) -> None:
        request_validator = BaselineRulesRequest(
            {
                "integer_value": 10,
                "boolean_value": True,
                "list_value": ["value"],
                "dict_value": {"key": "value"},
                "short_string": "valid",
                "choice": "one",
            }
        )

        request_validator.validate()

        self.assertEqual(request_validator.validated_data["integer_value"], 10)

    def test_integer_rule_rejects_a_boolean(self) -> None:
        request_validator = BaselineRulesRequest({"integer_value": True})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("integer_value", raised_error.exception.detail)

    def test_boolean_rule_rejects_a_non_boolean(self) -> None:
        request_validator = BaselineRulesRequest({"boolean_value": 1})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("boolean_value", raised_error.exception.detail)

    def test_list_rule_rejects_a_non_list(self) -> None:
        request_validator = BaselineRulesRequest({"list_value": "value"})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("list_value", raised_error.exception.detail)

    def test_dict_rule_rejects_a_non_dict(self) -> None:
        request_validator = BaselineRulesRequest({"dict_value": ["value"]})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("dict_value", raised_error.exception.detail)

    def test_min_length_rule_rejects_a_short_value(self) -> None:
        request_validator = BaselineRulesRequest({"short_string": "a"})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("short_string", raised_error.exception.detail)

    def test_choices_rule_rejects_an_unknown_value(self) -> None:
        request_validator = BaselineRulesRequest({"choice": "three"})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("choice", raised_error.exception.detail)

    def test_unique_rule_rejects_an_existing_value(self) -> None:
        User.objects.create_user(
            email="unique-engine@example.com",
            password="StrongPassword123!",
        )
        request_validator = UniqueEmailRequest({"email": "UNIQUE-engine@example.com"})

        with self.assertRaises(ValidationError) as raised_error:
            request_validator.validate()

        self.assertIn("email", raised_error.exception.detail)
