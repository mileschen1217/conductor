---
name: orchestration-mode
description: Use when a task warrants commander-mode dispatch on Claude Code — the orchestrator grades subtasks and routes them to tiered workers through task-contract files. Skip when the L1 entry gate says not-open — run the light path instead.
---

# orchestration-mode — Claude Code adapter

Binds the L1 dispatch primitive's harness step to the Claude Code Agent tool.
**conductor root** — `${CLAUDE_PLUGIN_ROOT}` when installed as a plugin; the
repo checkout root when running from a clone. Every path below resolves
against it. Doctrine lives at `${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md`
(cite, never restate); tier→model resolution lives in `binding.md` beside
this file.

**contract checker** — `python3 ${CLAUDE_PLUGIN_ROOT}/contract/check-result.py <result.json>`;
VALID/exit 0 is the only acceptable worker return.

## Phase 1 — Entry

Evaluate the L1 entry gate (§ Entry gate) and present the call to the human
before any dispatch. Record the decision in `dispatch-plan.md` (§ Audit
surface (dispatch-plan)).

- [ ] dispatch-plan.md exists with an entry decision naming both disqualifiers.

## Phase 2 — Plan the wave

Grade each subtask (§ Complexity tiering), assign a capability tier (§
Capability tiers), resolve the concrete model from `binding.md`, and write
one task-contract file per subtask from
`${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md`. Fill all four dispatch
elements (§ Dispatch contract). Respect the concurrency hard cap
(§ Complexity tiering).

- [ ] Every subtask row in dispatch-plan.md has grade, tier, resolved model, contract path, wave.

## Phase 3 — Dispatch (the harness-bound step)

Per contract file, launch ONE worker with the Agent tool:

- Read-only fan-out (search/research/review lenses): `subagent_type:
  "Explore"` — its toolset has no Write/Edit (§ Single-writer rule — this is
  its CC preventive binding; must appear in the dispatch record).
- Writing work (implementation): `subagent_type: "general-purpose"`, ONE at a
  time (§ Single-writer rule — this is its CC preventive binding).
- Set `model` from binding.md. Worker prompt template (fill both paths):

  > You are a worker under orchestration mode. Read the task contract at
  > `<contract-path>`; it is the single home of your duties — obey its
  > implementer behavioral contract in full and produce its Expected Output
  > into `<task-dir>` (result schema:
  > `${CLAUDE_PLUGIN_ROOT}/contract/task-result.schema.json` — fill as an
  > absolute path). Your final message: one line — the result.json path.

- [ ] Each dispatch record notes agent type (read-only or write-capable), model, contract path.

## Phase 4 — Harvest

Run the contract checker on each result.json. INVALID → apply the L1
escalation ladder (§ Escalation ladder). Non-empty `scope_change_request` →
escalate to the human (§ Judgment reservation). Acceptance of deliverables
goes to a fresh-context worker (§ Verification).

- [ ] Every harvested result: checker exit code recorded; scope-change requests (if any) escalated, not adjudicated.

## Related

- Doctrine: `${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md` — single home of mode behavior.
- Binding: `binding.md` beside this file — tier→model table.
