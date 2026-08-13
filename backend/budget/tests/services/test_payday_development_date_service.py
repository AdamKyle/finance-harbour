import datetime
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings

from authentication.models import User
from budget.services.payday_development_date_service import (
    load_payday_development_date,
    reset_payday_development_date,
    resolve_payday_effective_date,
    set_payday_development_date,
)


class PaydayDevelopmentDateServiceTest(TestCase):
    @override_settings(DEBUG=True)
    def test_user_override_can_be_set_loaded_and_reset(self) -> None:
        owner = User.objects.create_user(email="dev-date-owner@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                set_payday_development_date(owner, datetime.date(2026, 8, 21))
                self.assertEqual(load_payday_development_date(owner), datetime.date(2026, 8, 21))
                reset_payday_development_date(owner)
                self.assertIsNone(load_payday_development_date(owner))

    @override_settings(DEBUG=True)
    def test_one_users_override_does_not_affect_another(self) -> None:
        jane = User.objects.create_user(email="dev-date-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="dev-date-bob@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                set_payday_development_date(jane, datetime.date(2026, 8, 21))
                self.assertEqual(load_payday_development_date(jane), datetime.date(2026, 8, 21))
                self.assertIsNone(load_payday_development_date(bob))

    @override_settings(DEBUG=True)
    def test_invalid_stored_value_is_ignored(self) -> None:
        owner = User.objects.create_user(email="dev-date-invalid@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            path.write_text(f'{{"{owner.id}": "not-a-date"}}', encoding="utf-8")
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                self.assertIsNone(load_payday_development_date(owner))

    @override_settings(DEBUG=False)
    def test_non_debug_ignores_override_and_refuses_writes(self) -> None:
        owner = User.objects.create_user(email="dev-date-production@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            path.write_text(f'{{"{owner.id}": "2026-08-21"}}', encoding="utf-8")
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                self.assertIsNone(load_payday_development_date(owner))
                with self.assertRaises(RuntimeError):
                    set_payday_development_date(owner, datetime.date(2026, 8, 21))

    @override_settings(DEBUG=True)
    def test_real_date_is_used_without_override(self) -> None:
        owner = User.objects.create_user(email="dev-date-real@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                self.assertEqual(resolve_payday_effective_date(owner), datetime.date.today())
