#!/usr/bin/env python3
"""Fallback result generator — L2-owned.

Result-shape knowledge lives beside the schema and checker; an adapter that
must synthesize a failure result (harness invocation died, worker left no
usable artifact) calls this instead of hand-building result fields.

Usage: make-fallback-result.py <task_dir> <runtime> <fallback_reason>
Writes <task_dir>/result.json: schema-valid, status "failed", task_id read
from <task_dir>/task-contract.md frontmatter (falls back to "unknown").
Stdlib only.
"""
import datetime
import json
import os
import sys


def read_task_id(task_dir):
    try:
        with open(os.path.join(task_dir, "task-contract.md"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("task_id:"):
                    return line.split(":", 1)[1].strip().strip("\"'") or "unknown"
    except OSError:
        pass
    return "unknown"


def main():
    if len(sys.argv) != 4:
        print("usage: make-fallback-result.py <task_dir> <runtime> <fallback_reason>")
        sys.exit(2)
    task_dir, runtime, reason = sys.argv[1:4]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {
        "schema_version": "1.1",
        "task_id": read_task_id(task_dir),
        "role": "implementer",
        "runtime": runtime,
        "status": "failed",
        "scope_change_request": None,
        "summary": "harness invocation failed before the worker produced a usable result",
        "files_changed": [],
        "commands_run": [],
        "tests_passed": None,
        "risks": ["infra-level failure: no usable worker result; see fallback_reason"],
        "handoff_notes": "",
        "observations": "",
        "started_at": now,
        "completed_at": now,
        "duration_ms": 0,
        "fallback_reason": reason,
    }
    with open(os.path.join(task_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(os.path.join(task_dir, "result.json"))


if __name__ == "__main__":
    main()
