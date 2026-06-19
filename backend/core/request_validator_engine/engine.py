from collections.abc import Mapping, Sized

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
            if validation_rule in {"required", "nullable"}:
                return None

            if validation_rule == "string":
                if not isinstance(field_value, str):
                    return self._message(field_name, validation_rule)

                return None

            if validation_rule == "integer":
                if not isinstance(field_value, int) or isinstance(field_value, bool):
                    return self._message(field_name, validation_rule)

                return None

            if validation_rule == "boolean":
                if not isinstance(field_value, bool):
                    return self._message(field_name, validation_rule)

                return None

            if validation_rule == "list":
                if not isinstance(field_value, list):
                    return self._message(field_name, validation_rule)

                return None

            if validation_rule == "dict":
                if not isinstance(field_value, dict):
                    return self._message(field_name, validation_rule)

                return None

            if validation_rule == "email":
                if not isinstance(field_value, str):
                    return self._message(field_name, validation_rule)

                try:
                    validate_email(field_value)
                except DjangoValidationError:
                    return self._message(field_name, validation_rule)

                return None

        rule_name, rule_value = validation_rule

        if rule_name == "max_length":
            if not isinstance(field_value, Sized) or len(field_value) > rule_value:
                return self._message(field_name, rule_name)

            return None

        if rule_name == "min_length":
            if not isinstance(field_value, Sized) or len(field_value) < rule_value:
                return self._message(field_name, rule_name)

            return None

        if rule_name == "choices":
            if field_value not in rule_value:
                return self._message(field_name, rule_name)

            return None

        if rule_name == "unique" and self._value_exists(field_value, rule_value):
            return self._message(field_name, rule_name)

        return None

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
            "choices": "Select a valid choice.",
            "unique": "This value is already in use.",
        }

        return default_messages[rule_name]
