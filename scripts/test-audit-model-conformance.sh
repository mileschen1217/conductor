#!/usr/bin/env bash
# Runs scripts/audit-model-conformance.py over scripts/fixtures/model-conformance/ (spec AC-5).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="python3 $ROOT/scripts/audit-model-conformance.py"
F="$ROOT/scripts/fixtures/model-conformance"
fail=0
check() { local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc; out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else echo "ok: $name"; fi
}
check clean           0 '^CLEAN'                    $A "$F/journal-clean.jsonl" "$F/telemetry-clean.jsonl"
check mismatch        1 '^VIOLATION: dispatch line' $A "$F/journal-clean.jsonl" "$F/telemetry-mismatch.jsonl"
check stamp-mismatch  1 '^VIOLATION: commander_stamp' $A "$F/journal-clean.jsonl" "$F/telemetry-stamp-mismatch.jsonl"
check late-stamp      1 '^VIOLATION: .*first event'  $A "$F/journal-late-stamp.jsonl" "$F/telemetry-clean.jsonl"
check no-stamp        1 '^VIOLATION: .*first event'  $A "$F/journal-no-stamp.jsonl" "$F/telemetry-clean.jsonl"
check no-stamp-empty-telemetry 1 '^VIOLATION: .*first event' $A "$F/journal-no-stamp.jsonl" "$F/telemetry-empty.jsonl"
check empty-telemetry 2 '^UNVERIFIABLE: '           $A "$F/journal-clean.jsonl" "$F/telemetry-empty.jsonl"
check missing-telemetry 2 '^UNVERIFIABLE: '         $A "$F/journal-clean.jsonl" "$F/telemetry-nonexistent.jsonl"
check no-stamp-missing-telemetry 1 '^VIOLATION: .*first event' $A "$F/journal-no-stamp.jsonl" "$F/telemetry-nonexistent.jsonl"
check no-stamp-malformed-telemetry 1 '^VIOLATION: .*first event' $A "$F/journal-no-stamp.jsonl" "$F/telemetry-malformed.jsonl"
check malformed-telemetry 2 '^UNVERIFIABLE: .*JSON parse error' $A "$F/journal-clean.jsonl" "$F/telemetry-malformed.jsonl"
# --- C0 without telemetry (AC-21): the close chain invokes this audit on EVERY
#     instrumented run, so C0 must return a verdict with no telemetry argument.
#     Absent telemetry leaves C1/C2 UNVERIFIABLE and can never read CLEAN.
check c0-only-clean   2 '^C0 CLEAN'                 $A "$F/journal-clean.jsonl"
check c0-only-unverif 2 '^UNVERIFIABLE: no telemetry export given' $A "$F/journal-clean.jsonl"
check c0-only-late    1 '^VIOLATION: .*first event' $A "$F/journal-late-stamp.jsonl"
check c0-only-nostamp 1 '^VIOLATION: .*first event' $A "$F/journal-no-stamp.jsonl"
# --- the exit contract's two failure codes must never collide. The close chain
#     keeps only the code (it records fail(<rc>)), so 2 has to mean "ran, could
#     not conclude for want of evidence" and nothing else. A caller bug exiting
#     2 would be recorded as an owed evidence gap — a broken call reading as an
#     honest red. These two checks are what hold the codes apart: c0-only-unverif
#     above pins 2 to the evidence gap, no-args pins 3 to the caller bug.
check no-args         3 '^usage: '                  $A
check too-many-args   3 '^usage: '                  $A "$F/journal-clean.jsonl" "$F/telemetry-clean.jsonl" extra
exit "$fail"
