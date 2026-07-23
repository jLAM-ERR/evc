#!/usr/bin/env python3
"""kb-lint CLI — thin wrapper over evclib (CONTRACT.md §CLI protocols).

Usage: kb_lint.py [--root PATH] [--layout evc|project] [--write]
Exit codes: 0 clean, 1 warnings, 2 hard fail.
Default mode is read-only (the CI gate); --write is local pre-flight only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from evclib import kb_checks  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kb-lint", description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="repo root")
    parser.add_argument("--layout", choices=("evc", "project"), default="evc")
    parser.add_argument(
        "--write",
        action="store_true",
        help="local pre-flight: maintain last_verified (never use in CI)",
    )
    args = parser.parse_args(argv)
    findings, code = kb_checks.run_all(args.root, args.layout, write=args.write)
    for f in findings:
        print(f"{f.severity.upper()} [{f.check}] {f.path}: {f.message}")
    if findings:
        print(f"kb-lint: {len(findings)} finding(s), exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
