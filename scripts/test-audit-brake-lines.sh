#!/usr/bin/env bash
# test-audit-brake-lines.sh — fixture suite for the AC-7 brake-line auditor.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="$ROOT/scripts/audit-brake-lines.py"
F="$ROOT/scripts/fixtures/brake-lines"
fail=0
check() { local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc; out="$(python3 "$A" "$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else echo "ok: $name"; fi
}
check conformant    0 '^CONFORMANT line 1'                "$F/plan-conformant.md" --table "$F/table.jsonl"
check invented-pay  1 '^VIOLATION line 1: pay=999'        "$F/plan-invented-pay.md" --table "$F/table.jsonl"
check bad-cite      1 '^VIOLATION line 1: constants_row'  "$F/plan-bad-cite.md" --table "$F/table.jsonl"
check bad-r         1 'outside the allowed binding set'   "$F/plan-bad-r.md" --table "$F/table.jsonl"
check coldstart     0 '^DEVIATION line 1: .*cold-start|pending-measurement' "$F/plan-coldstart.md" --table "$F/table.jsonl"
check none          0 '^NO-BRAKE-LINES'                   "$F/plan-none.md" --table "$F/table.jsonl"
check missing-plan  2 'usage error'                       "$F/does-not-exist.md" --table "$F/table.jsonl"
# --commander-r narrowing (MR7 regression): a same-model offload mislabeled
# r=0.2 passes bare set-membership but FAILS under the sonnet commander's
# narrowed column {1.0, 0.5}
check mislabel-loose  0 '^CONFORMANT|^DEVIATION'            "$F/plan-same-model-mislabel.md" --table "$F/table.jsonl"
check mislabel-narrow 1 'outside the allowed binding set'   "$F/plan-same-model-mislabel.md" --table "$F/table.jsonl" --commander-r 0.5
# --- v3.1 journal typed-event dialect (REQ-9 / AC-19); dialect keyed on the
#     vocab stamp, never on event presence ---
ANCHORS='prose=4,code=3,cjk=1.5,correction=1.3'
check j-conformant  0 '^CONFORMANT event 1'                    "$F/journal-brake-conformant.jsonl" --anchors "$ANCHORS" --probe "$F/probe.jsonl"
check j-invented    1 'INVENTED VALUE'                         "$F/journal-brake-invented-value.jsonl" --anchors "$ANCHORS" --probe "$F/probe.jsonl"
check j-bad-ref     1 'does not resolve in the probe record'   "$F/journal-brake-bad-ref.jsonl" --probe "$F/probe.jsonl"
check j-owed        1 'owed-but-missing'                       "$F/journal-brake-owed-missing.jsonl"
check j-not-comp    1 'conservative-closed'                    "$F/journal-brake-not-computable.jsonl"
check j-legacy      0 '^LEGACY'                                "$F/journal-legacy.jsonl"
# malformed --anchors = usage error (exit 2), never an uncaught crash
check j-bad-anchors 2 'usage error: anchor'                    "$F/journal-brake-conformant.jsonl" --anchors 'code=3'
check j-zero-anchor 2 'usage error: anchor .prose. must be positive' "$F/journal-brake-conformant.jsonl" --anchors 'prose=0,code=3,cjk=1.5'
[ "$fail" -eq 0 ] || exit 1
exit 0
