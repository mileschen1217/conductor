#!/usr/bin/env bash
# test-collect-run-stats.sh — fixture suite for the CC binding's tier-0
# constants collector (v3 REQ-5 / AC-15). Offline, deterministic.
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

# 1. full journal -> constants row, exit 0, expected medians x weights
out="$TMP/t1.jsonl"
python3 "$COL" "$FIX/journal-full.jsonl" --binding claude-code --out "$out" --project fixt >"$TMP/t1.stdout"
check "full: exit 0" 0 $?
row="$(head -1 "$out")"
check "full: kind constants" constants "$(python3 -c "import json,sys;print(json.loads(open('$out').readline())['kind'])")"
check "full: C_fresh (median 40000 x 0.25)" 10000 "$(python3 -c "import json;print(json.loads(open('$out').readline())['const']['C_fresh'])")"
check "full: C_brief_cmd (median 3000 x 1)" 3000 "$(python3 -c "import json;print(json.loads(open('$out').readline())['const']['C_brief_cmd'])")"
check "full: C_brief_worker (3000 x 0.2)" 600 "$(python3 -c "import json;print(json.loads(open('$out').readline())['const']['C_brief_worker'])")"
check "full: C_reread (median 4000 x 0.2)" 800 "$(python3 -c "import json;print(json.loads(open('$out').readline())['const']['C_reread'])")"
check "full: family from journal" read-heavy "$(python3 -c "import json;print(json.loads(open('$out').readline())['key']['family'])")"
check "full: status measured" measured "$(python3 -c "import json;print(json.loads(open('$out').readline())['status'])")"
check "full: drift lines on stdout" 2 "$(grep -c estimate-drift "$TMP/t1.stdout")"

# 2. usage missing -> UNVERIFIABLE, exit 0, run not blocked
out="$TMP/t2.jsonl"
python3 "$COL" "$FIX/journal-no-usage.jsonl" --binding claude-code --out "$out" >/dev/null
check "no-usage: exit 0" 0 $?
check "no-usage: kind unverifiable" unverifiable "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"

# 3. zero-dispatch inline run -> UNVERIFIABLE (nothing to measure)
out="$TMP/t3.jsonl"
python3 "$COL" "$FIX/journal-inline.jsonl" --binding claude-code --out "$out" >/dev/null
check "inline: exit 0" 0 $?
check "inline: kind unverifiable" unverifiable "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"

# 4. family missing -> UNVERIFIABLE naming the gap
out="$TMP/t4.jsonl"
python3 "$COL" "$FIX/journal-no-family.jsonl" --binding claude-code --out "$out" >/dev/null
check "no-family: exit 0" 0 $?
check "no-family: reason names family" 1 "$(python3 -c "import json;print(1 if 'family' in json.loads(open('$out').readline())['reason'] else 0)")"

# 5. journal path missing -> usage error exit 2
python3 "$COL" "$FIX/does-not-exist.jsonl" --binding claude-code --out "$TMP/t5.jsonl" 2>/dev/null
check "missing journal: exit 2" 2 $?

# 6. append-only: second run appends a second line, first line unchanged
out="$TMP/t6.jsonl"
python3 "$COL" "$FIX/journal-full.jsonl" --binding claude-code --out "$out" >/dev/null
first="$(head -1 "$out")"
python3 "$COL" "$FIX/journal-full.jsonl" --binding claude-code --out "$out" >/dev/null
check "append: 2 lines" 2 "$(wc -l < "$out" | tr -d ' ')"
check "append: line 1 unchanged" "$first" "$(head -1 "$out")"

# 8. corrupt journal LINE -> UNVERIFIABLE exit 0 (degrade, never block; nonzero = usage errors only)
out="$TMP/t8.jsonl"
python3 "$COL" "$FIX/journal-malformed.jsonl" --binding claude-code --out "$out" >/dev/null
check "malformed line: exit 0" 0 $?
check "malformed line: kind unverifiable" unverifiable "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"
check "malformed line: reason names parse failure" 1 "$(python3 -c "import json;print(1 if 'parse failure' in json.loads(open('$out').readline())['reason'] else 0)")"

# 9. family absent -> unverifiable row keys family 'unknown', never a real family
out="$TMP/t9.jsonl"
python3 "$COL" "$FIX/journal-no-family.jsonl" --binding claude-code --out "$out" >/dev/null
check "no-family: key.family unknown" unknown "$(python3 -c "import json;print(json.loads(open('$out').readline())['key']['family'])")"

# 10. cache_creation absent -> falls back to input_tokens; duplicate dispatch_result task_id -> last-wins, no double count
out="$TMP/t10.jsonl"
python3 "$COL" "$FIX/journal-fallback-dup.jsonl" --binding claude-code --out "$out" > "$TMP/t10.stdout"
check "fallback-dup: exit 0" 0 $?
check "fallback-dup: kind constants" constants "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"
check "fallback-dup: C_fresh from input_tokens fallback (40000 x 0.25)" 10000 "$(python3 -c "import json;print(json.loads(open('$out').readline())['const']['C_fresh'])")"
check "fallback-dup: duplicate result deduped (1 drift line, last-wins ratio 0.5)" 1 "$(grep -c estimate-drift "$TMP/t10.stdout")"
check "fallback-dup: last-wins output used" 0.5 "$(python3 -c "import json,sys;print([json.loads(l)['ratio'] for l in open('$TMP/t10.stdout') if 'estimate-drift' in l][0])")"

# 11. empty journal file -> UNVERIFIABLE (no commander_stamp), exit 0
out="$TMP/t11.jsonl"
python3 "$COL" "$FIX/journal-empty.jsonl" --binding claude-code --out "$out" >/dev/null
check "empty journal: exit 0" 0 $?
check "empty journal: kind unverifiable" unverifiable "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"

# 7. unknown binding -> UNVERIFIABLE (degrade, never block)
out="$TMP/t7.jsonl"
python3 "$COL" "$FIX/journal-full.jsonl" --binding no-such-harness --out "$out" >/dev/null
check "unknown binding: exit 0" 0 $?
check "unknown binding: kind unverifiable" unverifiable "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"

echo "----"
echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
