#!/usr/bin/env bash
# test-estimate-tokens.sh — fixture suite for the tier-0 conversion helper (v3.1 AC-5).
# Expected tok-eq values are HAND-COMPUTED from the fixture byte contents and the
# test anchors (prose=4, code=3, cjk=1.5 chars/tok, correction=1.3) — never derived
# by running the helper (a checker written only to be passed would pass).
#   prose.md   45 bytes ASCII prose  -> round(1.3*45/4)            = 15
#   code.py    32 bytes ASCII code   -> round(1.3*32/3)            = 14
#   cjk-mixed  30 bytes (9 ASCII + 7 CJK chars) -> round(1.3*(9/4 + 7/1.5)) = 9
#   empty.md   0 bytes               -> 0
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="$ROOT/scripts/estimate-tokens.py"
F="$ROOT/scripts/fixtures/estimate-tokens"
ANCHORS="prose=4,code=3,cjk=1.5,correction=1.3"
fail=0
check() { local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc; out="$(python3 "$A" "$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else echo "ok: $name"; fi
}
check prose      0 'prose\.md 45 15$'        --anchors "$ANCHORS" "$F/prose.md"
check code       0 'code\.py 32 14$'         --anchors "$ANCHORS" "$F/code.py"
check cjk-mixed  0 'cjk-mixed\.md 30 9$'     --anchors "$ANCHORS" "$F/cjk-mixed.md"
check empty      0 'empty\.md 0 0$'          --anchors "$ANCHORS" "$F/empty.md"
check total      0 '^TOTAL 107 38$'          --anchors "$ANCHORS" "$F/prose.md" "$F/code.py" "$F/cjk-mixed.md" "$F/empty.md"
check no-cjk-anchor 2 'usage error: anchor .cjk. missing' --anchors "prose=4,code=3" "$F/prose.md"
check bad-file   2 'usage error: cannot read'  --anchors "$ANCHORS" "$F/does-not-exist.md"
# determinism: same input, same output, twice
o1="$(python3 "$A" --anchors "$ANCHORS" "$F/prose.md" "$F/cjk-mixed.md")"
o2="$(python3 "$A" --anchors "$ANCHORS" "$F/prose.md" "$F/cjk-mixed.md")"
if [ "$o1" = "$o2" ]; then echo "ok: deterministic"; else echo "FAIL: nondeterministic output"; fail=1; fi
# zero embedded values: the script must not contain a numeric anchor default
if grep -nE '"(prose|code|cjk)":\s*[0-9]' "$A" >/dev/null; then
  echo "FAIL: embedded anchor value found in helper"; fail=1
else echo "ok: no embedded anchor values"; fi
exit "$fail"
