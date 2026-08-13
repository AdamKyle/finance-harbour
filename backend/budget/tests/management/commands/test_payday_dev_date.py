import datetime
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from authentication.models import User
from budget.models import BudgetPayPeriod, BudgetPlan


class PaydayDevDateCommandTest(TestCase):
    @override_settings(DEBUG=False)
    def test_non_debug_refuses_operation(self) -> None:
        owner = User.objects.create_user(email="dev-command-production@example.com", password="StrongPassword123!")

        with self.assertRaisesMessage(CommandError, "available only when DEBUG is true"):
            call_command("payday_dev_date", "--user-id", owner.id, "--show")

    @override_settings(DEBUG=True)
    def test_set_and_show_are_user_scoped(self) -> None:
        jane = User.objects.create_user(email="dev-command-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="dev-command-bob@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                call_command("payday_dev_date", "--user-id", jane.id, "--set", "2026-08-21")
                jane_output = StringIO()
                bob_output = StringIO()
                call_command("payday_dev_date", "--user-id", jane.id, "--show", stdout=jane_output)
                call_command("payday_dev_date", "--user-id", bob.id, "--show", stdout=bob_output)

        self.assertEqual(jane_output.getvalue().strip(), "2026-08-21")
        self.assertEqual(bob_output.getvalue().strip(), "real date")

    @override_settings(DEBUG=True)
    def test_reset_removes_override(self) -> None:
        owner = User.objects.create_user(email="dev-command-reset@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                call_command("payday_dev_date", "--user-id", owner.id, "--set", "2026-08-21")
                call_command("payday_dev_date", "--user-id", owner.id, "--reset")
                output = StringIO()
                call_command("payday_dev_date", "--user-id", owner.id, "--show", stdout=output)

        self.assertEqual(output.getvalue().strip(), "real date")

    @override_settings(DEBUG=True)
    def test_next_sets_next_owned_payday(self) -> None:
        owner = User.objects.create_user(email="dev-command-next@example.com", password="StrongPassword123!")
        plan = BudgetPlan.objects.create(
            user=owner,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 8, 1),
            pay_period_type="MONTHLY",
            income_per_pay_period_cents=100000,
        )
        BudgetPayPeriod.objects.create(
            plan=plan,
            sequence=0,
            pay_date=datetime.date(2026, 8, 21),
            pay_cheque_cents=100000,
            total_available_cents=100000,
            left_over_cents=100000,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            with patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path):
                call_command("payday_dev_date", "--user-id", owner.id, "--set", "2026-08-01")
                output = StringIO()
                call_command("payday_dev_date", "--user-id", owner.id, "--next", stdout=output)

        self.assertEqual(output.getvalue().strip(), "2026-08-21")

    @override_settings(DEBUG=True)
    def test_next_requires_user_id(self) -> None:
        with self.assertRaises(CommandError):
            call_command("payday_dev_date", "--next")

    @override_settings(DEBUG=True)
    def test_unknown_user_is_rejected(self) -> None:
        with self.assertRaisesMessage(CommandError, "requested user does not exist"):
            call_command("payday_dev_date", "--user-id", 999999, "--show")

    @override_settings(DEBUG=True)
    def test_no_next_payday_is_rejected(self) -> None:
        owner = User.objects.create_user(email="dev-command-no-next@example.com", password="StrongPassword123!")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "payday-dates.json"
            with (
                patch("budget.services.payday_development_date_service.PAYDAY_DEVELOPMENT_DATE_PATH", path),
                self.assertRaisesMessage(CommandError, "No later Payday exists"),
            ):
                call_command("payday_dev_date", "--user-id", owner.id, "--next")
