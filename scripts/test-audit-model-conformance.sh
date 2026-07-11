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
exit "$fail"
