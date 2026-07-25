#!/usr/bin/env python3
"""audit-judgment-flow.py — judgment-flow audit over a run journal (v2 spec REQ-3, AC-3/AC-4).

Python 3 stdlib ONLY.

Usage:
  python3 scripts/audit-judgment-flow.py <journal.jsonl> [--threshold N]
      [--results <result.json> ...] [--advisor-observations <observations.jsonl>]

Dialect keying (v3.1 REQ-8): the journal's dialect is decided by
commander_stamp.vocab — an integer stamp, NEVER inferred from event presence
(presence inference would let a drifting commander escape full audit by
writing old-form events). vocab >= 2 → semantic rules S1-S3 below enforced in
full; vocab absent → legacy audit only, with a named LEGACY output line
(visible degradation: an honest old journal never eats a false VIOLATION,
and the downgrade is never silent).

Semantic face (vocab >= 2 only; kills semantic drift that typed carriers
alone cannot — fixture blueprints: the quality-spine-p2 live-run drift forms):
  S1 moment_id uniqueness   one judgment_moment per moment_id per journal
                            (paired intent/ruling/blocked references echoing
                            a moment are not re-uses)
  S2 referential pairing    every dispatch_result.task_id and every warm
                            dispatch's warm_prior must resolve to an EARLIER
                            dispatch line in the SAME journal; a warm_prior
                            target's contract_family must equal the referring
                            line's (cross-run warm = necessarily dangling;
                            same-run cross-family warm = equally VIOLATION)
  S3 usage enum             dispatch_result.usage is a token-count object or
                            the typed marker "unavailable"; prose pointers
                            (e.g. "see-transcript") are illegal
  S4 override reason        an entry event whose class_default overrides the
                            mechanical class's frozen default set must carry
                            a non-empty recorded reason inside the override
                            marker; an empty reason takes the licence without
                            paying for it -> VIOLATION

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
(undisclosed use). An observed call whose task_id no result discloses =
UNVERIFIABLE (a call charged to no task cannot be cleared — otherwise an
unrecognized id is a hiding place). --results WITHOUT observations degrades
this check to UNVERIFIABLE, never CLEAN (fail-closed).

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

    violations, calibrations, unverifiables, legacy_notes = [], [], [], []
    events = load_jsonl(args.journal, "journal")

    stamp = next((e for _, e in events if e.get("event") == "commander_stamp"), None)
    vocab = (stamp or {}).get("vocab")
    semantic = isinstance(vocab, int) and not isinstance(vocab, bool) and vocab >= 2
    if not semantic:
        legacy_notes.append(
            "LEGACY: commander_stamp carries no vocab stamp (or vocab < 2) — "
            "semantic rules S1-S3 are not applicable to this journal dialect; "
            "legacy audit only (visible degradation, never a false VIOLATION)")

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
    # Semantic face (vocab >= 2 dialect only)
    if semantic:
        # S1 — moment_id uniqueness
        for mid, lst in moments.items():
            if len(lst) > 1:
                lines = ", ".join(str(ln) for ln, _ in lst)
                violations.append(
                    f"semantic rule S1 (moment_id uniqueness): moment_id {mid} declared by {len(lst)} judgment_moment lines ({lines})")
        dispatch_by_line = [(ln, e) for ln, e in events if e.get("event") == "dispatch"]
        result_by_line = [(ln, e) for ln, e in events if e.get("event") == "dispatch_result"]
        # S2 — referential pairing
        for ln, e in result_by_line:
            tid = e.get("task_id")
            if not any(ln2 < ln and d.get("task_id") == tid for ln2, d in dispatch_by_line):
                violations.append(
                    f"semantic rule S2 (referential pairing): dispatch_result line {ln} task_id {tid!r} resolves to no earlier dispatch line in this journal")
        for ln, e in dispatch_by_line:
            if e.get("warm") is True:
                wp = e.get("warm_prior")
                target = None
                if wp:
                    target = next((d for ln2, d in dispatch_by_line
                                   if ln2 < ln and d.get("task_id") == wp), None)
                if target is None:
                    violations.append(
                        f"semantic rule S2 (referential pairing): warm dispatch line {ln} warm_prior {wp!r} resolves to no earlier dispatch in this journal (a cross-run warm reference is necessarily dangling)")
                elif e.get("contract_family") is None or target.get("contract_family") != e.get("contract_family"):
                    violations.append(
                        f"semantic rule S2 (referential pairing): warm dispatch line {ln} contract_family {e.get('contract_family')!r} != warm_prior target's {target.get('contract_family')!r} (same-run cross-family warm is a VIOLATION)")
        # S3 — usage enum
        for ln, e in result_by_line:
            u = e.get("usage")
            if not (isinstance(u, dict) or u == "unavailable"):
                violations.append(
                    f"semantic rule S3 (usage enum): dispatch_result line {ln} usage {u!r} is not a token-count object or \"unavailable\" (prose pointers are illegal)")
        # S4 — override reason (entry event's class_default)
        for ln, e in events:
            if e.get("event") != "entry":
                continue
            cd = e.get("class_default")
            if cd is None or cd == "cited":
                continue
            if not isinstance(cd, str):
                violations.append(
                    f"semantic rule S4 (override reason): entry line {ln} class_default {cd!r} is not a string (legal values: \"cited\" | \"overridden(<reason>)\")")
                continue
            if not cd.startswith("overridden"):
                violations.append(
                    f"semantic rule S4 (override reason): entry line {ln} class_default {cd!r} is neither \"cited\" nor an \"overridden(<reason>)\" marker")
                continue
            reason = cd[len("overridden"):].strip()
            if not (reason.startswith("(") and reason.endswith(")") and reason[1:-1].strip()):
                violations.append(
                    f"semantic rule S4 (override reason): entry line {ln} class_default {cd!r} overrides the frozen default set with no recorded reason (the override is legal only because the reason is recorded)")

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
    if args.observations and not args.results:
        # Observations without results is not a lighter audit — it is an audit
        # with the accounting side missing. Every observed call is orphaned by
        # construction, so nothing can be cleared.
        unverifiables.append(
            "--advisor-observations given without --results: observed advisor calls have no disclosure to check against — UNVERIFIABLE, never CLEAN")
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
            # An observed call under a task_id no result claims is not a
            # non-event: it is a call nobody accounted for. Ignoring it would
            # let any producer hide undisclosed use behind an unrecognized id.
            for tid, n_obs in sorted(observed.items()):
                if tid not in disclosed:
                    unverifiables.append(
                        f"observed {n_obs} advisor call(s) under task {tid!r}, which no result file discloses — unattributable observation, UNVERIFIABLE (a call charged to no task cannot be cleared)")
        else:
            unverifiables.append(
                "undisclosed-use check has no observation surface (--advisor-observations absent) — UNVERIFIABLE, never CLEAN")

    for v in violations:
        print(f"VIOLATION: {v}")
    for c in calibrations:
        print(f"CALIBRATION: {c}")
    for u in unverifiables:
        print(f"UNVERIFIABLE: {u}")
    for n in legacy_notes:
        print(n)
    if violations:
        sys.exit(1)
    if unverifiables:
        sys.exit(2)
    if not calibrations and not legacy_notes:
        print("CLEAN")
    sys.exit(0)


if __name__ == "__main__":
    main()
