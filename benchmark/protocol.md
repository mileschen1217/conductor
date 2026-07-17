# Benchmark protocol v2 — commander×topology matrix

One-shot comparative acceptance procedure (NOT standing eval infrastructure).
Human-governed: the human selects the task, adjudicates quality, and rules
pass/fail — this protocol contains NO automatic pass logic.

## Task selection (human)

Criteria (all required): a real repo; the task spans ≥3 files; subtasks are
heterogeneous; quality is decidable by tests and/or severity-graded review.
The selection (task, repo, why it meets each criterion) is recorded in the
run ledger entry (`task_ref`).

## Matrix (v2 — supersedes the single inline-vs-conductor pair)

Commander models (4, human-confirmable at R1): fable / opus / sonnet / haiku
(CC binding table 2026-07-11). Cells: 4 commander models × {inline, v2-form}
plus ONE bare-inline ablation cell = **9 cells / 9 ledger rows**.

- **matrix inline cell** = the mode's 0-worker form: contract + entry gate +
  journal + checker + result.json discipline, pen stays with the commander.
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
cell appends one ledger row AND one precedent/v1 line to
`.conductor/precedent.jsonl`.

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

5. **No undisclosed tier leakage** — a cell's whole point is the claim "this
   work was done at tier X". A worker that silently consults a frontier advisor
   makes that claim false while every number still looks clean, so each cell is
   checked at close: worker advisor calls observed vs disclosed in
   result.json's `judgment_events`. Mismatch voids the cell's tier claim.
   Because this is a *measurement* duty and not a mode duty (doctrine
   § Advisor primitive: the mode binds a harness's interface, never its
   internals; ordinary runs rest at UNVERIFIABLE), the machinery lives here:

   - CC arms: `benchmark/tools/cc-advisor-observations.py` produces the
     observation file, and each dispatch prompt in a measured run must carry a
     literal `Task contract: <task_id>` line for its calls to be attributable.
     The tool reads CC-internal transcripts and **will break on a CC upgrade**;
     when it does, verify by having an agent read the run's worker sessions, or
     record UNVERIFIABLE. Never deepen the excavation.
   - codex arms: no advisor path is reachable from the worker sandbox
     (*reasoned*, not probed) — record UNVERIFIABLE, not CLEAN, until probed.
   - Either way the verdict is joined by
     `scripts/audit-judgment-flow.py --results … --advisor-observations …`
     (vendor-neutral; absent observations = UNVERIFIABLE, never CLEAN).

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

## v3 regression — distill kernel 4+1 arms (acceptance protocol for doctrine v3)

Harness single home: the distill repo's `benchmark/` (run-arm / summarize /
cost scripts and the cross-check rule in its README — cite, never restate).
Frozen inputs: distill arm-base `a43c48a`, byte-identical spec per arm (plus
each arm's own methodology paragraph only), same main model on every arm,
headless, arms run serially, worktree isolation per arm (invariants above
apply unchanged). Operator constants table: isolate per arm (HOME-level
override or per-arm table path) — the 2026-07-17 run showed serial arms
couple through the shared table (a later arm's brake consumed an earlier
arm's appended row); harmless there (topologies were pinned or pre-dated
the row) but it is an arm-order variance channel. The at-start snapshot
into run meta stays required either way.

Arms (5): `inline` (floor) / `inline+v3form` (the mode's 0-worker form under
v3 doctrine) / `anvil-sdd` (incumbent) / `conductor-v3` (gate's own topology)
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
