"""python manage.py record_test_run <results.json> — store one pytest run in the reports database.

Called by tests/conftest.py at the end of every recorded run (in a separate process, so it writes to the real
reports database and never to the test databases).
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from testreports.services import record_run


class Command(BaseCommand):
    help = "Record a pytest run (summary + one execution per test) from a results.json file."

    def add_arguments(self, parser):
        parser.add_argument("results", type=Path)

    def handle(self, *args, results: Path, **options):
        from tests.catalog import TEST_CASES

        if not results.exists():
            raise CommandError(f"{results} not found")
        summary = record_run(results, TEST_CASES)
        self.stdout.write(self.style.SUCCESS(
            f"Recorded run {summary.pk}: {summary.passed_tests} passed, {summary.failed_tests} failed, "
            f"{summary.skipped_tests} skipped of {summary.total_tests} in {summary.total_execution_time:.1f} s."))
