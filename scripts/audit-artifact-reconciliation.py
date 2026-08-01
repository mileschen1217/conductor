#!/usr/bin/env python3
"""Reconcile an instrumented run's artifacts against its journal, both directions.

Journal-only: reads journal.jsonl, never file mtimes, never a transcript
(doctrine § Machine pointers — journal).
Filename convention both directions pair on is contractual (doctrine RT-5
@ artifact-naming).
Journal event vocabulary: contract/journal-event.schema.json (doctrine § Machine pointers).

Usage:
  python3 scripts/audit-artifact-reconciliation.py <dir>
  python3 scripts/audit-artifact-reconciliation.py --self-test
Exit: 0 = CLEAN / vacuous; 1 = reconciliation failure(s); 2 = environment error.
"""
import json
import os
import sys
from typing import NamedTuple


class Claims(NamedTuple):
    """What the journal says exists."""
    dispatched_contracts: dict   # contract relpath -> task_id
    aborted_contracts: set       # contract relpaths from aborted-dispatch deviations
    executed_task_dirs: set      # task dirs whose dispatch got a dispatch_result
    errors: list


def _relnorm(base, path):
    p = path.replace("\\", "/")
    if os.path.isabs(p):
        try:
            p = os.path.relpath(p, base)
        except ValueError:
            pass
    return os.path.normpath(p)


def _read_claims(journal_path, base):
    dispatched, contract_of_task, aborted, tasks_with_result, errors = {}, {}, set(), set(), []
    if not os.path.isfile(journal_path):
        return Claims(dispatched, aborted, set(), errors)   # empty journal is vacuous
    with open(journal_path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"journal line {n}: not JSON")
                continue
            kind, contract, task = ev.get("event"), ev.get("contract"), ev.get("task_id")
            if kind == "dispatch" and contract:
                dispatched[_relnorm(base, contract)] = task
                if task:
                    contract_of_task[task] = _relnorm(base, contract)
            elif kind == "deviation" and ev.get("kind") == "aborted-dispatch" and contract:
                aborted.add(_relnorm(base, contract))
            elif kind == "dispatch_result" and task:
                tasks_with_result.add(task)
    executed = {os.path.dirname(contract_of_task[t])
                for t in tasks_with_result if t in contract_of_task}
    return Claims(dispatched, aborted, executed, errors)


def _find_artifacts(base):
    contracts, results = [], []
    for root, _dirs, files in os.walk(base):
        for f in files:
            rel = os.path.normpath(os.path.relpath(os.path.join(root, f), base))
            if f.startswith("task-contract") and f.endswith(".md"):
                contracts.append(rel)
            elif f == "result.json":
                results.append(rel)
    return sorted(contracts), sorted(results)


def reconcile(base):
    claims = _read_claims(os.path.join(base, "journal.jsonl"), base)
    contracts, results = _find_artifacts(base)
    accounted = set(claims.dispatched_contracts) | claims.aborted_contracts
    failures = []

    for c in contracts:
        if c not in accounted:
            failures.append((c, "ORPHAN: contract with no journal dispatch / aborted-dispatch record"))
    for r in results:
        if os.path.dirname(r) not in claims.executed_task_dirs:
            failures.append((r, "ORPHAN: result.json with no matching dispatch_result (no worker executed this task)"))

    # The journal->disk leg is what catches a RENAMED contract: the disk scan
    # globs on basename, so a rename makes the orphan check above go silent while
    # the run still reads as fully accounted.
    for c in sorted(accounted):
        if not os.path.isfile(os.path.join(base, c)):
            failures.append((c, "DANGLING: journal names this contract path but no such file exists"))
    for d in sorted(claims.executed_task_dirs):
        rp = os.path.join(d, "result.json") if d else "result.json"
        if not os.path.isfile(os.path.join(base, rp)):
            failures.append((rp, "DANGLING: journal records a dispatch_result for this task but no result.json exists"))

    return failures, claims.errors, len(contracts) + len(results)


def _run(base):
    if not os.path.isdir(base):
        print(f"ERROR: not a directory: {base}", file=sys.stderr)
        return 2
    failures, errors, n_artifacts = reconcile(base)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if failures:
        for path, reason in failures:
            print(f"{reason} — {path}")
        print(f"FAIL: {len(failures)} reconciliation failure(s)")
        return 1
    if n_artifacts == 0:
        print("CLEAN: no contract/result artifacts and nothing claimed by the journal (vacuous)")
    else:
        print(f"CLEAN: {n_artifacts} artifact(s) reconciled to journal, both directions")
    return 0


def _self_test():
    fixdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "reconciliation")
    if not os.path.isdir(fixdir):
        print(f"SELF-TEST ERROR: fixtures missing at {fixdir}", file=sys.stderr)
        return 2
    failed = 0
    for name in sorted(os.listdir(fixdir)):
        d = os.path.join(fixdir, name)
        if not os.path.isdir(d):
            continue
        failures, errors, _ = reconcile(d)
        got_fail = bool(failures) or bool(errors)
        want_fail = not name.startswith("clean-")
        if got_fail != want_fail:
            print(f"SELF-TEST FAIL: {name} want_fail={want_fail} got_fail={got_fail} failures={failures}")
            failed = 1
        else:
            print(f"ok: {name} ({'flagged' if want_fail else 'clean'})")
    print("SELF-TEST FAIL" if failed else "SELF-TEST OK")
    return failed


def main(argv):
    if len(argv) == 2 and argv[1] == "--self-test":
        return _self_test()
    if len(argv) != 2:
        print(__doc__.split("Usage:")[1].rstrip(), file=sys.stderr)
        return 2
    return _run(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
