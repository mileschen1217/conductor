#!/usr/bin/env python3
"""audit-precedent.py — precedent-ledger audit + calibration trigger check (v2 spec REQ-5/AC-6).

Python 3 stdlib ONLY.

Usage:
  python3 scripts/audit-precedent.py <precedent.jsonl> <dispatch-plan.md>
  python3 scripts/audit-precedent.py --calibration-check <precedent.jsonl>

Structural checks (both modes):
  L1 every line parses; schema is precedent/v1 or calibration/v1; required
     fields present; enums legal (deviation_signal.kind, calibration status)
  L2 ts monotonic non-decreasing (append-only in-line consistency)
  L3 a promoted/rejected calibration line requires an EARLIER proposed line
     with the same calibration_id; promoted requires non-null m9_run
  History immutability (rewriting an existing line) is a version-control
  audit, outside this script's capability — stated, not pretended.

Plan mode (cite-or-deviate; similarity key = task_shape.kind + write_surface):
  reads `task-shape: kind=<k>, write_surface=<w>` and `precedent: ...` from
  the dispatch plan. Matching ledger line + neither citation nor deviation =
  VIOLATION; citation of an unknown run_id = VIOLATION; no matching line =
  vacuous pass ("no precedent match"); missing task-shape line = UNVERIFIABLE.

--calibration-check (run-close tier-0 trigger): >=3 same-shape runs with a
  consistent deviation_signal (per-kind semantics: threshold-crossed /
  precedent-deviation match on kind; grade-override / checker-reject-pattern
  match on canonicalized value) -> TRIGGER with derived calibration_id,
  unless the LATEST calibration line with that id is status=proposed (an open
  proposal suppresses duplicates); a promoted/rejected latest status does NOT
  suppress — the trigger notes the prior ruling and a re-proposal supersedes
  by append. Informational: exit stays 0.

Exit: 1 VIOLATION > 2 UNVERIFIABLE > 0.
"""
import hashlib
import json
import re
import sys

SIGNAL_KINDS = {"threshold-crossed", "grade-override", "checker-reject-pattern", "precedent-deviation"}
KIND_ONLY = {"threshold-crossed", "precedent-deviation"}
CAL_STATUS = {"proposed", "promoted", "rejected"}
PRECEDENT_REQ = ["schema", "ts", "run_id", "task_shape", "decisions", "outcome", "deviation_signal", "lesson"]
TASK_SHAPE_REQ = ["kind", "units", "corpus_est_tokens", "write_surface", "acceptance_mechanical"]
DECISIONS_REQ = ["entry", "topology", "grades", "advisor_calls"]
OUTCOME_REQ = ["cost_usd", "quality", "retries", "checker_rejects", "verdict"]
CALIBRATION_REQ = ["schema", "ts", "calibration_id", "rule", "basis", "status", "supersedes", "decided_by", "decision_reason", "m9_run"]


def load_ledger(path):
    lines = []
    try:
        f = open(path, encoding="utf-8")
    except OSError as err:
        print(f"UNVERIFIABLE: cannot read ledger: {err}")
        sys.exit(2)
    with f:
        for i, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append((i, json.loads(raw)))
            except json.JSONDecodeError as err:
                print(f"UNVERIFIABLE: ledger line {i}: JSON parse error: {err}")
                sys.exit(2)
    return lines


def canon_value(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def derive_calibration_id(kind, write_surface, sig_kind, sig_value):
    key = f"{kind}|{write_surface}|{sig_kind}|{canon_value(sig_value)}"
    return "cal-" + hashlib.sha256(key.encode()).hexdigest()[:12]


def structural(lines):
    violations = []
    prev_ts = ""
    proposed_ids = set()
    for i, e in lines:
        schema = e.get("schema")
        if schema == "precedent/v1":
            for k in PRECEDENT_REQ:
                if k not in e:
                    violations.append(f"ledger line {i}: precedent/v1 missing field {k}")
            shape = e.get("task_shape") or {}
            for k in TASK_SHAPE_REQ:
                if k not in shape:
                    violations.append(f"ledger line {i}: task_shape missing field {k}")
            dec = e.get("decisions") or {}
            for k in DECISIONS_REQ:
                if k not in dec:
                    violations.append(f"ledger line {i}: decisions missing field {k}")
            out = e.get("outcome") or {}
            for k in OUTCOME_REQ:
                if k not in out:
                    violations.append(f"ledger line {i}: outcome missing field {k}")
            sig = e.get("deviation_signal")
            if sig is not None and sig.get("kind") not in SIGNAL_KINDS:
                violations.append(f"ledger line {i}: deviation_signal.kind {sig.get('kind')!r} not in enum")
        elif schema == "calibration/v1":
            for k in CALIBRATION_REQ:
                if k not in e:
                    violations.append(f"ledger line {i}: calibration/v1 missing field {k}")
            status = e.get("status")
            if status not in CAL_STATUS:
                violations.append(f"ledger line {i}: status {status!r} not in enum")
            cid = e.get("calibration_id")
            if status == "proposed":
                proposed_ids.add(cid)
            elif status in ("promoted", "rejected"):
                if cid not in proposed_ids:
                    violations.append(
                        f"ledger line {i}: {status} calibration {cid} without a prior proposed line (supersede-by-append broken)")
                if status == "promoted" and not e.get("m9_run"):
                    violations.append(f"ledger line {i}: promoted calibration {cid} has null m9_run (regression citation required)")
        else:
            violations.append(f"ledger line {i}: unknown schema {schema!r}")
        ts = e.get("ts", "")
        if prev_ts and ts < prev_ts:
            violations.append(f"ledger line {i}: ts regression ({ts} < {prev_ts}) — append-only order broken")
        prev_ts = ts or prev_ts
    return violations


def plan_mode(lines, plan_path):
    violations, unverifiables, notes = [], [], []
    try:
        plan = open(plan_path, encoding="utf-8").read()
    except OSError as err:
        print(f"UNVERIFIABLE: cannot read dispatch plan: {err}")
        sys.exit(2)
    m = re.search(r"^task-shape:\s*kind=([^,]+),\s*write_surface=(.+)$", plan, re.MULTILINE)
    if not m:
        unverifiables.append("dispatch plan has no machine-readable task-shape line — lookup key unavailable")
        return violations, unverifiables, notes
    kind, surface = m.group(1).strip(), m.group(2).strip()
    run_ids = {e.get("run_id") for _, e in lines if e.get("schema") == "precedent/v1"}
    matches = [e for _, e in lines if e.get("schema") == "precedent/v1"
               and (e.get("task_shape") or {}).get("kind") == kind
               and (e.get("task_shape") or {}).get("write_surface") == surface]
    cite = re.search(r"^precedent:\s*cited\s+(\S+)", plan, re.MULTILINE)
    dev = re.search(r"^precedent:\s*deviation\s*[—-]\s*(\S.*)$", plan, re.MULTILINE)
    if cite and cite.group(1) not in run_ids:
        violations.append(f"dispatch plan cites unknown run_id {cite.group(1)!r}")
    elif not matches:
        notes.append(f"no precedent match (kind={kind}, write_surface={surface}) — vacuous pass")
    elif cite:
        notes.append(f"precedent cited: {cite.group(1)}")
    elif dev:
        notes.append(f"deviation recorded: {dev.group(1)}")
    else:
        violations.append(
            f"matching precedent exists (kind={kind}, write_surface={surface}: {sorted(e.get('run_id') for e in matches)}) but the dispatch plan neither cited nor deviated")
    return violations, unverifiables, notes


def calibration_check(lines):
    notes = []
    cal_ids = {}
    for _, e in lines:
        if e.get("schema") == "calibration/v1":
            cal_ids[e.get("calibration_id")] = e.get("status")
    groups = {}
    for _, e in lines:
        if e.get("schema") != "precedent/v1":
            continue
        sig = e.get("deviation_signal")
        if not sig:
            continue
        shape = e.get("task_shape") or {}
        sig_kind = sig.get("kind")
        vkey = "" if sig_kind in KIND_ONLY else canon_value(sig.get("value"))
        key = (shape.get("kind"), shape.get("write_surface"), sig_kind, vkey)
        groups.setdefault(key, []).append(e)
    triggered = False
    for (kind, surface, sig_kind, vkey), rows in sorted(groups.items(), key=str):
        if len(rows) < 3:
            continue
        sample_value = rows[0]["deviation_signal"].get("value")
        cid = derive_calibration_id(kind, surface, sig_kind, sample_value if vkey else None)
        basis = [r.get("run_id") for r in rows]
        if cal_ids.get(cid) == "proposed":
            # ONLY an open (unruled) proposed line suppresses; promoted/rejected
            # are human rulings, not open proposals — a re-trigger after them
            # re-proposes by append (supersedes field carries the lineage)
            notes.append(f"SUPPRESSED: open proposal {cid} already covers shape={kind}/{surface} signal={sig_kind}")
        elif cid in cal_ids:
            notes.append(f"TRIGGER: calibration_id={cid} shape={kind}/{surface} signal={sig_kind} basis={basis} (prior {cal_ids[cid]} line exists — a new proposal supersedes by append)")
        else:
            notes.append(f"TRIGGER: calibration_id={cid} shape={kind}/{surface} signal={sig_kind} basis={basis}")
        triggered = True
    if not triggered:
        notes.append("NO-TRIGGER")
    return notes


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--calibration-check":
        if len(argv) != 2:
            print("usage: audit-precedent.py --calibration-check <precedent.jsonl>")
            sys.exit(2)
        lines = load_ledger(argv[1])
        violations = structural(lines)
        notes = calibration_check(lines)
        unverifiables = []
    elif len(argv) == 2:
        lines = load_ledger(argv[0])
        violations = structural(lines)
        pv, unverifiables, notes = plan_mode(lines, argv[1])
        violations += pv
    else:
        print("usage: audit-precedent.py <precedent.jsonl> <dispatch-plan.md> | --calibration-check <precedent.jsonl>")
        sys.exit(2)

    for v in violations:
        print(f"VIOLATION: {v}")
    for u in unverifiables:
        print(f"UNVERIFIABLE: {u}")
    for n in notes:
        print(n)
    if violations:
        sys.exit(1)
    if unverifiables:
        sys.exit(2)
    if not notes:
        print("CLEAN")
    sys.exit(0)


if __name__ == "__main__":
    main()
