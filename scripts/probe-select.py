#!/usr/bin/env python3
"""probe-select.py — tier-0 boot-probe row selector (v3.1 REQ-4 / AC-8).

Python 3 stdlib ONLY. Deterministic three-state decision over the project's
append-only probe record (schema: contract/probe.schema.json):

  HIT <config_hash>@<ts> boot_tokens=<n>
      — the LATEST row (file order) matches the current harness + config_hash
        + model_gen (three axes, equal weight).
  REPROBE
      — no matching row (including: record file absent — the first-entry
        case), or the record is empty. The caller runs the binding's probe
        procedure and appends a new row; old rows are never edited.
  ERROR <reason>
      — record file exists but is unreadable, or ANY line is malformed
        (bad JSON, wrong schema tag, missing/ill-typed fields). Fail-safe:
        a suspicious row is never consumed (doctrine § Amortization brake
        conservative-closed path).

Usage:
  probe-select.py <probe.jsonl> --harness <binding id> --config-hash <hex> \
      --model-gen <gen tag>

Exit: 0 = HIT; 1 = REPROBE; 2 = ERROR.
"""
import argparse
import os
import sys


def validate_row(row):
    if not isinstance(row, dict):
        return "row is not an object"
    if row.get("schema") != "boot-probe/v1":
        return f"schema tag {row.get('schema')!r} != boot-probe/v1"
    key = row.get("key")
    if not isinstance(key, dict):
        return "key missing or not an object"
    for f in ("harness", "model_gen"):
        if not isinstance(key.get(f), str) or not key.get(f):
            return f"key.{f} missing or not a non-empty string"
    bt = row.get("boot_tokens")
    if not isinstance(bt, int) or isinstance(bt, bool) or bt < 0:
        return "boot_tokens missing or not a non-negative integer"
    if not isinstance(row.get("config_hash"), str) or not row.get("config_hash"):
        return "config_hash missing or not a non-empty string"
    prov = row.get("provenance")
    if not isinstance(prov, dict) or not isinstance(prov.get("ts"), str):
        return "provenance.ts missing"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record")
    ap.add_argument("--harness", required=True)
    ap.add_argument("--config-hash", dest="config_hash", required=True)
    ap.add_argument("--model-gen", dest="model_gen", required=True)
    args = ap.parse_args()

    if not os.path.exists(args.record):
        print("REPROBE")
        return 1

    import json
    try:
        with open(args.record, encoding="utf-8") as f:
            raw_lines = f.readlines()
    except OSError as err:
        print(f"ERROR cannot read record: {err}")
        return 2

    rows = []
    for n, raw in enumerate(raw_lines, 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as err:
            print(f"ERROR line {n}: JSON parse error: {err}")
            return 2
        problem = validate_row(row)
        if problem:
            print(f"ERROR line {n}: malformed row: {problem}")
            return 2
        rows.append(row)

    hit = None
    for row in rows:  # file order; last match wins (append-only ⇒ latest)
        if (
            row["key"]["harness"] == args.harness
            and row["config_hash"] == args.config_hash
            and row["key"]["model_gen"] == args.model_gen
        ):
            hit = row
    if hit is None:
        print("REPROBE")
        return 1
    print(f"HIT {hit['config_hash']}@{hit['provenance']['ts']} boot_tokens={hit['boot_tokens']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
