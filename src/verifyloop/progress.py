from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from verifyloop.runner import TestRunResult


@dataclass(frozen=True)
class ProgressEntry:
    name: str
    ok: bool
    passed: int
    failed: int
    errors: int
    duration_s: float
    at: str


class ProgressLog:
    """Append-only progress record, keyed by check name, backed by a JSON file.

    Written for a long-running session to check "did this already pass"
    without re-running everything, and for whoever resumes the session to
    see what's been verified so far without reading the full output log.
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        if not self._path.exists():
            self._path.write_text(json.dumps({"entries": []}))

    def record(self, name: str, result: TestRunResult) -> ProgressEntry:
        entry = ProgressEntry(
            name=name,
            ok=result.ok,
            passed=result.passed,
            failed=result.failed,
            errors=result.errors,
            duration_s=result.duration_s,
            at=datetime.now(timezone.utc).isoformat(),
        )
        data = json.loads(self._path.read_text())
        data["entries"].append(asdict(entry))
        self._path.write_text(json.dumps(data, indent=2))
        return entry

    def latest(self, name: str) -> ProgressEntry | None:
        matches = [e for e in json.loads(self._path.read_text())["entries"] if e["name"] == name]
        return ProgressEntry(**matches[-1]) if matches else None

    def summary(self) -> dict[str, bool]:
        data = json.loads(self._path.read_text())["entries"]
        latest_by_name: dict[str, bool] = {}
        for entry in data:
            latest_by_name[entry["name"]] = entry["ok"]
        return latest_by_name
