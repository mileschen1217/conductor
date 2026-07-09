---
name: orchestration-mode
description: Use when a task warrants commander-mode dispatch on Claude Code — the orchestrator grades subtasks and routes them to tiered workers through task-contract files. Skip when the L1 entry gate says not-open (decomposition fully predictable, or task value does not repay the token premium) — run the light path instead.
---

# orchestration-mode — Claude Code adapter

Binds the L1 dispatch primitive's harness step to the Claude Code Agent tool.
Doctrine lives at `doctrine/orchestration-mode.md` (cite, never restate);
tier→model resolution lives in `binding.md` beside this file.

**contract checker** — `python3 contract/check-result.py <result.json>`;
VALID/exit 0 is the only acceptable worker return.

## Phase 1 — Entry

Evaluate the L1 entry gate (§ Entry gate) and present the call to the human
before any dispatch. Record the decision in `dispatch-plan.md` (§ Audit
surface (dispatch-plan)).

- [ ] dispatch-plan.md exists with an entry decision naming both disqualifiers.

## Phase 2 — Plan the wave

Grade each subtask (§ Complexity tiering), assign a capability tier (§
Capability tiers), resolve the concrete model from `binding.md`, and write
one task-contract file per
subtask from `contract/task-contract.md`. Fill all four dispatch elements
(§ Dispatch contract). Respect the concurrency hard cap (5).

- [ ] Every subtask row in dispatch-plan.md has grade, tier, resolved model, contract path, wave.

## Phase 3 — Dispatch (the harness-bound step)

Per contract file, launch ONE worker with the Agent tool:

- Read-only fan-out (search/research/review lenses): `subagent_type:
  "Explore"` — its toolset has no Write/Edit (this read-only declaration is
  the run's preventive single-writer enforcement; it must appear in the
  dispatch record).
- Writing work (implementation): `subagent_type: "general-purpose"`, ONE at a
  time — never two write-capable workers concurrently.
- Set `model` from binding.md. Worker prompt template (fill both paths):

  > You are a worker under orchestration mode. Read the task contract at
  > `<contract-path>` and obey its implementer behavioral contract. Do the
  > work within Scope only. Write `result.json` (schema:
  > `contract/task-result.schema.json`, schema_version "1.1") into
  > `<task-dir>`, recording every command you ran with its exit code in
  > commands_run. If the contracted Commands to Run fail, still write a
  > schema-valid result.json — status "failed", risks and/or fallback_reason
  > filled — never crash, never leave no artifact. Your final message: one
  > line — the result.json path.

- [ ] Each dispatch record notes agent type (read-only or write-capable), model, contract path.

## Phase 4 — Harvest

Run the contract checker on each result.json. INVALID → do not trust the
output; apply the L1 escalation ladder (§ Escalation ladder) — never
hand-patch fields. Non-empty `scope_change_request` → stop that line,
escalate to the human verbatim (§ Judgment reservation). Acceptance of
deliverables goes to a fresh-context worker, never the builder (§ Verification).

- [ ] Every harvested result: checker exit code recorded; scope-change requests (if any) escalated, not adjudicated.

## Related

- Doctrine: `doctrine/orchestration-mode.md` — single home of mode behavior.
- Binding: `adapters/claude-code/binding.md` — tier→model table.
