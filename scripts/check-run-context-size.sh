#!/usr/bin/env bash
# check-run-context-size.sh — the meter on what a run is instructed to read
# (mode-at-first-dispatch REQ-7 / AC-21).
#
# Measured set: scripts/run-obeyed.manifest, verbatim — the SAME set doctrine/REV keys on,
# so a file cannot be obeyed-but-unpriced or priced-but-unkeyed. Baseline and
# every recorded exception: scripts/context-budget.conf, the one tracked home for
# both. Neither is restated here; this script reads them.
#
# Relocating text WITHIN the set scores as zero reduction, which is the whole
# point — moving prose from the doctrine into another run-loaded file buys
# nothing and the meter says so.
#
# INVOCATION OCCASION (named, because a check with no named runner is a check
# nobody runs — this repo has no CI): it joins the ship-time check set beside
# check-doctrine-rev, check-role-cards and check-neutrality (AC-28).
#
# Usage:
#   bash scripts/check-run-context-size.sh              # verify
#   bash scripts/check-run-context-size.sh --report     # per-member sizes, always exit 0
#   bash scripts/check-run-context-size.sh --self-test  # prove it detects growth AND a missing member
# Exit: 0 = within budget (or paired/decided); 1 = unpaired growth, or a member
#       missing/unreadable; 2 = environment error.
set -u
# The three overrides exist for --self-test only: it re-invokes THIS script
# against a fixture tree so the legs below exercise the real comparison path
# rather than a copy of it.
ROOT="${CHECK_CONTEXT_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
MANIFEST="${CHECK_CONTEXT_MANIFEST:-$ROOT/scripts/run-obeyed.manifest}"
BUDGET="${CHECK_CONTEXT_BUDGET:-$ROOT/scripts/context-budget.conf}"

if [ "${1:-}" = "--self-test" ]; then
  # Both legs are planted against the REAL comparison path — the script is
  # re-invoked with a fixture manifest and budget, never with an inlined copy of
  # its own logic.
  fail=0
  tmp="$(mktemp -d)" || exit 2
  trap 'rm -rf "$tmp"' EXIT
  mkdir -p "$tmp/repo/doctrine"
  printf 'aaaaaaaaaa\n' > "$tmp/repo/doctrine/a.md"        # 11 chars
  printf '# fixture manifest\ndoctrine/a.md\n' > "$tmp/man"

  # leg 1 — a planted INCREASE must be detected (baseline below actual, and no
  # pairing token reachable because the fixture budget is not in git history)
  printf 'baseline: 5\n' > "$tmp/budget-low"
  rc="$(CHECK_CONTEXT_ROOT="$tmp/repo" CHECK_CONTEXT_MANIFEST="$tmp/man" CHECK_CONTEXT_BUDGET="$tmp/budget-low" bash "$0" >"$tmp/out" 2>&1; echo $?)"
  if [ "$rc" = "1" ] && grep -q 'no paired deletion' "$tmp/out"; then
    echo "ok: planted increase detected (rc=1)"
  else
    echo "SELF-TEST FAIL: planted increase not detected (rc=$rc)"; sed 's/^/    /' "$tmp/out"; fail=1
  fi

  # leg 2 — a planted MISSING member must be detected, and must NOT be scored
  # as zero chars (which would read as a free reduction and PASS)
  printf '# fixture manifest\ndoctrine/a.md\ndoctrine/gone.md\n' > "$tmp/man2"
  printf 'baseline: 999999\n' > "$tmp/budget-high"   # generous: only the missing member can fail this
  rc="$(CHECK_CONTEXT_ROOT="$tmp/repo" CHECK_CONTEXT_MANIFEST="$tmp/man2" CHECK_CONTEXT_BUDGET="$tmp/budget-high" bash "$0" >"$tmp/out" 2>&1; echo $?)"
  if [ "$rc" = "1" ] && grep -q 'gone.md' "$tmp/out"; then
    echo "ok: planted missing member detected, and not scored as zero chars"
  else
    echo "SELF-TEST FAIL: missing member not detected (rc=$rc) — a generous baseline"
    echo "                would otherwise let a DELETED run-obeyed file read as a reduction"
    sed 's/^/    /' "$tmp/out"; fail=1
  fi

  # leg 3 — the honest control: a conformant tree must PASS, or the two legs
  # above prove only that the script can fail, not that it can distinguish
  printf 'baseline: 11\n' > "$tmp/budget-exact"
  rc="$(CHECK_CONTEXT_ROOT="$tmp/repo" CHECK_CONTEXT_MANIFEST="$tmp/man" CHECK_CONTEXT_BUDGET="$tmp/budget-exact" bash "$0" >"$tmp/out" 2>&1; echo $?)"
  if [ "$rc" = "0" ]; then
    echo "ok: a tree exactly at baseline passes"
  else
    echo "SELF-TEST FAIL: conformant tree did not pass (rc=$rc)"; sed 's/^/    /' "$tmp/out"; fail=1
  fi

  [ "$fail" -eq 0 ] && { echo "SELF-TEST OK"; exit 0; } || { echo "SELF-TEST FAIL"; exit 1; }
fi

[ -r "$MANIFEST" ] || { echo "ERROR: manifest unreadable: $MANIFEST" >&2; exit 2; }
[ -r "$BUDGET" ]   || { echo "ERROR: budget unreadable: $BUDGET" >&2; exit 2; }

members() { grep -vE '^[[:space:]]*(#|$)' "$MANIFEST" | sed 's/^stamped //'; }

baseline="$(grep -E '^baseline:[[:space:]]*[0-9]+' "$BUDGET" | head -1 | tr -dc '0-9')"
[ -n "$baseline" ] || { echo "ERROR: no 'baseline: <int>' line in $BUDGET" >&2; exit 2; }

# ---- measure -----------------------------------------------------------
total=0
missing=""
report=""
while IFS= read -r rel; do
  f="$ROOT/$rel"
  if [ -r "$f" ] && [ -f "$f" ]; then
    n="$(wc -c < "$f" | tr -dc '0-9')"
    total=$((total + n))
    report="$report$(printf '%9d  %s' "$n" "$rel")
"
  else
    missing="$missing $rel"
  fi
done <<EOF
$(members)
EOF

if [ "${1:-}" = "--report" ]; then
  printf '%s' "$report" | sort -rn
  echo "---------"
  printf '%9d  TOTAL (baseline %s)\n' "$total" "$baseline"
  exit 0
fi

# A member that cannot be measured is NEVER scored as zero: that would make
# deleting a run-obeyed file read as a free reduction. Both consumers of the one
# manifest fail closed on this condition, or neither does.
if [ -n "$missing" ]; then
  for m in $missing; do
    echo "FAIL: manifest member missing or unreadable: $m"
  done
  echo "FAIL: a member that cannot be measured is never scored as zero chars"
  exit 1
fi

# ---- compare -----------------------------------------------------------
delta=$((total - baseline))

if [ "$delta" -le 0 ]; then
  echo "CLEAN: $total chars over $(members | wc -l | tr -d ' ') members; baseline $baseline (headroom $((-delta)))"
  [ "$delta" -lt 0 ] && echo "  note: bank the reduction by setting 'baseline: $total' in $(basename "$BUDGET")"
  exit 0
fi

# Growth. Legal only if the commits since the budget file last changed carry the
# pairing token, or a decision line accounts for it.
paired=""
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  since="$(git -C "$ROOT" log -1 --format=%H -- "${BUDGET#$ROOT/}" 2>/dev/null)"
  if [ -n "$since" ]; then
    paired="$(git -C "$ROOT" log "$since"..HEAD --format=%B 2>/dev/null | grep -E '^context-budget: \+[0-9]+ -[0-9]+ .+' || true)"
  fi
fi

if [ -n "$paired" ]; then
  echo "PAIRED: +$delta chars over baseline $baseline, paired by:"
  printf '%s\n' "$paired" | sed 's/^/  /'
  echo "  update 'baseline: $total' in $(basename "$BUDGET") in the same change"
  exit 0
fi

echo "FAIL: run-context grew $delta chars (now $total, baseline $baseline) with no paired deletion."
echo "The members that grew, largest first — compare against git:"
printf '%s' "$report" | sort -rn | head -6 | sed 's/^/  /'
echo
echo "Three legal routes, and no fourth:"
echo "  1. delete something in the measured set and record the pairing in the"
echo "     commit message:  context-budget: +$delta -<deleted> <what>"
echo "  2. reduce the growth until it fits the baseline"
echo "  3. spec-level decision: add a 'decision:' line to $(basename "$BUDGET")"
echo "     and move 'baseline:' to $total — an increase with nothing to delete is"
echo "     legal only as a recorded decision, never silently"
exit 1
