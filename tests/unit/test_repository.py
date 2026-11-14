"""The repository ships everything the app needs: no template, static file or Python source is hidden by .gitignore.
(A loose `reports/` pattern once hid templates/adminpanel/reports/ from every fresh clone.)"""

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIRS = ["templates", "static", "accounts", "adminpanel", "catalog", "config", "core", "messaging", "orders",
               "recommender", "reviews", "testreports", "tests"]


@pytest.mark.skipif(shutil.which("git") is None or not (ROOT / ".git").exists(), reason="needs git and a checkout")
def test_no_source_file_is_git_ignored():
    files = [p.relative_to(ROOT).as_posix() for d in SOURCE_DIRS for p in (ROOT / d).rglob("*")
             if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    # bytes, not text: on Windows text mode would send CRLF line endings and git would see "name.html\r"
    result = subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(files).encode(), cwd=ROOT, capture_output=True)
    ignored = [line.strip() for line in result.stdout.decode().splitlines() if line.strip()]
    assert ignored == [], f"source files hidden by .gitignore: {ignored[:10]}"
