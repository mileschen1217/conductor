#!/usr/bin/env bash
# Journal event vocabulary: contract/journal-event.schema.json (doctrine § Machine pointers).
# test-close-chain.sh — portability + membership fixture suite for the close
# chain (mode-at-first-dispatch AC-17).
#
# The bug this suite exists for: the shipped chain used ${PIPESTATUS[0]} to
# read a member's exit code. Under zsh that expands to empty, so every
# member's rc read as success — a chain that reported CLEAN while a member
# had failed. Three separate runs paid for it. So the acceptance is not "the
# snippet looks portable": it is that the SAME chain, executed by bash and by
# zsh, reports the SAME per-member exit codes.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHAIN="$ROOT/adapters/claude-code/tools/close-chain.sh"
ANCHORS='prose=4,code=3,cjk=1.5,correction=1.3'
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail=0

if ! command -v zsh >/dev/null 2>&1; then
  echo "UNVERIFIABLE: zsh is not installed — the cross-shell leg of AC-17 cannot be exercised on this machine"
  exit 2
fi

JOURNAL_OK='{"event":"commander_stamp","ts":"2026-07-27T00:00:00Z","model":"m","doctrine_rev":"abc1234","model_gen":"g1","vocab":3}
{"event":"entry","ts":"2026-07-27T00:00:01Z","family":"write-heavy","write_shape":"1-worker","read_breadth":0,"config":{"tiers":"worker=mid"},"grounds":"fixture","veto":null}
{"event":"close","ts":"2026-07-27T00:00:02Z","terminal":"done","members":[]}'

# --- fixture 1: a clean instrumented run, telemetry present ---
mkdir -p "$TMP/clean"
printf '%s\n' "$JOURNAL_OK" > "$TMP/clean/journal.jsonl"
printf '%s\n' '{"type":"session","model":"m"}' > "$TMP/clean/telemetry.jsonl"

# --- fixture 2: same run, telemetry ABSENT. Every instrumented run is
#     deliberately armed by an operator, so the evidence it depends on is owed: the
#     conformance member must FAIL, not pass and not drop. ---
mkdir -p "$TMP/notelemetry"
printf '%s\n' "$JOURNAL_OK" > "$TMP/notelemetry/journal.jsonl"

# --- fixture 3: an S1 violation, so judgment-flow must FAIL ---
mkdir -p "$TMP/dirty"
cat > "$TMP/dirty/journal.jsonl" <<'EOF'
{"event":"commander_stamp","ts":"2026-07-27T00:00:00Z","model":"m","doctrine_rev":"abc1234","model_gen":"g1","vocab":3}
{"event":"judgment_moment","ts":"2026-07-27T00:00:01Z","moment_id":1,"decision_type":"entry-gate","disposition":"frozen"}
{"event":"judgment_moment","ts":"2026-07-27T00:00:02Z","moment_id":1,"decision_type":"grading-dispute","disposition":"frozen"}
EOF

run_under() {  # <shell> <tag> -> echoes rc, writes "$TMP/<shell>-<tag>.out"
  sh_bin="$1"; tag="$2"; dir="$TMP/$tag"
  if [ -r "$dir/telemetry.jsonl" ]; then
    "$sh_bin" "$CHAIN" --journal "$dir/journal.jsonl" --task-dir "$dir" \
        --anchors "$ANCHORS" --telemetry "$dir/telemetry.jsonl" > "$TMP/$sh_bin-$tag.out" 2>&1
  else
    "$sh_bin" "$CHAIN" --journal "$dir/journal.jsonl" --task-dir "$dir" \
        --anchors "$ANCHORS" > "$TMP/$sh_bin-$tag.out" 2>&1
  fi
  echo $?
}

statuses() { grep -E '^close-members: ' "$1"; }

for tag in clean notelemetry dirty; do
  rc_bash="$(run_under bash "$tag")"
  rc_zsh="$(run_under zsh "$tag")"
  if [ "$rc_bash" != "$rc_zsh" ]; then
    echo "FAIL: $tag — chain exit differs by shell (bash=$rc_bash zsh=$rc_zsh)"; fail=1
  else
    echo "ok: $tag — same chain exit under bash and zsh (rc=$rc_bash)"
  fi
  s_bash="$(statuses "$TMP/bash-$tag.out")"
  s_zsh="$(statuses "$TMP/zsh-$tag.out")"
  if [ "$s_bash" != "$s_zsh" ]; then
    echo "FAIL: $tag — per-member statuses differ by shell"
    echo "  bash: $s_bash"
    echo "  zsh:  $s_zsh"; fail=1
  else
    echo "ok: $tag — same per-member statuses under bash and zsh"
  fi
done

# --- the statuses themselves must be right, not merely equal ---
expect() {  # <name> <file> <pattern>
  if grep -qE "$3" "$2"; then echo "ok: $1"; else
    echo "FAIL: $1 — pattern not found: $3"; sed 's/^/    /' "$2"; fail=1; fi
}
expect "clean: judgment-flow passes"         "$TMP/bash-clean.out" '^judgment-flow: pass'
expect "clean: reconciliation dropped"       "$TMP/bash-clean.out" '"name":"reconciliation","status":"dropped\(trigger-absent\)"'
expect "clean: conformance passes with telemetry" "$TMP/bash-clean.out" '"name":"conformance","status":"pass"'
# absent telemetry is a FAILURE, not a tolerated state: an instrumented run was
# chosen, so the evidence the measurement depends on is owed
expect "no telemetry: conformance fails"     "$TMP/bash-notelemetry.out" '"name":"conformance","status":"fail\(2\)"'
expect "no telemetry: failure names member"  "$TMP/bash-notelemetry.out" '^CHAIN-FAIL: conformance exit=2'
# ... and the status vocabulary has exactly three values — no fourth escape
if grep -q 'unverifiable' "$TMP/bash-notelemetry.out"; then
  echo "FAIL: close chain emitted a status outside pass|fail(<rc>)|dropped(trigger-absent)"; fail=1
else
  echo "ok: status vocabulary is the pinned three values"
fi
expect "dirty: failure names its member"     "$TMP/bash-dirty.out" '^CHAIN-FAIL: judgment-flow exit=1'
expect "dirty: failure recorded with rc"     "$TMP/bash-dirty.out" '"name":"judgment-flow","status":"fail\(1\)"'
# the chain does not stop at the first failure: later members are still recorded
expect "dirty: later members still recorded" "$TMP/bash-dirty.out" '"name":"run-stats"'

# exit codes: clean 0, the other two non-zero
rc="$(run_under bash clean)";       [ "$rc" -eq 0 ] || { echo "FAIL: clean chain exit=$rc want 0"; fail=1; }
rc="$(run_under bash notelemetry)"; [ "$rc" -ne 0 ] || { echo "FAIL: no-telemetry chain exit=0, want non-zero"; fail=1; }
rc="$(run_under bash dirty)";       [ "$rc" -ne 0 ] || { echo "FAIL: dirty chain exit=0, want non-zero"; fail=1; }
[ "$fail" -eq 0 ] && echo "ALL OK"
exit "$fail"
