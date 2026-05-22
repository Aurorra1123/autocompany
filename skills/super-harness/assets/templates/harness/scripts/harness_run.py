#!/usr/bin/env python3
"""Unified experiment entrypoint.

This is a thin alias for record_experiment.py so teams can standardize on a
short command name such as `python3 harness/scripts/harness_run.py ...`.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def main() -> int:
    recorder = Path(__file__).resolve().with_name("record_experiment.py")
    return subprocess.call([sys.executable, str(recorder), *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())
