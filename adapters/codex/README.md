# orchestration-mode — Codex adapter

Binds the L1 dispatch primitive's harness step to `codex exec` (non-interactive).
Doctrine: `doctrine/orchestration-mode.md` (cite, never restate). Tier→model:
`binding.md` beside this file. Codex-as-commander is documented at the end —
documentation only, not an acceptance surface (flip-trigger FT-2).

## AGENTS.md load fragment (worker side)

Paste into the task workspace's AGENTS.md so a Codex worker session picks up
the mode contract:

```markdown
## orchestration-mode worker contract
You may be dispatched as an orchestration-mode worker. When your prompt names
a task-contract file: read it; it is the single home of your duties — obey its
implementer behavioral contract in full and produce its Expected Output into
the task directory (result schema path given in your prompt).
```

## Thin-forwarder recipe (dispatch primitive, middle step)

Inputs: `$task_dir` containing `task-contract.md`; `$model` resolved from
`binding.md`; `$sandbox` = `read-only` for parallel fan-out workers,
`workspace-write` for the single write-capable worker; `$conductor` =
conductor repo root.

```bash
# 1. probe — CLI absent is NOT a task failure; it is adapter-unavailable:
#    report unavailable + fallback_reason upstream; portability ACs go blocked.
command -v codex >/dev/null || { echo "codex-unavailable"; exit 3; }

# 2. dispatch
#    sandbox: read-only for parallel fan-out; workspace-write for the single
#    write worker (doctrine § Single-writer rule)
#    stdin MUST be /dev/null: codex exec waits on stdin in non-interactive contexts
codex exec \
  --cd "$task_dir" \
  --sandbox "$sandbox" \
  -m "$model" \
  "You are a worker under orchestration mode. Read ./task-contract.md; it is the single home of your duties — obey its implementer behavioral contract in full and produce its Expected Output into this directory (result schema: $conductor/contract/task-result.schema.json). Final output: the single line RESULT: ./result.json" < /dev/null
rc=$?

# 3. infra-failure fallback (codex exec died, or left no/empty/invalid
#    result.json): the adapter still yields a schema-valid result.json —
#    status failed, fallback_reason = infra cause. Any existing invalid
#    file is preserved alongside, not overwritten silently.
if [ $rc -ne 0 ]; then
  if ! python3 "$conductor/contract/check-result.py" "$task_dir/result.json" >/dev/null 2>&1; then
    [ -f "$task_dir/result.json" ] && mv "$task_dir/result.json" "$task_dir/result.invalid.json"
    python3 - "$task_dir" "$rc" <<'PYEOF'
import json, sys, datetime
task_dir, rc = sys.argv[1], sys.argv[2]
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump({
  "schema_version": "1.1",
  "task_id": "unknown-infra-failure", "role": "implementer", "runtime": "codex",
  "status": "failed", "scope_change_request": None,
  "summary": "harness invocation failed before the worker produced a result",
  "files_changed": [], "commands_run": [f"codex exec … → exit {rc}"],
  "tests_passed": None, "risks": ["infra-level failure: codex exec exited nonzero with no result.json"],
  "handoff_notes": "", "observations": "",
  "started_at": now, "completed_at": now, "duration_ms": 0,
  "fallback_reason": f"infra: codex exec exit {rc}, no result.json produced"
}, open(f"{task_dir}/result.json", "w"), indent=2)
PYEOF
    # then fill task_id from the contract frontmatter before validating:
    tid=$(awk -F': ' '/^task_id:/{print $2; exit}' "$task_dir/task-contract.md")
    python3 - "$task_dir" "$tid" <<'PYEOF'
import json, sys
d = json.load(open(f"{sys.argv[1]}/result.json")); d["task_id"] = sys.argv[2]
json.dump(d, open(f"{sys.argv[1]}/result.json", "w"), indent=2)
PYEOF
  fi
fi

# 4. validate
python3 "$conductor/contract/check-result.py" "$task_dir/result.json"
```

## Codex-as-commander (documentation only — FT-2)

Running the commander side on Codex means: an AGENTS.md fragment carrying the
L1 doctrine pointer + this forwarder as the dispatch mechanism, with judgment
reservation intact. Codex offers no tool-scoping hardening for the commander
posture — AGENTS.md is a soft constraint. This stays out of acceptance until
flip-trigger FT-2 fires (a real case where CC is unavailable and Codex must
command).

`[unverified: FT-3]` Whether a TOML-defined agent can be spawned by file path
— re-verify against official Codex docs when this adapter is reworked.
