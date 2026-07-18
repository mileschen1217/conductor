---
name: orchestration-mode
description: Use when a task warrants commander-mode dispatch on Claude Code — the orchestrator grades subtasks and routes them to tiered workers through task-contract files. The entry gate outputs a declaration + topology (no refusal branch); the trivial-task form is the 0-worker inline pen.
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

Evaluate the L1 entry gate (§ Entry gate) and present the declaration to the
human before any dispatch. The journal is the sole record of record
(§ Audit surface); dispatch-plan.md is an OPTIONAL human-readable render
with no audit standing.

- [ ] journal.jsonl opened in the task directory; FIRST line is `commander_stamp` (self-reported model id + doctrine_rev = the doctrine FILE's own last-change commit, `git -C ${CLAUDE_PLUGIN_ROOT} log -1 --format=%h -- doctrine/orchestration-mode.md`, or — installed plugin, no `.git` — the shipped `${CLAUDE_PLUGIN_ROOT}/doctrine/REV` stamp. NEVER the plugin version (it can never equal a card's `graded_under` git rev, so staleness always misses and card citation silently dies) and never repo HEAD (moves on every commit, strands cards stale). Include an additive `run_id` field AND the `vocab: 2` stamp — auditors key their dialect on `vocab`, and a 0.4.0 run without it is audited as visible-LEGACY (a stamping duty miss, § Audit surface).
- [ ] Every journal line carries `ts` (ISO8601 UTC) — drift-window logic keys on timestamps.
- [ ] Boot-probe hook: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/probe-select.py .conductor/probe.jsonl --harness claude-code --config-hash <hex> --model-gen <gen>` (hash inputs + probe procedure: binding.md § Boot 探針). HIT → journal `probe` event `action:"hit"` citing the row. REPROBE/absent → run the binding's probe procedure, append the new row, journal `action:"probed"|"reprobed"`. ERROR → journal `action:"failed"` + deviation event; brake economics become not-computable (conservative-closed) — entry NEVER blocks on the probe.
- [ ] `[advisor-check]` BEFORE the entry ruling (entry-gate is a named call site).
- [ ] Typed `entry` event journaled (§ Audit surface): family (declared from the write surface, § Entry gate) + write_shape + read_breadth + config + grounds; human veto (who/changed-to/why) in the `veto` field when one lands.
- [ ] Typed `precedent` event journaled BEFORE the first dispatch: query `.conductor/precedent.jsonl` for the declared task shape — `cited <run_id>` | `deviation` + reason | `no-match`.

## Phase 2 — Plan the wave

Grade each subtask (§ Complexity tiering), assign a capability tier (§
Capability tiers), resolve the concrete model from `binding.md`, and write
one task-contract file per subtask from
`${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md`. Fill all four dispatch
elements (§ Dispatch contract). Respect the concurrency hard cap
(§ Complexity tiering).

- [ ] Every dispatch line carries grade (3 axes) OR a valid card citation (`card:"<role>@<graded_under>"` — check the card's `graded_under` against this run's `commander_stamp.doctrine_rev` and `binding.md`'s current gen-tag first; mismatch = `card:"none(<stale reason>)"` + full grading) plus `why_not_script`, tier, resolved model, contract path, wave.
- [ ] Typed `brake` event journaled BEFORE any offload launches (§ Audit surface computed-term shape): commander-side inputs (C_brief_cmd/C_reread) and per-offload worker-side terms (C_brief_worker/corpus) computed from artifact bytes via `scripts/estimate-tokens.py --anchors <binding anchors>` (values live ONLY in binding.md § 換算錨表 — never restate them here); `boot` from the probe row (`probe_ref` resolvable); `anchor_rev`/`r_rev` cite the binding changelog; W is the ONLY on-the-spot estimate. Economics-fail without a necessity ground = do not launch; probe unavailable ⇒ `verdict:"not-computable"`, necessity grounds only.
- [ ] `[advisor-check]` BEFORE freezing the grade/tier table (grading-dispute).
- [ ] Conditional typed events per trigger (§ Audit surface): `containment_check` (any write-role dispatch), `doubt` (entry/grading disposition ≠ frozen), `deviation` (first deviation event — escalation / scope-change ruling / threshold crossing / advisor-unavailable / estimate-drift / warm-fallback).

## Phase 3 — Dispatch (the harness-bound step)

Per contract file, launch ONE worker with the Agent tool:

- Card-cited dispatch: use the pre-cast agent type from
  `adapters/claude-code/agents/<role>.md` when installed (binding.md § Role
  card 綁定); otherwise fall back to the generic types below with an explicit
  `model:`.
- Read-only fan-out (search/research/review lenses): `subagent_type:
  "Explore"` — its toolset has no Write/Edit (§ Single-writer rule — this is
  its CC preventive binding; must appear in the dispatch record).
- Writing work (implementation): `subagent_type: "general-purpose"`, ONE at a
  time (§ Single-writer rule — this is its CC preventive binding).
- Journal `dispatch` line additive fields: `card` (role@rev or none),
  `brief_tokens_est` (contract+prompt size, anchor-computed), `w_est`
  (expected offloaded output), `contract_family` (stable id shared by
  same-family waves), `warm` + `warm_prior` (warm continuation: binding.md
  § Warm channel; a warm dispatch also carries `staleness_note`),
  `write_surface` (Owned Files digest, or `read-only`) — the brake audit
  and the semantic audit read these.
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
- [ ] Every harvested result: checker exit code recorded; a `dispatch_result` journal line lands per task (checker verdict + `usage` as the typed ENUM — the harness's in-channel token counts verbatim, or `"unavailable"`; a prose pointer is a semantic VIOLATION — + `reread_tokens_est`); scope-change requests (if any) escalated, not adjudicated.
- [ ] Journal audits run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit-judgment-flow.py <journal>` exits 0 (vocab 2 dialect: semantic rules S1-S3 on); `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit-brake-lines.py <journal> --anchors <binding anchors> --probe .conductor/probe.jsonl` exits 0; with a telemetry export also `audit-model-conformance.py <journal> <telemetry>` (absent telemetry = UNVERIFIABLE, recorded, never claimed CLEAN).

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

At precedent-append time, run the estimate-drift emitter (degradation never
blocks close):
`python3 ${CLAUDE_PLUGIN_ROOT}/adapters/claude-code/tools/collect-run-stats.py <journal>`
— journal any `estimate-drift` lines it prints as typed `deviation` events
before appending the precedent line. Its `w_actual_source` is a named proxy
(in-channel output count); the doctrine-canonical drift basis is delivered
diff bytes through the anchors — when the delivered files are on disk,
compute that basis with `scripts/estimate-tokens.py --anchors <binding
anchors>` over them and journal it in the same deviation event. The tool
writes nothing anywhere: the operator constants table is HISTORY (binding.md
§ User-level 常數表) and stays byte-identical through close.

- [ ] Precedent line appended; drift emitter run (its output journaled, no table rows appended anywhere); calibration check run; any TRIGGER surfaced (calibration target = the binding's conversion anchors), not self-ruled.

## Related

- Doctrine: `${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md` — single home of mode behavior.
- Binding: `binding.md` beside this file — tier→model table.
