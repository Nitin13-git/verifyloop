# VerifyLoop

Runs your verification command, parses whether it actually passed, triages
what kind of thing failed, and records it to an append-only progress log —
so a long-running agent session (or whoever resumes it) can check "did this
already pass" without re-running everything or trusting a self-report.

## How it works

- **`run(command)`** — runs a shell command (built for pytest, works with
  anything that prints `N passed`/`N failed`/`N error` style summaries) and
  parses pass/fail/error/skip counts plus duration.
- **`triage(result)`** — scans pytest's `E   SomeError: ...` traceback
  lines and returns a `Counter` of exception types, so "3 failed" becomes
  "2 AssertionError, 1 ValueError" without reading the full log.
- **`ProgressLog`** — append-only JSON log keyed by check name. `record`
  appends a run's outcome; `summary()` returns the latest pass/fail per
  check name.

## Quickstart

```bash
pip install -e ".[dev]"
verifyloop "pytest -q" --name unit-tests --progress progress.json
pytest
```

```python
from verifyloop import ProgressLog, run, triage

result = run("pytest -q tests/")
ProgressLog("progress.json").record("unit-tests", result)

if not result.ok:
    print(triage(result))  # Counter({'AssertionError': 2, 'ValueError': 1})
```

## License

MIT
