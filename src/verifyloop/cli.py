from __future__ import annotations

import argparse
import sys

from verifyloop.progress import ProgressLog
from verifyloop.runner import run
from verifyloop.triage import triage


def main() -> None:
    parser = argparse.ArgumentParser(prog="verifyloop")
    parser.add_argument("command", help="verification command to run, e.g. 'pytest -q'")
    parser.add_argument("--name", default="default", help="check name to record progress under")
    parser.add_argument("--progress", default="progress.json")
    args = parser.parse_args()

    result = run(args.command)
    log = ProgressLog(args.progress)
    log.record(args.name, result)

    print(f"{args.name}: {'PASS' if result.ok else 'FAIL'} "
          f"({result.passed} passed, {result.failed} failed, {result.errors} errors)")

    if not result.ok:
        for category, count in triage(result).items():
            print(f"  {category}: {count}")

    sys.exit(0 if result.ok else 1)


if __name__ == "__main__":
    main()
