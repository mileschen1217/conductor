#!/usr/bin/env bash
# test-audit-brake-lines.sh — fixture suite for the brake auditor.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="$ROOT/scripts/audit-brake-lines.py"
F="$ROOT/scripts/fixtures/brake-lines"
ANCHORS='prose=4,code=3,cjk=1.5,correction=1.3'
fail=0
check() { local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc; out="$(python3 "$A" "$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else echo "ok: $name"; fi
}

# --- computed-term recomputability ---
check conformant    0 '^CONFORMANT event 1'                    "$F/journal-brake-conformant.jsonl" --anchors "$ANCHORS" --probe "$F/probe.jsonl"
check invented      1 'INVENTED VALUE'                         "$F/journal-brake-invented-value.jsonl" --anchors "$ANCHORS" --probe "$F/probe.jsonl"
check bad-ref       1 'does not resolve in the probe record'   "$F/journal-brake-bad-ref.jsonl" --probe "$F/probe.jsonl"
check owed          1 'owed-but-missing'                       "$F/journal-brake-owed-missing.jsonl"
# fail-open holes closed 2026-07-18: boot=0 with no probe_ref on a computed
# verdict, and a malformed probe record making probe_ref unverifiable
check cold-boot0    1 'probe_ref is null/absent'               "$F/journal-brake-cold-boot0-no-ref.jsonl"
check probe-malformed 1 'malformed line.*unverifiable|suspicious record' "$F/journal-brake-conformant.jsonl" --probe "$F/probe-malformed.jsonl"

# --- ground enum + the launch rule (AC-19) ---
# The doctrine sentence "an economics-failing dispatch without a necessity
# ground does not launch" had ZERO mechanical enforcement before this suite.
check bad-ground    1 'ground off enum'                        "$F/journal-brake-bad-ground.jsonl" --probe "$F/probe.jsonl"
check launch-rule   1 'economics-failing dispatch without a necessity ground' "$F/journal-brake-fail-launched-no-ground.jsonl" --probe "$F/probe.jsonl"
check not-computable 1 'economics-failing dispatch without a necessity ground' "$F/journal-brake-not-computable.jsonl"
# economics failed and the commander did NOT launch: the rule working
check not-launched  0 '^CONFORMANT event 1'                    "$F/journal-brake-fail-not-launched.jsonl" --probe "$F/probe.jsonl"
# the doctrine-mandated verifier dispatch: economics fail, launched, legal —
# this is the taste-AC path that used to read as a 34x brake violation
check verif-mandated 0 '^CONFORMANT event 1'                   "$F/journal-brake-verification-mandated.jsonl" --probe "$F/probe.jsonl"

# --- stamp gate (AC-20): fail-closed, no legacy dialect remains ---
check no-stamp      1 '^VIOLATION: stamp gate: .*no commander_stamp' "$F/journal-brake-no-stamp.jsonl"
check stale-vocab   1 '^VIOLATION: stamp gate: .*below the'    "$F/journal-brake-stale-vocab.jsonl"

# --- r-value narrowing (MR7 regression) ---
check bad-r         1 'outside the allowed binding set'        "$F/journal-brake-conformant.jsonl" --probe "$F/probe.jsonl" --commander-r 0.5

# --- usage errors are exit 2, never an uncaught crash or a silent pass ---
check missing-file  2 'usage error: journal not found'         "$F/does-not-exist.jsonl"
check bad-anchors   2 'usage error: anchor'                    "$F/journal-brake-conformant.jsonl" --anchors 'code=3'
check zero-anchor   2 'usage error: anchor .prose. must be positive' "$F/journal-brake-conformant.jsonl" --anchors 'prose=0,code=3,cjk=1.5'

[ "$fail" -eq 0 ] || exit 1
exit 0
