#!/usr/bin/env python3
"""audit-judgment-flow.py — judgment-flow audit over a run journal (v2 spec REQ-3, AC-3/AC-4).

Python 3 stdlib ONLY.

Usage:
  python3 scripts/audit-judgment-flow.py <journal.jsonl> [--threshold N]
      [--results <result.json> ...] [--advisor-observations <observations.jsonl>]

Journal face (always on; pairing is by moment_id, NEVER adjacency; covers
RECOGNIZED moments only — decision_type within the five call sites):
  J1 pre-call order    every advisor_ruling has an EARLIER advisor_intent, same moment_id
  J2 single consult    no moment_id carries two advisor_intent lines
  J3 under-consult     judgment_moment disposition=advisor -> moment_id-matched
                       advisor_intent or advisor_unavailable must follow;
                       disposition=blocked -> blocked_to_human must follow
  J4 dangling call     advisor_intent without moment_id-matched advisor_ruling
                       or advisor_unavailable
  J5 ruling schema     advisor_ruling payload (line minus envelope keys event,
                       moment_id) validates against contract/advisor-ruling.schema.json
  J6 threshold         consults = count of advisor_intent lines; crossing the
                       threshold is REPORTED as a calibration signal (never a
                       violation); a crossing with no advisor_threshold line is
                       a journaling violation, and the line at the crossing
                       must carry the right values (threshold, consults_so_far
                       = threshold+1, moment_id of the crossing consult)
  J7 echo              advisor_intent.decision_type must echo its
                       judgment_moment's; advisor_ruling.decision_type must
                       echo its paired advisor_intent's
  J8 notify enum       calibration_notify.status must be sent|report-only|failed

Worker face (--results): judgment_events decision_type must be "tactical";
the other enum values are worker-layer violations (should-have-escalated).
--declared-scope <task_id>=<n> (repeatable; harvest feeds it from the
contract's tactical_consults_declared): disclosed count > n is reported as
CALIBRATION (overage is calibration data, never a violation).
Observation face (--advisor-observations, joins --results by task_id):
observed advisor-call count > disclosed judgment_events count = VIOLATION
(undisclosed use). --results WITHOUT observations degrades this check to
UNVERIFIABLE, never CLEAN (fail-closed).

Exit: 1 if any VIOLATION, else 2 if any UNVERIFIABLE, else 0 (max severity).
"""
import argparse
import json
import os
import sys

CALL_SITES = {"entry-gate", "grading-dispute", "worker-blocked",
              "acceptance-ambiguity", "scope-change-preview"}

TYPES = {"string": str, "array": list, "object": dict, "integer": int,
         "number": (int, float), "boolean": bool, "null": type(None)}


def type_ok(value, names):
    for t in names:
        if t in ("integer", "number") and isinstance(value, bool):
            continue
        if isinstance(value, TYPES[t]):
            return True
    return False


def load_jsonl(path, label):
    entries = []
    try:
        f = open(path, encoding="utf-8")
    except OSError as err:
        print(f"UNVERIFIABLE: cannot read {label}: {err}")
        sys.exit(2)
    with f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append((i, json.loads(line)))
            except json.JSONDecodeError as err:
                print(f"UNVERIFIABLE: {label} line {i}: JSON parse error: {err}")
                sys.exit(2)
    return entries


def validate_ruling(payload, schema):
    problems = []
    props = schema["properties"]
    for req in schema.get("required", []):
        if req not in payload:
            problems.append(f"{req}: required field missing")
    for k, v in payload.items():
        if k not in props:
            problems.append(f"{k}: unknown field")
            continue
        allowed = props[k]["type"] if isinstance(props[k]["type"], list) else [props[k]["type"]]
        if not type_ok(v, allowed):
            problems.append(f"{k}: expected type {'|'.join(allowed)}, got {type(v).__name__}")
            continue
        if "enum" in props[k] and v not in props[k]["enum"]:
            problems.append(f"{k}: value {v!r} not in enum")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("journal")
    ap.add_argument("--threshold", type=int, default=3)
    ap.add_argument("--results", nargs="+", default=None)
    ap.add_argument("--advisor-observations", dest="observations", default=None)
    ap.add_argument("--declared-scope", dest="declared_scope", action="append", default=[])
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", "contract", "advisor-ruling.schema.json"),
              encoding="utf-8") as f:
        ruling_schema = json.load(f)

    violations, calibrations, unverifiables = [], [], []
    events = load_jsonl(args.journal, "journal")

    moments, intents, rulings, unavailables, blockeds = {}, {}, {}, {}, {}
    intent_order = []
    threshold_lines = []
    for lineno, e in events:
        ev, mid = e.get("event"), e.get("moment_id")
        if ev == "judgment_moment":
            moments.setdefault(mid, []).append((lineno, e))
        elif ev == "advisor_intent":
            intents.setdefault(mid, []).append((lineno, e))
            intent_order.append((lineno, mid))
        elif ev == "advisor_ruling":
            rulings.setdefault(mid, []).append((lineno, e))
        elif ev == "advisor_unavailable":
            unavailables.setdefault(mid, []).append((lineno, e))
        elif ev == "blocked_to_human":
            blockeds.setdefault(mid, []).append((lineno, e))
        elif ev == "advisor_threshold":
            threshold_lines.append((lineno, e))
        elif ev == "calibration_notify":
            if e.get("status") not in ("sent", "report-only", "failed"):
                violations.append(
                    f"calibration_notify line {lineno}: status {e.get('status')!r} not in sent|report-only|failed")

    # J2 — single consult per moment
    for mid, lst in intents.items():
        if len(lst) > 1:
            lines = ", ".join(str(ln) for ln, _ in lst)
            violations.append(f"moment_id {mid} consulted twice (advisor_intent lines {lines})")
    # J1 — pre-call order
    for mid, lst in rulings.items():
        for lineno, _ in lst:
            earlier = [ln for ln, _ in intents.get(mid, []) if ln < lineno]
            if not earlier:
                violations.append(
                    f"advisor_ruling at line {lineno} (moment_id {mid}) lacks its pre-call advisor_intent line")
    # J3 — under-consultation (recognized moments only)
    for mid, lst in moments.items():
        for lineno, m in lst:
            if m.get("decision_type") not in CALL_SITES:
                continue
            disp = m.get("disposition")
            if disp == "advisor" and mid not in intents and mid not in unavailables:
                violations.append(
                    f"UNDER-CONSULTATION: judgment_moment line {lineno} (moment_id {mid}) disposition=advisor has no moment_id-matched advisor_intent or advisor_unavailable")
            if disp == "blocked" and mid not in blockeds:
                violations.append(
                    f"UNDER-CONSULTATION: judgment_moment line {lineno} (moment_id {mid}) disposition=blocked has no moment_id-matched blocked_to_human")
    # J4 — dangling call
    for mid, lst in intents.items():
        if mid not in rulings and mid not in unavailables:
            violations.append(
                f"dangling call: advisor_intent line {lst[0][0]} (moment_id {mid}) has no moment_id-matched advisor_ruling or advisor_unavailable")
    # J5 — ruling schema
    for mid, lst in rulings.items():
        for lineno, e in lst:
            payload = {k: v for k, v in e.items() if k not in ("event", "moment_id")}
            for p in validate_ruling(payload, ruling_schema):
                violations.append(f"ruling schema: line {lineno} (moment_id {mid}): {p}")
    # J7 — decision_type echo across moment -> intent -> ruling
    for mid, lst in intents.items():
        if mid in moments:
            mdt = moments[mid][0][1].get("decision_type")
            for lineno, e in lst:
                if e.get("decision_type") != mdt:
                    violations.append(
                        f"decision_type echo broken: advisor_intent line {lineno} (moment_id {mid}) says {e.get('decision_type')!r}, its judgment_moment says {mdt!r}")
    for mid, lst in rulings.items():
        if mid in intents:
            idt = intents[mid][0][1].get("decision_type")
            for lineno, e in lst:
                if e.get("decision_type") != idt:
                    violations.append(
                        f"decision_type echo broken: advisor_ruling line {lineno} (moment_id {mid}) says {e.get('decision_type')!r}, its advisor_intent says {idt!r}")
    # J6 — threshold accounting
    consults = len(intent_order)
    if consults > args.threshold:
        calibrations.append(
            f"attention threshold {args.threshold} crossed: {consults} consults this run (calibration signal, not a violation)")
        if not threshold_lines:
            violations.append(
                f"threshold crossing unjournaled: {consults} consults > threshold {args.threshold} but no advisor_threshold line")
        else:
            crossing_line, crossing_mid = intent_order[args.threshold]  # the (threshold+1)-th consult
            terminal_after = [ln for ln, _ in rulings.get(crossing_mid, []) + unavailables.get(crossing_mid, [])
                              if ln > crossing_line]
            window_end = min(terminal_after) if terminal_after else None
            good = [ln for ln, e in threshold_lines
                    if e.get("threshold") == args.threshold
                    and e.get("consults_so_far") == args.threshold + 1
                    and e.get("moment_id") == crossing_mid
                    and ln > crossing_line
                    and (window_end is None or ln < window_end)]
            if not good:
                violations.append(
                    f"advisor_threshold line malformed or misplaced: expected threshold={args.threshold}, consults_so_far={args.threshold + 1}, moment_id={crossing_mid}, landing AT the crossing (after intent line {crossing_line}, before that moment's terminal)")

    # Worker + observation faces
    if args.results:
        disclosed = {}
        for rp in args.results:
            try:
                with open(rp, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError) as err:
                unverifiables.append(f"cannot read result {rp}: {err}")
                continue
            tid = data.get("task_id", rp)
            evs = data.get("judgment_events") or []
            disclosed[tid] = len(evs)
            for i, ev in enumerate(evs):
                dt = ev.get("decision_type")
                if dt != "tactical":
                    violations.append(
                        f"worker-layer illegal decision_type in {rp} judgment_events[{i}]: {dt!r} (worker should have escalated, not consulted)")
        declared = {}
        for spec in args.declared_scope:
            task, _, n = spec.partition("=")
            declared[task] = int(n)
        for tid, n_disc in disclosed.items():
            if tid in declared and n_disc > declared[tid]:
                calibrations.append(
                    f"disclosed overage: task {tid} disclosed {n_disc} consult(s), declared tactical scope {declared[tid]} (calibration data, not a violation)")
        if args.observations:
            observed = {}
            for _, o in load_jsonl(args.observations, "observations"):
                if o.get("event") == "advisor_call":
                    observed[o.get("task_id")] = observed.get(o.get("task_id"), 0) + 1
            for tid, n_disc in disclosed.items():
                n_obs = observed.get(tid, 0)
                if n_obs > n_disc:
                    violations.append(
                        f"undisclosed advisor use: task {tid} observed {n_obs} call(s), disclosed {n_disc}")
        else:
            unverifiables.append(
                "undisclosed-use check has no observation surface (--advisor-observations absent) — UNVERIFIABLE, never CLEAN")

    for v in violations:
        print(f"VIOLATION: {v}")
    for c in calibrations:
        print(f"CALIBRATION: {c}")
    for u in unverifiables:
        print(f"UNVERIFIABLE: {u}")
    if violations:
        sys.exit(1)
    if unverifiables:
        sys.exit(2)
    if not calibrations:
        print("CLEAN")
    sys.exit(0)


if __name__ == "__main__":
    main()
