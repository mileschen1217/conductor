#!/usr/bin/env bash
# Journal event vocabulary: contract/journal-event.schema.json (doctrine § Machine pointers).
# audit-single-writer.sh — post-hoc single-writer audit (invariant I2).
#
# This is the DETECTIVE half of the rule. The preventive half — read-only
# worker toolsets, one write-capable worker at a time — is a procedural step
# in every adapter and binds every dispatch run, instrumented or not
# (doctrine RT-6 @ dispatch-record). This script exists only where a journal
# does, which is to say on instrumented runs.
#
# Write activity lives on {"event":"dispatch","read_only":false,"wave":N}
# lines. CLEAN when write dispatches never share a wave (writes
# single-threaded by wave sequence). Two+ write dispatches in ONE wave are
# legal ONLY under disjoint-write containment, which the journal's wave field
# does not carry — this instrument then fails CLOSED with
# REQUIRES-CONTAINMENT-REVIEW (exit 1): discharge it against the dispatch
# line's containment statement, not here.
#
# Stamp gate (fail-closed, same polarity as every stamp-keyed audit): the
# journal must open with a commander_stamp carrying vocab >= 3. There is no
# legacy dialect and no fallback — a journal from an earlier vocabulary
# belongs to a run that has closed, and is never re-invoked.
#
# A run with zero write dispatches is CLEAN by construction: single-writer
# held because nothing contended for the pen.
#
# Usage:
#   bash scripts/audit-single-writer.sh <journal.jsonl>
#   bash scripts/audit-single-writer.sh --self-test   # prove the detections are alive
# Exit: 0 clean; 1 violation / containment-review required / stamp gate failed
#       (or self-test fail); 2 malformed input / environment error.
set -u

VOCAB=3

if [ "${1:-}" = "--self-test" ]; then
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  stamp='{"event":"commander_stamp","model":"m","doctrine_rev":"abc1234","vocab":3,"run_id":"self-test"}'
  # planted same-wave double write must be caught
  {
    printf '%s\n' "$stamp"
    printf '%s\n' '{"event":"dispatch","task_id":"a","read_only":false,"wave":1}'
    printf '%s\n' '{"event":"dispatch","task_id":"b","read_only":false,"wave":1}'
  } > "$tmp/same-wave.jsonl"
  bash "$0" "$tmp/same-wave.jsonl" >/dev/null 2>&1 && { echo "SELF-TEST FAIL: same-wave writes not caught"; exit 1; }
  # serial writes must be clean
  {
    printf '%s\n' "$stamp"
    printf '%s\n' '{"event":"dispatch","task_id":"a","read_only":false,"wave":1}'
    printf '%s\n' '{"event":"dispatch","task_id":"b","read_only":false,"wave":2}'
  } > "$tmp/serial.jsonl"
  bash "$0" "$tmp/serial.jsonl" >/dev/null 2>&1 || { echo "SELF-TEST FAIL: serial writes flagged"; exit 1; }
  # stamp gate: a journal with no stamp must FAIL, never fall back to a dialect
  printf '%s\n' '{"event":"dispatch","task_id":"a","read_only":false,"wave":1}' > "$tmp/no-stamp.jsonl"
  bash "$0" "$tmp/no-stamp.jsonl" >/dev/null 2>&1 && { echo "SELF-TEST FAIL: stamp-less journal not caught"; exit 1; }
  # stamp gate: an older vocabulary must FAIL too
  {
    printf '%s\n' '{"event":"commander_stamp","model":"m","doctrine_rev":"abc1234","vocab":2,"run_id":"self-test"}'
    printf '%s\n' '{"event":"dispatch","task_id":"a","read_only":false,"wave":1}'
  } > "$tmp/stale.jsonl"
  bash "$0" "$tmp/stale.jsonl" >/dev/null 2>&1 && { echo "SELF-TEST FAIL: stale-vocab journal not caught"; exit 1; }
  echo "SELF-TEST OK: same-wave, serial, stamp-less and stale-vocab all behave"
  exit 0
fi

[ $# -eq 1 ] || { echo "usage: audit-single-writer.sh <journal.jsonl> | --self-test"; exit 2; }
VOCAB="$VOCAB" python3 - "$1" <<'PYEOF'
import json, os, sys
from collections import defaultdict

VOCAB = int(os.environ["VOCAB"])

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
    print("MALFORMED: empty journal — an instrumented run opens on commander_stamp")
    sys.exit(2)

stamp = events[0][1] if events[0][1].get("event") == "commander_stamp" else None
if stamp is None:
    print("VIOLATION: stamp gate: journal does not open on commander_stamp — a journal "
          f"handed to this audit must declare its dialect (vocab {VOCAB}); there is no "
          "legacy fallback")
    sys.exit(1)
vocab = stamp.get("vocab")
if not isinstance(vocab, int) or isinstance(vocab, bool) or vocab < VOCAB:
    print(f"VIOLATION: stamp gate: commander_stamp.vocab={vocab!r} is absent or below the "
          f"current vocabulary {VOCAB} — this journal was written in a dialect whose run "
          "has closed; it is not re-audited under the current rules")
    sys.exit(1)

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
        print(f"REQUIRES-CONTAINMENT-REVIEW: wave {w} has {len(tasks)} write dispatches "
              f"({', '.join(tasks)}) — legal only under disjoint-write; the journal's wave "
              "field carries no surfaces, discharge against the dispatch line's containment "
              "statement")
    sys.exit(1)
n = sum(len(t) for t in waves.values())
print(f"AUDIT CLEAN ({n} write dispatch(es), single-threaded by wave)")
sys.exit(0)
PYEOF
