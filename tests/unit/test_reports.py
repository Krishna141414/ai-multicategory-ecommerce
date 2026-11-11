"""Test reporting: a run's results.json becomes TestSummary + TestExecution rows; the admin pages show them."""

import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from testreports.models import TestCase, TestExecution, TestSummary
from testreports.services import record_run, sync_catalog

pytestmark = [pytest.mark.unit, pytest.mark.django_db(databases=["default", "reports"])]

CASES = {
    "TC-CUS-02": {"test_name": "Customer Login", "module": "Customer", "test_description": "Sign in.", "expected_result": "Signed in."},
    "TC-CUS-03": {"test_name": "Invalid Customer Login", "module": "Customer", "test_description": "Wrong password.", "expected_result": "Error."},
}


@pytest.fixture
def results(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(json.dumps({
        "started": "2026-11-11T10:00:00", "duration": 12.5, "command": "pytest tests/customer", "browser_mode": "headless",
        "report_path": "reports/runs/20261111-100000/report.html",
        "tests": [
            {"node_id": "tests/customer/test_account.py::test_customer_login", "tc": "TC-CUS-02", "status": "Passed",
             "duration": 1.2, "actual_result": "As expected. Signed in.", "screenshot": ""},
            {"node_id": "tests/customer/test_account.py::test_invalid_customer_login", "tc": "TC-CUS-03", "status": "Failed",
             "duration": 5.1, "actual_result": "AssertionError: login-error not visible",
             "screenshot": "reports/screenshots/20261111-100000/test_invalid_customer_login.png"},
            {"node_id": "tests/unit/test_models.py::test_x", "tc": "", "status": "Skipped", "duration": 0.0,
             "actual_result": "Skipped: not today", "screenshot": ""},
        ],
    }), encoding="utf-8")
    return path


def test_record_run_creates_summary_and_executions(results):
    summary = record_run(results, CASES)
    assert (summary.total_tests, summary.passed_tests, summary.failed_tests, summary.skipped_tests) == (3, 1, 1, 1)
    assert summary.total_execution_time == 12.5 and summary.report_path.endswith("report.html")
    failed = TestExecution.objects.get(status="Failed")
    assert failed.test_case_id == "TC-CUS-03" and failed.screenshot_path.endswith(".png")
    assert TestExecution.objects.get(status="Skipped").test_case is None  # unit tests are not catalogued
    assert TestCase.objects.count() == 2


def test_sync_catalog_is_idempotent():
    sync_catalog(CASES)
    sync_catalog(CASES)
    assert TestCase.objects.count() == 2


@pytest.fixture
def admin_client(client):
    client.force_login(User.objects.create_user("storeadmin", password="x", is_staff=True))
    return client


def test_report_pages(admin_client, results):
    summary = record_run(results, CASES)
    listing = admin_client.get(reverse("adminpanel:test_reports")).content.decode()
    assert 'data-testid="latest-run"' in listing and f"Run {summary.pk}" in listing
    detail = admin_client.get(reverse("adminpanel:test_report_detail", args=[summary.pk]))
    assert len(detail.context["rows"]) == 3
    failed_only = admin_client.get(reverse("adminpanel:test_report_detail", args=[summary.pk]), {"status": "Failed"})
    assert [r.test_case_id for r in failed_only.context["rows"]] == ["TC-CUS-03"]
    assert failed_only.context["rows"][0].screenshot_url.endswith("test_invalid_customer_login.png")


def test_report_pages_are_admin_only(client):
    assert reverse("adminpanel:login") in client.get(reverse("adminpanel:test_reports"))["Location"]


def test_report_file_view_stays_inside_reports(admin_client, settings, tmp_path):
    settings.REPORTS_DIR = tmp_path
    (tmp_path / "runs").mkdir()
    (tmp_path / "runs" / "report.html").write_text("<h1>ok</h1>", encoding="utf-8")
    (tmp_path.parent / "secret.txt").write_text("nope", encoding="utf-8")
    ok = admin_client.get(reverse("adminpanel:test_report_file", args=["runs/report.html"]))
    assert ok.status_code == 200 and b"ok" in b"".join(ok.streaming_content)
    assert admin_client.get(reverse("adminpanel:test_report_file", args=["../secret.txt"])).status_code == 404
