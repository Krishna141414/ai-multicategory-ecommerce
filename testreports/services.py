"""Store automated test results in the reports database (brief: Test Execution Report, Test Summary Report).

The pytest run writes reports/runs/<stamp>/results.json; `record_run` turns it into one TestSummary row and one
TestExecution row per test. Shop data (the default database) is never touched.
"""

import json
from datetime import datetime
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from testreports.models import TestCase, TestExecution, TestSummary


def sync_catalog(cases: dict[str, dict]) -> int:
    """Copy the test case catalogue (tests/catalog.py) into the TestCase table. Returns the number of cases."""
    for tc_id, fields in cases.items():
        TestCase.objects.update_or_create(id=tc_id, defaults=fields)
    return len(cases)


@transaction.atomic(using="reports")
def record_run(results_path: Path, cases: dict[str, dict] | None = None) -> TestSummary:
    """Save one pytest run (summary + executions) from its results.json."""
    if cases:
        sync_catalog(cases)
    data = json.loads(Path(results_path).read_text(encoding="utf-8"))
    started = datetime.fromisoformat(data["started"])
    if timezone.is_naive(started):
        started = timezone.make_aware(started)
    tests = data["tests"]
    summary = TestSummary.objects.create(
        execution_date=started,
        total_tests=len(tests),
        passed_tests=sum(t["status"] == TestExecution.Status.PASSED for t in tests),
        failed_tests=sum(t["status"] == TestExecution.Status.FAILED for t in tests),
        skipped_tests=sum(t["status"] == TestExecution.Status.SKIPPED for t in tests),
        total_execution_time=round(data["duration"], 2),
        report_path=data.get("report_path", ""),
        command=data.get("command", "")[:300],
        browser_mode=data.get("browser_mode", ""),
    )
    known = set(TestCase.objects.values_list("id", flat=True))
    TestExecution.objects.bulk_create([
        TestExecution(summary=summary, test_case_id=t["tc"] if t.get("tc") in known else None, node_id=t["node_id"][:300],
                      execution_date=started, actual_result=t["actual_result"], status=t["status"],
                      execution_time=round(t["duration"], 3), screenshot_path=t.get("screenshot", ""))
        for t in tests
    ])
    return summary
