#!/usr/bin/env bash
# close-chain.sh — the canonical close audit set, as ONE invocation. This file is
# the single home of the chain's MEMBERSHIP and ORDER (doctrine § Definitions —
# close law).
#
# Journal event vocabulary: contract/journal-event.schema.json (doctrine
# § Machine pointers). Member statuses and their meaning: doctrine's close law
# plus RT-3 @ close-verdict (ran-but-inconclusive is a fail).
#
# PORTABILITY IS A HARD REQUIREMENT: this runs under whatever shell the operator
# has. No ${PIPESTATUS[...]} (empty under zsh), no arrays (bash indexes from 0,
# zsh from 1), no `local`. scripts/test-close-chain.sh executes this file under
# bash AND zsh and asserts identical per-member exit codes — that suite, not this
# comment, is what holds the requirement.
#
# Usage:
#   close-chain.sh --journal <journal.jsonl> --task-dir <dir> --anchors <spec>
#                  [--probe <probe.jsonl>] [--telemetry <telemetry.jsonl>]
#
# --anchors takes the binding's conversion-anchor spec verbatim; this script
# embeds no anchor values.
#
# Output: one line per member, then a `close-members:` line carrying the JSON
# array the commander journals in the `close` event.
# Exit: 0 = every member passed or was legitimately dropped;
#       1 = at least one member failed; 2 = usage error.
set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)          # adapters/<harness>/tools
ROOT=$(cd "$SCRIPT_DIR/../../.." && pwd)           # conductor root

JOURNAL=""; TASK_DIR=""; ANCHORS=""; PROBE=""; TELEMETRY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --journal)   JOURNAL="${2:-}"; shift 2 ;;
    --task-dir)  TASK_DIR="${2:-}"; shift 2 ;;
    --anchors)   ANCHORS="${2:-}"; shift 2 ;;
    --probe)     PROBE="${2:-}"; shift 2 ;;
    --telemetry) TELEMETRY="${2:-}"; shift 2 ;;
    *) echo "usage error: unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$JOURNAL" ] || { echo "usage error: --journal is required" >&2; exit 2; }
[ -n "$TASK_DIR" ] || { echo "usage error: --task-dir is required" >&2; exit 2; }
[ -n "$ANCHORS" ] || { echo "usage error: --anchors is required (values live in the binding)" >&2; exit 2; }
[ -r "$JOURNAL" ] || { echo "usage error: journal not readable: $JOURNAL" >&2; exit 2; }

MEMBERS=""
FAILED=0

record() {  # <name> <status>
  if [ -n "$MEMBERS" ]; then MEMBERS="$MEMBERS,"; fi
  MEMBERS="$MEMBERS{\"name\":\"$1\",\"status\":\"$2\"}"
}

# run_member <name> <cmd...>
# rc is read from the command itself, on the line after it — never through a
# pipe, and never from ${PIPESTATUS[...]}.
run_member() {
  name="$1"; shift
  out=$("$@" 2>&1)
  rc=$?
  if [ "$rc" -eq 0 ]; then
    record "$name" "pass"
    echo "$name: pass"
  else
    record "$name" "fail($rc)"
    FAILED=1
    echo "CHAIN-FAIL: $name exit=$rc"
    echo "$out" | sed 's/^/    /'
  fi
}

run_member judgment-flow python3 "$ROOT/scripts/audit-judgment-flow.py" "$JOURNAL"

if [ -n "$PROBE" ]; then
  run_member brake-lines python3 "$ROOT/scripts/audit-brake-lines.py" "$JOURNAL" --anchors "$ANCHORS" --probe "$PROBE"
else
  run_member brake-lines python3 "$ROOT/scripts/audit-brake-lines.py" "$JOURNAL" --anchors "$ANCHORS"
fi

run_member single-writer bash "$ROOT/scripts/audit-single-writer.sh" "$JOURNAL"

# Reconciliation's trigger is a dispatch: a run that dispatched has artifacts
# to pair in both directions, and a run that did not has neither side.
if grep -q '"event":[ ]*"dispatch"' "$JOURNAL" 2>/dev/null; then
  run_member reconciliation python3 "$ROOT/scripts/audit-artifact-reconciliation.py" "$TASK_DIR"
else
  record reconciliation "dropped(trigger-absent)"
  echo "reconciliation: dropped(trigger-absent) — journal records no dispatch; dropped is not run and not passed"
fi

# Conformance always runs: C0 is telemetry-independent, and gating the whole
# audit on a telemetry export is exactly how C0 never ran. Absent telemetry is
# a FAILURE, not a tolerated state — an instrumented run was chosen, so the
# evidence it depends on is owed.
if [ -n "$TELEMETRY" ]; then
  run_member conformance python3 "$ROOT/scripts/audit-model-conformance.py" "$JOURNAL" "$TELEMETRY"
else
  run_member conformance python3 "$ROOT/scripts/audit-model-conformance.py" "$JOURNAL"
fi

run_member run-stats python3 "$SCRIPT_DIR/collect-run-stats.py" "$JOURNAL"

echo "close-members: [$MEMBERS]"
exit "$FAILED"
