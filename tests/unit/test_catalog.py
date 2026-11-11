"""Every test case in the catalogue has exactly one automated test, and every tc() marker names a real case."""

import re
from collections import Counter
from pathlib import Path

import pytest

from tests.catalog import TEST_CASES

pytestmark = pytest.mark.unit
TESTS_DIR = Path(__file__).resolve().parent.parent


def test_every_catalogue_entry_has_one_test():
    used = Counter()
    for path in TESTS_DIR.rglob("test_*.py"):
        used.update(re.findall(r'@pytest\.mark\.tc\("([^"]+)"\)', path.read_text(encoding="utf-8")))
    assert set(used) - set(TEST_CASES) == set(), "tc() markers that are not in tests/catalog.py"
    assert set(TEST_CASES) - set(used) == set(), "catalogue entries without a test"
    assert [tc for tc, n in used.items() if n > 1] == [], "test cases covered by more than one test"


def test_catalogue_counts_match_the_brief():
    modules = Counter(case["module"] for case in TEST_CASES.values())
    assert modules == {"Admin": 22, "Customer": 27, "AI Recommendation": 8, "End-to-End": 4, "Negative": 8}
