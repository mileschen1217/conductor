#!/usr/bin/env python3
"""audit-artifact-reconciliation.py — consumer-gating invariant enforcement.

The 0-worker consumer-gating rule (doctrine § Entry gate, inline write-shape
row): contract and result artifacts are produced ONLY for a task a second
context consumes. This audit is that rule's STANDING mechanical enforcement:
every contract/result artifact on disk must reconcile to a journal event that
accounts for it; an orphan artifact — paper with no journal home — is the
producer=judge ceremony the rule exists to kill (regression-ratchet: without a
standing check the silent drift re-enacts itself).

Reconciliation is journal-only (doctrine:583 journal-only audit boundary): it
reads the append-only journal, NEVER file mtimes, NEVER a session transcript.

Artifacts reconciled (by basename convention):
  - `task-contract*.md`  → accounted iff cited by a journal `dispatch` line's
    `contract` field, OR by a `deviation{kind:"aborted-dispatch"}` line's
    STRUCTURED `contract` field (a decided-but-unlaunched dispatch's record;
    NOT free-text `note` parsing — doctrine § Audit surface additive-fields).
  - `result.json`        → accounted iff its task dir holds a contract cited by
    a `dispatch` whose `task_id` has a matching `dispatch_result` line (a worker
    executed the task; the read-only-worker carrier — commander-persisted result
    — rides the same dispatch_result, doctrine § Report contract).

Owed-when: a pure 0-worker run (zero artifacts) is vacuous — exit 0, nothing to
reconcile (the SKILL side does not even call this on a pure 0-worker close; the
script side is the double-check, doctrine owed-when).

Usage:
  python3 scripts/audit-artifact-reconciliation.py <dir>
  python3 scripts/audit-artifact-reconciliation.py --self-test
Exit: 0 = CLEAN / vacuous; 1 = orphan artifact(s) found; 2 = environment error.
"""
import json
import os
import sys


def _relnorm(base, path):
    """Normalize `path` to a base-relative posix path for comparison.
    Absolute paths under base become relative; others are normpath'd as-is."""
    p = path.replace("\\", "/")
    if os.path.isabs(p):
        try:
            p = os.path.relpath(p, base)
        except ValueError:
            pass
    return os.path.normpath(p)


def _parse_journal(journal_path, base):
    """Return (dispatched_contracts, aborted_contracts, result_dirs, errors).
    dispatched_contracts: {relnorm contract path -> task_id}
    aborted_contracts: set of relnorm contract paths (aborted-dispatch record)
    result_dirs: set of relnorm task dirs that have a worker-executed result
    """
    dispatched = {}          # contract relpath -> task_id
    dispatch_by_task = {}    # task_id -> contract relpath
    aborted = set()          # contract relpaths from aborted-dispatch deviations
    result_task_ids = set()  # task_ids with a dispatch_result
    errors = []
    if not os.path.isfile(journal_path):
        return dispatched, aborted, set(), errors  # empty-journal semantics
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
            kind = ev.get("event")
            if kind == "dispatch":
                c = ev.get("contract")
                tid = ev.get("task_id")
                if c:
                    rc = _relnorm(base, c)
                    dispatched[rc] = tid
                    if tid:
                        dispatch_by_task[tid] = rc
            elif kind == "deviation" and ev.get("kind") == "aborted-dispatch":
                c = ev.get("contract")
                if c:
                    aborted.add(_relnorm(base, c))
            elif kind == "dispatch_result":
                tid = ev.get("task_id")
                if tid:
                    result_task_ids.add(tid)
    # a task dir has a legitimate result iff its contract's dispatch has a result
    result_dirs = set()
    for tid in result_task_ids:
        rc = dispatch_by_task.get(tid)
        if rc:
            result_dirs.add(os.path.dirname(rc))
    return dispatched, aborted, result_dirs, errors


def _find_artifacts(base):
    contracts, results = [], []
    for root, _dirs, files in os.walk(base):
        for f in files:
            full = os.path.join(root, f)
            # disk artifacts are always under `base` (os.walk starts there);
            # make them base-relative directly so comparison holds whether the
            # caller passed base as an absolute or a relative path.
            rel = os.path.normpath(os.path.relpath(full, base))
            if f.startswith("task-contract") and f.endswith(".md"):
                contracts.append(rel)
            elif f == "result.json":
                results.append(rel)
    return sorted(contracts), sorted(results)


def reconcile(base):
    """Return (orphans, errors). orphans: list of (path, reason)."""
    journal_path = os.path.join(base, "journal.jsonl")
    dispatched, aborted, result_dirs, errors = _parse_journal(journal_path, base)
    contracts, results = _find_artifacts(base)
    orphans = []
    accounted_contracts = set(dispatched) | aborted
    for c in contracts:
        if c not in accounted_contracts:
            orphans.append((c, "contract with no journal dispatch / aborted-dispatch record"))
    for r in results:
        if os.path.dirname(r) not in result_dirs:
            orphans.append((r, "result.json with no matching dispatch_result (no worker executed this task)"))
    return orphans, errors, len(contracts) + len(results)


def _run(base):
    if not os.path.isdir(base):
        print(f"ERROR: not a directory: {base}", file=sys.stderr)
        return 2
    orphans, errors, n_artifacts = reconcile(base)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if orphans:
        for path, reason in orphans:
            print(f"ORPHAN: {path} — {reason}")
        print(f"FAIL: {len(orphans)} orphan artifact(s)")
        return 1
    if n_artifacts == 0:
        print("CLEAN: no contract/result artifacts (vacuous — pure 0-worker or empty)")
    else:
        print(f"CLEAN: {n_artifacts} artifact(s) reconciled to journal")
    return 0


def _self_test():
    """Prove the reconciler on planted fixtures under scripts/fixtures/reconciliation/.
    Filename convention on each fixture subdir mirrors test-*.sh: dir name
    prefix `clean-`/`orphan-` encodes expectation."""
    here = os.path.dirname(os.path.abspath(__file__))
    fixdir = os.path.join(here, "fixtures", "reconciliation")
    if not os.path.isdir(fixdir):
        print(f"SELF-TEST ERROR: fixtures missing at {fixdir}", file=sys.stderr)
        return 2
    failed = 0
    for name in sorted(os.listdir(fixdir)):
        d = os.path.join(fixdir, name)
        if not os.path.isdir(d):
            continue
        orphans, errors, _ = reconcile(d)
        got_fail = bool(orphans) or bool(errors)
        want_fail = name.startswith("orphan-")
        if got_fail != want_fail:
            print(f"SELF-TEST FAIL: {name} want_fail={want_fail} got_fail={got_fail} orphans={orphans}")
            failed = 1
        else:
            print(f"ok: {name} ({'orphan flagged' if want_fail else 'clean'})")
    if failed:
        print("SELF-TEST FAIL")
        return 1
    print("SELF-TEST OK")
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "--self-test":
        return _self_test()
    if len(argv) != 2:
        print(__doc__.split("Usage:")[1].rstrip(), file=sys.stderr)
        return 2
    return _run(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
