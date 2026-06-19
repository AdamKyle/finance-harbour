from core.request_validator_engine import RequestValidatorEngine


class LeftOverWarningThresholdRequest(RequestValidatorEngine):
    rules = {
        "left_over_warning_amount_cents": (
            "required",
            "integer",
            ("min_value", 0),
        ),
    }
    messages = {
        "left_over_warning_amount_cents": {
            "required": "Left over warning amount is required.",
            "integer": "Left over warning amount must be an integer.",
            "min_value": "Left over warning amount must be zero or more.",
        },
    }
