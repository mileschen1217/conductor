#!/usr/bin/env bash
# check-neutrality.sh — vendor-neutrality scan (spec AC-9 / REQ-5).
# Lives in repo-root scripts/ because this file itself carries the banned-noun
# list and must stay OUTSIDE the scan scope (doctrine/ + contract/).
# The term list is contractual: additions/removals = spec change.
#
# Usage:
#   bash scripts/check-neutrality.sh              # scan doctrine/ + contract/
#   bash scripts/check-neutrality.sh --self-test  # prove scanner detects planted terms
# Exit: 0 = clean (or self-test positive); 1 = hits found (or self-test failed).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TERMS='claude|anthropic|codex|openai|gpt|opus|sonnet|haiku|subagent|AGENTS\.md|SKILL\.md|MCP|TOML'

if [ "${1:-}" = "--self-test" ]; then
  if grep -rnioEH "$TERMS" "$ROOT/scripts/fixtures/neutrality-selfcheck.md" >/dev/null 2>&1; then
    echo "SELF-TEST OK: planted terms detected"
    exit 0
  fi
  echo "SELF-TEST FAIL: planted terms NOT detected"
  exit 1
fi

for d in "$ROOT/doctrine" "$ROOT/contract"; do
  if [ ! -d "$d" ] || [ ! -r "$d" ]; then
    echo "ERROR: scan directory missing or unreadable: $d" >&2
    exit 2
  fi
done

hits="$(grep -rnioEH "$TERMS" "$ROOT/doctrine" "$ROOT/contract" 2>/dev/null)"
rc=$?
case "$rc" in
  0)
    # matches found; normalize to: <repo-relative-file>:<line>: <matched-term>
    printf '%s\n' "$hits" | sed -e "s|^$ROOT/||" -e 's|^\([^:]*:[0-9]*\):|\1: |'
    exit 1
    ;;
  1)
    echo "CLEAN"
    exit 0
    ;;
  *)
    echo "ERROR: grep failed (exit $rc) while scanning doctrine/ + contract/" >&2
    exit 2
    ;;
esac
