#!/usr/bin/env bash
# test-probe-select.sh — fixture suite for the tier-0 probe-row selector
# (v3.1 AC-8 (c)/(d) legs: three-axis match, deterministic three-state output).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="$ROOT/scripts/probe-select.py"
F="$ROOT/scripts/fixtures/probe-select"
fail=0
check() { local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc; out="$(python3 "$A" "$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else echo "ok: $name"; fi
}
# hit: latest matching row wins (append-only file order)
check hit-latest    0 '^HIT aaa111@2026-07-18T01:00:00Z boot_tokens=12000$' \
  "$F/probe-record.jsonl" --harness harness-x --config-hash aaa111 --model-gen g1
# hash mismatch -> reprobe (cache invalidation)
check hash-miss     1 '^REPROBE$' \
  "$F/probe-record.jsonl" --harness harness-x --config-hash ccc333 --model-gen g1
# model-gen axis: hash matches, gen tag is old -> reprobe (AC-8(c))
check gen-miss      1 '^REPROBE$' \
  "$F/probe-record.jsonl" --harness harness-x --config-hash aaa111 --model-gen g2
# harness axis: hash+gen match a row of ANOTHER harness -> reprobe (AC-8(c))
check harness-miss  1 '^REPROBE$' \
  "$F/probe-record.jsonl" --harness harness-z --config-hash aaa111 --model-gen g1
# absent record file = first-entry case -> reprobe, not error
check absent-file   1 '^REPROBE$' \
  "$F/no-such-record.jsonl" --harness harness-x --config-hash aaa111 --model-gen g1
# malformed row (ill-typed field) -> ERROR, fail-safe (AC-8(d))
check malformed-field 2 '^ERROR line 1: malformed row: boot_tokens' \
  "$F/probe-malformed-field.jsonl" --harness harness-x --config-hash aaa111 --model-gen g1
# malformed JSON -> ERROR (AC-8(d))
check malformed-json 2 '^ERROR line 1: JSON parse error' \
  "$F/probe-malformed-json.jsonl" --harness harness-x --config-hash aaa111 --model-gen g1
# determinism: same query, same answer, twice
o1="$(python3 "$A" "$F/probe-record.jsonl" --harness harness-x --config-hash aaa111 --model-gen g1)"
o2="$(python3 "$A" "$F/probe-record.jsonl" --harness harness-x --config-hash aaa111 --model-gen g1)"
if [ "$o1" = "$o2" ]; then echo "ok: deterministic"; else echo "FAIL: nondeterministic"; fail=1; fi
exit "$fail"
