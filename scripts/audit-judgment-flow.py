#!/usr/bin/env python3
"""audit-judgment-flow.py — semantic audit over an instrumented run journal.

Python 3 stdlib ONLY.

Usage:
  python3 scripts/audit-judgment-flow.py <journal.jsonl>

Scope: the journal its own close chain hands it (doctrine § Audit surface).
This audit runs only on instrumented runs, because only instrumented runs have
a journal at all.

Stamp gate (fail-closed). The journal's dialect is declared by
commander_stamp.vocab — an integer stamp, NEVER inferred from event presence
(presence inference would let a drifting commander escape audit by writing
old-form events). A journal handed to this audit that carries no stamp, or a
stamp below VOCAB, is a VIOLATION: there is no legacy dialect and no fallback.
An honest historical journal is not misread here — it is simply never
re-invoked, because its run closed under the vocabulary it was written in.

The four semantic rules (doctrine § Audit surface — single home of their
definitions; this file is their enforcement path):
  S1 moment_id uniqueness   one judgment_moment per moment_id per journal
                            (a blocked_to_human echoing its moment is not a
                            re-use)
  S2 referential pairing    every dispatch_result.task_id resolves to an
                            EARLIER dispatch.task_id in the SAME journal — a
                            result attributed to a dispatch this journal never
                            recorded is unattributable work
  S3 usage enum             dispatch_result.usage is a token-count object or
                            the typed marker "unavailable"; prose pointers
                            (e.g. "see-transcript") are illegal
  S4 override reason        an entry event that declares a task class owes a
                            class_default; when that class_default overrides
                            the frozen default set it must carry a non-empty
                            recorded reason inside the marker. An empty reason
                            -- or an omitted class_default -- takes the licence
                            without paying for it -> VIOLATION

Exit: 1 if any VIOLATION, 2 if the journal cannot be read or parsed, else 0.
"""
import argparse
import json
import sys

VOCAB = 3


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


def check_stamp(events, violations):
    """Fail-closed dialect gate. Returns True when the journal is auditable."""
    stamp = next((e for _, e in events if e.get("event") == "commander_stamp"), None)
    if stamp is None:
        violations.append(
            "stamp gate: journal carries no commander_stamp — a journal handed "
            f"to this audit must declare its dialect (vocab {VOCAB}); there is "
            "no legacy fallback")
        return False
    vocab = stamp.get("vocab")
    if not isinstance(vocab, int) or isinstance(vocab, bool):
        violations.append(
            f"stamp gate: commander_stamp.vocab is {vocab!r}, not an integer "
            f"(expected {VOCAB})")
        return False
    if vocab < VOCAB:
        violations.append(
            f"stamp gate: commander_stamp.vocab={vocab} is below the current "
            f"vocabulary {VOCAB} — this journal was written in a dialect whose "
            "run has closed; it is not re-audited under the current rules")
        return False
    return True


def rule_s1(events, violations):
    moments = {}
    for lineno, e in events:
        if e.get("event") == "judgment_moment":
            moments.setdefault(e.get("moment_id"), []).append(lineno)
    for mid, lines in moments.items():
        if len(lines) > 1:
            joined = ", ".join(str(ln) for ln in lines)
            violations.append(
                f"semantic rule S1 (moment_id uniqueness): moment_id {mid} "
                f"declared by {len(lines)} judgment_moment lines ({joined})")


def rule_s2(events, violations):
    dispatches = [(ln, e) for ln, e in events if e.get("event") == "dispatch"]
    for ln, e in events:
        if e.get("event") != "dispatch_result":
            continue
        tid = e.get("task_id")
        if not any(ln2 < ln and d.get("task_id") == tid for ln2, d in dispatches):
            violations.append(
                f"semantic rule S2 (referential pairing): dispatch_result line "
                f"{ln} task_id {tid!r} resolves to no earlier dispatch line in "
                "this journal")


def rule_s3(events, violations):
    for ln, e in events:
        if e.get("event") != "dispatch_result":
            continue
        u = e.get("usage")
        if not (isinstance(u, dict) or u == "unavailable"):
            violations.append(
                f"semantic rule S3 (usage enum): dispatch_result line {ln} "
                f"usage {u!r} is not a token-count object or \"unavailable\" "
                "(prose pointers are illegal)")


def rule_s4(events, violations):
    for ln, e in events:
        if e.get("event") != "entry":
            continue
        cd = e.get("class_default")
        if e.get("class") is not None and cd is None:
            # Omission is the cheapest way to take the licence: declare the
            # class, silently leave the default set, record nothing. An entry
            # that declares a class owes its class_default.
            violations.append(
                f"semantic rule S4 (override reason): entry line {ln} declares "
                f"class {e.get('class')!r} but carries no class_default (a "
                "declared class owes \"cited\" or \"overridden(<reason>)\")")
            continue
        if cd is None or cd == "cited":
            continue
        if not isinstance(cd, str):
            violations.append(
                f"semantic rule S4 (override reason): entry line {ln} "
                f"class_default {cd!r} is not a string (legal values: "
                "\"cited\" | \"overridden(<reason>)\")")
            continue
        if not cd.startswith("overridden"):
            violations.append(
                f"semantic rule S4 (override reason): entry line {ln} "
                f"class_default {cd!r} is neither \"cited\" nor an "
                "\"overridden(<reason>)\" marker")
            continue
        reason = cd[len("overridden"):].strip()
        if not (reason.startswith("(") and reason.endswith(")") and reason[1:-1].strip()):
            violations.append(
                f"semantic rule S4 (override reason): entry line {ln} "
                f"class_default {cd!r} overrides the frozen default set with no "
                "recorded reason (the override is legal only because the reason "
                "is recorded)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("journal")
    args = ap.parse_args()

    violations = []
    events = load_jsonl(args.journal, "journal")

    if check_stamp(events, violations):
        rule_s1(events, violations)
        rule_s2(events, violations)
        rule_s3(events, violations)
        rule_s4(events, violations)

    for v in violations:
        print(f"VIOLATION: {v}")
    if violations:
        sys.exit(1)
    print("CLEAN")
    sys.exit(0)


if __name__ == "__main__":
    main()
