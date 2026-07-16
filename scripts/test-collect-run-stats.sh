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

# 6. append-only + state machine: first row measured (bootstrap, consumable);
#    a second same-key collector row lands proposed (not consumable) until a
#    human promotes; first line never rewritten
out="$TMP/t6.jsonl"
python3 "$COL" "$FIX/journal-full.jsonl" --binding claude-code --out "$out" >/dev/null
first="$(head -1 "$out")"
python3 "$COL" "$FIX/journal-full.jsonl" --binding claude-code --out "$out" >/dev/null
check "append: 2 lines" 2 "$(wc -l < "$out" | tr -d ' ')"
check "append: line 1 unchanged" "$first" "$(head -1 "$out")"
check "state machine: first row measured" measured "$(python3 -c "import json;print(json.loads(open('$out').readline())['status'])")"
check "state machine: second same-key row proposed" proposed "$(python3 -c "import json;print(json.loads(list(open('$out'))[1])['status'])")"
# different key (family) in the same table still bootstraps measured
python3 "$COL" "$FIX/journal-total-proxy.jsonl" --binding claude-code --out "$out" >/dev/null
check "state machine: different key bootstraps measured" measured "$(python3 -c "import json;print(json.loads(list(open('$out'))[2])['status'])")"
# a promoted row for the key also blocks new measured rows
out="$TMP/t6b.jsonl"
python3 - "$out" <<'PYEOF'
import json,sys
row={"schema":"constants/v1","kind":"constants","key":{"family":"read-heavy","harness":"claude-code","model_gen":"g2026.07"},"const":{"C_fresh":1,"C_brief_cmd":1,"C_brief_worker":1,"C_reread":1},"unit":"tok-eq","burner":{"C_fresh":"worker","C_brief_cmd":"commander","C_brief_worker":"worker","C_reread":"commander"},"status":"promoted","fidelity":"seed","provenance":{"run_id":"seed","project":"t","ts":"2026-07-16T00:00:00Z"}}
open(sys.argv[1],"w").write(json.dumps(row)+"\n")
PYEOF
python3 "$COL" "$FIX/journal-full.jsonl" --binding claude-code --out "$out" >/dev/null
check "state machine: promoted row forces proposed" proposed "$(python3 -c "import json;print(json.loads(list(open('$out'))[1])['status'])")"

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

# 12. total_tokens-only usage -> total-proxy fallback leg, fidelity named
out="$TMP/t12.jsonl"
python3 "$COL" "$FIX/journal-total-proxy.jsonl" --binding claude-code --out "$out" >/dev/null
check "total-proxy: exit 0" 0 $?
check "total-proxy: C_fresh (32000 x 0.25)" 8000 "$(python3 -c "import json;print(json.loads(open('$out').readline())['const']['C_fresh'])")"
check "total-proxy: fidelity names source" 1 "$(python3 -c "import json;print(1 if 'total-proxy' in json.loads(open('$out').readline())['fidelity'] else 0)")"

# 13. Agent-tool subagent_tokens shape (live-run finding) -> total-proxy leg
out="$TMP/t13.jsonl"
python3 "$COL" "$FIX/journal-subagent-tokens.jsonl" --binding claude-code --out "$out" >/dev/null
check "subagent-tokens: exit 0" 0 $?
check "subagent-tokens: kind constants" constants "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"
check "subagent-tokens: C_fresh (47061 x 0.25 -> int)" 11765 "$(python3 -c "import json;print(json.loads(open('$out').readline())['const']['C_fresh'])")"
check "subagent-tokens: fidelity names total-proxy" 1 "$(python3 -c "import json;print(1 if 'total-proxy' in json.loads(open('$out').readline())['fidelity'] else 0)")"

# 14. heterogeneous usage shapes -> fidelity names ALL sources used
out="$TMP/t14.jsonl"
python3 "$COL" "$FIX/journal-mixed-source.jsonl" --binding claude-code --out "$out" >/dev/null
check "mixed-source: exit 0" 0 $?
check "mixed-source: fidelity lists both sources" "in-channel-worker-usage(cache-creation+total-proxy)+journal-estimate" "$(python3 -c "import json;print(json.loads(open('$out').readline())['fidelity'])")"

# 7. unknown binding -> UNVERIFIABLE (degrade, never block)
out="$TMP/t7.jsonl"
python3 "$COL" "$FIX/journal-full.jsonl" --binding no-such-harness --out "$out" >/dev/null
check "unknown binding: exit 0" 0 $?
check "unknown binding: kind unverifiable" unverifiable "$(python3 -c "import json;print(json.loads(open('$out').readline())['kind'])")"

echo "----"
echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
