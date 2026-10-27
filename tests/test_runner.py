import sys
from pathlib import Path

from verifyloop.progress import ProgressLog
from verifyloop.runner import run
from verifyloop.triage import triage

_PASSING = """
def test_ok():
    assert True
"""

_FAILING = """
def test_bad():
    assert 1 == 2

def test_also_bad():
    raise ValueError("boom")
"""


def _write_and_run(tmp_path: Path, content: str):
    test_file = tmp_path / "test_target.py"
    test_file.write_text(content)
    return run(f"{sys.executable} -m pytest -q {test_file}")


def test_run_parses_a_passing_suite(tmp_path: Path) -> None:
    result = _write_and_run(tmp_path, _PASSING)
    assert result.ok
    assert result.passed == 1
    assert result.failed == 0


def test_run_parses_a_failing_suite(tmp_path: Path) -> None:
    result = _write_and_run(tmp_path, _FAILING)
    assert not result.ok
    assert result.failed == 2


def test_triage_categorizes_exception_types(tmp_path: Path) -> None:
    result = _write_and_run(tmp_path, _FAILING)
    categories = triage(result)
    assert categories["AssertionError"] >= 1
    assert categories["ValueError"] >= 1


def test_triage_is_empty_for_a_passing_run(tmp_path: Path) -> None:
    result = _write_and_run(tmp_path, _PASSING)
    assert triage(result) == {}


def test_progress_log_records_and_summarizes(tmp_path: Path) -> None:
    log = ProgressLog(tmp_path / "progress.json")
    log.record("suite-a", _write_and_run(tmp_path, _PASSING))
    log.record("suite-b", _write_and_run(tmp_path, _FAILING))

    summary = log.summary()
    assert summary == {"suite-a": True, "suite-b": False}
    assert log.latest("suite-a").passed == 1
