#!/usr/bin/env python3
"""Builds synthetic CC transcript trees for test-advisor-observations.sh.

Shapes are copied from real records observed in probe 2 (2026-07-12): an
advisor call is an assistant `server_tool_use` block named `advisor`; a
dispatch is an assistant `tool_use` block named `Agent` whose input.prompt
carries the commander's `Task contract:` marker; a subagent's meta.json holds
{agentType, description, toolUseId, spawnDepth} and no task_id.
"""
import json
import os
import shutil
import sys


def rec(*blocks):
    return {"type": "assistant", "message": {"role": "assistant", "content": list(blocks)}}


def dispatch(tool_use_id, prompt):
    return rec({"type": "tool_use", "id": tool_use_id, "name": "Agent",
                "input": {"prompt": prompt}})


def advisor():
    return rec({"type": "server_tool_use", "id": "srvtoolu_x", "name": "advisor",
                "input": {}})


def write(root, name, main_records, subagents, main_extra_lines=()):
    """subagents: list of (agent_id, meta_dict|None, records|str)"""
    base = os.path.join(root, name)
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)
    tpath = os.path.join(base, "session.jsonl")
    with open(tpath, "w", encoding="utf-8") as f:
        for r in main_records:
            f.write(json.dumps(r) + "\n")
        for raw in main_extra_lines:
            f.write(raw + "\n")
    if subagents is not None:
        sub = os.path.join(base, "session", "subagents")
        os.makedirs(sub)
        for agent_id, meta, records in subagents:
            p = os.path.join(sub, f"agent-{agent_id}.jsonl")
            if isinstance(records, str):          # raw text (malformed-line case)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(records)
            else:
                with open(p, "w", encoding="utf-8") as f:
                    for r in records:
                        f.write(json.dumps(r) + "\n")
            if meta is not None:
                with open(p[:-len(".jsonl")] + ".meta.json", "w", encoding="utf-8") as f:
                    json.dump(meta, f)
    return tpath


def meta(tool_use_id, depth=1):
    return {"agentType": "Explore", "description": "d",
            "toolUseId": tool_use_id, "spawnDepth": depth}


def main():
    root = sys.argv[1]
    os.makedirs(root, exist_ok=True)

    # happy: one marked dispatch whose worker consulted twice; commander consulted
    # once (must NOT be emitted); a second worker never consulted.
    write(root, "happy",
          [dispatch("toolu_1", "Task contract: t-alpha\n\nDo the thing."),
           dispatch("toolu_2", "Task contract: t-beta\n\nOther thing."),
           advisor()],
          [("a1", meta("toolu_1"), [advisor(), advisor()]),
           ("a2", meta("toolu_2"), [rec({"type": "text", "text": "no consult"})])])

    # every fatal path: a worker consulted, and something makes it unattributable
    write(root, "no-marker",
          [dispatch("toolu_1", "Do the thing, no marker anywhere.")],
          [("a1", meta("toolu_1"), [advisor()])])

    write(root, "unknown-task",
          [dispatch("toolu_1", "Task contract: t-ghost\n\nDo it.")],
          [("a1", meta("toolu_1"), [advisor()])])

    write(root, "two-markers",
          [dispatch("toolu_1", "Task contract: t-alpha\nTask contract: t-beta\n")],
          [("a1", meta("toolu_1"), [advisor()])])

    write(root, "nested",
          [dispatch("toolu_1", "Task contract: t-alpha\n")],
          [("a1", meta("toolu_1", depth=2), [advisor()])])

    write(root, "no-meta",
          [dispatch("toolu_1", "Task contract: t-alpha\n")],
          [("a1", None, [advisor()])])

    write(root, "unknown-tooluseid",
          [dispatch("toolu_OTHER", "Task contract: t-alpha\n")],
          [("a1", meta("toolu_MISSING"), [advisor()])])

    write(root, "malformed-line",
          [dispatch("toolu_1", "Task contract: t-alpha\n")],
          [("a1", meta("toolu_1"),
            json.dumps(advisor()) + "\n{ this is not json\n")])

    write(root, "bad-content-shape",
          [dispatch("toolu_1", "Task contract: t-alpha\n")],
          [("a1", meta("toolu_1"),
            [{"type": "assistant", "message": {"role": "assistant",
                                               "content": "plain string"}}])])

    # a marker the commander decorated (backticks/bold): the token captured is
    # `t-alpha` not t-alpha, so it names no declared task -> fatal, never a
    # silent miscount. Guards the SKILL.md template against re-growing markup.
    write(root, "decorated-marker",
          [dispatch("toolu_1", "Task contract: `t-alpha`\n")],
          [("a1", meta("toolu_1"), [advisor()])])

    # no subagents dir at all, yet the caller names dispatched tasks
    write(root, "no-subagents-dir",
          [dispatch("toolu_1", "Task contract: t-alpha\n")], None)


if __name__ == "__main__":
    main()
