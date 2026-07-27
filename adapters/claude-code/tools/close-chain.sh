#!/usr/bin/env bash
# close-chain.sh — the canonical close audit set, as ONE invocation.
#
# This file is the single home of the chain's MEMBERSHIP and ORDER (doctrine
# § Audit surface, "The close event and its chain"). Anything that says "the
# close audits" cites this script rather than re-enumerating them, and a
# caller never sequences members by hand.
#
# PORTABILITY IS A HARD REQUIREMENT of this file. It is executed by whatever
# shell the operator happens to be running, and it must behave identically
# under at least sh, bash and zsh. Concretely, and each of these has drawn
# blood:
#   - no ${PIPESTATUS[...]} — a bash-ism that expands to empty under zsh, so
#     every member's exit code silently reads as success (three incidents)
#   - no arrays — bash indexes from 0, zsh from 1
#   - no `local` — not POSIX; status is accumulated in plain strings
#   - every member's rc is captured immediately after its own invocation,
#     never inferred from a pipeline
# scripts/test-close-chain.sh executes this file under bash AND zsh and
# asserts both report the same per-member exit codes.
#
# Members are ALL run — the chain does not stop at the first failure, because
# the close event records every member and a record truncated at the first
# problem is a record with holes. A failure names its member and its exit
# code, and the chain's own exit is non-zero.
#
# Member status vocabulary (doctrine § Audit surface, close event):
#   pass                     ran, exit 0
#   fail(<rc>)               ran and did not conclude in the affirmative.
#                            A member that could not conclude for want of
#                            evidence lands here too, and is meant to: every
#                            instrumented run is deliberately triggered, so the
#                            evidence a measurement depends on is owed.
#   dropped(trigger-absent)  not run because its trigger did not fire
#
# Usage:
#   close-chain.sh --journal <journal.jsonl> --task-dir <dir> --anchors <spec>
#                  [--probe <probe.jsonl>] [--telemetry <telemetry.jsonl>]
#
# --anchors takes the binding's conversion-anchor spec verbatim (the values
# live only in binding.md § 換算錨表; this script embeds none).
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
