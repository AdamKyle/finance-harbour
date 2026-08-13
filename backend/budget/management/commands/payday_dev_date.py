import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from authentication.models import User
from budget.models import BudgetPayPeriod
from budget.services.payday_development_date_service import (
    load_payday_development_date,
    reset_payday_development_date,
    resolve_payday_effective_date,
    set_payday_development_date,
)


class Command(BaseCommand):
    help = "Manage a user's development-only Payday effective date."

    def add_arguments(self, parser: CommandParser) -> None:
        actions = parser.add_mutually_exclusive_group(required=True)
        actions.add_argument("--show", action="store_true")
        actions.add_argument("--set", dest="set_date")
        actions.add_argument("--reset", action="store_true")
        actions.add_argument("--next", action="store_true")
        parser.add_argument("--user-id", type=int, required=True)

    def handle(self, *args: object, **options: object) -> None:
        if not settings.DEBUG:
            raise CommandError("This command is available only when DEBUG is true.")

        user_id = options["user_id"]
        user = User.objects.filter(id=user_id).first()

        if user is None:
            raise CommandError("The requested user does not exist.")

        if options["show"]:
            value = load_payday_development_date(user)
            self.stdout.write(value.isoformat() if value is not None else "real date")
            return

        if options["reset"]:
            reset_payday_development_date(user)
            self.stdout.write(self.style.SUCCESS("Payday development date reset."))
            return

        if options["next"]:
            effective_date = resolve_payday_effective_date(user)
            next_date = (
                BudgetPayPeriod.objects.filter(plan__user=user, pay_date__gt=effective_date)
                .order_by("pay_date")
                .values_list("pay_date", flat=True)
                .first()
            )
            if next_date is None:
                raise CommandError("No later Payday exists for this user.")
            set_payday_development_date(user, next_date)
            self.stdout.write(self.style.SUCCESS(next_date.isoformat()))
            return

        submitted_date = options["set_date"]
        try:
            value = datetime.date.fromisoformat(str(submitted_date))
        except ValueError as error:
            raise CommandError("--set requires YYYY-MM-DD.") from error
        set_payday_development_date(user, value)
        self.stdout.write(self.style.SUCCESS(value.isoformat()))
