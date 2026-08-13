import datetime
import json
import os
import tempfile
from pathlib import Path

from django.conf import settings

from authentication.models import User

PAYDAY_DEVELOPMENT_DATE_PATH = Path("/tmp/finance-harbour-payday-dev-dates.json")


def load_payday_development_date(user: User) -> datetime.date | None:
    if not settings.DEBUG:
        return None

    if not PAYDAY_DEVELOPMENT_DATE_PATH.exists():
        return None

    try:
        values = json.loads(PAYDAY_DEVELOPMENT_DATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError, OSError:
        return None

    if not isinstance(values, dict):
        return None

    value = values.get(str(user.id))

    if not isinstance(value, str):
        return None

    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def set_payday_development_date(user: User, value: datetime.date) -> None:
    _require_debug()
    values = _load_values()
    values[str(user.id)] = value.isoformat()
    _write_values(values)


def reset_payday_development_date(user: User) -> None:
    _require_debug()
    values = _load_values()
    values.pop(str(user.id), None)
    _write_values(values)


def resolve_payday_effective_date(user: User) -> datetime.date:
    from django.utils import timezone

    return load_payday_development_date(user) or timezone.localdate()


def _require_debug() -> None:
    if not settings.DEBUG:
        raise RuntimeError("Payday development dates are unavailable when DEBUG is false.")


def _load_values() -> dict[str, str]:
    if not PAYDAY_DEVELOPMENT_DATE_PATH.exists():
        return {}

    try:
        values = json.loads(PAYDAY_DEVELOPMENT_DATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError, OSError:
        return {}

    if not isinstance(values, dict):
        return {}

    return {str(key): str(value) for key, value in values.items()}


def _write_values(values: dict[str, str]) -> None:
    file_descriptor, temporary_path = tempfile.mkstemp(
        dir=PAYDAY_DEVELOPMENT_DATE_PATH.parent,
        prefix="finance-harbour-payday-",
        suffix=".json",
        text=True,
    )

    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as temporary_file:
            json.dump(values, temporary_file, sort_keys=True)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, PAYDAY_DEVELOPMENT_DATE_PATH)
    except BaseException:
        if Path(temporary_path).exists():
            Path(temporary_path).unlink()
        raise
