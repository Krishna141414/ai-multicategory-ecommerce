"""Admin "Test Reports": the automated test runs stored in the reports database.

Brief: Generate HTML Test Report, View Passed / Failed Test Cases, Capture Screenshots for Failed Test Cases,
View Test Execution Summary. Runs are written by tests/conftest.py through `manage.py record_test_run`.
"""

import mimetypes

from django.conf import settings
from django.db.models import Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from adminpanel.views.common import paginate
from core.permissions import admin_required
from testreports.models import TestCase, TestExecution, TestSummary

STATUSES = [s for s, _ in TestExecution.Status.choices]


def report_file_url(path: str) -> str:
    """'reports/runs/x/report.html' → the admin URL that serves it ('' when there is no file)."""
    from django.urls import reverse

    if not path:
        return ""
    relative = path.removeprefix("reports/")
    return reverse("adminpanel:test_report_file", args=[relative])


@admin_required
def report_list(request):
    """Every recorded run, newest first, with the latest run's summary on top."""
    runs = TestSummary.objects.all()
    latest = runs.first()
    if latest:
        latest.report_url = report_file_url(latest.report_path)
    page = paginate(request, runs)
    for run in page:
        run.report_url = report_file_url(run.report_path)
    return render(request, "adminpanel/reports/list.html", {
        "section": "reports", "page": page, "latest": latest, "case_count": TestCase.objects.count(),
    })


@admin_required
def report_detail(request, pk: int):
    """One run: the result of every test, filterable by Passed / Failed / Skipped, with failure screenshots."""
    run = get_object_or_404(TestSummary, pk=pk)
    run.report_url = report_file_url(run.report_path)
    status = request.GET.get("status", "")
    module = request.GET.get("module", "")
    executions = run.executions.select_related("test_case")
    counts = dict(executions.values_list("status").annotate(n=Count("id")))
    modules = sorted({e.test_case.module for e in executions if e.test_case})
    if status in STATUSES:
        executions = executions.filter(status=status)
    if module:
        executions = executions.filter(test_case__module=module)
    rows = list(executions)
    for row in rows:
        row.screenshot_url = report_file_url(row.screenshot_path)
    return render(request, "adminpanel/reports/detail.html", {
        "section": "reports", "run": run, "rows": rows, "status": status, "module": module, "modules": modules,
        "tabs": [("", "All", run.total_tests)] + [(s, s, counts.get(s, 0)) for s in STATUSES],
    })


@admin_required
def report_file(request, path: str):
    """Serve a file from reports/ (HTML report, screenshot) to the admin only, never outside that folder."""
    root = settings.REPORTS_DIR.resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise Http404("Report file not found")
    content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    return FileResponse(target.open("rb"), content_type=content_type)
