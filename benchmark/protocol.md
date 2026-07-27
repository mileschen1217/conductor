# Benchmark protocol — comparative acceptance procedures

One-shot comparative acceptance procedures (NOT standing eval infrastructure).
Human-governed: the human selects the task, adjudicates quality, and rules
pass/fail — this protocol contains NO automatic pass logic.

**How to read this file.** Sections below marked **[historical — ran under
<revision>]** describe protocols that already executed. They are kept in the
vocabulary of the doctrine revision they ran under, because a record rewritten
to match current vocabulary is no longer a record of what happened. Only the
unmarked sections — § Isolation invariants, § Ceremony-replay method,
§ Ledger, § Quality rubric, § Acceptance-judge instruction — are live
procedure for a new run.

Vocabulary note for every historical section: they predate the
pay-at-first-dispatch cut (0.7.0), so they speak of a "0-worker form" — a run
that entered the mode and paid its ceremony without dispatching anything.
That form no longer exists: a run that never dispatches is not in the mode.
The measurements those sections report remain valid measurements OF that
form.

## Task selection (human)

Criteria (all required): a real repo; the task spans ≥3 files; subtasks are
heterogeneous; quality is decidable by tests and/or severity-graded review.
The selection (task, repo, why it meets each criterion) is recorded in the
run ledger entry (`task_ref`).

## Matrix (v2) **[historical — ran under the v2 revision, 2026-07-12/13]**

Commander models (4, human-confirmable at R1): fable / opus / sonnet / haiku
(CC binding table 2026-07-11). Cells: 4 commander models × {inline, v2-form}
plus ONE bare-inline ablation cell = **9 cells / 9 ledger rows**.

- **matrix inline cell** = the v2 "0-worker form": journal + entry-gate
  declaration, pen stays with the commander; contract/result artifacts
  produced only when a second context consumed them. (Under the current
  revision this cell is not constructible — an undelegated run does not enter
  the mode at all.)
- **v2-form cell** = topology per the entry gate's own output for the task.
- **bare-inline ablation cell** (the 9th): prompt-only, NO mode machinery, on
  the mid-tier commander model (sonnet — the tier the gate's refusal
  threshold serves).

**Ablation pair (discipline unit price):** the 9th cell vs the matrix's own
mid-tier inline cell (REUSED, not rerun). The ledger records, as separate
fields on the ablation ruling row: `discipline_unit_price_usd` (cost delta)
and `quality_delta` (what mechanical acceptance caught that bare inline
missed) — never folded into topology comparisons.

**Staged execution:** inline row first (4 cells), then v2-form row, ablation
cell last. Cell 2 (opus-inline) may reuse the 2026-07-10 ledger data ONLY if
the task is identical to v1's; else rerun (+cost accepted). Every completed
cell appended one ledger row (and, under that revision, one line to the
per-project precedent ledger — a mechanism since removed).

**Adjudication:** the commander-vs-inline face is human-ruled per cell pair
by the R3 formula (quality not-worse AND cost lower — § Quality rubric).
This protocol still contains NO automatic pass logic.

**Model pinning is verified, never assumed (standing rule):**
operator-level configuration can silently re-pin dispatched workers — the
2026-07-12 incident: a forgotten `CLAUDE_CODE_SUBAGENT_MODEL` env override
in the operator's settings pinned every worker to the mid tier regardless
of the requested model; the M8 conformance audit caught it
(smoke/ac-14 — planned-vs-actual VIOLATION), root-caused to config, fixed
by removing the override + session restart. Therefore: (1) every cell's
models are verified post-run by `audit-model-conformance.py`
(journal × telemetry), never assumed from the plan; (2) the R1 human
ruling confirms the reachable cell set against the CURRENT session's
verified dispatch behavior (one probe dispatch per distinct model before
the matrix starts); (3) any planned-vs-actual mismatch voids the cell's
tier claim, whatever its cause.

## Isolation invariants (all five hold per cell; violation voids the arm)

1. **Worktree per arm** — each cell runs in its own worktree; no shared
   working tree between arms.
2. **Shared contract names no directory** — the task contract binds Scope by
   EXACTLY declaration (the explicit deliverable set) plus a sibling
   do-not-touch (DNT) declaration; it never names another arm's directory.
3. **Byte-identical fresh-context judges** — both arms' acceptance judges get
   the fixed judge text (§ Acceptance-judge instruction), only the two path
   slots vary; a judge is never its arm's builder.
4. **Asymmetric contamination voids the arm** — any arm whose inputs contain
   another arm's outputs is void: no verification-record line from it; void +
   rerun recorded in the ledger (symmetric contamination is acceptable and
   noted).

5. **The tier claim is verified, not assumed** — a cell's whole point is the
   claim "this work was done at tier X", and a claim about which model ran is
   worth exactly the evidence behind it. Each cell is checked at close by
   `scripts/audit-model-conformance.py <journal> [<telemetry>]`, which joins
   every journal `dispatch` line's `resolved_model` against the run's
   execution telemetry (C1) and the commander's own stamp against the session
   rows (C2). Its C0 leg — the journal opens on `commander_stamp` — is
   telemetry-independent and runs on every instrumented close, with or without
   a telemetry export.

   A cell with no telemetry export is recorded **UNVERIFIABLE, never CLEAN**,
   and an UNVERIFIABLE tier claim may not be published as a tier claim. This
   is the whole of the leakage check that survives: the earlier
   consult-observation machinery is gone with the primitive it observed, and
   nothing replaced it, because there is no longer a second model the worker
   could quietly reach.

   Any planned-vs-actual mismatch voids the cell's tier claim, whatever its
   cause (doctrine: a harness that misreports which model it ran is that
   harness's defect, not this mode's threat model — but the arm's numbers are
   void either way).

Isolation audit: before adjudication, an audit of each arm's inputs (worktree
diff provenance + transcript reads) confirms invariant 4; the audit record
lands beside the ledger rows.

## Verification record (adapters/*/README)

One line per cell that completed a protocol run: `verified-run:
<commander>×<topology> — ledger <run_id>`. Lines cite ledger rows ONLY —
no prose claims; a cell without run evidence never appears (claim ≤
evidence). **A verification record is not a capability claim** (miles
ruling 2026-07-13): each line asserts only that the combination ran
validly under this protocol; comparative verdicts (R3) live in the
ledger's ruling rows, including negative ones.

## v3 regression — distill kernel 4+1 arms **[historical — ran under v3, 2026-07-17]**

Harness single home: the distill repo's `benchmark/` (run-arm / summarize /
cost scripts and the cross-check rule in its README — cite, never restate).
Frozen inputs: distill arm-base `a43c48a`, byte-identical spec per arm (plus
each arm's own methodology paragraph only), same main model on every arm,
headless, arms run serially, worktree isolation per arm (invariants above
apply unchanged). (That revision also kept an operator-level
constants table, which coupled serial arms through a shared file; the table
and its coupling are gone.)

Arms (5): `inline` (floor) / `inline+v3form` (the v3 "0-worker form") / `anvil-sdd` (incumbent) / `conductor-v3` (gate's own topology)
/ `forced-1-worker` (commander never holds the pen; the forcing is the
doctrine's human-veto mechanism — who/changed-to/why recorded in the arm
brief, so the conformance audit reads it as governed, not violating).

Acceptance targets (these numbers live ONLY here and in the v3 spec's AC
layer — never in doctrine/adapter text; a fresh operator's table starts
empty):

- conductor-v3 arm on the kernel task: no fan-out (brake-line refusal on the
  record), or gate refusal → the arm completes via the light path and its
  cost criterion becomes same order as the floor arm.
- 0-worker arm discipline price ≤ **+3,500 tok-eq** (v2 baseline +5,800);
  cache-write/output ratio ≤ **3.0×** (v2 baseline 4.14×, floor 2.09×).
- spec-fidelity held: single check home = distill held-out suite
  `test_ac47_lock_dir_is_injectable_and_the_vault_stays_clean`, both mode
  arms.
- Comparison verdicts come from a fresh-context judge (producer ≠ judge,
  doctrine § Verification); an arm's executor never self-rules.

Every arm lands one ledger row; each completed cell adds a `verified-run:`
line to the adapter README **stamped with the doctrine rev it ran under**
(judgment claims do not cross doctrine revisions).

### v2 → v3 dispatch-plan field mapping (journal/plan comparability)

| v2 mandatory field (7) | v3 home |
|---|---|
| 1. Entry decision | mandatory 1 — Entry decision (+ family + price-row citation) |
| 2. Task-shape declaration | mandatory 2 — Shape & precedent (merged) |
| 3. Precedent line | mandatory 2 — Shape & precedent (merged) |
| 4. Subtask table | mandatory 3 — Subtask table (card citation may replace grade columns) |
| 5. Containment check | conditional — owed iff any write-role dispatch |
| 6. Doubt surfacing | conditional — owed iff entry/grading disposition ≠ frozen |
| 7. Deviation log | conditional — opens at first deviation event |
| — (new) | conditional — brake line, owed iff any offload planned/executed |

Journal events: v2 vocabulary unchanged (zero-shrink); v3 adds
`dispatch_result` (checker verdict + in-channel worker usage) and additive
`dispatch` fields (`card`, `brief_tokens_est`, `w_est`).

## judgment-surface-reduction re-run **[historical — ran under 0.6.0, 2026-07-25]**

Harness single home: the distill repo's `benchmark/` (cite, never restate),
frozen kernel Phase 1 task, frozen held-out pytest suite (133 assertions),
commander = frontier tier, arms run serially in isolated worktrees (the
isolation invariants above apply unchanged).

**Shared denominator — the reused floor.** Both arms are scored against the
existing measured floor **$11.254** (bare inline, no mode; reproduced across
two prior pairs at 0.1% variance). The floor is NOT re-run. **Validity check,
recorded in the findings BEFORE either verdict:** the commander model's
current billing rates must equal those the floor fit used (in 5 / out 25 /
cache-read 0.5 / 1h-write 10 USD per MTok). Any mismatch voids the reused
floor and forces a fresh floor run.

**Pinned session settings (every arm, no exceptions).** An arm inherits from
the CLI exactly what it does not pin, and CLI defaults move: the `opus` alias
resolved to `claude-opus-4-8` when the floor was measured and to
`claude-opus-5` two days later, which would have put a model generation inside
a discipline-price delta had it not been caught. Therefore every arm pins the
commander model (`ARM_MODEL`) and the reasoning effort (`ARM_EFFORT`)
explicitly, and `summary.json` records the effort and CLI version actually
observed in the transcript. An arm whose recorded settings differ from another
arm's is not comparable with it, and a recorded value of `UNRECORDED` voids the
comparison rather than being read as "probably the default". Effort is an
operator setting, not a conductor lever — this harness's dispatch primitive
exposes no effort parameter — so it is controlled, never optimised.

**Canonical turn metric (both arms):** unique API calls, deduped by message
id from the session transcript. The summary fields `num_turns` /
`num_turns_reported` are advisory only and DISQUALIFIED as evidence — the
sidechain-inclusive count produced a "+9 turns" narrative that the deduped
count overturned (floor 65 vs 59). Per-arm tables stay isolated: neither arm
is reported in the other's row.

### Arm — form (the 0.6.0 "0-worker form")

- Brief: `benchmark/briefs/jsr-form-arm.md`.
- Installed from the published marketplace at the revision under test; the
  entry gate declares the task class and the journal records it.
- Targets: billed ≤ floor × 1.10; unique API calls ≤ 65; frozen suite 133/0;
  the close audit set CLEAN over the arm's journal; ceremony invocations ≤ 5
  (membership: ANY tool invocation that reads or writes `.conductor/` run
  artifacts — journal appends INCLUDED — or runs a mode script, in any phase;
  conditional mid-run events count when they fire; the task's own build /
  test / version-control commands are excluded).
- A band miss is an honest negative presented for human accept, never a
  silent re-tune.

### Arm — nudge (native turn economy, no mode)

- Brief: `benchmark/briefs/jsr-nudge-arm.md`, which carries the canonical
  marker `<!-- nudge:batch-v1 -->` beside its batching instruction.
- Floor task plus the permissive batching nudge; no mode machinery.
- Targets: billed ≤ floor × 0.95; unique API calls ≤ 58 (the mechanism
  witness, gated separately from cost so a cost win with no turn cut is
  visible); frozen suite 133/0.
- Owed either way: the deduped-usage decomposition, and an offline
  batching-integrity review of the transcript — every multi-call turn's calls
  pairwise independent, an ambiguous group counting as a violation, each
  violation reported with its turn id.
- **Pollution rule:** the nudge text and its marker appear in this arm's
  brief only. Every other arm brief is checked both ways — a grep for the
  marker and a read for the same guidance in any paraphrase.

## Ceremony-replay method (live procedure)

The instrument that attributes an arm's cost to the mode rather than to the
task. It replays the arm's own transcript and counts the calls that exist
only because the mode was installed. Two measurements rest on it — the
null-check band and the instrumentation share of a delegating arm — so its
membership rule is fixed here rather than re-decided per run.

**Unit.** The billed unit is the API round-trip, not the byte. A single call
at a large context costs on the order of a tenth of a dollar whatever it
carries, and the mode's own TEXT is nearly free (a measured +159 tokens
across a whole run's ceremony). Count calls; do not count characters.

**Membership — a call is a ceremony call iff it does one of:**

1. reads or writes an artifact under the run's `.conductor/` tree (journal
   appends INCLUDED — an append is a round-trip like any other);
2. invokes a mode script (anything under the conductor root's `scripts/` or
   an adapter's `tools/`);
3. reads a mode document *during the run* in order to act (the doctrine, an
   adapter file, a task-contract template) — reading it to author the arm's
   brief before the run starts is setup, not ceremony.

**Excluded, always:** the task's own build, test, lint, and version-control
commands; the harness's own session bookkeeping; anything the floor arm also
does. The test is counterfactual and mechanical: *would this call exist in
the uninstalled floor arm?* If yes, it is not ceremony.

**Conditional events count when they fire.** A mid-run event that the
doctrine owes only under a trigger is a ceremony call on the runs where its
trigger fired, and no call at all on the runs where it did not. Averaging it
across runs would hide exactly the conditioning the current revision is
built on.

**Null check (the instrument's own calibration).** Before trusting a replay
number, run the replayer against a floor arm — an arm with no mode installed.
It must report **0** ceremony calls and $0.00. A replayer that finds ceremony
in an arm that has none is measuring its own assumptions, and its numbers on
the other arms are void.

**Outputs, per arm:** the ceremony call count, the dollar attribution
(ceremony calls × that arm's measured per-call cost), and the ceremony share
of billed total. For a delegating arm, report the production estimate
(billed − instrumentation) alongside billed, and never in place of it.

**Reproducibility.** The replayer script is archived with the run meta of the
round that used it, and the archived copy — not a re-derivation — is what a
later round re-runs. A replay whose instrument was not preserved is not a
reproducible measurement, which is how one prior round lost its baseline.

## Ledger — `benchmark/ledger.jsonl` (append-only; one run per line; never rewrite)

```json
{"run_id": "", "task_ref": {"task": "", "repo": "", "selection_basis": ""},
 "side": "inline|conductor", "models": [], "tokens_in": 0, "tokens_out": 0,
 "cost": 0.0, "cost_source": "billing-surface|tokens-x-list-price(<date>)",
 "quality": {"tests": "", "review_critical": 0, "review_high": 0, "verdict_by": ""},
 "artifacts": []}
```

Cost rules: prefer the side's actual billing/usage surface; when absent,
tokens × that day's official list price; either way `cost_source` says which.

## Ledger v2 row additions

v1 fields keep their meaning. New: `run_id` unique per row (canonical
citation key), `cell` (`<commander>x<inline|v2-form|bare-inline>`), and on
the ablation ruling row `discipline_unit_price_usd` + `quality_delta`.
v1 rows (2026-07-10) are immutable history in legacy shape.

## Quality rubric (human adjudication)

Floor: the task's own tests/checks all green. Above the floor: the human
reviews both deliverables and grades defects by severity. **Not-worse** =
conductor tests ≥ inline AND conductor Critical/High defect count ≤ inline.
**Overall pass** = quality not-worse AND conductor $ cost lower. The human's
ruling and identity go in `quality.verdict_by`.

## Acceptance-judge instruction (fixed text — portability parity, AC-8)

Both sides' judges receive this block byte-identical; ONLY the two path slots
`<contract-path>` and `<task-dir>` vary. The judge is fresh-context and is
never that side's builder.

```text
You are a fresh-context acceptance judge. You did not build the artifacts you
are judging. Read the task contract at <contract-path> and the artifacts in
<task-dir> (result.json and every file it references). For EACH acceptance
criterion in the contract's Acceptance Criteria section, judge pass or fail
STRICTLY from the artifacts in front of you — do not re-run the task, do not
repair anything, do not consult any other context. Cite evidence as file:line
or a quoted command-output line. Write EXACTLY one JSON array (no prose, no
wrapper object) to <task-dir>/acceptance.json:
[{"ac_id": "<id>", "status": "pass"|"fail", "evidence": "<file:line or quote>"}]
```

Parity comparison: join the two acceptance.json arrays on ac_id; verdicts
must match (both pass or both fail) for every ac_id. On mismatch: first
rule out instruction divergence (byte-identical instruction = ruled out),
then read the divergence against flip-trigger FT-1 (invocation-semantics
fork → reopen the architecture decision, ADR 0001).
