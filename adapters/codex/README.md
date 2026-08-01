# orchestration-mode — Codex adapter

Binds the L1 dispatch primitive's harness step to `codex exec` (non-interactive).
Doctrine is cited, never restated. Tier→model: `binding.md` beside this file.

Scope: doctrine RT-1. The forwarder recipe is the always-on part: contract in,
result out, checker verdict.
Self-audit ceremony applies only to a run an operator armed (RT-9 @ switch;
carrier in `binding.md` § Instrumentation switch).

## Verification record

No `verified-run:` lines yet — no benchmark cell has been executed through this
adapter (procedure: `benchmark/protocol.md`). A verification record is not a
capability claim.

## AGENTS.md load fragment (worker side)

Paste into the task workspace's AGENTS.md:

```markdown
## orchestration-mode worker contract
You may be dispatched as an orchestration-mode worker. When your prompt names
a task-contract file: read it for your task-specific duties, and obey the
implementer behavioral contract it cites at
`$conductor/contract/task-contract.md § Implementer behavioral contract`;
produce its Expected Output into the task directory (result schema path given
in your prompt).
```

## Preventive single-writer enforcement (doctrine RT-6, bound to this harness's sandbox flag)

- Read-only fan-out: `--sandbox read-only`. Any number in parallel.
- Write-capable work: `--sandbox workspace-write`, ONE worker at a time per
  write surface.
- The sandbox value actually passed is what an instrumented run records as the
  dispatch line's `read_only` field (`read-only` → `true`).

## Thin-forwarder recipe (dispatch primitive, middle step)

Inputs: `$task_dir` containing `task-contract.md` (RT-5 @ artifact-naming); `$model` from
`binding.md`; `$sandbox` per the rule above; `$conductor` = conductor repo root.

```bash
# 1. probe — CLI absent is NOT a task failure; it is adapter-unavailable:
#    report unavailable + fallback_reason upstream; portability ACs go blocked.
command -v codex >/dev/null || { echo "codex-unavailable"; exit 3; }

# 2. dispatch. stdin MUST be /dev/null: codex exec waits on stdin non-interactively
codex exec \
  --cd "$task_dir" \
  --sandbox "$sandbox" \
  -m "$model" \
  "You are a worker under orchestration mode. Read ./task-contract.md for your task-specific duties, and obey the implementer behavioral contract it cites at $conductor/contract/task-contract.md § Implementer behavioral contract; produce its Expected Output into this directory (result schema: $conductor/contract/task-result.schema.json). Final output: the single line RESULT: ./result.json" < /dev/null
rc=$?

# 3. infra-failure fallback (codex exec died, or no/empty/invalid result.json):
#    synthesize a schema-valid failure via the L2-owned generator; any existing
#    invalid file is preserved.
if [ $rc -ne 0 ]; then
  if ! python3 "$conductor/contract/check-result.py" "$task_dir/result.json" >/dev/null 2>&1; then
    [ -f "$task_dir/result.json" ] && mv "$task_dir/result.json" "$task_dir/result.invalid.json"
    python3 "$conductor/contract/make-fallback-result.py" "$task_dir" codex \
      "infra: codex exec exit $rc, no usable result.json"
  fi
fi

# 4. validate
python3 "$conductor/contract/check-result.py" "$task_dir/result.json"
```

## Codex-as-commander (documentation only — FT-2)

An AGENTS.md fragment carrying the L1 doctrine pointer plus the forwarder above
as the dispatch mechanism, with judgment reservation intact. Codex offers no
tool-scoping hardening for the commander posture, so AGENTS.md is a soft
constraint. This stays out of acceptance until FT-2 fires.

An FT-2 rework SHALL import the commander stations landed for the other adapter
meanwhile — verify-locus routing, the mechanical judgment-check form, the switch
read at the first actual dispatch, and the single-invocation close chain — rather
than re-deriving them.

`[unverified: FT-3]` Whether a TOML-defined agent can be spawned by file path.
