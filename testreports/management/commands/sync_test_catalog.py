"""python manage.py sync_test_catalog — copy tests/catalog.py into the TestCase table (reports database)."""

from django.core.management.base import BaseCommand

from testreports.services import sync_catalog


class Command(BaseCommand):
    help = "Load the test case catalogue (tests/catalog.py) into the reports database."

    def handle(self, *args, **options):
        from tests.catalog import TEST_CASES

        self.stdout.write(self.style.SUCCESS(f"Test catalogue synced: {sync_catalog(TEST_CASES)} test cases."))
