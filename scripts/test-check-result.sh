#!/usr/bin/env bash
# Runs contract/check-result.py over contract/fixtures/ (spec AC-5).
# Filename convention encodes expectation:
#   valid-*.json   → exit 0, output VALID
#   invalid-*.json → exit 1, every output line starts INVALID:
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
for f in "$ROOT"/contract/fixtures/*.json; do
  out="$(python3 "$ROOT/contract/check-result.py" "$f" 2>&1)"; rc=$?
  base="$(basename "$f")"
  case "$base" in
    valid-*)   want_rc=0; want_pat='^VALID$' ;;
    invalid-*) want_rc=1; want_pat='^INVALID: ' ;;
    *) echo "UNKNOWN FIXTURE CLASS: $base"; fail=1; continue ;;
  esac
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $base rc=$rc out=$out"; fail=1
  else
    echo "ok: $base"
  fi
done
exit "$fail"
