#!/usr/bin/env bash
# Journal event vocabulary: contract/journal-event.schema.json (doctrine § Machine pointers).
# test-collect-run-stats.sh — fixture suite for the harness binding's tier-0
# estimate-drift emitter (the tool writes nothing anywhere).
# Offline, deterministic.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COL="$ROOT/adapters/claude-code/tools/collect-run-stats.py"
FIX="$ROOT/scripts/fixtures/collect-run-stats"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0

check() { # <name> <expected> <actual>
  if [ "$2" = "$3" ]; then pass=$((pass+1)); else
    fail=$((fail+1)); echo "FAIL: $1 — expected [$2] got [$3]"
  fi
}

# 1. full journal -> estimate-drift lines on stdout, exit 0
python3 "$COL" "$FIX/journal-full.jsonl" >"$TMP/t1.stdout"
check "full: exit 0" 0 $?
check "full: drift lines on stdout" 2 "$(grep -c estimate-drift "$TMP/t1.stdout")"
check "full: ratio computed" 1 "$(head -1 "$TMP/t1.stdout" | grep -c '"ratio"')"

# 2. zero-dispatch inline run -> NOTE, exit 0 (degradation never blocks close)
out="$(python3 "$COL" "$FIX/journal-inline.jsonl")"; rc=$?
check "inline: exit 0" 0 $rc
check "inline: NOTE no offload" 1 "$(printf '%s\n' "$out" | grep -c 'NOTE: no offload')"

# 3. usage missing -> exit 0, zero drift lines, NOTE
out="$(python3 "$COL" "$FIX/journal-no-usage.jsonl")"; rc=$?
check "no-usage: exit 0" 0 $rc
check "no-usage: no drift lines" 0 "$(printf '%s\n' "$out" | grep -c estimate-drift)"
check "no-usage: NOTE" 1 "$(printf '%s\n' "$out" | grep -c '^NOTE:')"

# 4. corrupt journal LINE -> NOTE, exit 0 (degrade, never block)
out="$(python3 "$COL" "$FIX/journal-malformed.jsonl")"; rc=$?
check "malformed: exit 0" 0 $rc
check "malformed: NOTE names parse" 1 "$(printf '%s\n' "$out" | grep -c 'not valid JSON')"

# 5. journal path missing -> usage error exit 2
python3 "$COL" "$TMP/does-not-exist.jsonl" >/dev/null 2>&1
check "missing journal: exit 2" 2 $?

# 6. retired flags rejected — a caller still passing --out/--binding must hear
#    about it, not get a silent no-op
python3 "$COL" "$FIX/journal-full.jsonl" --binding claude-code --out "$TMP/t6.jsonl" >/dev/null 2>&1
check "retired flags: exit 2" 2 $?
check "retired flags: no file created" 0 "$(ls "$TMP"/t6.jsonl 2>/dev/null | wc -l | tr -d ' ')"

# 7. duplicated dispatch_result task_id -> last-wins, single drift line
python3 "$COL" "$FIX/journal-fallback-dup.jsonl" >"$TMP/t7.stdout"
check "dup results: single drift line" 1 "$(grep -c estimate-drift "$TMP/t7.stdout")"
check "dup results: last-wins ratio 0.5" 0.5 "$(python3 -c "import json;print([json.loads(l)['ratio'] for l in open('$TMP/t7.stdout') if 'estimate-drift' in l][0])")"

# 8. empty journal -> NOTE, exit 0
out="$(python3 "$COL" "$FIX/journal-empty.jsonl")"; rc=$?
check "empty journal: exit 0" 0 $rc
check "empty journal: NOTE" 1 "$(printf '%s\n' "$out" | grep -c '^NOTE:')"

# 9. usage "unavailable" (typed degradation marker) -> no drift, no crash
cat > "$TMP/t9-journal.jsonl" <<'EOF'
{"event":"commander_stamp","model":"m","doctrine_rev":"abc1234","vocab":2,"run_id":"t9"}
{"event":"dispatch","task_id":"t1","tier":"mid","resolved_model":"m","read_only":true,"wave":1,"contract":"c","w_est":1000}
{"event":"dispatch_result","task_id":"t1","checker":"VALID","usage":"unavailable"}
EOF
out="$(python3 "$COL" "$TMP/t9-journal.jsonl")"; rc=$?
check "usage-unavailable: exit 0" 0 $rc
check "usage-unavailable: no drift" 0 "$(printf '%s\n' "$out" | grep -c estimate-drift)"

# 10. write-nothing guarantee: the ONLY files in TMP are the ones this test made
check "no side files" 3 "$(ls "$TMP" | wc -l | tr -d ' ')"

echo "----"
echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
