from collections.abc import Collection, Mapping, Sized

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db.models import Model
from rest_framework.exceptions import ValidationError

from core.request_validator_engine.definitions import (
    UniqueRuleOptions,
    ValidationMessages,
    ValidationRule,
    ValidationRules,
)


class RequestValidatorEngine:
    rules: ValidationRules = {}
    messages: ValidationMessages = {}

    def __init__(
        self,
        request_data: Mapping[str, object],
        instance: Model | None = None,
    ) -> None:
        self.request_data = request_data
        self.instance = instance
        self._validated_data: dict[str, object] = {}

    @property
    def validated_data(self) -> dict[str, object]:
        return self._validated_data.copy()

    def validate(self) -> None:
        errors: dict[str, list[str]] = {}
        validated_data: dict[str, object] = {}

        for field_name, field_rules in self.rules.items():
            field_is_present = field_name in self.request_data

            if not field_is_present:
                if "required" in field_rules:
                    errors[field_name] = [self._message(field_name, "required")]

                continue

            field_value = self.request_data[field_name]

            if field_value is None and "nullable" in field_rules:
                validated_data[field_name] = field_value

                continue

            for validation_rule in field_rules:
                error_message = self._validate_rule(
                    field_name,
                    field_value,
                    validation_rule,
                )

                if error_message is not None:
                    errors[field_name] = [error_message]

                    break

            if field_name not in errors:
                validated_data[field_name] = field_value

        if errors:
            raise ValidationError(errors)

        self._validated_data = validated_data

    def _validate_rule(
        self,
        field_name: str,
        field_value: object,
        validation_rule: ValidationRule,
    ) -> str | None:
        if isinstance(validation_rule, str):
            return self._validate_simple_rule(
                field_name,
                field_value,
                validation_rule,
            )

        rule_name, rule_value = validation_rule

        return self._validate_parameterized_rule(
            field_name,
            field_value,
            rule_name,
            rule_value,
        )

    def _validate_simple_rule(
        self,
        field_name: str,
        field_value: object,
        rule_name: str,
    ) -> str | None:
        if rule_name in {"required", "nullable"}:
            return None

        type_rules: dict[str, type[object]] = {
            "string": str,
            "boolean": bool,
            "list": list,
            "dict": dict,
        }
        expected_type = type_rules.get(rule_name)

        if expected_type is not None:
            if not isinstance(field_value, expected_type):
                return self._message(field_name, rule_name)

            return None

        if rule_name == "integer":
            return self._validate_integer_rule(field_name, field_value)

        if rule_name == "email":
            return self._validate_email_rule(field_name, field_value)

        return None

    def _validate_integer_rule(
        self,
        field_name: str,
        field_value: object,
    ) -> str | None:
        if not isinstance(field_value, int) or isinstance(field_value, bool):
            return self._message(field_name, "integer")

        return None

    def _validate_email_rule(
        self,
        field_name: str,
        field_value: object,
    ) -> str | None:
        if not isinstance(field_value, str):
            return self._message(field_name, "email")

        try:
            validate_email(field_value)
        except DjangoValidationError:
            return self._message(field_name, "email")

        return None

    def _validate_parameterized_rule(
        self,
        field_name: str,
        field_value: object,
        rule_name: str,
        rule_value: object,
    ) -> str | None:
        match rule_name:
            case "max_length":
                return self._validate_max_length(field_name, field_value, rule_value)
            case "min_length":
                return self._validate_min_length(field_name, field_value, rule_value)
            case "min_value":
                return self._validate_min_value(field_name, field_value, rule_value)
            case "choices":
                return self._validate_choices(field_name, field_value, rule_value)
            case "unique":
                return self._validate_unique(field_name, field_value, rule_value)

        return None

    def _validate_max_length(
        self,
        field_name: str,
        field_value: object,
        rule_value: object,
    ) -> str | None:
        if not isinstance(rule_value, int):
            return self._message(field_name, "max_length")

        if not isinstance(field_value, Sized) or len(field_value) > rule_value:
            return self._message(field_name, "max_length")

        return None

    def _validate_min_length(
        self,
        field_name: str,
        field_value: object,
        rule_value: object,
    ) -> str | None:
        if not isinstance(rule_value, int):
            return self._message(field_name, "min_length")

        if not isinstance(field_value, Sized) or len(field_value) < rule_value:
            return self._message(field_name, "min_length")

        return None

    def _validate_min_value(
        self,
        field_name: str,
        field_value: object,
        rule_value: object,
    ) -> str | None:
        if not isinstance(rule_value, int):
            return self._message(field_name, "min_value")

        if not isinstance(field_value, int) or field_value < rule_value:
            return self._message(field_name, "min_value")

        return None

    def _validate_choices(
        self,
        field_name: str,
        field_value: object,
        rule_value: object,
    ) -> str | None:
        if not isinstance(rule_value, Collection) or field_value not in rule_value:
            return self._message(field_name, "choices")

        return None

    def _validate_unique(
        self,
        field_name: str,
        field_value: object,
        rule_value: object,
    ) -> str | None:
        if not isinstance(rule_value, UniqueRuleOptions):
            return None

        if not self._value_exists(field_value, rule_value):
            return None

        return self._message(field_name, "unique")

    def _value_exists(
        self,
        field_value: object,
        unique_options: UniqueRuleOptions,
    ) -> bool:
        if field_value in unique_options.ignored_values:
            return False

        lookup_suffix = "__iexact" if unique_options.case_insensitive else ""
        lookup = f"{unique_options.field}{lookup_suffix}"
        queryset = unique_options.model._default_manager.filter(**{lookup: field_value})

        if self.instance is not None and isinstance(self.instance, unique_options.model):
            queryset = queryset.exclude(pk=self.instance.pk)

        return queryset.exists()

    def _message(self, field_name: str, rule_name: str) -> str:
        configured_message = self.messages.get(field_name, {}).get(rule_name)

        if configured_message is not None:
            return configured_message

        default_messages = {
            "required": "This field is required.",
            "nullable": "This field may be null.",
            "string": "This field must be a string.",
            "integer": "This field must be an integer.",
            "boolean": "This field must be a boolean.",
            "list": "This field must be a list.",
            "dict": "This field must be a dictionary.",
            "email": "Enter a valid email address.",
            "max_length": "This field is too long.",
            "min_length": "This field is too short.",
            "min_value": "This field is below the minimum value.",
            "choices": "Select a valid choice.",
            "unique": "This value is already in use.",
        }

        return default_messages[rule_name]
