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

## Advisor check — one line per station (at every `[advisor-check]` item below)

Recognition is the first capability to fail as commander tier drops
(§ Advisor primitive); this adapter makes the check mechanical. Every
`[advisor-check]` station is answered by exactly ONE written line, in the
journal (or dispatch-plan.md when one is rendered):

```
advisor-check: <station> / match(<call site>) | no-match | misfit-but-uncertain / <one-line why>
```

The disposition is read against the five call sites — entry-gate /
grading-dispute / worker-blocked / acceptance-ambiguity /
scope-change-preview (§ Advisor primitive). **match** names its site and
consults. **misfit-but-uncertain** — no site fits AND you are unsure of your
own ruling — **IS a consult trigger.** **no-match** still owes its why.

Preserved semantics (unchanged):

- "The doctrine covers this / deterministic" is a no-match claim, not an
  answer — it still owes its one-line why.
- Consult ≠ escalate: a reserved-set moment (§ Judgment reservation)
  terminates at the HUMAN regardless. Journal line = `judgment_moment` +
  disposition; one consult per `moment_id`.
- Advisor not attached / pairing illegal → `advisor_unavailable` line,
  proceed on own judgment (degradation, never a block).

Worked examples — examples of the FORM, not additional stations:

```
advisor-check: harvest / match(acceptance-ambiguity) / two ACs are satisfied
  by the same artifact and I cannot tell which one it accepts -> consult
advisor-check: entry / misfit-but-uncertain / no call site covers a corpus
  half-frozen mid-run, and I do not trust my own ruling -> consult
advisor-check: entry / no-match / doctrine covers this
  ^ ILLEGAL — a no-match claim standing in for its why. Legal form:
advisor-check: entry / no-match / the declared-mechanical class pre-answers
  this station (§ Entry gate); no topology question is left open
```

## Phase 1 — Entry

Evaluate the L1 entry gate (§ Entry gate) and present the declaration to the
human before any dispatch. The journal is the sole record of record
(§ Audit surface); dispatch-plan.md is an OPTIONAL human-readable render with
no audit standing — a 0-worker run renders none, and a run that upgrades to a
dispatch may render one: optional, never mandatory.

- [ ] journal.jsonl opened in the task directory; FIRST line is `commander_stamp` (self-reported model id + doctrine_rev = the doctrine FILE's own last-change commit, `git -C ${CLAUDE_PLUGIN_ROOT} log -1 --format=%h -- doctrine/orchestration-mode.md`, or — installed plugin, no `.git` — the shipped `${CLAUDE_PLUGIN_ROOT}/doctrine/REV` stamp; NEVER the plugin version or repo HEAD, both of which strand card `graded_under` staleness silently). Include an additive `run_id` field AND the `vocab: 2` stamp — auditors key their dialect on `vocab` (a stamp-less 0.4.0 run is audited visible-LEGACY, § Audit surface).
- [ ] Every journal line carries `ts` (ISO8601 UTC) — drift-window logic keys on timestamps.
- [ ] **Open chain — ONE invocation, before the first task action.** Chain the boot-probe hook and the precedent query in a single command and journal both events from its digest:

  ```bash
  P=${CLAUDE_PLUGIN_ROOT}
  python3 $P/scripts/probe-select.py .conductor/probe.jsonl \
      --harness claude-code --config-hash <hex> --model-gen <gen>; echo "probe-select rc=$?"
  grep -F '"kind": "<declared task kind>"' .conductor/precedent.jsonl | tail -1; echo "precedent-query rc=${PIPESTATUS[0]}"
  ```

  (hash inputs + probe procedure: binding.md § Boot 探針). Probe HIT → journal `probe` event `action:"hit"` citing the row. REPROBE/absent → run the binding's probe procedure, append the new row, journal `action:"probed"|"reprobed"`. ERROR → journal `action:"failed"` + deviation event; brake economics become not-computable (conservative-closed) — entry NEVER blocks on the probe. This chain is deliberately NOT fail-fast — entry never blocks on either leg — so each member echoes its OWN exit code (`${PIPESTATUS[0]}` past a pipe, never the pipeline's): a failed leg is journaled as the failure it was, and no member's status can be swallowed by the one after it. Silence is not a legal reading of a missing rc.
- [ ] `[advisor-check]` BEFORE the entry ruling (entry-gate is a named call site) — pre-answered by the class declaration when the task is declared mechanical (§ Entry gate); pre-answered means the line is still written.
- [ ] Typed `entry` event journaled (§ Audit surface): family (declared from the write surface, § Entry gate) + write_shape + read_breadth + config + grounds; human veto (who/changed-to/why) in the `veto` field when one lands. When the task is declared mechanical (§ Entry gate), the same event carries `class:"mechanical"` and `class_default:"cited"` — or `"overridden(<reason>)"`, whose reason may not be empty (§ Audit surface semantic rule 4).
- [ ] Typed `precedent` event journaled BEFORE the first dispatch, from the open chain's second leg — `cited <run_id>` | `deviation` + reason | `no-match`.
- [ ] **Journal duties (all phases).** Appends are append-only writes: never re-read and never re-print the journal to confirm an append landed — the write either raised or it did not. Script output is consumed as exit code plus the final verdict line; the full output is never re-narrated back into the transcript.

## Phase 2 — Plan the wave

Grade each subtask (§ Complexity tiering), assign a capability tier (§
Capability tiers), and resolve the concrete model from `binding.md`. Author a
task-contract file AT the dispatch decision (§ Dispatch primitive — written
when a worker is about to consume it, not pre-written per subtask): the
instance carries its task-specific fields plus a one-line citation to
`${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md § Implementer behavioral
contract`, never a copy (§ Dispatch contract). Fill all four dispatch
elements; respect the concurrency hard cap (§ Complexity tiering).

- [ ] Every dispatch line carries grade (3 axes) OR a valid card citation (`card:"<role>@<graded_under>"` — check the card's `graded_under` against this run's `commander_stamp.doctrine_rev` and `binding.md`'s current gen-tag first; mismatch = `card:"none(<stale reason>)"` + full grading) plus `why_not_script`, tier, resolved model, contract path, wave.
- [ ] Typed `brake` event journaled BEFORE any offload launches (§ Audit surface computed-term shape): commander-side inputs (C_brief_cmd/C_reread) and per-offload worker-side terms (C_brief_worker/corpus) computed from artifact bytes via `scripts/estimate-tokens.py --anchors <binding anchors>` (values live ONLY in binding.md § 換算錨表 — never restate them here); `boot` from the probe row (`probe_ref` resolvable); `anchor_rev`/`r_rev` cite the binding changelog; W is the ONLY on-the-spot estimate. Economics-fail without a necessity ground = do not launch; probe unavailable ⇒ `verdict:"not-computable"`, necessity grounds only.
- [ ] `[advisor-check]` BEFORE freezing the grade/tier table (grading-dispute).
- [ ] Conditional typed events per trigger (§ Audit surface): `containment_check` (any write-role dispatch), `doubt` (entry/grading disposition ≠ frozen), `deviation` (first deviation event — escalation / scope-change ruling / threshold crossing / advisor-unavailable / estimate-drift / warm-fallback).

## Phase 3 — Dispatch (the harness-bound step)

Per contract file, launch ONE worker with the Agent tool:

- Card-cited dispatch: use the pre-cast agent type from
  `adapters/claude-code/agents/<role>.md` when installed (binding.md § Role
  card 綁定); else fall back to the generic types below with explicit `model:`.
- Read-only fan-out: `subagent_type: "Explore"` (no Write/Edit); writing work:
  `subagent_type: "general-purpose"`, ONE at a time. Both = the CC preventive
  binding of § Single-writer rule; note the type in the dispatch record.
- Journal `dispatch` line additive fields (§ Audit surface, anchor-computed
  where sized): `card`, `brief_tokens_est`, `w_est`, `contract_family`,
  `warm`/`warm_prior` (+`staleness_note` when warm, binding.md § Warm
  channel), `write_surface` — the brake and semantic audits read these.
- **Model param (ST-5 regression point):** every Agent call MUST carry an
  explicit `model:` equal to the binding-resolved model — never rely on the
  default. The SAME resolved id goes into the journal `dispatch` line
  (`resolved_model`) before the call; `audit-model-conformance.py` joins
  journal vs telemetry after the run. Worker prompt template (fill both paths):

  > You are a worker under orchestration mode. Read the task contract at
  > `<contract-path>` for your task-specific duties, and obey the implementer
  > behavioral contract it cites at
  > `${CLAUDE_PLUGIN_ROOT}/contract/task-contract.md § Implementer behavioral
  > contract`; produce its Expected Output into `<task-dir>` (result schema:
  > `${CLAUDE_PLUGIN_ROOT}/contract/task-result.schema.json` — fill as an
  > absolute path). Your final message: one line — the result.json path.

- [ ] Each dispatch record notes agent type (read-only or write-capable), model, contract path.

## Phase 4 — Harvest

Run the contract checker on each result.json that exists — whether a worker
wrote it or the commander persisted a read-only worker's report verbatim
(§ Report contract); per result, not per planned subtask. INVALID → apply the
L1 escalation ladder (§ Escalation ladder). Non-empty `scope_change_request`
→ escalate to the human (§ Judgment reservation). Acceptance routes PER
ACCEPTANCE CRITERION (§ Verification): an AC carrying a runnable,
builder-independent check artifact is accepted by that artifact's execution
— tier-0, no verifier dispatch; an AC carrying none (a taste criterion) goes
to the named fresh-context verifier.

- [ ] `[advisor-check]` at EACH worker report intake (worker-blocked — a blocked/failed/boundary/misfit report is the canonical trigger) and BEFORE each acceptance verdict (acceptance-ambiguity); any scope event → scope-change-preview may inform the framing, the ruling stays the human's.
- [ ] Every harvested result: checker exit code recorded; a `dispatch_result` journal line lands per task (checker verdict + `usage` as the typed ENUM — the harness's in-channel token counts verbatim, or `"unavailable"`; a prose pointer is a semantic VIOLATION — + `reread_tokens_est`); scope-change requests (if any) escalated, not adjudicated.
- [ ] Journal audits are NOT run here — they ride the Phase 5 close chain (one invocation, canonical set). Two rules this phase owns: the vocab-2 dialect is what `audit-judgment-flow.py` will enforce (semantic rules S1-S4), and `audit-model-conformance.py` runs only with a telemetry export — absent telemetry is recorded UNVERIFIABLE, never claimed CLEAN.

## Phase 5 — Close

**Close chain — ONE invocation, after delivery.** Append the run's
`precedent/v1` line to `.conductor/precedent.jsonl` (schema:
`${CLAUDE_PLUGIN_ROOT}/contract/precedent.schema.json`; append on EVERY
terminal — done, failed, blocked), then run the **canonical close audit set**
— this list is the single home; the run report and any acceptance criterion
that names "the close audits" cites it:

```bash
P=${CLAUDE_PLUGIN_ROOT}; J=<journal>; run(){ n="$1"; shift; "$@"; rc=$?; \
  [ $rc -eq 0 ] || { echo "CHAIN-FAIL: $n exit=$rc"; exit $rc; }; }
run judgment-flow  python3 $P/scripts/audit-judgment-flow.py "$J"
run brake-lines    python3 $P/scripts/audit-brake-lines.py "$J" --anchors <binding anchors> --probe .conductor/probe.jsonl
run single-writer  bash    $P/scripts/audit-single-writer.sh "$J"
run reconciliation python3 $P/scripts/audit-artifact-reconciliation.py <task-dir>   # owed iff artifacts exist
run conformance    python3 $P/scripts/audit-model-conformance.py "$J" <telemetry>   # owed iff a telemetry export exists
run run-stats      python3 $P/adapters/claude-code/tools/collect-run-stats.py "$J"
run calibration    python3 $P/scripts/audit-precedent.py --calibration-check .conductor/precedent.jsonl
```

Membership rules, unchanged by the batching:

- **Owed-when members.** Reconciliation runs iff the run produced any
  contract or result artifact — every artifact reconciles to a journal
  `dispatch`/`dispatch_result` or an `aborted-dispatch` deviation, an orphan
  is a FAIL; a pure 0-worker close (zero artifacts) drops that member from
  the chain. Conformance runs iff a telemetry export exists; absent
  telemetry is recorded UNVERIFIABLE (Phase 4), never claimed CLEAN. A
  member dropped for an absent trigger is recorded as such — dropped ≠ run
  ≠ passed.
- **Fail-fast names its member.** The chain stops at the first non-zero and
  reports WHICH member failed with its exit code (`CHAIN-FAIL: <name>
  exit=<rc>`). A bare non-zero is not an acceptable close: batching may not
  hide which check failed.
- **Ordering.** The precedent append comes first, so the calibration check
  sees this run's own line (its trigger counts same-shape runs). The two
  journal appends this chain can produce — `deviation` events for
  `estimate-drift`, and `calibration_notify` — therefore land after the
  precedent line, written from the chain's digest in one append. Nothing is
  dropped: the deviation record is complete at close, and that completeness,
  not the line's position, is what the record is for.

On calibration TRIGGER: append the `calibration/v1 status=proposed` line,
list it in the run report's pending-calibrations section, emit the
promote-pending notification via the binding-named channel, and journal
`calibration_notify`. Promotion/rejection is the human's (§ Precedent & eval
loop) — never auto-promote.

The drift emitter degrades, never blocks close. Its `w_actual_source` is a
proxy (in-channel output count); when the delivered files are on disk,
compute the doctrine-canonical basis (diff bytes through the anchors) with
`scripts/estimate-tokens.py` and journal it in the same event. The tool
writes nothing: the operator constants table is HISTORY (binding.md § User-
level 常數表), byte-identical through close.

- [ ] Close chain run as ONE invocation after delivery; every owed-when member either ran or is recorded as trigger-absent; any failure names its member; precedent line appended; drift + calibration events journaled from the digest (no table rows appended); any TRIGGER surfaced (target = the binding's conversion anchors), not self-ruled.

## Related

- Doctrine: `${CLAUDE_PLUGIN_ROOT}/doctrine/orchestration-mode.md` — single home of mode behavior.
- Binding: `binding.md` beside this file — tier→model table.
