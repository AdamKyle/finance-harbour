from core.request_validator_engine import RequestValidatorEngine


class PaymentPlanPatchRequest(RequestValidatorEngine):
    rules = {
        "extra_payment_cents": (
            "integer",
            ("min_value", 0),
        ),
        "spending_payment_percentage_basis_points": (
            "integer",
            ("min_value", 0),
        ),
    }
    messages = {
        "extra_payment_cents": {
            "integer": "Extra payment must be an integer.",
            "min_value": "Extra payment must be zero or more.",
        },
        "spending_payment_percentage_basis_points": {
            "integer": "Spending payment percentage must be an integer.",
            "min_value": "Spending payment percentage must be zero or more.",
        },
    }
