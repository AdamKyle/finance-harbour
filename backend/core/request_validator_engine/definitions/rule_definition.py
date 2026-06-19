from collections.abc import Collection
from dataclasses import dataclass
from typing import Literal

from django.db.models import Model


@dataclass(frozen=True)
class UniqueRuleOptions:
    model: type[Model]
    field: str
    case_insensitive: bool = False
    ignored_values: tuple[object, ...] = ()


type SimpleValidationRule = Literal[
    "required",
    "nullable",
    "string",
    "integer",
    "boolean",
    "list",
    "dict",
    "email",
]
type ParameterizedValidationRule = (
    tuple[Literal["max_length", "min_length"], int]
    | tuple[Literal["choices"], Collection[object]]
    | tuple[Literal["unique"], UniqueRuleOptions]
)
type ValidationRule = SimpleValidationRule | ParameterizedValidationRule
type ValidationRules = dict[str, tuple[ValidationRule, ...]]
type ValidationMessages = dict[str, dict[str, str]]
