#!/usr/bin/env python3
"""audit-brake-lines.py — deterministic brake-line-vs-table audit (v3 AC-7).

Checks every `brake:` line in a dispatch plan against the constants table and
an allowed r-value set: constants are table-read (cited by row identity),
never invented; r values come from the binding's ratio table; save/pay
arithmetic is consistent with the line's own W/r and the cited row's C_*.

Usage:
  audit-brake-lines.py <dispatch-plan.md> --table <constants.jsonl> \
      [--r-values 1.0,0.4,0.2,0.1,0.5] [--commander-r 0.2,0.1]

--commander-r narrows the legal set to the given commander's OWN column of
the binding's per-pair table (plus 1.0, always legal for same-model). Without
it the audit can only check set membership, not pair correctness — a live
witness run (MR7) wrote r=0.2 for a same-model offload (true value 1.0) and
set-membership alone passed it. CAVEAT: even with --commander-r the
protection is commander-dependent, not general pair-correctness — the
offload's tier label is not cross-checked against r, so a mislabeled r that
coincides with another legitimate value in the SAME commander's column
(e.g. 0.2 under an opus commander, where 0.2 is the legitimate haiku rate)
still passes. Full pair verification needs the worker's resolved model,
which brake lines do not carry.

Per-line verdicts:
  CONFORMANT — parses, r values allowed, citation resolves, arithmetic checks
  DEVIATION  — parses loosely but off the documented format (e.g. verdict off
               enum, save/pay declared uncomputable, cold-start citation) —
               calibration data, not a violation
  VIOLATION  — an invented constant: numeric save/pay inconsistent (>5%) with
               W/r and the cited row; an r outside the allowed set; or a row
               citation that does not resolve in the table

Exit: 0 = no VIOLATION (deviations reported); 1 = any VIOLATION; 2 = env/usage.
"""
import argparse
import json
import os
import re
import sys

OFFLOAD_RE = re.compile(r"\{tier:([^,}]+),W≈(\d+),r=([0-9.]+)[^}]*\}")
FIELD_RE = {
    "save": re.compile(r"save=(\S+)"),
    "pay": re.compile(r"pay=(\S+)"),
    "verdict": re.compile(r"verdict=(\S+)"),
    "ground": re.compile(r"ground=(\S+)"),
    "constants_row": re.compile(r"constants_row=(\S+)"),
}


def load_table(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("kind") == "constants":
                rows.append(r)
    return rows


def resolve_citation(cite, rows):
    """A citation resolves iff its run_id (the @<run_id>/ part) matches a
    constants row's provenance.run_id and every key token embedded in the
    cite's key part appears among that row's key values."""
    m = re.match(r"(.+)@([^/]+)/(.+)", cite)
    if not m:
        return None
    keystr, run_id, _ts = m.group(1), m.group(2), m.group(3)
    for r in rows:
        if r.get("provenance", {}).get("run_id") != run_id:
            continue
        vals = set(str(v) for v in r.get("key", {}).values())
        tokens = [t for t in re.split(r"[,:|{}\s]+", keystr) if t]
        embedded = [t for t in tokens if t in vals]
        if embedded:
            return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--table", required=True)
    ap.add_argument("--r-values", default="1.0,0.4,0.2,0.1,0.5")
    ap.add_argument("--commander-r", default=None,
                    help="the commander's own column of the per-pair r table; narrows the legal set (1.0 stays legal)")
    args = ap.parse_args()

    if not os.path.isfile(args.plan):
        print(f"usage error: plan not found: {args.plan}", file=sys.stderr)
        return 2
    allowed_r = {float(x) for x in args.r_values.split(",")}
    if args.commander_r:
        allowed_r = {1.0} | {float(x) for x in args.commander_r.split(",")}
    rows = load_table(args.table)

    plan = open(args.plan, encoding="utf-8").read()
    # A brake record is LOGICAL: it starts at `brake:` (possibly
    # backtick-wrapped) and runs until a blank line, a heading, or end of
    # text — live plans wrap and continue lines. Collapse to one string.
    lines = [
        re.sub(r"\s+", " ", m.group(0).replace("`", "")).strip()
        for m in re.finditer(r"`?brake:\s*offload=.*?(?=\n\s*\n|\n#|\Z)", plan, re.DOTALL)
    ]
    if not lines:
        print("NO-BRAKE-LINES: plan carries none (legal for a zero-offload inline run)")
        return 0

    violations = 0
    for n, line in enumerate(lines, 1):
        problems, deviations = [], []
        offloads = [(t.strip(), int(w), float(r)) for t, w, r in OFFLOAD_RE.findall(line)]
        if not offloads:
            deviations.append("no parseable offload entries")
        for _t, _w, r in offloads:
            if r not in allowed_r:
                problems.append(f"r={r} outside the allowed binding set {sorted(allowed_r)}")
        f = {k: (rx.search(line).group(1) if rx.search(line) else None) for k, rx in FIELD_RE.items()}
        if f["verdict"] not in ("pass", "fail"):
            deviations.append(f"verdict off enum: {f['verdict']}")
        cite = f["constants_row"] or ""
        cited_row = None
        if cite.startswith("none(") or "pending-measurement" in cite:
            deviations.append(f"cold-start citation: {cite}")
        elif cite:
            cited_row = resolve_citation(cite, rows)
            if cited_row is None:
                problems.append(f"constants_row citation does not resolve in table: {cite}")
        else:
            deviations.append("constants_row field absent")

        def as_int(s):
            try:
                return int(s)
            except (TypeError, ValueError):
                return None

        save, pay = as_int(f["save"]), as_int(f["pay"])
        if save is None or pay is None:
            deviations.append(f"save/pay non-numeric ({f['save']}/{f['pay']}) — economics leg declared uncomputable")
        elif offloads:
            exp_save = sum(w * (1 - r) for _t, w, r in offloads)
            if abs(exp_save - save) > max(5, 0.05 * max(exp_save, 1)):
                problems.append(f"save={save} inconsistent with Σ W·(1−r)={exp_save:.0f}")
            if cited_row:
                c = cited_row["const"]
                exp_pay = c["C_reread"] + c["C_brief_cmd"] + sum(
                    r * (c["C_fresh"] + c["C_brief_worker"]) for _t, _w, r in offloads
                )
                if abs(exp_pay - pay) > max(5, 0.05 * max(exp_pay, 1)):
                    problems.append(f"pay={pay} inconsistent with table row arithmetic {exp_pay:.0f}")

        if problems:
            violations += 1
            print(f"VIOLATION line {n}: " + "; ".join(problems))
        elif deviations:
            print(f"DEVIATION line {n}: " + "; ".join(deviations))
        else:
            print(f"CONFORMANT line {n}")

    if violations:
        print(f"RESULT: {violations} violation(s) in {len(lines)} brake line(s)")
        return 1
    print(f"RESULT: CLEAN ({len(lines)} brake line(s); deviations are calibration data)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
