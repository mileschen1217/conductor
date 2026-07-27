#!/usr/bin/env python3
"""audit-model-conformance.py — journal x telemetry model-conformance audit.

Python 3 stdlib ONLY.

Usage: python3 scripts/audit-model-conformance.py <journal.jsonl> [telemetry.jsonl]

Telemetry is OPTIONAL, and that is the point of this script's shape. C0 is
telemetry-independent: it reads the journal alone. While telemetry was a
required argument, the close chain could only invoke this audit when a
telemetry export existed, so on every run without one C0 — the cheapest and
most load-bearing check of the three — never ran at all. Model drift was
caught three times by a human reading the journal, and never once by this
script. So: the audit runs on every instrumented close, telemetry or not.

Telemetry format (fixed contract of this script; converters live in bindings):
  {"type":"agent","model":"<id>"}    one row per worker execution
  {"type":"session","model":"<id>"}  optional; the commander's own session model

Checks:
  C0 the journal's FIRST event is commander_stamp (self-stamp duty); missing
     or late stamp is a VIOLATION. Runs always.
  C1 every journal dispatch line's resolved_model consumes one matching
     telemetry agent row (multiset join — telemetry carries no task ids);
     an unconsumable dispatch line is a VIOLATION naming that line (ST-5 shape)
  C2 when session rows exist, the journal's commander_stamp model must appear
     among them (the self-report mirror of ST-5)
  Leftover agent rows are an informational NOTE (e.g. acceptance judges).

Fail-closed: absent, empty, or unparseable telemetry, or dispatches present
with zero agent rows -> C1/C2 are UNVERIFIABLE and the run is NEVER reported
CLEAN. C0 still returns its own verdict in every one of those cases.
Exit: 1 VIOLATION > 2 UNVERIFIABLE > 0 CLEAN, and 3 = CALLED WRONG.

Codes 2 and 3 are deliberately distinct, and must stay distinct. The close
chain records a failing member as fail(<rc>), so the exit code is the only
thing that survives into the close event: 2 there reads "this audit ran and
could not conclude for want of evidence", which on an instrumented run is a
real, owed failure. If a caller bug — wrong argument count after some future
refactor of the invocation — also exited 2, that bug would be recorded as a
legitimate evidence gap and read as an honest red rather than a broken call.
That is the silent-false-green shape this whole audit surface exists to
prevent, so a usage error gets its own code and never borrows this one.
"""
import json
import sys
from collections import Counter


def load_jsonl(path, label):
    entries = []
    try:
        f = open(path, encoding="utf-8")
    except OSError as err:
        return entries, f"cannot read {label}: {err}"
    with f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append((i, json.loads(line)))
            except json.JSONDecodeError as err:
                return entries, f"{label} line {i}: JSON parse error: {err}"
    return entries, None


def main():
    if len(sys.argv) not in (2, 3):
        print("usage: audit-model-conformance.py <journal.jsonl> [telemetry.jsonl]")
        sys.exit(3)  # CALLED WRONG — never 2; see the exit contract above

    journal, journal_error = load_jsonl(sys.argv[1], "journal")
    if journal_error is not None:
        print(f"UNVERIFIABLE: {journal_error}")
        sys.exit(2)

    dispatches = [(ln, e) for ln, e in journal if e.get("event") == "dispatch"]
    stamps = [e for _, e in journal if e.get("event") == "commander_stamp"]

    # C0 is telemetry-independent — evaluate before loading telemetry so a
    # genuine C0 violation always outranks any telemetry fail-closed reason
    # (priority: 1 VIOLATION > 2 UNVERIFIABLE > 0 CLEAN).
    violations = []
    if not journal or journal[0][1].get("event") != "commander_stamp":
        violations.append("journal's first event is not commander_stamp (self-stamp duty)")

    if len(sys.argv) == 2:
        # No telemetry offered. C0 has already run; C1/C2 cannot, and saying
        # so is the whole difference between this and not running at all.
        for v in violations:
            print(f"VIOLATION: {v}")
        if not violations:
            print("C0 CLEAN: journal's first event is commander_stamp")
        print("UNVERIFIABLE: no telemetry export given — C1 (dispatch↔agent join) and "
              "C2 (commander session model) cannot be evaluated; never CLEAN on missing evidence")
        sys.exit(1 if violations else 2)

    telemetry, telemetry_error = load_jsonl(sys.argv[2], "telemetry")
    if telemetry_error is not None:
        for v in violations:
            print(f"VIOLATION: {v}")
        print(f"UNVERIFIABLE: {telemetry_error}")
        sys.exit(1 if violations else 2)

    agent_models = Counter(e.get("model") for _, e in telemetry if e.get("type") == "agent")
    session_models = {e.get("model") for _, e in telemetry if e.get("type") == "session"}

    fail_closed_reason = None
    if not telemetry:
        fail_closed_reason = "telemetry export is empty — cannot join (never CLEAN on missing evidence)"
    elif dispatches and not agent_models:
        fail_closed_reason = "journal has dispatch lines but telemetry has zero agent rows"

    if fail_closed_reason is not None:
        for v in violations:
            print(f"VIOLATION: {v}")
        print(f"UNVERIFIABLE: {fail_closed_reason}")
        sys.exit(1 if violations else 2)

    for ln, e in dispatches:
        model = e.get("resolved_model")
        if agent_models.get(model, 0) > 0:
            agent_models[model] -= 1
        else:
            violations.append(
                f"dispatch line {ln} (task_id {e.get('task_id')!r}, resolved_model {model!r}) has no matching agent telemetry row")
    if session_models and stamps:
        stamp_model = stamps[0].get("model")
        if stamp_model not in session_models:
            violations.append(
                f"commander_stamp model {stamp_model!r} not among session telemetry models {sorted(session_models)}")

    leftovers = sorted(m for m, c in agent_models.items() if c > 0 for _ in range(c))
    for v in violations:
        print(f"VIOLATION: {v}")
    if leftovers:
        print(f"NOTE: unconsumed agent telemetry rows (not a violation): {leftovers}")
    if violations:
        sys.exit(1)
    print(f"CLEAN ({len(dispatches)} dispatch line(s) joined)")
    sys.exit(0)


if __name__ == "__main__":
    main()
