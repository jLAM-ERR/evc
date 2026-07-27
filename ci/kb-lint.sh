#!/bin/sh
# CI-agnostic kb-lint entrypoint (CONTRACT.md §CLI protocols).
# Read-only by design: no --write, no network, stdlib-only Python.
# Wire this single line into any CI (works in offline/air-gapped runners).
set -eu
cd "$(dirname "$0")/.."
exec python3 tools/kb_lint.py --layout hub
