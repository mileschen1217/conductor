#!/usr/bin/env python3
# Journal event vocabulary: contract/journal-event.schema.json (doctrine § Machine pointers).
"""collect-run-stats.py — L3 tier-0 estimate-drift emitter.

Runs on an instrumented close only, because only an instrumented run has the
journal this reads. Its one duty is the estimate-drift signal —
dispatch.w_est vs the dispatch_result's harness-reported output tokens —
printed as JSON lines for the commander to journal as typed deviation events.
Drift is evidence for a later change to the binding's anchors, which travels
the evidence path in ADR 0003. This tool WRITES NOTHING
anywhere.

Inputs are EXACTLY the run journal (doctrine: the mode binds a harness's
interface, never its internals — session transcripts and on-disk internal
formats are illegal sources; this script never touches them). A
dispatch_result whose usage is the typed degradation marker "unavailable"
contributes no drift line (legal, visible in the journal itself).

Usage:
  collect-run-stats.py <journal-path>

Exit: 0 = drift lines (possibly zero) printed; degradation prints a NOTE and
still exits 0 — collector degradation never blocks a run close. 2 = usage
error (journal path missing / unknown flags).
"""
import argparse
import json
import sys


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("journal")
    args = ap.parse_args()

    try:
        events = load_journal(args.journal)
    except OSError as err:
        print(f"usage error: cannot read journal: {err}", file=sys.stderr)
        return 2
    except ValueError as err:
        print(f"NOTE: {err} — run-artifact degradation, no drift emitted (never blocks close)")
        return 0

    dispatches = {e.get("task_id"): e for e in events if e.get("event") == "dispatch"}
    # last-wins by task_id: a duplicated dispatch_result must not double-count
    results = list(
        {e.get("task_id"): e for e in events if e.get("event") == "dispatch_result"}.values()
    )

    if not dispatches or not results:
        print("NOTE: no offload in run (zero dispatch/dispatch_result pairs) — no drift to measure")
        return 0

    emitted = 0
    for r in results:
        usage = r.get("usage")
        if not isinstance(usage, dict):
            continue  # "unavailable" (typed degradation) or absent — no drift measurable
        d = dispatches.get(r.get("task_id"), {})
        w_est, w_act = d.get("w_est"), usage.get("output_tokens")
        if w_est and w_act:
            emitted += 1
            print(json.dumps({
                "signal": "estimate-drift",
                "task_id": r.get("task_id"),
                "w_est": w_est,
                "w_actual": w_act,
                # doctrine's canonical drift basis is delivered diff bytes
                # through the anchors; the in-channel output count is a PROXY
                # this journal-only tool can reach — named so a later reader
                # never mistakes it for a bytes measurement. The
                # commander computes the bytes-basis drift at close via
                # estimate-tokens.py on the delivered files (SKILL Phase 5).
                "w_actual_source": "usage-output-tokens(proxy)",
                "ratio": round(w_act / w_est, 2),
            }, ensure_ascii=False))
    if not emitted:
        print("NOTE: no measurable w_est/output pairs — no drift emitted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
