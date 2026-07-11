#!/usr/bin/env bash
# Fixture suite for adapters/claude-code/advisor-observations.py.
#
# The producer feeds a false-negative-hostile check (undisclosed advisor use),
# so the property under test is not "does it count calls" but "does it ever
# emit a file that could be mistaken for evidence of absence". Every fatal case
# therefore asserts BOTH a non-zero exit AND empty stdout: a consumable file
# written under doubt is the failure mode, not the exit code.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
P="python3 $ROOT/adapters/claude-code/advisor-observations.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 "$ROOT/adapters/claude-code/fixtures/build.py" "$TMP"
fail=0

check() { # <name> <want_rc> <want_stdout_lines> <want_stderr_pattern> <fixture>
  local name="$1" want_rc="$2" want_lines="$3" want_pat="$4" fx="$5"
  local out err rc lines
  out="$($P --transcript "$TMP/$fx/session.jsonl" --task-ids t-alpha t-beta 2>"$TMP/err")"
  rc=$?
  err="$(cat "$TMP/err")"
  lines="$(printf '%s' "$out" | grep -c . || true)"
  if [ "$rc" -ne "$want_rc" ] || [ "$lines" -ne "$want_lines" ] \
     || ! printf '%s\n' "$err" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) stdout_lines=$lines (want $want_lines)"
    echo "  stdout: $out"
    echo "  stderr: $err"
    fail=1
  else
    echo "ok: $name"
  fi
}

# the only path that produces a file: every advisor call attributed
check happy             0 2 'observed 2 worker advisor call' happy
# ...and the commander's own call is not among those rows
if $P --transcript "$TMP/happy/session.jsonl" --task-ids t-alpha t-beta 2>/dev/null \
     | grep -q 'commander'; then
  echo "FAIL: commander-not-emitted (a commander row is unjoinable by construction)"; fail=1
else
  echo "ok: commander-not-emitted"
fi
# every way a call can go unattributed is fatal AND silent on stdout
check no-marker         1 0 'no .Task contract' no-marker
check unknown-task      1 0 'not among --task-ids' unknown-task
check two-markers       1 0 'multiple task contracts' two-markers
check nested            1 0 'spawnDepth 2' nested
check no-meta           1 0 'no agent-a1.meta.json' no-meta
check unknown-tooluseid 1 0 'matches no Agent dispatch' unknown-tooluseid
check malformed-line    1 0 'not valid JSON' malformed-line
check bad-content-shape 1 0 'non-list content' bad-content-shape
check no-subagents-dir  1 0 'no subagents directory' no-subagents-dir

exit "$fail"
