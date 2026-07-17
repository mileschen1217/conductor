#!/usr/bin/env bash
# check-doctrine-rev.sh — guard that doctrine/REV (the shipped rev stamp read
# by installed-plugin contexts, which have no .git) matches the doctrine
# file's actual last-change commit. Run from a git checkout; installed
# contexts consume REV, they don't check it — this guard is why they can
# trust it. Stale REV = role-card graded_under staleness silently breaks
# (the v3 regression's gap 1/4 root cause).
#
# Usage:
#   bash scripts/check-doctrine-rev.sh              # verify
#   bash scripts/check-doctrine-rev.sh --self-test  # prove the check detects a mismatch
# Exit: 0 = match (or self-test positive); 1 = mismatch; 2 = environment error.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCTRINE="doctrine/orchestration-mode.md"
REV_FILE="${CHECK_DOCTRINE_REV_FILE:-$ROOT/doctrine/REV}"   # override exists for --self-test only

actual="$(git -C "$ROOT" log -1 --format=%h -- "$DOCTRINE" 2>/dev/null)"
[ -n "$actual" ] || { echo "ERROR: not a git checkout or doctrine file missing" >&2; exit 2; }

if [ "${1:-}" = "--self-test" ]; then
  # replay the REAL comparison path against a planted wrong stamp
  tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
  printf 'deadbee\n' > "$tmp"
  if CHECK_DOCTRINE_REV_FILE="$tmp" bash "$0" >/dev/null 2>&1; then
    echo "SELF-TEST FAIL: planted wrong REV stamp not detected" >&2
    exit 1
  fi
  echo "SELF-TEST OK: planted wrong REV stamp detected by the real comparison path"
  exit 0
fi

[ -r "$REV_FILE" ] || { echo "MISMATCH: doctrine/REV missing (expected $actual)"; exit 1; }
shipped="$(tr -d '[:space:]' < "$REV_FILE")"
if [ "$shipped" = "$actual" ]; then
  echo "CLEAN: doctrine/REV = $actual"
  exit 0
fi
echo "MISMATCH: doctrine/REV=$shipped but doctrine file last-change=$actual — after any doctrine edit, update doctrine/REV in the follow-up commit (the hash exists only post-commit; role-card graded_under re-keys ride the same follow-up)"
exit 1
