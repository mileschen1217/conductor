#!/usr/bin/env bash
# audit-single-writer.sh — post-hoc single-writer audit (spec AC-10, portable half).
# Input: a run-journal JSONL; each line {"phase","worker","action","path"}.
# Violation: any action=="write" on a phase=="parallel" line.
set -u
[ $# -eq 1 ] || { echo "usage: audit-single-writer.sh <journal.jsonl>"; exit 2; }
python3 - "$1" <<'PYEOF'
import json, sys
violations = []
with open(sys.argv[1], encoding="utf-8") as f:
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
