---
name: orchestration-mode
description: Use when a task warrants commander-mode dispatch on Claude Code — the orchestrator grades subtasks and routes them to tiered workers through task-contract files. Entry economics and instrumentation arming are doctrine RT-1 and RT-9; this adapter binds them to the Agent tool.
---

# orchestration-mode — Claude Code adapter

Binds the doctrine's one harness-bound step — starting a worker — to the
Claude Code Agent tool. Doctrine is cited, never restated:
`${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md` (roots RT-1..RT-10,
application slab, definitions). Tier→model resolution: `binding.md` beside
this file. Judgment stations and the one-line answer form: doctrine
§ Definitions — judgment stations / the judgment line.

## Harness facts

| fact | value |
|---|---|
| conductor root | `${CLAUDE_PLUGIN_ROOT}` when installed as a plugin. Running from a clone leaves it UNSET: substitute the checkout root into every path here before use, and never execute a command with it unexpanded — an unset expansion yields a broken `/contract/...` path. |
| contract checker | `python3 ${CLAUDE_PLUGIN_ROOT}/contract/check-result.py <result.json>` — VALID / exit 0 is the only acceptable worker return. |
| instrumentation switch | `[ -f .conductor-instrumented ]` (carrier: `binding.md` § Instrumentation switch; rules: doctrine RT-9 + RT-9 @ switch-writer) |
| `doctrine_rev` | the last-change commit across the declared manifest (command below). Installed as a plugin there is no `.git`: read the shipped `${CLAUDE_PLUGIN_ROOT}/doctrine/REV`. Never the plugin version and never repo HEAD — neither equals a card's `graded_under`, so staleness checks silently never fire. |
| script exit codes | read `rc` on the line after the command — never through a pipe, never from `${PIPESTATUS[...]}`, which expands to empty under zsh. |
| journal writes | append-only: never re-read or re-print the journal to confirm an append landed; consume script output as exit code plus final verdict line. |
| brake on an unarmed run | qualitative and out loud: no probe is read and the boot term is not priced (accepted deviation — the 2026-07-27 mode-at-first-dispatch spec § Risks, "ordinary-run brake is qualitative"). |

```bash
git -C ${CLAUDE_PLUGIN_ROOT} log -1 --format=%h \
    -- $(grep -vE '^\s*(#|$)' ${CLAUDE_PLUGIN_ROOT}/scripts/run-obeyed.manifest)
```

## Dispatch mechanics (the Agent tool)

- Read-only fan-out: `subagent_type: "Explore"` (no Write/Edit tools), any
  number in parallel. Writing work: `subagent_type: "general-purpose"`, ONE
  write-capable worker at a time per surface — the preventive half of RT-6,
  bound here; the recorded half is RT-6 @ dispatch-record.
- Card-cited dispatch: use the pre-cast agent type from
  `adapters/claude-code/agents/<role>.md` when installed (`binding.md` § Role
  card 綁定); else a generic type.
- Every Agent call carries an explicit `model:` equal to the binding-resolved
  model. Never rely on the default.
- Worker prompt (fill both paths):

  > You are a worker under orchestration mode. Read the task contract at
  > `<contract-path>` for your task-specific duties, and obey the implementer
  > behavioral contract it cites at
  > `${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md § Implementer behavioral
  > contract`; produce its Expected Output into `<task-dir>` (result schema:
  > `${CLAUDE_PLUGIN_ROOT}/contract/task-result.schema.json` — fill as an
  > absolute path). Your final message: one line — the result.json path.

## Ordering principles

Three orderings are load-bearing on this harness; everything else follows the
doctrine's moments.

1. The task-contract file is written, complete, before the Agent call that
   consumes it. Name it `task-contract.md` (or `task-contract-<suffix>.md`);
   the result is `result.json` (RT-5 @ artifact-naming).
2. The switch is read once, at the moment a worker is actually about to
   start, and the answer is latched for the run (RT-9 @ switch).
3. Close runs once, after delivery, as ONE invocation of the close tool —
   never hand-rolled inline, never re-run without the missing evidence.

## Instrumentation

One principle: on an armed run (RT-9), instrumentation adds exactly three
things — the journal (per `contract/journal-event.schema.json`, the single
home of events, required fields and the owed-when map), the
execution-telemetry export the close chain's conformance member joins against
(`binding.md` § Offered surfaces — without it that member fails, because the
evidence a chosen measurement depends on is owed), and the boot probe.
Nothing else changes. The **[instrumented]** command table:

| when | command / artifact |
|---|---|
| journal open (first line) | `.conductor/runs/<run-slug>/journal.jsonl` — `commander_stamp`: self-reported model id, `doctrine_rev` (see Harness facts), `model_gen` from `binding.md`, `vocab: 3`, additive `run_id`. Every line carries `ts` (ISO8601 UTC). |
| before the first dispatch | boot probe, one invocation: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/probe-select.py" .conductor/probe.jsonl --harness claude-code --config-hash <hex> --model-gen <gen>` then `rc=$?; echo "probe-select rc=$rc"`. HIT → journal `probe` `action:"hit"` citing the row; REPROBE or absent → run the binding's procedure, append, journal `"probed"` or `"reprobed"`; ERROR → journal `"failed"` plus a deviation. Nothing blocks on the probe. Hash inputs: `binding.md` § Boot 探針. |
| telemetry | arrange the export before dispatching. |
| brake terms | computed via `scripts/estimate-tokens.py --anchors <binding anchors>`; `boot` from the probe row; `anchor_rev`/`r_rev` cite the binding changelog. |
| close, once, after delivery | `bash "${CLAUDE_PLUGIN_ROOT}/adapters/claude-code/tools/close-chain.sh" --journal <journal> --task-dir <task-dir> --anchors <binding anchors> [--probe .conductor/probe.jsonl] [--telemetry <telemetry>]` — journal the `close` event from its `close-members:` output with the run's `terminal`. This closes the journal. |
| drift emitter | degrades, never blocks close. Its `w_actual_source` is a proxy; when the delivered files are on disk, compute the canonical basis with `scripts/estimate-tokens.py` and journal it in the same event. |
