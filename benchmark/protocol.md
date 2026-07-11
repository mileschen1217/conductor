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

**Harness constraint (2026-07-12, cc 2.1.205):** the CC Agent tool's
`model` param is currently inert — every dispatched worker executes the
default mid-tier model regardless of the requested one (three-witness
evidence: smoke/ac-14). Until fixed upstream: (1) non-default WORKER
models cannot be pinned in-session — matrix cells requiring them run
their commander as a separately-launched session (`claude --model X`,
the main-loop selector works) with workers on the default tier only;
(2) every cell's models are verified post-run by
`audit-model-conformance.py` (journal × telemetry), never assumed from
the plan; (3) the R1 human ruling confirms the reachable cell set
before any cell runs.

## Isolation invariants (all four hold per cell; violation voids the arm)

1. **Worktree per arm** — each cell runs in its own worktree; no shared
   working tree between arms.
2. **Shared contract names no directory** — the task contract binds Scope by
   EXACTLY declaration (the explicit deliverable set) plus a sibling
   do-not-touch (DNT) declaration; it never names another arm's directory.
3. **Byte-identical fresh-context judges** — both arms' acceptance judges get
   the fixed judge text (§ Acceptance-judge instruction), only the two path
   slots vary; a judge is never its arm's builder.
4. **Asymmetric contamination voids the arm** — any arm whose inputs contain
   another arm's outputs is void: no envelope claim from it; void + rerun
   recorded in the ledger (symmetric contamination is acceptable and noted).

Isolation audit: before adjudication, an audit of each arm's inputs (worktree
diff provenance + transcript reads) confirms invariant 4; the audit record
lands beside the ledger rows.

## Validated envelope (adapters/*/README)

One line per validated cell: `validated: <commander>×<topology> — ledger
<run_id>`. Envelope lines cite ledger rows ONLY — no prose claims; an
unvalidated cell never appears (claim ≤ evidence).

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
