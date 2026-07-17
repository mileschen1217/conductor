#!/usr/bin/env bash
# audit-single-writer.sh — post-hoc single-writer audit (invariant I2).
# Speaks BOTH journal dialects, auto-detected per file:
#
#   v1 dialect — lines {"phase","worker","action","path"}.
#     Violation: any action=="write" on a phase=="parallel" line.
#   v3 dialect — first line {"event":"commander_stamp",...}; write activity
#     lives on {"event":"dispatch","read_only":false,"wave":N} lines.
#     CLEAN when write dispatches never share a wave (writes single-threaded
#     by wave sequence). Two+ write dispatches in ONE wave are legal ONLY
#     under disjoint-write containment, which the journal does not carry —
#     this instrument then fails CLOSED with REQUIRES-CONTAINMENT-REVIEW
#     (exit 1): discharge it against the dispatch-plan's containment check,
#     not here.
#
# 0/1-worker degenerate semantics (both dialects): CLEAN means "trivially
# clean — single-writer held by construction"; the remaining audit surface
# for such runs is the judgment stream (audit-judgment-flow), not this script.
#
# Usage:
#   bash scripts/audit-single-writer.sh <journal.jsonl>
#   bash scripts/audit-single-writer.sh --self-test   # prove both dialects' detection is alive
# Exit: 0 clean; 1 violation / containment-review required (or self-test fail);
#       2 malformed input / environment error.
set -u

if [ "${1:-}" = "--self-test" ]; then
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  # v1: planted parallel write must be caught
  printf '%s\n' '{"phase":"parallel","worker":"w1","action":"write","path":"a.py"}' > "$tmp/v1.jsonl"
  bash "$0" "$tmp/v1.jsonl" >/dev/null 2>&1 && { echo "SELF-TEST FAIL: v1 parallel write not caught"; exit 1; }
  # v3: planted same-wave double write must be caught
  {
    printf '%s\n' '{"event":"commander_stamp","model":"m","doctrine_rev":"abc1234","run_id":"self-test"}'
    printf '%s\n' '{"event":"dispatch","task_id":"a","read_only":false,"wave":1}'
    printf '%s\n' '{"event":"dispatch","task_id":"b","read_only":false,"wave":1}'
  } > "$tmp/v3.jsonl"
  bash "$0" "$tmp/v3.jsonl" >/dev/null 2>&1 && { echo "SELF-TEST FAIL: v3 same-wave writes not caught"; exit 1; }
  # v3: serial writes must be clean
  {
    printf '%s\n' '{"event":"commander_stamp","model":"m","doctrine_rev":"abc1234","run_id":"self-test"}'
    printf '%s\n' '{"event":"dispatch","task_id":"a","read_only":false,"wave":1}'
    printf '%s\n' '{"event":"dispatch","task_id":"b","read_only":false,"wave":2}'
  } > "$tmp/v3ok.jsonl"
  bash "$0" "$tmp/v3ok.jsonl" >/dev/null 2>&1 || { echo "SELF-TEST FAIL: v3 serial writes flagged"; exit 1; }
  echo "SELF-TEST OK: v1 parallel-write, v3 same-wave, v3 serial all behave"
  exit 0
fi

[ $# -eq 1 ] || { echo "usage: audit-single-writer.sh <journal.jsonl> | --self-test"; exit 2; }
python3 - "$1" <<'PYEOF'
import json, sys
from collections import defaultdict

try:
    lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
except OSError as err:
    print(f"MALFORMED: cannot read journal: {err}")
    sys.exit(2)

events = []
for i, line in enumerate(lines, 1):
    line = line.strip()
    if not line:
        continue
    try:
        events.append((i, json.loads(line)))
    except json.JSONDecodeError as err:
        print(f"MALFORMED: line {i}: {err}")
        sys.exit(2)

if not events:
    print("AUDIT CLEAN (empty journal — nothing dispatched)")
    sys.exit(0)

# dialect detection: v3 journals stamp themselves on line 1
if events[0][1].get("event") == "commander_stamp":
    waves = defaultdict(list)   # wave -> [task_id]
    for lineno, d in events:
        if d.get("event") != "dispatch":
            continue
        if "read_only" not in d:
            print(f"MALFORMED: line {lineno}: dispatch missing read_only")
            sys.exit(2)
        if d["read_only"]:
            continue
        # missing wave -> conservative: group under one unknown bucket
        waves[d.get("wave", "unknown")].append(d.get("task_id", "?"))
    bad = {w: t for w, t in waves.items() if len(t) > 1}
    if bad:
        for w, tasks in bad.items():
            print(f"REQUIRES-CONTAINMENT-REVIEW: wave {w} has {len(tasks)} write dispatches ({', '.join(tasks)}) — legal only under disjoint-write; journal carries no surfaces, discharge against the dispatch-plan containment check")
        sys.exit(1)
    n = sum(len(t) for t in waves.values())
    print(f"AUDIT CLEAN (v3 dialect: {n} write dispatch(es), single-threaded by wave)")
    sys.exit(0)

# v1 dialect
violations = []
for i, e in events:
    for key in ("phase", "worker", "action", "path"):
        if key not in e:
            print(f"MALFORMED: line {i}: missing key {key}")
            sys.exit(2)
    if e["phase"] not in ("parallel", "single") or e["action"] not in ("read", "write"):
        print(f"MALFORMED: line {i}: bad phase/action value")
        sys.exit(2)
    if e["phase"] == "parallel" and e["action"] == "write":
        violations.append(f"VIOLATION: {e.get('worker', '?')} wrote {e.get('path', '?')} during parallel phase (line {i})")
if violations:
    print("\n".join(violations))
    sys.exit(1)
print("AUDIT CLEAN")
sys.exit(0)
PYEOF
