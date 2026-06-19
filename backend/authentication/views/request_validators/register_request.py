from authentication.models import User
from core.request_validator_engine import RequestValidatorEngine
from core.request_validator_engine.definitions import UniqueRuleOptions


class RegisterRequest(RequestValidatorEngine):
    rules = {
        "email": (
            "required",
            "string",
            "email",
            ("max_length", 254),
            (
                "unique",
                UniqueRuleOptions(
                    model=User,
                    field="email",
                    case_insensitive=True,
                ),
            ),
        ),
        "password": (
            "required",
            "string",
        ),
    }
    messages = {
        "email": {
            "required": "Email is required.",
            "string": "Email must be a string.",
            "email": "Enter a valid email address.",
            "max_length": "Email must be 254 characters or fewer.",
            "unique": "An account with this email already exists.",
        },
        "password": {
            "required": "Password is required.",
            "string": "Password must be a string.",
        },
    }
