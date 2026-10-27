from __future__ import annotations

import re
import shlex
import subprocess
import time
from dataclasses import dataclass

_SUMMARY_COUNT = re.compile(r"(\d+)\s+(passed|failed|error|skipped)")


@dataclass(frozen=True)
class TestRunResult:
    command: str
    passed: int
    failed: int
    errors: int
    skipped: int
    duration_s: float
    output: str

    @property
    def ok(self) -> bool:
        return self.failed == 0 and self.errors == 0


def run(command: str, *, timeout_s: float = 120.0) -> TestRunResult:
    """Run `command` (expected to be a pytest invocation) and parse its summary line."""
    start = time.monotonic()
    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired as exc:
        output = f"timed out after {timeout_s}s: {exc}"
    duration_s = time.monotonic() - start

    counts = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
    for match in _SUMMARY_COUNT.finditer(output):
        count, kind = match.groups()
        counts[kind] = int(count)

    return TestRunResult(
        command=command,
        passed=counts["passed"],
        failed=counts["failed"],
        errors=counts["error"],
        skipped=counts["skipped"],
        duration_s=duration_s,
        output=output,
    )
