---
name: orchestration-mode
description: Use when a task warrants commander-mode dispatch on Claude Code — the orchestrator grades subtasks and routes them to tiered workers through task-contract files. Skip when the L1 entry gate says not-open — run the light path instead.
---

# orchestration-mode — Claude Code adapter

Binds the L1 dispatch primitive's harness step to the Claude Code Agent tool.
**conductor root** — `${CLAUDE_PLUGIN_ROOT}` when installed as a plugin
(substituted automatically); when running from a clone the variable is UNSET —
you (the commander) substitute the checkout root into every path below before
using it, and never execute a command with the variable unexpanded (an unset
expansion yields a broken `/contract/...` path). Doctrine lives at
`${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md`
(cite, never restate); tier→model resolution lives in `binding.md` beside
this file.

**contract checker** — `python3 ${CLAUDE_PLUGIN_ROOT}/contract/check-result.py <result.json>`;
VALID/exit 0 is the only acceptable worker return.

## Advisor check — forced enumeration (at every `[advisor-check]` item below)

The doctrine's advisor protocol fires on RECOGNIZED judgment moments
(§ Advisor primitive) — and recognition is the first capability to fail as
commander tier drops. This adapter therefore does not ask you to recognize;
it makes the check mechanical. At each `[advisor-check]`, WRITE DOWN (in
dispatch-plan.md or the journal, one line) your answer to:

> Should I ask the advisor before this step? Test against the five call
> sites — entry-gate / grading-dispute / worker-blocked /
> acceptance-ambiguity / scope-change-preview (semantics: § Advisor
> primitive): **match** (name it → consult), **no-match** (one line saying
> why), or **misfit-but-uncertain** — no site fits AND I am not sure of my
> own ruling. **Misfit-but-uncertain IS a consult trigger, not an
> exemption.**

- "The doctrine covers this / this is deterministic" is not an answer by
  itself — that is a no-match claim and still owes its one-line why.
- Consult ≠ escalate: a moment in the reserved set (§ Judgment reservation)
  terminates at the HUMAN whether or not you consulted first.
- Vocabulary: the operational word here is *advisor*; the journal line it
  lands as is `judgment_moment` + disposition (§ Advisor primitive). One
  consult per `moment_id`.
- Advisor not attached / pairing illegal → `advisor_unavailable` line,
  proceed on your own judgment (degradation, never a block).

## Phase 1 — Entry

Evaluate the L1 entry gate (§ Entry gate) and present the call to the human
before any dispatch. Record the decision in `dispatch-plan.md` (§ Audit
surface).

- [ ] journal.jsonl opened in the task directory; FIRST line is `commander_stamp` (self-reported model id + doctrine_rev via `git -C ${CLAUDE_PLUGIN_ROOT} rev-parse --short HEAD` or the installed release stamp).
- [ ] `[advisor-check]` BEFORE the entry ruling (entry-gate is a named call site).
- [ ] dispatch-plan.md exists with the entry decision (write shape + execution config + named grounds), the `task-shape:` line, and the `precedent:` line (query `.conductor/precedent.jsonl` first — cite or deviate; § Precedent & eval loop).

## Phase 2 — Plan the wave

Grade each subtask (§ Complexity tiering), assign a capability tier (§
Capability tiers), resolve the concrete model from `binding.md`, and write
one task-contract file per subtask from
`${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md`. Fill all four dispatch
elements (§ Dispatch contract). Respect the concurrency hard cap
(§ Complexity tiering).

- [ ] Every subtask row in dispatch-plan.md has grade, tier, resolved model, contract path, wave.
- [ ] `[advisor-check]` BEFORE freezing the grade/tier table (grading-dispute).
- [ ] dispatch-plan.md carries per-subtask `why-not-a-script`, the containment-check line, and doubt-surfacing (§ Audit surface).

## Phase 3 — Dispatch (the harness-bound step)

Per contract file, launch ONE worker with the Agent tool:

- Read-only fan-out (search/research/review lenses): `subagent_type:
  "Explore"` — its toolset has no Write/Edit (§ Single-writer rule — this is
  its CC preventive binding; must appear in the dispatch record).
- Writing work (implementation): `subagent_type: "general-purpose"`, ONE at a
  time (§ Single-writer rule — this is its CC preventive binding).
- **Model param (ST-5 regression point):** every Agent call MUST carry an
  explicit `model:` equal to the binding-resolved model — never rely on the
  default. The SAME resolved id goes into the journal `dispatch` line
  (`resolved_model`) before the call; `audit-model-conformance.py` joins
  journal vs telemetry after the run. Worker prompt template (fill both paths):

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

- [ ] `[advisor-check]` at EACH worker report intake (worker-blocked — a blocked/failed/boundary/misfit report is the canonical trigger) and BEFORE each acceptance verdict (acceptance-ambiguity); any scope event → scope-change-preview may inform the framing, the ruling stays the human's.
- [ ] Every harvested result: checker exit code recorded; scope-change requests (if any) escalated, not adjudicated.
- [ ] Journal audits run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit-judgment-flow.py <journal>` exits 0; with a telemetry export also `audit-model-conformance.py <journal> <telemetry>` (absent telemetry = UNVERIFIABLE, recorded, never claimed CLEAN).

## Phase 5 — Close

Append the run's `precedent/v1` line to `.conductor/precedent.jsonl` (schema:
`${CLAUDE_PLUGIN_ROOT}/contract/precedent.schema.json`; append on EVERY
terminal — done, failed, blocked). Run the calibration trigger check:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit-precedent.py --calibration-check .conductor/precedent.jsonl`.
On TRIGGER: append the `calibration/v1 status=proposed` line, list it in the
run report's pending-calibrations section, emit the promote-pending
notification via the binding-named channel, and journal `calibration_notify`.
Promotion/rejection is the human's (§ Precedent & eval loop) — never
auto-promote.

- [ ] Precedent line appended; calibration check run; any TRIGGER surfaced, not self-ruled.

## Related

- Doctrine: `${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md` — single home of mode behavior.
- Binding: `binding.md` beside this file — tier→model table.
