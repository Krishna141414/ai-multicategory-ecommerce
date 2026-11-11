"""python manage.py clean_test_reports [--delete]

Lists the run folders in reports/runs/ and reports/screenshots/ and says which ones belong to a run stored in the
reports database (shown on the admin Test Reports page) and which are leftovers (runs made with --no-record, or runs
whose database row was deleted). Nothing is removed unless you add --delete, and then only the leftovers.
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from testreports.models import TestExecution, TestSummary

SUBFOLDERS = ("runs", "screenshots")


def linked_run_names() -> set[str]:
    """Run folder names (e.g. 20261111-135630) that a recorded run points at."""
    names = set()
    for path in TestSummary.objects.exclude(report_path="").values_list("report_path", flat=True):
        names.add(Path(path).parent.name)  # reports/runs/<name>/report.html
    for path in TestExecution.objects.exclude(screenshot_path="").values_list("screenshot_path", flat=True):
        names.add(Path(path).parent.name)  # reports/screenshots/<name>/<test>.png
    return names


class Command(BaseCommand):
    help = "Show which report folders are linked to recorded runs and which are leftovers; --delete removes the leftovers."

    def add_arguments(self, parser):
        parser.add_argument("--delete", action="store_true", help="Delete the leftover folders (default: only list them).")

    def handle(self, *args, delete: bool = False, **options):
        root = Path(settings.REPORTS_DIR)
        linked = linked_run_names()
        leftovers = []
        for sub in SUBFOLDERS:
            folder = root / sub
            if not folder.is_dir():
                continue
            self.stdout.write(self.style.MIGRATE_HEADING(f"reports/{sub}/"))
            for run in sorted(p for p in folder.iterdir() if p.is_dir()):
                if run.name in linked:
                    self.stdout.write(f"  keep      {run.name}  (linked to a recorded run)")
                else:
                    self.stdout.write(f"  leftover  {run.name}")
                    leftovers.append(run)
        if not leftovers:
            self.stdout.write(self.style.SUCCESS("No leftover folders."))
            return
        if not delete:
            self.stdout.write(self.style.WARNING(f"{len(leftovers)} leftover folder(s). Run again with --delete to remove them."))
            return
        for run in leftovers:
            # only ever a direct child of reports/runs or reports/screenshots
            if run.resolve().parent.parent != root.resolve():
                continue
            shutil.rmtree(run)
        self.stdout.write(self.style.SUCCESS(f"Deleted {len(leftovers)} leftover folder(s)."))
