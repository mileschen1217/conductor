#!/usr/bin/env bash
# Runs scripts/audit-judgment-flow.py over scripts/fixtures/judgment-flow/.
# Table-driven: each case = expected exit code + required output pattern.
# Every rule the audit enforces has a fixture that fails without it and one
# that passes with it (mode-at-first-dispatch AC-12, AC-20).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="python3 $ROOT/scripts/audit-judgment-flow.py"
F="$ROOT/scripts/fixtures/judgment-flow"
fail=0
check() { # <name> <want_rc> <want_pattern> <cmd...>
  local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else
    echo "ok: $name"
  fi
}

# --- stamp gate (AC-20): fail-closed, no legacy dialect and no fallback ---
check clean            0 '^CLEAN$'                                      $A "$F/journal-clean.jsonl"
check no-stamp         1 '^VIOLATION: stamp gate: .*no commander_stamp' $A "$F/journal-no-stamp.jsonl"
check stale-vocab      1 '^VIOLATION: stamp gate: .*below the current'  $A "$F/journal-stale-vocab.jsonl"

# --- the four semantic rules (AC-12) ---
check s1-moment-reuse  1 '^VIOLATION: semantic rule S1'                 $A "$F/journal-moment-reuse.jsonl"
check s2-broken-pair   1 '^VIOLATION: semantic rule S2 .*dispatch_result' $A "$F/journal-broken-pairing.jsonl"
check s3-usage-prose   1 '^VIOLATION: semantic rule S3'                 $A "$F/journal-usage-prose.jsonl"
check s4-cited         0 '^CLEAN$'                                      $A "$F/journal-class-cited.jsonl"
check s4-reasoned      0 '^CLEAN$'                                      $A "$F/journal-class-override-reasoned.jsonl"
check s4-empty-reason  1 '^VIOLATION: semantic rule S4'                 $A "$F/journal-class-override-empty.jsonl"
# omission is the cheaper route to the same licence: declare the class, record
# no class_default at all.
check s4-no-default    1 '^VIOLATION: semantic rule S4 .*no class_default' $A "$F/journal-class-no-default.jsonl"

# --- environment errors are exit 2, never a silent pass ---
check missing-journal  2 '^UNVERIFIABLE: cannot read journal'           $A "$F/nonexistent.jsonl"
exit "$fail"
