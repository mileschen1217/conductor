#!/usr/bin/env bash
# test-journal-event-schema.sh — fixture suite for contract/journal-event.schema.json
# (mode-at-first-dispatch REQ-6 / AC-19).
#
# AC-19 asks that the fixture journals validate against the schema "so the
# fixtures cannot drift from the home they exist to pin". The honest form of
# that is NOT "every fixture validates": several fixtures exist precisely to
# carry a violation, and a suite that demanded they all pass would have to
# either weaken the schema or delete the fixtures. So this suite asserts a
# POLARITY PER FIXTURE, and every journal fixture must appear in the table
# below — an unlisted fixture is a failure, not a skip, so a new fixture cannot
# slip in unclassified and quietly widen what the schema is thought to allow.
#
# Usage: bash scripts/test-journal-event-schema.sh
# Exit: 0 = every fixture matches its declared polarity; 1 = mismatch.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECK="python3 $ROOT/contract/check-journal-event.py"
fail=0
ok=0

# Fixtures that MUST be rejected, each with the violation it exists to carry.
# A fixture leaving this list is a schema weakening; one joining it silently is
# a fixture whose purpose changed without anyone saying so.
declare_invalid() { INVALID_LIST="$INVALID_LIST
$1|$2"; }
INVALID_LIST=""
declare_invalid "brake-lines/journal-brake-bad-ground.jsonl"          "necessity ground outside the closed four-ground enum"
declare_invalid "brake-lines/journal-brake-invented-value.jsonl"      "computed term with no basis — an invented value"
declare_invalid "brake-lines/journal-brake-stale-vocab.jsonl"         "vocab 2: a dialect below the current vocabulary"
declare_invalid "collect-run-stats/journal-malformed.jsonl"           "crash-truncated write: a line that is not JSON"
declare_invalid "collect-run-stats/journal-no-usage.jsonl"            "dispatch_result omitting usage — the typed marker \"unavailable\" exists so omission is not a legal degradation"
declare_invalid "judgment-flow/journal-class-override-empty.jsonl"    "S4: class_default override with an empty reason"
declare_invalid "judgment-flow/journal-class-no-default.jsonl"        "S4: entry declares a class and omits class_default"
declare_invalid "judgment-flow/journal-stale-vocab.jsonl"             "vocab 2: a dialect below the current vocabulary"
declare_invalid "judgment-flow/journal-usage-prose.jsonl"             "S3: usage as a prose see-elsewhere pointer"

expected_invalid() {
  printf '%s\n' "$INVALID_LIST" | grep -q "^$1|" && return 0 || return 1
}
reason_for() {
  printf '%s\n' "$INVALID_LIST" | grep "^$1|" | head -1 | cut -d'|' -f2
}

echo "== fixture polarity =="
for f in $(find "$ROOT/scripts/fixtures" -name '*.jsonl' | grep -vE 'probe|telemetry' | sort); do
  rel="$(basename "$(dirname "$f")")/$(basename "$f")"
  $CHECK "$f" >/dev/null 2>&1; rc=$?
  if expected_invalid "$rel"; then
    if [ "$rc" -ne 0 ]; then
      ok=$((ok+1))
    else
      echo "FAIL: $rel VALIDATES but must not — it carries: $(reason_for "$rel")"
      echo "      the schema no longer catches the violation this fixture exists to pin"
      fail=1
    fi
  else
    if [ "$rc" -eq 0 ]; then
      ok=$((ok+1))
    else
      echo "FAIL: $rel does not validate, and is not declared as a deliberate violation:"
      $CHECK "$f" 2>&1 | sed 's/^/      /' | head -4
      fail=1
    fi
  fi
done
echo "  $ok fixtures matched their declared polarity"

# Every declared-invalid entry must correspond to a fixture that still exists —
# a stale entry would let a deleted fixture keep vouching for the schema.
echo "== declared-invalid entries all resolve to a real fixture =="
printf '%s\n' "$INVALID_LIST" | grep '|' | cut -d'|' -f1 | while read -r rel; do
  [ -n "$rel" ] || continue
  if ! find "$ROOT/scripts/fixtures" -path "*/$rel" | grep -q .; then
    echo "FAIL: declared-invalid fixture no longer exists: $rel"
    exit 1
  fi
done || fail=1

# The schema must enforce every keyword it uses; an unenforced keyword is a
# constraint a reader would believe is checked and is not.
echo "== validator covers every keyword the schema uses =="
if $CHECK --schema-audit >/dev/null 2>&1; then
  echo "  clean"
else
  echo "FAIL: schema uses keywords this validator does not enforce:"
  $CHECK --schema-audit | sed 's/^/      /'
  fail=1
fi

# Negative control: the suite must be able to fail. A planted violation on a
# fixture that otherwise validates has to be caught, or every green above is
# vacuous.
echo "== negative control (a planted violation is caught) =="
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
src="$ROOT/scripts/fixtures/judgment-flow/journal-clean.jsonl"
python3 - "$src" "$tmp/planted.jsonl" <<'PY'
import json, sys
out = []
for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    d = json.loads(line)
    if d.get("event") == "judgment_moment":
        d["disposition"] = "sort-of"        # outside the closed enum
    out.append(json.dumps(d, separators=(',', ':')))
open(sys.argv[2], "w").write("\n".join(out) + "\n")
PY
if $CHECK "$tmp/planted.jsonl" >/dev/null 2>&1; then
  echo "FAIL: a planted out-of-enum disposition was NOT caught — the suite is vacuous"
  fail=1
else
  echo "  planted out-of-enum disposition caught"
fi

[ "$fail" -eq 0 ] && echo "PASS" || echo "FAIL"
exit $fail
