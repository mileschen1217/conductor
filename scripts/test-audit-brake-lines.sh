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
[ "$fail" -eq 0 ] || exit 1
exit 0
