"""Wipe the shop database and load fresh demo data (for a clean video/demo run).

Only the "default" (shop) database is flushed. Test reports in reports.sqlite3 are kept.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete all shop data and reload the demo data. Test reports are kept."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")

    def handle(self, *args, **options):
        if not options["yes"]:
            answer = input("This deletes ALL shop data (orders, customers, products). Type RESET to continue: ")
            if answer.strip() != "RESET":
                self.stdout.write("Cancelled.")
                return
        call_command("flush", database="default", interactive=False, verbosity=0)
        call_command("create_default_admin")
        call_command("seed_demo")
        self.stdout.write(self.style.SUCCESS("Demo data reset."))
