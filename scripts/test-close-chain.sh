#!/usr/bin/env bash
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

# --- fixture 1: a clean instrumented run that dispatched nothing ---
mkdir -p "$TMP/clean"
cat > "$TMP/clean/journal.jsonl" <<'EOF'
{"event":"commander_stamp","ts":"2026-07-27T00:00:00Z","model":"m","doctrine_rev":"abc1234","model_gen":"g1","vocab":3}
{"event":"entry","ts":"2026-07-27T00:00:01Z","family":"write-heavy","write_shape":"1-worker","read_breadth":0,"config":{"tiers":"worker=mid"},"grounds":"fixture","veto":null}
{"event":"close","ts":"2026-07-27T00:00:02Z","terminal":"done","members":[]}
EOF

# --- fixture 2: a journal with an S1 violation, so judgment-flow must FAIL ---
mkdir -p "$TMP/dirty"
cat > "$TMP/dirty/journal.jsonl" <<'EOF'
{"event":"commander_stamp","ts":"2026-07-27T00:00:00Z","model":"m","doctrine_rev":"abc1234","model_gen":"g1","vocab":3}
{"event":"judgment_moment","ts":"2026-07-27T00:00:01Z","moment_id":1,"decision_type":"entry-gate","disposition":"frozen"}
{"event":"judgment_moment","ts":"2026-07-27T00:00:02Z","moment_id":1,"decision_type":"grading-dispute","disposition":"frozen"}
EOF

run_under() {  # <shell> <dir> -> writes "$TMP/<shell>-<tag>.out", echoes rc
  sh_bin="$1"; dir="$2"; tag="$3"
  "$sh_bin" "$CHAIN" --journal "$dir/journal.jsonl" --task-dir "$dir" --anchors "$ANCHORS" \
      > "$TMP/$sh_bin-$tag.out" 2>&1
  echo $?
}

# member-status lines only, so the comparison is about verdicts not formatting
statuses() { grep -E '^close-members: ' "$1"; }

for tag in clean dirty; do
  dir="$TMP/$tag"
  rc_bash="$(run_under bash "$dir" "$tag")"
  rc_zsh="$(run_under zsh "$dir" "$tag")"
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
expect "clean: judgment-flow passes"        "$TMP/bash-clean.out" '^judgment-flow: pass'
expect "clean: reconciliation dropped"      "$TMP/bash-clean.out" '"name":"reconciliation","status":"dropped\(trigger-absent\)"'
# absent telemetry: C0 still ran, and the rest is unverifiable — never a pass
expect "clean: conformance unverifiable"    "$TMP/bash-clean.out" '"name":"conformance","status":"unverifiable"'
expect "clean: chain exits 0"               "$TMP/bash-clean.out" 'close-members:'
expect "dirty: failure names its member"    "$TMP/bash-dirty.out" '^CHAIN-FAIL: judgment-flow exit=1'
expect "dirty: failure recorded with rc"    "$TMP/bash-dirty.out" '"name":"judgment-flow","status":"fail\(1\)"'
# the chain does not stop at the first failure: later members are still recorded
expect "dirty: later members still recorded" "$TMP/bash-dirty.out" '"name":"run-stats"'

# clean must exit 0, dirty must exit non-zero
rc="$(run_under bash "$TMP/clean" clean)"; [ "$rc" -eq 0 ] || { echo "FAIL: clean chain exit=$rc want 0"; fail=1; }
rc="$(run_under bash "$TMP/dirty" dirty)"; [ "$rc" -ne 0 ] || { echo "FAIL: dirty chain exit=0, want non-zero"; fail=1; }
[ "$fail" -eq 0 ] && echo "ALL OK"
exit "$fail"
