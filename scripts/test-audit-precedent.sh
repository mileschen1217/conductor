#!/usr/bin/env bash
# Runs scripts/audit-precedent.py over scripts/fixtures/precedent/ (spec AC-6).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="python3 $ROOT/scripts/audit-precedent.py"
F="$ROOT/scripts/fixtures/precedent"
fail=0
check() { local name="$1" want_rc="$2" want_pat="$3"; shift 3
  local out rc; out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ] || ! printf '%s\n' "$out" | grep -qE "$want_pat"; then
    echo "FAIL: $name rc=$rc (want $want_rc) out=$out"; fail=1
  else echo "ok: $name"; fi
}
check cited            0 'precedent cited'          $A "$F/ledger-match.jsonl" "$F/plan-cited.md"
check deviation        0 'deviation recorded'       $A "$F/ledger-match.jsonl" "$F/plan-deviation.md"
check missing-citation 1 '^VIOLATION: .*neither cited nor deviated' $A "$F/ledger-match.jsonl" "$F/plan-missing-citation.md"
check no-match         0 '^no precedent match'      $A "$F/ledger-match.jsonl" "$F/plan-nomatch.md"
check bad-cite         1 '^VIOLATION: .*cites unknown run_id' $A "$F/ledger-match.jsonl" "$F/plan-bad-cite.md"
check no-taskshape     2 '^UNVERIFIABLE: '          $A "$F/ledger-match.jsonl" "$F/plan-no-taskshape.md"
check ts-regress       1 '^VIOLATION: .*ts regression' $A --calibration-check "$F/ledger-ts-regress.jsonl"
check no-proposed      1 '^VIOLATION: .*without a prior proposed' $A --calibration-check "$F/ledger-promoted-no-proposed.jsonl"
check no-m9run         1 '^VIOLATION: .*m9_run'     $A --calibration-check "$F/ledger-promoted-no-m9run.jsonl"
check trigger          0 '^TRIGGER: calibration_id=' $A --calibration-check "$F/ledger-trigger.jsonl"
check constants-drift  0 '^TRIGGER: .*signal=constants-drift' $A --calibration-check "$F/ledger-constants-drift-trigger.jsonl"
check estimate-drift   0 '^TRIGGER: .*signal=estimate-drift' $A --calibration-check "$F/ledger-estimate-drift-trigger.jsonl"
check mixed-signal     0 '^NO-TRIGGER'              $A --calibration-check "$F/ledger-mixed-signal.jsonl"
check below-threshold  0 '^NO-TRIGGER'              $A --calibration-check "$F/ledger-below-threshold.jsonl"
check suppressed       0 '^SUPPRESSED: '            $A --calibration-check "$F/ledger-suppressed.jsonl"
check missing-outcome  1 '^VIOLATION: .*outcome missing field' $A --calibration-check "$F/ledger-missing-outcome-field.jsonl"
check retrigger-reject 0 '^TRIGGER: .*prior rejected' $A --calibration-check "$F/ledger-retrigger-after-reject.jsonl"
check supersede-chain  0 '^NO-TRIGGER|^SUPPRESSED'  $A --calibration-check "$F/ledger-supersede-chain.jsonl"
check missing-ledger   2 '^UNVERIFIABLE: '          $A --calibration-check "$F/nonexistent.jsonl"
# --- v3.1 calibration target split (REQ-5 / AC-11): anchor promotes owe no
#     m9_run; doctrine-default promotes still do; enum guarded ---
check anchor-no-m9run  0 '^NO-TRIGGER'              $A --calibration-check "$F/ledger-promoted-anchor-no-m9run.jsonl"
check dd-no-m9run      1 '^VIOLATION: .*target=doctrine-default.*m9_run' $A --calibration-check "$F/ledger-promoted-dd-no-m9run.jsonl"
check bad-target       1 '^VIOLATION: .*not in enum anchor' $A --calibration-check "$F/ledger-bad-target.jsonl"
# estimate-drift trigger names its proposal object (binding conversion anchors)
check drift-target     0 'target=anchor \(proposal object: the binding' $A --calibration-check "$F/ledger-estimate-drift-trigger.jsonl"
# --- v3.1 journal dialect (REQ-7: typed precedent event is the record;
#     plan is legacy — batch cross-vendor catch, 2026-07-18) ---
check j-cited          0 'precedent cited: run-0001'  $A "$F/ledger-match.jsonl" "$F/journal-precedent-cited.jsonl"
check j-owed-missing   1 '^VIOLATION: .*owed-but-missing' $A "$F/ledger-match.jsonl" "$F/journal-precedent-owed-missing.jsonl"
check j-false-nomatch  1 '^VIOLATION: .*declares no-match but matching' $A "$F/ledger-match.jsonl" "$F/journal-precedent-false-nomatch.jsonl"
check j-legacy         0 '^LEGACY: '                  $A "$F/ledger-match.jsonl" "$F/journal-precedent-legacy.jsonl"
exit "$fail"
