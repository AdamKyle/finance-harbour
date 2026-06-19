from authentication.models import User
from core.request_validator_engine import RequestValidatorEngine
from core.request_validator_engine.definitions import UniqueRuleOptions


class ProfileOnboardingPartialUpdateRequest(RequestValidatorEngine):
    rules = {
        "nickname": (
            "string",
            ("max_length", 100),
            (
                "unique",
                UniqueRuleOptions(
                    model=User,
                    field="nickname",
                    case_insensitive=True,
                    ignored_values=("",),
                ),
            ),
        ),
        "profile_photo": (
            "string",
            ("max_length", 100),
        ),
    }
    messages = {
        "nickname": {
            "string": "Nickname must be a string.",
            "max_length": "Nickname must be 100 characters or fewer.",
            "unique": "This nickname is already in use.",
        },
        "profile_photo": {
            "string": "Profile photo must be a string.",
            "max_length": "Profile photo must be 100 characters or fewer.",
        },
    }
