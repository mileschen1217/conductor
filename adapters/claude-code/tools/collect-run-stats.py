#!/usr/bin/env python3
"""collect-run-stats.py — L3 tier-0 constants collector (v3 REQ-5 / AC-15).

Runs at precedent-append time. Inputs are EXACTLY the run journal plus the
binding's declared offered surfaces (doctrine: the mode binds a harness's
interface, never its internals — session transcripts and on-disk internal
formats are illegal sources; this script never touches them).

Derivation (documented so the fidelity mark is honest):
  - per-worker usage comes from journal `dispatch_result.usage` lines — the
    harness's in-channel report, recorded verbatim by the commander
    (offered surface: in-channel-worker-usage);
  - brief / re-read volumes come from journal additive estimate fields
    `dispatch.brief_tokens_est` and `dispatch_result.reread_tokens_est`
    (offered surface: journal-estimate);
  - task family and run id come from the journal (entry-gate judgment_moment
    `family` field; commander_stamp `run_id`).
  Constants land in tok-eq via the binding's unit weights (parsed from
  binding.md — the single home of r/weights/gen-tag):
    C_fresh        = median(worker cache-creation tokens) x weight[cache-write]   (burner: worker)
    C_brief_worker = median(brief_tokens_est) x weight[input]                     (burner: worker)
    C_brief_cmd    = median(brief_tokens_est) x weight[output]                    (burner: commander)
    C_reread       = median(reread_tokens_est) x weight[input]                    (burner: commander)

Any missing input degrades the run to ONE `unverifiable` row (reason names
the gap) and exits 0 — collector degradation never blocks a run close.
Discipline-price rows are NEVER produced here (ablation pairs only).
W-estimate drift (dispatch.w_est vs dispatch_result.usage output) is printed
to stdout as an `estimate-drift` JSON line for the commander to journal —
it never enters the table (W is per-task, not a family constant).

Usage:
  collect-run-stats.py <journal-path> --binding claude-code --out <table-path> [--project <slug>]

Exit: 0 = one row appended (constants or unverifiable); 2 = usage error.
"""
import argparse
import datetime
import fcntl
import json
import os
import re
import sys
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
BINDING_MD = {"claude-code": os.path.join(HERE, "..", "binding.md")}


def parse_binding(binding_id):
    """Parse unit weights + current gen-tag from the binding doc (single home)."""
    path = BINDING_MD.get(binding_id)
    if path is None or not os.path.isfile(path):
        return None, None, "unknown binding id or binding.md missing"
    text = open(path, encoding="utf-8").read()
    m = re.search(
        r"weight\[output\]=([0-9.]+),\s*weight\[cache-write\]=([0-9.]+),\s*weight\[input\]=([0-9.]+)",
        text,
    )
    g = re.search(r"gen-tag：\*\*`(g[0-9.]+)`\*\*", text)
    if not m or not g:
        return None, None, "binding.md weights/gen-tag not parseable"
    weights = {
        "output": float(m.group(1)),
        "cache-write": float(m.group(2)),
        "input": float(m.group(3)),
    }
    return weights, g.group(1), None


def load_journal(path):
    events = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                raise ValueError(f"journal line {n} is not valid JSON")
    return events


def append_row(out_path, row):
    """flock-serialized single-line O_APPEND (cross-project concurrency safe)."""
    data = (json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    fd = os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, data)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("journal")
    ap.add_argument("--binding", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--project", default=os.path.basename(os.getcwd()))
    args = ap.parse_args()

    if not os.path.isfile(args.journal):
        print(f"usage error: journal not found: {args.journal}", file=sys.stderr)
        return 2

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # A corrupt LINE inside an existing journal is run-artifact degradation
    # (e.g. a crash-truncated write), not a caller mistake: degrade to an
    # UNVERIFIABLE row, never a nonzero exit (nonzero = usage errors only).
    parse_error = None
    try:
        events = load_journal(args.journal)
    except ValueError as e:
        events, parse_error = [], str(e)

    stamp = next((e for e in events if e.get("event") == "commander_stamp"), None)
    run_id = (stamp or {}).get("run_id") or "unknown-run"
    family = next(
        (
            e.get("family")
            for e in events
            if e.get("event") == "judgment_moment"
            and e.get("decision_type") == "entry-gate"
            and e.get("family")
        ),
        None,
    )
    weights, model_gen, binding_err = parse_binding(args.binding)

    key = {
        # "unknown" is legal ONLY on unverifiable rows (schema x_notes); the
        # constants path below re-keys with the journal-declared family.
        "family": family or "unknown",
        "harness": args.binding,
        "model_gen": model_gen or "unknown",
    }
    provenance = {"run_id": run_id, "project": args.project, "ts": ts}

    def unverifiable(reason, surface="none"):
        row = {
            "schema": "constants/v1",
            "kind": "unverifiable",
            "key": key,
            "reason": reason,
            "surface": surface,
            "provenance": provenance,
        }
        append_row(args.out, row)
        print(f"UNVERIFIABLE row appended: {reason}")
        return 0

    if parse_error:
        return unverifiable(f"journal parse failure: {parse_error}")
    if binding_err:
        return unverifiable(binding_err)
    if stamp is None:
        return unverifiable("journal has no commander_stamp")
    if family is None:
        return unverifiable("family missing from journal (entry-gate judgment_moment carries no family field)")

    dispatches = {e.get("task_id"): e for e in events if e.get("event") == "dispatch"}
    # last-wins by task_id (mirrors dispatches): a duplicated dispatch_result
    # line must not double-count one observation into the medians
    results = list(
        {e.get("task_id"): e for e in events if e.get("event") == "dispatch_result"}.values()
    )

    if not dispatches or not results:
        return unverifiable("no offload in run (zero dispatch/dispatch_result pairs) — nothing to measure")

    fresh, briefs, rereads, drifts = [], [], [], []
    fresh_sources = []
    for r in results:
        usage = r.get("usage") or {}
        # fallback chain, best fidelity first; the chosen source is named in
        # the row's fidelity mark (a total is only a PROXY upper bound for the
        # fresh-context load — CC's in-channel report often offers totals only)
        for ukey, tag in (
            ("cache_creation_input_tokens", "cache-creation"),
            ("input_tokens", "input"),
            ("total_tokens", "total-proxy"),
            ("subagent_tokens", "total-proxy"),  # the Agent tool's actual in-channel key (live-run finding, calib-r1)
        ):
            cc = usage.get(ukey)
            if cc is not None:
                fresh.append(cc)
                fresh_sources.append(tag)  # per-worker; heterogeneous shapes all named in fidelity
                break
        rr = r.get("reread_tokens_est")
        if rr is not None:
            rereads.append(rr)
        d = dispatches.get(r.get("task_id"), {})
        b = d.get("brief_tokens_est")
        if b is not None:
            briefs.append(b)
        w_est, w_act = d.get("w_est"), usage.get("output_tokens")
        if w_est and w_act:
            drifts.append(
                {
                    "signal": "estimate-drift",
                    "task_id": r.get("task_id"),
                    "w_est": w_est,
                    "w_actual": w_act,
                    "ratio": round(w_act / w_est, 2),
                }
            )

    missing = [
        name
        for name, vals in (
            ("usage (dispatch_result.usage)", fresh),
            ("brief_tokens_est (dispatch)", briefs),
            ("reread_tokens_est (dispatch_result)", rereads),
        )
        if not vals
    ]
    if missing:
        return unverifiable(
            "usage events incomplete: missing " + "; ".join(missing),
            surface="in-channel-worker-usage",
        )

    row = {
        "schema": "constants/v1",
        "kind": "constants",
        "key": key,
        "const": {
            "C_fresh": int(median(fresh) * weights["cache-write"]),
            "C_brief_cmd": int(median(briefs) * weights["output"]),
            "C_brief_worker": int(median(briefs) * weights["input"]),
            "C_reread": int(median(rereads) * weights["input"]),
        },
        "unit": "tok-eq",
        "burner": {
            "C_fresh": "worker",
            "C_brief_cmd": "commander",
            "C_brief_worker": "worker",
            "C_reread": "commander",
        },
        "status": "measured",
        "fidelity": f"in-channel-worker-usage({'+'.join(sorted(set(fresh_sources)))})+journal-estimate",
        "provenance": provenance,
    }
    append_row(args.out, row)
    print(f"constants row appended: {json.dumps(row['const'])} key={json.dumps(key)}")
    for d in drifts:
        print(json.dumps(d, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
