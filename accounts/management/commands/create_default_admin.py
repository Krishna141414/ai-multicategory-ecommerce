"""Create the default store admin from the values in .env."""

from django.core.management.base import BaseCommand, CommandError

from accounts.services import ensure_default_admin


class Command(BaseCommand):
    help = "Create (or update) the store admin from ADMIN_USERNAME, ADMIN_PASSWORD and ADMIN_EMAIL in .env."

    def add_arguments(self, parser):
        parser.add_argument("--reset-password", action="store_true", help="Also reset an existing admin's password from .env.")

    def handle(self, *args, **options):
        try:
            user, created = ensure_default_admin(reset_password=options["reset_password"])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} admin '{user.username}'."))
        self.stdout.write(self.style.WARNING("Change the default admin password before any deployment."))
