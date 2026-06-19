from core.request_validator_engine import RequestValidatorEngine


class OnboardingProgressPartialUpdateRequest(RequestValidatorEngine):
    step_choices = (
        "profile",
        "debts",
        "income",
        "expenses",
        "important_expenses",
        "left_over_warning",
        "conclude",
    )
    rules = {
        "current_step": (
            "string",
            ("max_length", 50),
            ("choices", step_choices),
        ),
        "completed_steps": ("list",),
        "form_data": ("dict",),
    }
    messages = {
        "current_step": {
            "string": "Current step must be a string.",
            "max_length": "Current step must be 50 characters or fewer.",
            "choices": "Current step is invalid.",
        },
        "completed_steps": {
            "list": "Completed steps must be a list.",
        },
        "form_data": {
            "dict": "Form data must be a dictionary.",
        },
    }
