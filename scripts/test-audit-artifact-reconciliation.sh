#!/usr/bin/env bash
# Runs audit-artifact-reconciliation.py --self-test over the six reconciliation
# fixtures (consumer-gated-ceremony AC-16). Fixture subdir prefix encodes
# expectation: clean-* → exit 0; orphan-* → exit 1 (orphan flagged).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/audit-artifact-reconciliation.py" --self-test
