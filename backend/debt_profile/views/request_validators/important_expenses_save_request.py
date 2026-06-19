from rest_framework.exceptions import ValidationError

from core.request_validator_engine import RequestValidatorEngine
from debt_profile.models import DebtProfile
from debt_profile.services import build_important_expense_cards


class ImportantExpensesSaveRequest(RequestValidatorEngine):
    rules = {
        "selected_keys": (
            "required",
            "list",
        ),
    }
    messages = {
        "selected_keys": {
            "required": "Selected expense keys are required.",
            "list": "Selected expense keys must be a list.",
        },
    }

    def __init__(
        self,
        request_data: dict[str, object],
        debt_profile: DebtProfile,
    ) -> None:
        super().__init__(request_data)
        self.debt_profile = debt_profile

    def validate(self) -> None:
        super().validate()

        selected_keys = self.validated_data["selected_keys"]

        if not isinstance(selected_keys, list):
            return

        if any(not isinstance(source_key, str) for source_key in selected_keys):
            raise ValidationError({"selected_keys": ["Every selected expense key must be a string."]})

        if len(selected_keys) != len(set(selected_keys)):
            raise ValidationError({"selected_keys": ["Selected expense keys must be unique."]})

        available_keys = {card["key"] for card in build_important_expense_cards(self.debt_profile)}

        if any(source_key not in available_keys for source_key in selected_keys):
            raise ValidationError({"selected_keys": ["Select only expenses available to your profile."]})
