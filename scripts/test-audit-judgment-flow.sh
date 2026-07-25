#!/usr/bin/env bash
# Runs scripts/audit-judgment-flow.py over scripts/fixtures/judgment-flow/ (spec AC-3/AC-4).
# Table-driven: each case = expected exit code + required output pattern.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="python3 $ROOT/scripts/audit-judgment-flow.py"
F="$ROOT/scripts/fixtures/judgment-flow"
fail=0
check() { # <name> <want_rc> <want_pattern> <cmd...>
  local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else
    echo "ok: $name"
  fi
}
check clean            0 '^CALIBRATION: attention threshold' $A "$F/journal-clean.jsonl"
check unavailable      0 '^LEGACY: '                         $A "$F/journal-unavailable.jsonl"
check no-precall       1 '^VIOLATION: .*pre-call'            $A "$F/journal-no-precall.jsonl"
check double-consult   1 '^VIOLATION: .*consulted twice'     $A "$F/journal-double-consult.jsonl"
check underc-advisor   1 '^VIOLATION: .*UNDER-CONSULTATION'  $A "$F/journal-underconsult-advisor.jsonl"
check underc-blocked   1 '^VIOLATION: .*UNDER-CONSULTATION'  $A "$F/journal-underconsult-blocked.jsonl"
check dangling         1 '^VIOLATION: .*dangling'            $A "$F/journal-dangling.jsonl"
check bad-ruling       1 '^VIOLATION: .*ruling schema'       $A "$F/journal-bad-ruling.jsonl"
check missing-thresh   1 '^VIOLATION: .*crossing unjournaled' $A "$F/journal-missing-threshold.jsonl"
check echo-mismatch    1 '^VIOLATION: .*echo broken'         $A "$F/journal-echo-mismatch.jsonl"
check wrong-threshold  1 '^VIOLATION: .*advisor_threshold line malformed' $A "$F/journal-wrong-threshold.jsonl"
check thresh-misplaced 1 '^VIOLATION: .*malformed or misplaced' $A "$F/journal-threshold-misplaced.jsonl"
check ruling-echo      1 '^VIOLATION: .*advisor_ruling line .* echo broken|^VIOLATION: .*echo broken: advisor_ruling' $A "$F/journal-echo-mismatch-ruling.jsonl"
check bad-notify       1 '^VIOLATION: calibration_notify'    $A "$F/journal-bad-notify.jsonl"
check missing-journal  2 '^UNVERIFIABLE: '                   $A "$F/nonexistent.jsonl"
check results-no-obs   2 '^UNVERIFIABLE: undisclosed-use'    $A "$F/journal-clean.jsonl" --results "$F/results/result-disclosed.json"
check undisclosed      1 '^VIOLATION: .*undisclosed'         $A "$F/journal-clean.jsonl" --results "$F/results/result-disclosed.json" "$F/results/result-silent.json" "$F/results/result-illegal.json" --advisor-observations "$F/observations.jsonl"
check disclosed-ok     0 '^CALIBRATION: '                    $A "$F/journal-clean.jsonl" --results "$F/results/result-disclosed.json" --advisor-observations "$F/observations-scoped.jsonl"
check illegal-type     1 '^VIOLATION: .*worker-layer'        $A "$F/journal-clean.jsonl" --results "$F/results/result-disclosed.json" "$F/results/result-silent.json" "$F/results/result-illegal.json" --advisor-observations "$F/observations.jsonl"
check overage          0 '^CALIBRATION: disclosed overage'   $A "$F/journal-clean.jsonl" --results "$F/results/result-disclosed.json" --advisor-observations "$F/observations-scoped.jsonl" --declared-scope w-disclosed=1
# an observed call charged to a task no result discloses: not a non-event — it is uncleared
check orphan-obs       2 '^UNVERIFIABLE: observed .* no result file discloses' $A "$F/journal-clean.jsonl" --results "$F/results/result-disclosed.json" --advisor-observations "$F/observations.jsonl"
# observations with no results = the accounting side is missing; every call is orphaned
check obs-no-results   2 '^UNVERIFIABLE: --advisor-observations given without --results' $A "$F/journal-unavailable.jsonl" --advisor-observations "$F/observations.jsonl"
# --- v3.1 semantic face (REQ-8 / AC-18): vocab-keyed dialect, three drift forms
#     (quality-spine-p2 blueprints) + warm referential legs + visible LEGACY ---
check sem-clean        0 '^CLEAN$'                             $A "$F/journal-semantic-clean.jsonl"
check sem-moment-reuse 1 '^VIOLATION: semantic rule S1'        $A "$F/journal-semantic-moment-reuse.jsonl"
check sem-broken-pair  1 '^VIOLATION: semantic rule S2 .*dispatch_result' $A "$F/journal-semantic-broken-pairing.jsonl"
check sem-usage-prose  1 '^VIOLATION: semantic rule S3'        $A "$F/journal-semantic-usage-prose.jsonl"
check warm-dangling    1 '^VIOLATION: semantic rule S2 .*warm dispatch' $A "$F/journal-warm-dangling.jsonl"
check warm-family      1 '^VIOLATION: semantic rule S2 .*cross-family'  $A "$F/journal-warm-family-mismatch.jsonl"
# legacy journal: drift forms PRESENT but vocab absent -> no false VIOLATION,
# named LEGACY line (polar pair: honest old journals pass, downgrade is visible)
check legacy-visible   0 '^LEGACY: '                           $A "$F/journal-legacy-no-vocab.jsonl"
# --- mechanical task class (jsr REQ-1 / AC-3, AC-4): the entry event's additive
#     class/class_default fields are additive (no vocab bump), and S4 makes the
#     override's recorded reason the price of taking the licence ---
check class-cited      0 '^CLEAN$'                             $A "$F/journal-class-cited.jsonl"
check class-override   0 '^CLEAN$'                             $A "$F/journal-class-override-reasoned.jsonl"
check class-empty      1 '^VIOLATION: semantic rule S4'        $A "$F/journal-class-override-empty.jsonl"
# omission is the cheaper route to the same licence: declare the class, record
# no class_default at all. Caught by the anvil final review, ratcheted here.
check class-no-default 1 '^VIOLATION: semantic rule S4 .*no class_default' $A "$F/journal-class-no-default.jsonl"
# vocabulary unchanged by the adapter-side advisor-check reshape (jsr AC-12)
check vocab2-advisor   0 '^CLEAN$'                             $A "$F/journal-vocab2-advisor-unchanged.jsonl"
exit "$fail"
