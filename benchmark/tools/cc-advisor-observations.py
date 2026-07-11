#!/usr/bin/env python3
"""Benchmark tool (NOT part of the mode): CC session transcripts -> observations.jsonl.

**Read this before using it, and before promoting it.**

This script reads Claude Code's session transcripts — an *internal* on-disk
format that CC never promised to keep stable. Doctrine § Advisor primitive
forbids the mode from binding a harness's internals, so this cannot live in
`adapters/` and no binding may depend on it. It lives here because a
*measurement-bearing* run (a benchmark cell, a parity run, an ablation) makes
claims that attribute work to a tier, and an undisclosed worker→advisor consult
would silently falsify exactly those claims. Verifying one such run is a
bounded, one-off act with a known cost. That is the whole of its warrant.

Expect it to break on a CC upgrade. When it breaks, the correct response is
UNVERIFIABLE — or an agent reading the sessions by hand — never a deeper
excavation into CC's internals.

It emits the observation face consumed by
`scripts/audit-judgment-flow.py --advisor-observations` (line shape:
`{"event":"advisor_call","task_id":"<id>"}`): observed advisor calls >
disclosed `judgment_events` for a task_id is a VIOLATION. That consumer is
vendor-neutral and stays in the mode; only this producer is CC-internal.

Governance stance: this is a producer for a FALSE-NEGATIVE-hostile check. A
missed advisor call reads as innocence, so every ambiguity is fatal:

  **On any doubt, this script writes NO observations file and exits non-zero.**

That is the fail-closed path, and it is the *only* one: an absent observations
file makes the audit report UNVERIFIABLE (never CLEAN). A partial or
best-effort file would be worse than none — it would look like evidence of
absence. Nothing is emitted to stdout until every advisor call found has been
attributed to a task_id the caller named.

Fatal (no output, exit 1): a malformed transcript line; an assistant record
whose content is not a block list; a subagent that called the advisor but
whose dispatch cannot be resolved (missing meta, unknown toolUseId, no
`Task contract:` marker, a marker naming a task_id the caller did not supply,
or `spawnDepth > 1` — nested dispatch is out of the doctrine's topology and
its parent Agent call does not live in the main transcript, so it cannot be
joined); or a missing `subagents/` directory when task_ids were supplied.

## How a worker advisor call is attributed

CC records an advisor call in the CALLER's transcript as a `server_tool_use`
block named `advisor` — main session and subagents alike (probe 2,
2026-07-12). But a subagent's `agent-<id>.meta.json` carries only the spawning
`toolUseId`, never a task_id. So:

  server_tool_use(advisor) in agent-<id>.jsonl
    -> agent-<id>.meta.json .toolUseId
    -> the Agent tool_use with that id in the MAIN transcript
    -> that prompt's `Task contract: <task_id>` marker line

The last hop imposes a requirement — **each dispatch prompt in the run must
carry a line `Task contract: <task_id>`** (exact, anchored: substring matching
would let a prompt that merely mentions another task steal the attribution).
That requirement belongs to the **benchmark protocol's run procedure**, not to
the mode: an ordinary run owes nothing to this tool. `benchmark/protocol.md`
§ Isolation invariants carries it for the runs that are measured.

Commander (main-session) advisor calls are NOT emitted: the audit joins
observations to worker results by task_id, so a commander row is unjoinable by
construction. The commander's own consults are disclosed in the run journal,
which is where the audit checks them. The count is reported on stderr.

Usage:
  python3 benchmark/tools/cc-advisor-observations.py \
      --transcript ~/.claude/projects/<slug>/<session-id>.jsonl \
      --task-ids t1 t2 ... > observations.jsonl
"""
import argparse
import json
import os
import re
import sys

MARKER = re.compile(r"^Task contract:[ \t]*(\S+)[ \t]*$", re.MULTILINE)


class Fatal(Exception):
    """Any condition under which a partial observations file would lie."""


def load(path, what):
    entries = []
    try:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise Fatal(f"{what} {path} line {n} is not valid JSON "
                                f"({exc}) — a dropped line could be the advisor "
                                f"call itself") from None
    except OSError as exc:
        raise Fatal(f"cannot read {what} {path}: {exc}") from None
    return entries


def advisor_calls(entries, path):
    """Count `server_tool_use` blocks named advisor in one transcript."""
    n = 0
    for e in entries:
        if e.get("type") != "assistant":
            continue
        content = e.get("message", {}).get("content")
        if not isinstance(content, list):
            # No benign null-content assistant shape exists (2397/2397 records
            # in the live project's transcripts carry a block list). Anything
            # else is format drift, and drift here reads as "no advisor call".
            raise Fatal(f"{path}: assistant record has non-list content "
                        f"({type(content).__name__}) — transcript format drift; "
                        f"an advisor call in an unrecognized shape would be "
                        f"counted as absent")
        for b in content:
            if (isinstance(b, dict)
                    and b.get("type") == "server_tool_use"
                    and b.get("name") == "advisor"):
                n += 1
    return n


def agent_dispatches(entries):
    """Agent tool_use id -> the prompt text it was dispatched with."""
    out = {}
    for e in entries:
        content = e.get("message", {}).get("content")
        if isinstance(content, list):
            for b in content:
                if (isinstance(b, dict) and b.get("type") == "tool_use"
                        and b.get("name") == "Agent"):
                    out[b.get("id")] = str(b.get("input", {}).get("prompt", ""))
    return out


def attribute(sub_path, prompts, task_ids):
    """The task_id that owns this subagent's advisor calls, or Fatal."""
    meta_path = sub_path[:-len(".jsonl")] + ".meta.json"
    if not os.path.exists(meta_path):
        raise Fatal(f"{os.path.basename(sub_path)} called the advisor but has "
                    f"no {os.path.basename(meta_path)} — unattributable")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise Fatal(f"cannot read {meta_path}: {exc}") from None

    depth = meta.get("spawnDepth")
    if depth is not None and depth > 1:
        raise Fatal(f"{os.path.basename(sub_path)} called the advisor at "
                    f"spawnDepth {depth} — its dispatching Agent call is not in "
                    f"the main transcript, so it cannot be joined (and nested "
                    f"dispatch is outside the doctrine's topology)")

    prompt = prompts.get(meta.get("toolUseId"))
    if prompt is None:
        raise Fatal(f"{os.path.basename(sub_path)} called the advisor but its "
                    f"toolUseId {meta.get('toolUseId')!r} matches no Agent "
                    f"dispatch in the main transcript — unattributable")

    found = MARKER.findall(prompt)
    if not found:
        raise Fatal(f"{os.path.basename(sub_path)} called the advisor but its "
                    f"dispatch prompt has no `Task contract: <task_id>` marker "
                    f"line — the commander must emit one on every dispatch")
    if len(set(found)) > 1:
        raise Fatal(f"{os.path.basename(sub_path)}: dispatch prompt names "
                    f"multiple task contracts {sorted(set(found))} — "
                    f"attribution is ambiguous")
    task_id = found[0]
    if task_id not in task_ids:
        raise Fatal(f"{os.path.basename(sub_path)}: dispatch prompt names task "
                    f"{task_id!r}, which is not among --task-ids {task_ids} — "
                    f"the caller's task list and the run's dispatches disagree")
    return task_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True,
                    help="main session transcript jsonl")
    ap.add_argument("--task-ids", nargs="+", required=True,
                    help="every task_id dispatched this run (from the journal's dispatch lines)")
    args = ap.parse_args()

    try:
        main_entries = load(args.transcript, "transcript")
        prompts = agent_dispatches(main_entries)
        n_commander = advisor_calls(main_entries, args.transcript)

        subdir = os.path.splitext(args.transcript)[0] + "/subagents"
        if not os.path.isdir(subdir):
            raise Fatal(f"no subagents directory at {subdir}, but --task-ids "
                        f"names {len(args.task_ids)} dispatched task(s) — worker "
                        f"advisor calls cannot be observed, so absence cannot be "
                        f"claimed")

        rows = []
        for name in sorted(os.listdir(subdir)):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(subdir, name)
            n = advisor_calls(load(path, "subagent transcript"), path)
            if not n:
                continue
            task_id = attribute(path, prompts, args.task_ids)
            rows.extend([{"event": "advisor_call", "task_id": task_id}] * n)
    except Fatal as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        print("no observations file written — the audit's undisclosed-use check "
              "must report UNVERIFIABLE rather than run on partial evidence",
              file=sys.stderr)
        return 1

    for r in rows:
        print(json.dumps(r))
    print(f"observed {len(rows)} worker advisor call(s) across "
          f"{len(set(r['task_id'] for r in rows))} task(s); "
          f"{n_commander} commander call(s) (journal's business, not emitted)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
