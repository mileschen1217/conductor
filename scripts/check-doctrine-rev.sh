#!/usr/bin/env bash
# check-doctrine-rev.sh — guard that doctrine/REV (the shipped rev stamp read
# by installed-plugin contexts, which have no .git) matches the last-change
# commit ACROSS THE DECLARED MANIFEST. Run from a git checkout; installed
# contexts consume REV, they don't check it — this guard is why they can
# trust it. Stale REV = role-card graded_under staleness silently breaks
# (the v3 regression's gap 1/4 root cause).
#
# KEYED ON A MANIFEST, NOT A FILE AND NOT A DIRECTORY (mode-at-first-dispatch
# AC-20). Until 2026-07-29 this keyed on doctrine/orchestration-mode.md alone.
# That became untenable when the journal vocabulary moved to
# contract/journal-event.schema.json: a run OBEYS that file, and a rev ignoring
# it would let the vocabulary change under cards still claiming to be graded
# under the current revision. `doctrine/` as a directory does not fix it either
# — the schema does not live there. The set is declared once, in
# scripts/run-obeyed.manifest, and it is the same set the size gate measures.
#
# Usage:
#   bash scripts/check-doctrine-rev.sh              # verify
#   bash scripts/check-doctrine-rev.sh --self-test  # prove the check detects a mismatch
# Exit: 0 = match (or self-test positive); 1 = mismatch, or a manifest member
#       missing/unreadable; 2 = environment error.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="${CHECK_DOCTRINE_MANIFEST:-$ROOT/scripts/run-obeyed.manifest}"
REV_FILE="${CHECK_DOCTRINE_REV_FILE:-$ROOT/doctrine/REV}"   # overrides: --self-test only

[ -r "$MANIFEST" ] || { echo "ERROR: manifest unreadable: $MANIFEST" >&2; exit 2; }
members="$(grep -vE '^[[:space:]]*(#|$)|^stamped ' "$MANIFEST")"
[ -n "$members" ] || { echo "ERROR: manifest declares no members" >&2; exit 2; }

# Fail closed on a member that is not there. A manifest naming a path that does
# not exist would otherwise key the rev on whatever remains — the same failure
# the size gate refuses when it declines to score a missing member as zero
# chars. Both consumers of the one manifest fail closed, or neither does.
missing=""
for rel in $members; do
  { [ -r "$ROOT/$rel" ] && [ -f "$ROOT/$rel" ]; } || missing="$missing $rel"
done
if [ -n "$missing" ]; then
  for m in $missing; do echo "FAIL: manifest member missing or unreadable: $m"; done
  echo "FAIL: the rev cannot be keyed on a set whose membership is not all present"
  exit 1
fi

# shellcheck disable=SC2086
actual="$(git -C "$ROOT" log -1 --format=%h -- $members 2>/dev/null)"
[ -n "$actual" ] || { echo "ERROR: not a git checkout, or no commit touches any manifest member" >&2; exit 2; }

if [ "${1:-}" = "--self-test" ]; then
  fail=0
  # leg 1 — replay the REAL comparison path against a planted wrong stamp
  tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
  printf 'deadbee\n' > "$tmp"
  if CHECK_DOCTRINE_REV_FILE="$tmp" bash "$0" >/dev/null 2>&1; then
    echo "SELF-TEST FAIL: planted wrong REV stamp not detected" >&2; fail=1
  else
    echo "ok: planted wrong REV stamp detected by the real comparison path"
  fi
  # leg 2 — a manifest member that does not exist must FAIL CLOSED, never key
  # the rev on the survivors
  man="$(mktemp)"
  { printf '# self-test manifest\n'; printf 'doctrine/orchestration-mode.md\n'; printf 'doctrine/does-not-exist.md\n'; } > "$man"
  if CHECK_DOCTRINE_MANIFEST="$man" bash "$0" >/dev/null 2>&1; then
    echo "SELF-TEST FAIL: a missing manifest member did not fail the check" >&2; fail=1
  else
    echo "ok: missing manifest member fails closed"
  fi
  rm -f "$man"
  [ "$fail" -eq 0 ] && { echo "SELF-TEST OK"; exit 0; } || { echo "SELF-TEST FAIL"; exit 1; }
fi

[ -r "$REV_FILE" ] || { echo "MISMATCH: doctrine/REV missing (expected $actual)"; exit 1; }
shipped="$(tr -d '[:space:]' < "$REV_FILE")"
if [ "$shipped" = "$actual" ]; then
  echo "CLEAN: doctrine/REV = $actual (last change across $(printf '%s\n' "$members" | grep -c . ) manifest members)"
  exit 0
fi
echo "MISMATCH: doctrine/REV=$shipped but the manifest's last-change commit=$actual"
echo "  The manifest spans L1, L2 and the source a run reads in order to call it, so ANY"
echo "  member's edit moves the rev — a script included. After any such edit, update"
echo "  doctrine/REV in the follow-up commit (the hash exists only post-commit; role-card"
echo "  graded_under re-keys ride the same follow-up). Members: scripts/run-obeyed.manifest"
exit 1
