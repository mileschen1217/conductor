#!/usr/bin/env bash
# check-rev-coherence.sh — re-key coherence gate (consumer-gated-ceremony AC-13).
# Two facts NEITHER check-doctrine-rev.sh NOR check-role-cards.sh discharges:
#   (1) all six stamped files' graded_under.doctrine_rev agree with doctrine/REV
#       — the 3 role cards (contract/roles/*.md) + the 3 pre-cast CC agents
#       (adapters/claude-code/agents/*.md). check-doctrine-rev only verifies the
#       REV stamp itself = doctrine last-change; check-role-cards only scans for
#       banned judgment-face literals — neither reads graded_under (ST-5
#       card-staleness regression-ratchet).
#   (2) .claude-plugin/plugin.json version was bumped relative to an EXPLICIT
#       pre-change baseline. The baseline is a required input (`--base <ref>`),
#       never an implicit repo-history assumption: "the previous version" has one
#       falsifiable definition — `git show <base>:.claude-plugin/plugin.json`.
#
# Usage:
#   bash scripts/check-rev-coherence.sh --base <git-ref>   # verify vs a ship base
#   bash scripts/check-rev-coherence.sh --base-file <path> # verify vs a file baseline
#   bash scripts/check-rev-coherence.sh --self-test        # prove it detects drift
# A fixture tree may be supplied with `--root <dir>` (holds REV, *.md cards,
# plugin.json); default root is the repo.
# Exit: 0 = coherent; 1 = incoherent (stale graded_under or unbumped version);
#       2 = environment error (including missing --base/--base-file).
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"

_version() {  # extract "version" from a plugin.json on stdin
  python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])'
}

# check-rev-coherence over one tree. Args: <root> <rev-baseline-cmd...>
# The baseline command must emit the pre-change plugin.json on stdout.
_check_tree() {
  root="$1"; shift
  rev_file="$root/doctrine/REV"
  plugin="$root/.claude-plugin/plugin.json"
  [ -r "$rev_file" ] || { echo "ERROR: REV missing at $rev_file" >&2; return 2; }
  [ -r "$plugin" ] || { echo "ERROR: plugin.json missing at $plugin" >&2; return 2; }
  rev="$(tr -d '[:space:]' < "$rev_file")"
  bad=0

  # (1) graded_under coherence over the stamped files. In repo mode the re-key
  # roster is EXACTLY six files (3 role cards + 3 CC agents); a MISSING member is
  # an incoherent re-key (fail-closed) — never a silent pass over whatever glob
  # happened to match (a dropped card must not slip the gate).
  if [ -d "$root/contract/roles" ]; then
    expected="contract/roles/read-scout.md contract/roles/mech-writer.md contract/roles/fresh-verifier.md adapters/claude-code/agents/read-scout.md adapters/claude-code/agents/mech-writer.md adapters/claude-code/agents/fresh-verifier.md"
    files=""
    for rel in $expected; do
      if [ -r "$root/$rel" ]; then
        files="$files $root/$rel"
      else
        echo "INCOHERENT: expected stamped file missing or unreadable: $rel"; bad=1
      fi
    done
  else
    files=$(ls "$root"/*.md 2>/dev/null)   # fixture tree: flat card dir
    [ -n "$files" ] || { echo "ERROR: no stamped files found under $root" >&2; return 2; }
  fi
  for f in $files; do
    gu="$(grep -oE 'doctrine_rev:[[:space:]]*"[^"]*"' "$f" | head -1 | grep -oE '"[^"]*"' | tr -d '"')"
    if [ -z "$gu" ]; then
      echo "INCOHERENT: $f has no graded_under.doctrine_rev"; bad=1
    elif [ "$gu" != "$rev" ]; then
      echo "INCOHERENT: $f graded_under=$gu but doctrine/REV=$rev (stale card)"; bad=1
    fi
  done

  # (2) version bumped vs explicit baseline
  cur="$(_version < "$plugin")"
  base_ver="$("$@" 2>/dev/null | _version 2>/dev/null)"
  if [ -z "$base_ver" ]; then
    echo "ERROR: could not read baseline plugin.json version" >&2; return 2
  fi
  if [ "$cur" = "$base_ver" ]; then
    echo "INCOHERENT: plugin.json version $cur not bumped from baseline $base_ver"; bad=1
  fi

  if [ "$bad" -ne 0 ]; then return 1; fi
  echo "CLEAN: 6-file graded_under = doctrine/REV=$rev; version $base_ver -> $cur (bumped)"
  return 0
}

# ---- argument parse ----
ROOT="$REPO"; BASE_REF=""; BASE_FILE=""; SELF_TEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE_REF="${2:-}"; shift 2 ;;
    --base-file) BASE_FILE="${2:-}"; shift 2 ;;
    --root) ROOT="${2:-}"; shift 2 ;;
    --self-test) SELF_TEST=1; shift ;;
    *) echo "ERROR: unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [ "$SELF_TEST" -eq 1 ]; then
  fixroot="$REPO/scripts/fixtures/rev-coherence"
  [ -d "$fixroot" ] || { echo "SELF-TEST ERROR: fixtures missing at $fixroot" >&2; exit 2; }
  fail=0
  for d in "$fixroot"/*/; do
    name="$(basename "$d")"
    _check_tree "$d" cat "$d/base-plugin.json" >/dev/null 2>&1; rc=$?
    case "$name" in
      consistent) want=0 ;;
      *)          want=1 ;;   # stale-* / unbumped-* must be flagged
    esac
    if [ "$rc" -eq "$want" ]; then
      echo "ok: $name (rc=$rc, want=$want)"
    else
      echo "SELF-TEST FAIL: $name rc=$rc want=$want"; fail=1
    fi
  done
  # prove --base is required (missing baseline = exit 2, not a silent pass)
  bash "$0" --root "$fixroot/consistent" >/dev/null 2>&1; rc=$?
  if [ "$rc" -eq 2 ]; then echo "ok: missing --base -> exit 2"; else echo "SELF-TEST FAIL: missing --base gave rc=$rc, want 2"; fail=1; fi
  [ "$fail" -eq 0 ] && { echo "SELF-TEST OK"; exit 0; } || { echo "SELF-TEST FAIL"; exit 1; }
fi

# baseline required: explicit input, never an implicit assumption
if [ -n "$BASE_FILE" ]; then
  [ -r "$BASE_FILE" ] || { echo "ERROR: --base-file not readable: $BASE_FILE" >&2; exit 2; }
  _check_tree "$ROOT" cat "$BASE_FILE"; exit $?
elif [ -n "$BASE_REF" ]; then
  _check_tree "$ROOT" git -C "$ROOT" show "$BASE_REF:.claude-plugin/plugin.json"; exit $?
else
  echo "ERROR: --base <git-ref> (or --base-file <path>) is required — the version baseline must be an explicit input, not an implicit repo-history assumption" >&2
  exit 2
fi
