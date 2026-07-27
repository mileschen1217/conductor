---
name: orchestration-mode
description: Use when a task warrants commander-mode dispatch on Claude Code — the orchestrator grades subtasks and routes them to tiered workers through task-contract files. The mode is paid for at the first dispatch decision: a run that never delegates creates nothing, and an ordinary dispatch run pays only contract + result + checker. Self-audit ceremony is instrumentation, switched on by a named trigger.
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

## Phase 0 — is this run in the mode at all?

**Do nothing here.** There is no opening ceremony, because the mode begins at
the first dispatch decision (§ Entry gate). Work the task normally. The moment
you are about to hand a piece of work to a separate context, go to Phase 1.

- [ ] A run that never reaches a dispatch decision writes NOTHING under
  `.conductor/` — no journal, no declaration, no probe read, no contract, no
  result. Not an empty file, not a "for the record" note. Zero artifacts is
  the observable this form is defined by.
- [ ] Reaching a dispatch decision and answering "no, I'll do it inline" is a
  legal answer and still costs nothing.
- [ ] Entry mid-run is forward-only (§ Entry gate): the mode starts at that
  moment. Never backfill a record of the inline stretch that preceded it.

## Phase 1 — the first dispatch decision (entry)

Evaluate the L1 entry gate (§ Entry gate) and present the declaration to the
human. Then decide, ONCE, whether this run is instrumented.

- [ ] **Instrumentation check (§ Audit surface trigger enum).** This run is
  instrumented iff one of: (a) it is a benchmark arm; (b) the human asked for
  one. Both are deliberate — no run becomes instrumented by itself. Otherwise
  the run is uninstrumented: skip every bracketed **[instrumented]** step
  below. Uninstrumented is the default and the common case.
- [ ] **[instrumented] Telemetry is owed, not optional.** Someone chose to
  measure this run, so arrange the execution-telemetry export the close chain's
  conformance member joins against (binding.md § Offered surfaces). Without it
  that member FAILS and the close reads red — by design, not by accident.
- [ ] **[instrumented] Open the journal** at `.conductor/runs/<run-slug>/journal.jsonl`.
  FIRST line is `commander_stamp` (self-reported model id + `doctrine_rev` =
  the doctrine FILE's own last-change commit,
  `git -C ${CLAUDE_PLUGIN_ROOT} log -1 --format=%h -- doctrine/orchestration-mode.md`,
  or — installed plugin, no `.git` — the shipped `${CLAUDE_PLUGIN_ROOT}/doctrine/REV`
  stamp; NEVER the plugin version or repo HEAD, both of which strand card
  `graded_under` staleness silently) + `model_gen` from binding.md + the
  `vocab: 3` stamp + an additive `run_id`. Every line carries `ts` (ISO8601
  UTC). A journal without the stamp FAILS every audit — there is no legacy
  dialect left to fall back to.
- [ ] **[instrumented] Boot probe**, one invocation, before the first dispatch:

  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/probe-select.py" .conductor/probe.jsonl \
      --harness claude-code --config-hash <hex> --model-gen <gen>
  rc=$?; echo "probe-select rc=$rc"
  ```

  Read the rc on the line after the command, never through a pipe and never
  from `${PIPESTATUS[...]}` — that is a bash-ism which expands to empty under
  zsh, and a silently-empty rc has cost this project three runs. (Hash inputs
  + probe procedure: binding.md § Boot 探針.) HIT → journal `probe` event
  `action:"hit"` citing the row. REPROBE/absent → run the binding's probe
  procedure, append the new row, journal `action:"probed"|"reprobed"`. ERROR →
  journal `action:"failed"` + a deviation event; brake economics become
  not-computable (conservative-closed). Entry NEVER blocks on the probe.
- [ ] `[judgment-check]` BEFORE the entry ruling (see § Judgment check below)
  — pre-answered by the class declaration when the task is declared mechanical
  (§ Entry gate); pre-answered means the line is still written.
- [ ] **[instrumented] Typed `entry` event journaled** (§ Audit surface):
  family (declared from the write surface) + write_shape + read_breadth +
  config + grounds; human veto (who/changed-to/why) in the `veto` field when
  one lands. When the task is declared mechanical, the same event carries
  `class:"mechanical"` and `class_default:"cited"` — or `"overridden(<reason>)"`,
  whose reason may not be empty (§ Audit surface semantic rule S4).
- [ ] **[instrumented] Journal duties (all phases).** Appends are append-only
  writes: never re-read and never re-print the journal to confirm an append
  landed — the write either raised or it did not. Script output is consumed as
  exit code plus the final verdict line; the full output is never re-narrated
  back into the transcript.

On an uninstrumented run the gate's questions are still answered — in-session,
out loud, where they are asked. They are simply not written down.

## Phase 2 — plan the wave

Grade each subtask (§ Complexity tiering), assign a capability tier (§
Capability tiers), and resolve the concrete model from `binding.md` (worker
tier default and the haiku admissibility conditions live there). Author a
task-contract file AT the dispatch decision (§ Dispatch primitive — written
when a worker is about to consume it, not pre-written per subtask): the
instance carries its task-specific fields plus a one-line citation to
`${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md § Implementer behavioral
contract`, never a copy (§ Dispatch contract). Fill all four dispatch
elements; respect the concurrency hard cap (§ Complexity tiering). Name the
contract file `task-contract.md` (or `task-contract-<suffix>.md`) and the
result `result.json` — the convention is contractual, and reconciliation pairs
on it in both directions.

- [ ] Apply the brake (§ Amortization brake) to every offload. On an
  uninstrumented run this is a qualitative judgment made out loud: nothing is
  computed, no probe is read, and the boot term is not priced. The launch rule
  still binds — an economics-failing dispatch launches only on a named
  necessity ground from the four-ground enum (`wall-clock`, `corpus`,
  `disjoint-write`, `verification-mandated`).
- [ ] **[instrumented] Typed `brake` event journaled BEFORE any offload
  launches** (§ Audit surface computed-term shape): commander-side inputs
  (C_brief_cmd/C_reread) and per-offload worker-side terms
  (C_brief_worker/corpus) computed from artifact bytes via
  `scripts/estimate-tokens.py --anchors <binding anchors>` (values live ONLY in
  binding.md § 換算錨表 — never restate them here); `boot` from the probe row
  (`probe_ref` resolvable); `anchor_rev`/`r_rev` cite the binding changelog; W
  is the ONLY on-the-spot estimate. Economics-fail without a necessity ground =
  do not launch; probe unavailable ⇒ `verdict:"not-computable"`.
- [ ] **[instrumented] Every dispatch line carries** grade (3 axes) OR a valid
  card citation (`card:"<role>@<graded_under>"` — check the card's
  `graded_under` against this run's `commander_stamp.doctrine_rev` and
  `binding.md`'s current gen-tag first; mismatch = `card:"none(<stale reason>)"`
  + full grading) plus `why_not_script`, tier, resolved model, contract path,
  wave.
- [ ] `[judgment-check]` BEFORE freezing the grade/tier table (grading-dispute).

## Phase 3 — dispatch (the harness-bound step)

Per contract file, launch ONE worker with the Agent tool:

- Card-cited dispatch: use the pre-cast agent type from
  `adapters/claude-code/agents/<role>.md` when installed (binding.md § Role
  card 綁定); else fall back to the generic types below with explicit `model:`.
- **Preventive single-writer enforcement — mandatory on EVERY dispatch run,
  instrumented or not** (§ Single-writer rule). Read-only fan-out:
  `subagent_type: "Explore"` (no Write/Edit tools), any number in parallel.
  Writing work: `subagent_type: "general-purpose"`, **ONE write-capable worker
  at a time**. This is the leg that actually prevents the damage; it is
  procedure, not paperwork, and it does not depend on a journal existing.
- **Model param (ST-5 regression point):** every Agent call MUST carry an
  explicit `model:` equal to the binding-resolved model — never rely on the
  default. Worker prompt template (fill both paths):

  > You are a worker under orchestration mode. Read the task contract at
  > `<contract-path>` for your task-specific duties, and obey the implementer
  > behavioral contract it cites at
  > `${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md § Implementer behavioral
  > contract`; produce its Expected Output into `<task-dir>` (result schema:
  > `${CLAUDE_PLUGIN_ROOT}/contract/task-result.schema.json` — fill as an
  > absolute path). Your final message: one line — the result.json path.

- [ ] **[instrumented] Dispatch record fields** (§ Audit surface, anchor-computed
  where sized): `task_id`, `tier`, `resolved_model` (the SAME id passed to the
  Agent call — `audit-model-conformance.py` joins journal vs telemetry after
  the run), **`read_only`** (literally this key: `true` for the read-only agent
  type, `false` for a write-capable one — `audit-single-writer.sh` hard-requires
  it and a dispatch line without it is MALFORMED), `wave`, `contract`, `card`,
  `brief_tokens_est`, `w_est`, `contract_family`, `write_surface`, plus the two
  folded judgment fields: `containment` on every write-role dispatch, and
  `doubt` on the dispatch of an entry/grading moment whose disposition was not
  `frozen`.

## Phase 4 — harvest

Run the contract checker on each result.json that exists — whether a worker
wrote it or the commander persisted a read-only worker's report verbatim
(§ Report contract); per result, not per planned subtask. INVALID → apply the
L1 escalation ladder (§ Escalation ladder). Non-empty `scope_change_request`
→ escalate to the human (§ Judgment reservation). Acceptance routes PER
ACCEPTANCE CRITERION (§ Verification): an AC carrying a runnable,
builder-independent check artifact is accepted by that artifact's execution
— tier-0, no verifier dispatch; an AC carrying none (a taste criterion) goes
to the named fresh-context verifier, whose brake ground is
`verification-mandated`.

- [ ] `[judgment-check]` at EACH worker report intake (worker-blocked — a
  blocked/failed/boundary/misfit report is the canonical trigger) and BEFORE
  each acceptance verdict (acceptance-ambiguity); any scope event →
  scope-change-preview may inform the framing, the ruling stays the human's.
- [ ] Every harvested result: checker exit code recorded. **[instrumented]** a
  `dispatch_result` journal line lands per task (checker verdict + `usage` as
  the typed ENUM — the harness's in-channel token counts verbatim, or
  `"unavailable"`; a prose pointer is a semantic VIOLATION — + `reread_tokens_est`).
- [ ] Audits are NOT run here — they ride the Phase 5 close chain.

## Phase 5 — close

**[instrumented] only.** An uninstrumented run has no journal, so it has no
close chain: the deliverable and version control are its record. Delivery
happens the same way on both.

**The close chain is ONE invocation of ONE script**, which is the single home
of the canonical member set and its order — cite it, never re-enumerate it:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/adapters/claude-code/tools/close-chain.sh" \
    --journal <journal> --task-dir <task-dir> \
    --anchors <binding anchors> [--probe .conductor/probe.jsonl] [--telemetry <telemetry>]
```

The script runs every member, records each as `pass` / `fail(<rc>)` /
`dropped(trigger-absent)`, names any failing member with its exit code, and
prints the `close-members:` JSON array. It is executed under
whatever shell the operator is running and is covered by a cross-shell
portability suite (`scripts/test-close-chain.sh`) — do not hand-roll the chain
inline, and never read a member's exit code through `${PIPESTATUS[...]}`.

- [ ] Close chain run as ONE invocation after delivery; the `close` event
  journaled from its `close-members:` output, with the run's `terminal`
  (`done|failed|blocked`). This event closes the journal.
- [ ] A member that ran and could not conclude for want of evidence is a
  `fail`, not a pass — see § Audit surface. Do not re-run the chain without
  the missing evidence and report the second result.
- [ ] The drift emitter degrades, never blocks close. Its `w_actual_source` is
  a proxy (in-channel output count); when the delivered files are on disk,
  compute the doctrine-canonical basis (diff bytes through the anchors) with
  `scripts/estimate-tokens.py` and journal it in the same event.

## Judgment check — one line per station

Recognition is the first capability to fail as commander tier drops
(§ Judgment moments); this adapter makes the check mechanical. Every
`[judgment-check]` station is answered by exactly ONE written line:

```
judgment-check: <station> / match(<call site>) | no-match | misfit-but-uncertain / <one-line why>
```

The disposition is read against the five call sites — entry-gate /
grading-dispute / worker-blocked / acceptance-ambiguity /
scope-change-preview. **match** names its site and **surfaces the moment to
the human**: state the moment and your own ruling in-channel and PROCEED —
surfacing is a disclosure, not a request for permission, and it never blocks.
**misfit-but-uncertain** — no site fits AND you are unsure of your own ruling
— **IS a surface trigger.** **no-match** still owes its why.

Preserved semantics:

- "The doctrine covers this / deterministic" is a no-match claim, not an
  answer — it still owes its one-line why.
- Surfacing ≠ escalating: a reserved-set moment (§ Judgment reservation)
  terminates at the HUMAN regardless of how this station answered.
- **[instrumented]** the line rides a `judgment_moment` event (`check` field +
  `disposition`); the answer→disposition mapping and the duties a `blocked`
  disposition carries are § Judgment moments' — read them there. On an
  uninstrumented run the station is exercised and not recorded.

Worked examples — examples of the FORM, not additional stations:

```
judgment-check: harvest / match(acceptance-ambiguity) / two ACs are satisfied
  by the same artifact and I cannot tell which one it accepts -> surface
judgment-check: entry / misfit-but-uncertain / no call site covers a corpus
  half-frozen mid-run, and I do not trust my own ruling -> surface
judgment-check: entry / no-match / doctrine covers this
  ^ ILLEGAL — a no-match claim standing in for its why. Legal form:
judgment-check: entry / no-match / the declared-mechanical class pre-answers
  this station (§ Entry gate); no topology question is left open
```

## Related

- Doctrine: `${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md` — single home of mode behavior.
- Binding: `binding.md` beside this file — tier→model table, anchors, probe.
