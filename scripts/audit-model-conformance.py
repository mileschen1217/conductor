#!/usr/bin/env python3
"""audit-model-conformance.py — journal x telemetry model-conformance audit (M8, spec REQ-4/AC-5).

Python 3 stdlib ONLY.

Usage: python3 scripts/audit-model-conformance.py <journal.jsonl> <telemetry.jsonl>

Telemetry format (fixed contract of this script; converters live in bindings):
  {"type":"agent","model":"<id>"}    one row per worker execution
  {"type":"session","model":"<id>"}  optional; the commander's own session model

Checks:
  C0 the journal's FIRST event is commander_stamp (REQ-4 self-stamp duty);
     missing or late stamp is a VIOLATION
  C1 every journal dispatch line's resolved_model consumes one matching
     telemetry agent row (multiset join — telemetry carries no task ids);
     an unconsumable dispatch line is a VIOLATION naming that line (ST-5 shape)
  C2 when session rows exist, the journal's commander_stamp model must appear
     among them (the self-report mirror of ST-5)
  Leftover agent rows are an informational NOTE (e.g. acceptance judges).

Fail-closed: missing/empty/unparseable telemetry, or dispatches present with
zero agent rows -> exit 2 UNVERIFIABLE, never CLEAN.
Exit: 1 VIOLATION > 2 UNVERIFIABLE > 0 CLEAN.
"""
import json
import sys
from collections import Counter


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


def main():
    if len(sys.argv) != 3:
        print("usage: audit-model-conformance.py <journal.jsonl> <telemetry.jsonl>")
        sys.exit(2)
    journal = load_jsonl(sys.argv[1], "journal")
    telemetry = load_jsonl(sys.argv[2], "telemetry")

    dispatches = [(ln, e) for ln, e in journal if e.get("event") == "dispatch"]
    stamps = [e for _, e in journal if e.get("event") == "commander_stamp"]
    agent_models = Counter(e.get("model") for _, e in telemetry if e.get("type") == "agent")
    session_models = {e.get("model") for _, e in telemetry if e.get("type") == "session"}

    if not telemetry:
        print("UNVERIFIABLE: telemetry export is empty — cannot join (never CLEAN on missing evidence)")
        sys.exit(2)
    if dispatches and not agent_models:
        print("UNVERIFIABLE: journal has dispatch lines but telemetry has zero agent rows")
        sys.exit(2)

    violations = []
    if not journal or journal[0][1].get("event") != "commander_stamp":
        violations.append("journal's first event is not commander_stamp (REQ-4 self-stamp duty)")
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
