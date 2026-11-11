"""Shared pytest setup for the whole suite.

- Unit tests use the Django test client (no browser).
- Browser tests (Playwright sync API) run against pytest-django's `live_server`, which uses the separate test
  database (test_db.sqlite3), flushed between tests: the real db.sqlite3 is never touched.
- Every failure is screenshotted to reports/screenshots/<run>/ and embedded in the HTML report.
- Every run is written to reports/runs/<run>/results.json and stored in the reports database
  (TestSummary + TestExecution) by `manage.py record_test_run`, unless --no-record is given.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Playwright's sync API runs an event loop in the main thread; Django's ORM must still be usable from tests.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

import pytest  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
RUN = {"stamp": datetime.now().strftime("%Y%m%d-%H%M%S"), "started": datetime.now(), "tests": {}, "t0": time.perf_counter()}


# --------------------------------------------------------------------------- options and config

def pytest_addoption(parser):
    parser.addoption("--no-record", action="store_true", default=False,
                     help="Do not store this run in the reports database (the HTML report is still written).")


def pytest_html_report_title(report):
    report.title = "Velora automated test report"


@pytest.fixture(autouse=True)
def fast_password_hashing(settings):
    """Hash test passwords with a fast hasher (real hashing stays on in the app)."""
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# --------------------------------------------------------------------------- browser fixtures

@pytest.fixture
def site(live_server):
    """Base URL of the test server, e.g. http://localhost:54321."""
    return live_server.url


@pytest.fixture
def browser_context_args(browser_context_args):
    """Desktop viewport by default; every test gets a fresh context (no shared cookies)."""
    return {**browser_context_args, "viewport": {"width": 1366, "height": 900}}


def sign_in_with_cookie(page, site: str, user) -> None:
    """Sign a user in without typing: create a real session for them and hand the browser its cookie.
    Used by every test except the login tests themselves."""
    from django.conf import settings
    from django.test import Client

    client = Client()
    backend = "django.contrib.auth.backends.ModelBackend" if user.is_staff else "accounts.backends.EmailBackend"
    client.force_login(user, backend=backend)
    cookie = client.cookies[settings.SESSION_COOKIE_NAME]
    page.context.add_cookies([{"name": settings.SESSION_COOKIE_NAME, "value": cookie.value, "url": site}])


@pytest.fixture
def as_customer(page, site):
    """`as_customer(customer)` signs the browser in as that customer."""
    return lambda customer: sign_in_with_cookie(page, site, customer.user)


@pytest.fixture
def as_admin(page, site):
    """`as_admin(user)` signs the browser in as a staff user."""
    return lambda user: sign_in_with_cookie(page, site, user)


# --------------------------------------------------------------------------- failure screenshots + results

def _safe_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid.split("::", 1)[-1])[:120]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    marker = item.get_closest_marker("tc")
    if marker and not any(k == "tc" for k, _ in item.user_properties):
        item.user_properties.append(("tc", marker.args[0]))
    page = item.funcargs.get("page")
    if report.failed and report.when in ("setup", "call") and page is not None:
        folder = REPORTS / "screenshots" / RUN["stamp"]
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{_safe_name(item.nodeid)}.png"
        try:
            png = page.screenshot(path=str(path), full_page=True)
        except Exception:  # the page may already be closed; the failure itself is still reported
            png = None
        if png:
            item.user_properties.append(("screenshot", path.relative_to(ROOT).as_posix()))
            try:
                import pytest_html

                extras = getattr(report, "extras", [])
                extras.append(pytest_html.extras.png(base64.b64encode(png).decode()))
                report.extras = extras
            except ImportError:
                pass
    report.user_properties = list(item.user_properties)


def _first_line(report) -> str:
    text = getattr(report, "longreprtext", "") or str(report.longrepr or "")
    lines = [l.strip() for l in text.splitlines() if l.strip().startswith("E ")]
    return (lines[0][2:].strip() if lines else text.strip().splitlines()[-1] if text.strip() else "Failed")[:500]


def pytest_runtest_logreport(report):
    """Keep one result per test: Passed / Failed / Skipped, total time, screenshot, actual result."""
    entry = RUN["tests"].setdefault(report.nodeid, {"node_id": report.nodeid, "duration": 0.0, "status": None,
                                                     "actual_result": "", "tc": "", "screenshot": ""})
    entry["duration"] += report.duration
    props = dict(report.user_properties)
    entry["tc"] = props.get("tc", entry["tc"])
    entry["screenshot"] = props.get("screenshot", entry["screenshot"])
    if report.skipped and entry["status"] is None:
        reason = report.longrepr[2] if isinstance(report.longrepr, tuple) else str(report.longrepr)
        entry.update(status="Skipped", actual_result=f"Skipped: {reason}"[:500])
    elif report.failed and entry["status"] != "Failed":
        entry.update(status="Failed", actual_result=_first_line(report))
    elif report.when == "call" and report.passed and entry["status"] is None:
        from tests.catalog import TEST_CASES

        expected = TEST_CASES.get(entry["tc"], {}).get("expected_result", "")
        entry.update(status="Passed", actual_result=f"As expected. {expected}".strip())


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    """After pytest-html has written its report: keep a copy per run and store the run in the reports database."""
    tests = [t for t in RUN["tests"].values() if t["status"]]
    if not tests or hasattr(config, "workerinput"):
        return
    run_dir = REPORTS / "runs" / RUN["stamp"]
    run_dir.mkdir(parents=True, exist_ok=True)
    report_path = ""
    html = getattr(config.option, "htmlpath", None)
    if html and Path(html).exists():
        shutil.copy(html, run_dir / "report.html")
        report_path = (run_dir / "report.html").relative_to(ROOT).as_posix()
    results = {
        "started": RUN["started"].isoformat(timespec="seconds"),
        "duration": time.perf_counter() - RUN["t0"],
        "command": "pytest " + " ".join(config.invocation_params.args),
        "browser_mode": "headed" if config.getoption("headed", default=False) else "headless",
        "report_path": report_path,
        "tests": tests,
    }
    results_file = run_dir / "results.json"
    results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    if not config.getoption("no_record"):
        # a separate process uses the normal settings, so it writes to reports.sqlite3, never to a test database
        env = {k: v for k, v in os.environ.items() if k != "DJANGO_ALLOW_ASYNC_UNSAFE"}
        done = subprocess.run([sys.executable, str(ROOT / "manage.py"), "record_test_run", str(results_file)],
                              cwd=ROOT, env=env, capture_output=True, text=True)
        print("\n" + (done.stdout or done.stderr).strip())
