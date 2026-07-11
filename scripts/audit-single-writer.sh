#!/usr/bin/env bash
# audit-single-writer.sh — post-hoc single-writer audit (spec AC-10, portable half).
# Input: a run-journal JSONL; each line {"phase","worker","action","path"}.
# Violation: any action=="write" on a phase=="parallel" line.
# 0/1-worker degenerate semantics (v2 REQ-1): an inline or 1-worker run's
# journal typically contains no parallel lines at all; AUDIT CLEAN then means
# "trivially clean — single-writer held by construction". The audit surface
# that remains for such runs is the v2 run journal's judgment stream
# (audit-judgment-flow.py), not this script. disjoint-write runs DO exercise
# this audit: each write surface is one pen, and the merge-back is a
# single-threaded phase.
set -u
[ $# -eq 1 ] || { echo "usage: audit-single-writer.sh <journal.jsonl>"; exit 2; }
python3 - "$1" <<'PYEOF'
import json, sys
violations = []
try:
    f = open(sys.argv[1], encoding="utf-8")
except OSError as err:
    print(f"MALFORMED: cannot read journal: {err}")
    sys.exit(2)
with f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError as err:
            print(f"MALFORMED: line {i}: {err}")
            sys.exit(2)
        for key in ("phase", "worker", "action", "path"):
            if key not in e:
                print(f"MALFORMED: line {i}: missing key {key}")
                sys.exit(2)
        if e["phase"] not in ("parallel", "single") or e["action"] not in ("read", "write"):
            print(f"MALFORMED: line {i}: bad phase/action value")
            sys.exit(2)
        if e.get("phase") == "parallel" and e.get("action") == "write":
            violations.append(
                f"VIOLATION: {e.get('worker', '?')} wrote {e.get('path', '?')} during parallel phase (line {i})"
            )
if violations:
    print("\n".join(violations))
    sys.exit(1)
print("AUDIT CLEAN")
sys.exit(0)
PYEOF
