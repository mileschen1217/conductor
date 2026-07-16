#!/usr/bin/env bash
# check-role-cards.sh — judgment-face scan over role cards (v3 REQ-4 / AC-14).
# A role card is a cached GRADING result; judgment duties (the doctrine's
# reserved set) must never appear on a card. This script is the single home
# of the banned judgment-face literal list — changing the list is a
# spec-level decision (same pattern as check-neutrality.sh's banned-noun
# list). The mechanical floor only: paraphrase escape is covered by the
# design-review / code-review I3 lens, not by this scan.
#
# Usage:
#   bash scripts/check-role-cards.sh              # scan contract/roles/*.md
#   bash scripts/check-role-cards.sh --self-test  # prove scanner detects planted terms
# Exit: 0 = clean (or self-test positive); 1 = hits found (or self-test failed);
#       2 = environment error.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Judgment-face literals: duty-verbs/nouns that constitute the reserved set
# (entry ruling, permission, contract changes, scope approval, promotion,
# quality verdicts). Cards phrase exclusions by section reference
# ("the doctrine's reserved set"), never by naming the duty.
TERMS='verdict|adjudicat|approv|veto|permission|promot|entry[- ]ruling|entry[- ]decision|contract[- ]change|scope[- ]change[- ]ruling|final[- ]say|gate[- ]decision|refus'

if [ "${1:-}" = "--self-test" ]; then
  if grep -inoEH "$TERMS" "$ROOT/scripts/fixtures/role-cards-selfcheck.md" >/dev/null 2>&1; then
    echo "SELF-TEST OK: planted judgment-face terms detected"
    exit 0
  fi
  echo "SELF-TEST FAIL: planted judgment-face terms NOT detected"
  exit 1
fi

D="$ROOT/contract/roles"
if [ ! -d "$D" ] || [ ! -r "$D" ]; then
  echo "ERROR: scan directory missing or unreadable: $D" >&2
  exit 2
fi

hits="$(grep -rnioEH "$TERMS" "$D" 2>/dev/null)"
rc=$?
case "$rc" in
  0)
    printf '%s\n' "$hits" | sed -e "s|^$ROOT/||" -e 's|^\([^:]*:[0-9]*\):|\1: |'
    exit 1
    ;;
  1)
    echo "CLEAN"
    exit 0
    ;;
  *)
    echo "ERROR: grep failed (exit $rc) while scanning contract/roles/" >&2
    exit 2
    ;;
esac
