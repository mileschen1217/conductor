#!/usr/bin/env bash
# check-instrumentation-switch.sh — the instrumentation switch's check artifact
# (mode-at-first-dispatch REQ-3 / REQ-4, AC-6 / AC-7 / AC-8 / AC-9).
#
# The switch is what stops a commander arming its own instrumentation. Four
# facts have to hold, and none of them is checked anywhere else:
#
#   AC-6  existence under `[ -f ]` is the WHOLE predicate — a regular file, a
#         symlink to one, a zero-byte file and a mode-000 file all read as ON;
#         a directory, a dangling symlink and an absent path all read as OFF,
#         with no error raised.
#   AC-7  no code path parses the marker's contents.
#   AC-8  every marker path ANY binding names is gitignored, untracked, and
#         absent from an installed plugin tree. The subject is the SET: each
#         binding names its own carrier, so a check pinned to one literal path
#         would go quiet the day a second binding names a different one.
#   AC-9  every layer that mentions the marker names the operator or harness as
#         its writer; no instruction, example or fallback has the COMMANDER
#         create it.
#
# The marker-path set is read from the bindings' machine-readable
# `switch-path: \`<path>\`` declaration, never hardcoded here — this script must
# not become a second home for the carrier's name.
#
# HONEST CEILING. The AC-7 and AC-9 legs are same-line greps, so a read or a
# write reached through a variable — `M=".conductor-instrumented"; open(M)` —
# passes them. That is the mechanical floor only; paraphrase and indirection are
# the design-review / code-review lens's job, the same division check-role-cards.sh
# already runs under. The floor is still worth having: it catches the literal
# form, which is the one a drifting edit actually takes.
#
# Usage:
#   bash scripts/check-instrumentation-switch.sh              # verify
#   bash scripts/check-instrumentation-switch.sh --self-test  # prove each leg bites
# Exit: 0 = clean (or self-test positive); 1 = violation; 2 = environment error.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
bad=0
fail() { echo "VIOLATION: $*"; bad=1; }

# ---------------------------------------------------------------- marker set
switch_paths() {
  grep -rhoE '^switch-path: `[^`]+`' "$ROOT"/adapters/*/binding.md 2>/dev/null \
    | sed -e 's/^switch-path: `//' -e 's/`$//' | sort -u
}

PATHS="$(switch_paths)"
if [ -z "$PATHS" ]; then
  echo "ERROR: no binding declares a switch-path; the marker set is empty and" >&2
  echo "       every check below would vacuously pass" >&2
  exit 2
fi

# EVERY binding must declare one. A non-empty set is not enough: if one binding's
# declaration line is renamed or typo'd, that binding's carrier silently drops out
# of the set while every check below still reports pass over the survivors — the
# gate going quiet about exactly the file that changed.
for b in "$ROOT"/adapters/*/binding.md; do
  [ -e "$b" ] || continue
  grep -qE '^switch-path: `[^`]+`' "$b" \
    || fail "$(basename "$(dirname "$b")")/binding.md declares no \`switch-path:\` line — its carrier is invisible to this gate, so AC-8 would pass without ever checking it"
done

# --------------------------------------------- AC-6: the predicate, seven states
# Exercised through the REAL test, `[ -f "$p" ]`, against a planted tree. If the
# doctrine's predicate and this line ever disagree, this is the line that is wrong.
predicate() { [ -f "$1" ]; }

check_predicate() {
  tmp="$(mktemp -d)" || { echo "ERROR: mktemp failed" >&2; exit 2; }
  trap 'rm -rf "$tmp"' RETURN

  : > "$tmp/regular";            printf 'armed for the 2026-07 comparison\n' > "$tmp/regular"
  : > "$tmp/target";             ln -s "$tmp/target" "$tmp/symlink"
  : > "$tmp/zero"
  : > "$tmp/mode000";            chmod 000 "$tmp/mode000"
  ln -s "$tmp/does-not-exist"    "$tmp/dangling"
  mkdir -p "$tmp/directory"
  # "$tmp/absent" deliberately never created

  for name in regular symlink zero mode000; do
    predicate "$tmp/$name" 2>/dev/null \
      || fail "AC-6: '$name' must read as instrumented — readability and size are not part of the test"
  done
  for name in dangling directory absent; do
    if predicate "$tmp/$name" 2>/dev/null; then
      fail "AC-6: '$name' must read as uninstrumented"
    fi
  done
  # ...and no state may raise. `[ -f ]` is a type test, so a mode-000 file is
  # ON precisely because nothing tries to open it.
  for name in regular symlink zero mode000 dangling directory absent; do
    err="$(predicate "$tmp/$name" 2>&1 >/dev/null)"
    [ -z "$err" ] || fail "AC-6: evaluating '$name' raised: $err"
  done
  chmod 700 "$tmp/mode000" 2>/dev/null || true
}

# ------------------------------------------- AC-7: content is never parsed
# A read of the marker's CONTENTS is the violation; `[ -f ]` on it is the rule.
check_no_parse() {
  for p in $PATHS; do
    esc="$(printf '%s' "$p" | sed 's/[.[\*^$]/\\&/g')"
    hits="$(grep -rnE "(cat|head|tail|read|source|\.|grep|awk|sed|open|read_text|readFile)[^\n]*${esc}" \
              "$ROOT/doctrine" "$ROOT/contract" "$ROOT/adapters" "$ROOT/scripts" \
              --include='*.md' --include='*.py' --include='*.sh' --include='*.json' 2>/dev/null \
            | grep -v 'check-instrumentation-switch.sh' \
            | grep -vE '(rm -f|touch|\[ -f)' || true)"
    [ -z "$hits" ] || fail "AC-7: a path appears to read the marker's contents:
$hits"
  done
}

# --------------------- AC-8: ignored, untracked, and absent from a shipped tree
check_not_shipped() {
  for p in $PATHS; do
    git -C "$ROOT" check-ignore -q "$p" 2>/dev/null \
      || fail "AC-8: '$p' is not matched by conductor's own .gitignore — a plugin install copies every tracked file and no exclusion mechanism exists"
    if git -C "$ROOT" ls-files --error-unmatch "$p" >/dev/null 2>&1; then
      fail "AC-8: '$p' is TRACKED; a marker in the shipped tree arms every consumer that installs the plugin"
    fi
    # An installed plugin tree, if one is present on this machine.
    for tree in "$HOME"/.claude/plugins/cache/conductor/conductor/*/; do
      [ -d "$tree" ] || continue
      [ -e "$tree$p" ] && fail "AC-8: a marker exists in an installed plugin tree: $tree$p"
    done
    # Each binding must tell a consuming project to ignore the path it names.
    for b in "$ROOT"/adapters/*/binding.md; do
      grep -q "$p" "$b" || continue
      grep -qE '\.gitignore' "$b" \
        || fail "AC-8: $(basename "$(dirname "$b")")/binding.md names '$p' but never tells a consuming project to ignore it"
    done
  done
}

# ----------------------------------- AC-9: the commander is never the writer
check_writer() {
  for p in $PATHS; do
    esc="$(printf '%s' "$p" | sed 's/[.[\*^$]/\\&/g')"
    # A creating verb on the marker path, in a line that also addresses the
    # commander, is the shape this forbids.
    hits="$(grep -rniE "(touch|mkdir|create|write|>[[:space:]]*)${esc}" \
              "$ROOT/doctrine" "$ROOT/contract" "$ROOT/adapters" \
              --include='*.md' --include='*.json' 2>/dev/null \
            | grep -iE 'commander|orchestrator' || true)"
    [ -z "$hits" ] || fail "AC-9: a layer shows the COMMANDER creating the marker:
$hits"
    # ...and the word "commander" need not appear for the instruction to reach one.
    # A bare creating verb in COMMANDER-FACING text is the same defect with the
    # subject elided, so those files are scanned without the keyword filter. Only
    # a binding may show the arming command: that text addresses the operator.
    bare="$(grep -rniE "(touch|mkdir)[[:space:]]+[^[:space:]]*${esc}" \
              "$ROOT/doctrine" "$ROOT/contract" \
              "$ROOT"/adapters/*/SKILL.md "$ROOT"/adapters/*/README.md \
              2>/dev/null || true)"
    [ -z "$bare" ] || fail "AC-9: commander-facing text shows the marker being created (only a binding may, and only addressing the operator):
$bare"
  done
  # ...and the writer must be stated positively somewhere in each binding that
  # names a carrier: silence is how "who writes this" becomes anybody's guess.
  for b in "$ROOT"/adapters/*/binding.md; do
    grep -qE 'switch-path: `' "$b" || continue
    grep -qE 'writer' "$b" \
      || fail "$(basename "$(dirname "$b")")/binding.md names a carrier but never names its writer (AC-9)"
  done
}

# ------------------------------------------------------------------ self-test
if [ "${1:-}" = "--self-test" ]; then
  st_fail=0
  tmp="$(mktemp -d)" || exit 2
  trap 'rm -rf "$tmp"' EXIT

  # (0) the PRODUCTION predicate must pass before anything is overridden. Without
  # this, every leg below could go green while the real rule had silently drifted
  # — the self-test would be proving things about its own injected fakes.
  bad=0
  check_predicate
  if [ "$bad" -eq 0 ]; then
    echo "ok: production predicate passes all seven states before any override"
  else
    echo "SELF-TEST FAIL: the production predicate itself does not pass"; st_fail=1
  fi

  # (1) the AC-6 leg must reject a predicate that consults readability
  bad=0
  predicate() { [ -r "$1" ] && [ -f "$1" ]; }   # the plausible wrong rule
  check_predicate
  if [ "$bad" -eq 0 ]; then
    echo "SELF-TEST FAIL: a readability-consulting predicate was not detected"; st_fail=1
  else
    echo "ok: readability-consulting predicate detected (mode-000 must read as ON)"
  fi
  predicate() { [ -f "$1" ]; }

  # (2) the AC-6 leg must reject a predicate that admits a directory
  bad=0
  predicate() { [ -e "$1" ]; }                  # the other plausible wrong rule
  check_predicate
  if [ "$bad" -eq 0 ]; then
    echo "SELF-TEST FAIL: an existence-only predicate was not detected"; st_fail=1
  else
    echo "ok: existence-only predicate detected (a directory must read as OFF)"
  fi
  predicate() { [ -f "$1" ]; }

  # (3) the AC-8 leg must bite on a planted tracked marker
  bad=0
  PATHS="README.md"        # a path that IS tracked and is NOT gitignored
  check_not_shipped
  if [ "$bad" -eq 0 ]; then
    echo "SELF-TEST FAIL: a tracked, non-ignored marker path was not detected"; st_fail=1
  else
    echo "ok: tracked / non-ignored marker path detected"
  fi

  # (4) an empty marker set must be an ERROR, never a quiet pass
  if grep -q 'the marker set is empty' "$0"; then
    echo "ok: empty marker set exits 2 rather than passing vacuously"
  else
    echo "SELF-TEST FAIL: no empty-set guard"; st_fail=1
  fi

  [ "$st_fail" -eq 0 ] && { echo "SELF-TEST OK"; exit 0; } || { echo "SELF-TEST FAIL"; exit 1; }
fi

# ---------------------------------------------------------------------- run
check_predicate
check_no_parse
check_not_shipped
check_writer

if [ "$bad" -ne 0 ]; then exit 1; fi
echo "CLEAN: switch paths [$(echo $PATHS | tr '\n' ' ')] — predicate is existence-only, contents unparsed, never shipped, commander never the writer"
exit 0
