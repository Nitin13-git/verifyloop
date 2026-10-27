from __future__ import annotations

import re
from collections import Counter

from verifyloop.runner import TestRunResult

_RAISED_ERROR_LINE = re.compile(r"^E\s+(\w+(?:Error|Exception|Warning)):", re.MULTILINE)
_ASSERT_LINE = re.compile(r"^E\s+assert\b", re.MULTILINE)
_TIMEOUT_HINT = re.compile(r"timed out|timeout", re.IGNORECASE)


def triage(result: TestRunResult) -> Counter[str]:
    """Categorize a failing run's output by exception type.

    Scans pytest's `E   SomeError: ...` traceback lines for explicitly
    raised exceptions, and `E   assert ...` lines (pytest's assertion
    rewriting doesn't name `AssertionError` explicitly) for plain
    `assert` failures — between the two, that covers how pytest reports
    almost every failure.
    """
    if result.ok:
        return Counter()

    categories = Counter(_RAISED_ERROR_LINE.findall(result.output))
    assert_failures = len(_ASSERT_LINE.findall(result.output))
    if assert_failures:
        categories["AssertionError"] += assert_failures
    if not categories and _TIMEOUT_HINT.search(result.output):
        categories["Timeout"] += 1
    if not categories and (result.failed or result.errors):
        categories["Unclassified"] += result.failed + result.errors
    return categories
