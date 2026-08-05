# Benchmark protocol — comparative acceptance procedures

One-shot comparative acceptance procedures (NOT standing eval infrastructure).
Human-governed: the human selects the task, adjudicates quality, and rules
pass/fail — this protocol contains NO automatic pass logic.

**How to read this file.** Only live procedure ships here: § Task selection,
§ Isolation invariants, § Verification record, § Ceremony-replay method,
§ Ledger, § Quality rubric, § Acceptance-judge instruction. Records of runs
that already executed (per-run protocol sections, arm briefs, findings,
probe logs) are operator-local working state — kept beside the ledger,
gitignored, never shipped: a record rewritten to match current vocabulary is
no longer a record of what happened, and rows reference local artifacts.
## Task selection (human)

Criteria (all required): a real repo; the task spans ≥3 files; subtasks are
heterogeneous; quality is decidable by tests and/or severity-graded review.
The selection (task, repo, why it meets each criterion) is recorded in the
run ledger entry (`task_ref`).

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

## Verification record (operator-local)

One line per cell that completed a protocol run: `verified-run:
<commander>×<topology> — ledger <run_id>`, kept with the operator's local
ledger (`benchmark/ledger.jsonl`, gitignored). Lines cite ledger rows ONLY —
no prose claims; a cell without run evidence never appears (claim ≤
evidence). **A verification record is not a capability claim** (maintainer
ruling 2026-07-13): each line asserts only that the combination ran validly
under this protocol; comparative verdicts (§ Quality rubric) live in the
ledger's ruling rows, including negative ones.

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

**Repair of 2026-07-29 (rule 3 mechanised; rules 2 and 1 corrected).** Until
this date the instrument implemented rule 1 and part of rule 2 only. Its path
predicate matched `.conductor/` and a hand-written allowlist of script
basenames, so a run-time read of a mode document in the installed plugin tree
scored as task work, and `close-chain.sh` — a rule-2 member under an adapter's
`tools/` — was never in the allowlist. The repaired instrument mechanises rule 3
with the **transcript's own start as the run boundary** (a read recorded inside
the transcript is a run-time read by construction, since the arm's brief is
authored before the transcript exists), replaces the basename allowlist with a
directory rule, and widens rule 1 from `.conductor/` to `.conductor` at a token
boundary. The carriers counted are the installed plugin tree, a clone rooted at
a directory named `conductor`, the `$VAR/scripts/…` and bare checkout-relative
shapes (the unset `${CLAUDE_PLUGIN_ROOT}` case), and `.conductor/`. Where a path
carries a conductor root the directory decides; where it does not, the name must
— `scripts/x.py` in the ARM's own repo is shape-identical to one in conductor's,
so a carrier-less token earns membership only by a name conductor owns.

**Two boundaries this method fixes in writing, because both were got wrong
once.** (i) Rules 2 and 3 are published with the verbs *invokes* and *reads*;
neither covers WRITING a file, so a write outside `.conductor/` is task work
however conductor-shaped its path — rule 1 is the only rule whose verb reaches
writes. (ii) A `cat` of a mode script's SOURCE does count, even though rule 2
says "invokes" and rule 3's parenthetical names documents rather than scripts.
That is continuity — the pre-repair instrument matched reading and executing
alike — and excluding it now would be an undisclosed narrowing against the
published baseline. It is stated here rather than left implicit because
script-source reads are exactly where the two arms' costs diverge.

**A null check is necessary and not sufficient.** A floor arm has no mode
installed, so scoring it zero proves the instrument invents no ceremony; it
cannot prove the predicate rejects the shapes a REAL task repo carries — its own
`scripts/`, a search pattern naming a mode document, a mode path quoted in
prose. Those need negative fixtures. The instrument therefore carries a
`--self-test` covering both directions, and a round that runs only the null check
has tested half the instrument.

**Mechanising rule 3 widened the rule's extension, and the reported number goes
up.** Rule 3's prior form asked the operator to judge whether a document was
read "in order to act"; a mechanical boundary admits reads that judgment could
have excluded, so post-repair figures are not comparable to pre-repair figures
and neither replaces the other. This is a stated amendment with both numbers on
the record, not a re-tuning: the governing spec's § Out-of-scope carves rule 3
in for exactly this reason while barring any re-tuning of an AC-24 prediction or
band. Old and new figures for all three re-scored arms, the instrument hashes,
and the null check are on record in the operator-local findings notes (kept
beside the ledger; they reference local artifacts). That round also
found the pre-repair under-count to be **asymmetric across arms**, which the
governing spec had assumed it was not — so a contrast drawn from pre-repair
figures alone may not survive re-scoring, and any future round comparing arms
must re-score both under one instrument rather than lift a published pair.

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

## Unit of analysis (cost verdicts on paired work units)

When both arms decompose the task into the same work units (e.g. one worker
per module on each side), **the cost finding of record is the per-unit paired
comparison**: each unit's cost on each arm, the paired statistic over the
per-unit log-ratios (mean, dispersion, n), and its sign. The estimator is
fixed as `log(conductor_unit_cost / inline_unit_cost)` — positive means
conductor is more expensive; a report using any other orientation says so
explicitly or is misread. Run totals are
derived numbers — reported, never the headline. Rationale, from a five-pair
round (2026-08): the totals differed −0.5% while the paired per-unit mean was
+4.2% with two large opposite-signed effects cancelling inside the aggregate
— the aggregate manufactured a headline with the wrong sign and hid that the
data contained no signal at all (t=0.26, n=5). Log-ratio is the estimator
because costs are ratio-scale and unit sizes differ; a round whose arms do
not share a unit decomposition states so and falls back to run totals
explicitly.

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
or a quoted command-output line. Reason as much as the judgement needs; your
reply's FINAL block must be a single fenced ```json block containing one array
and nothing else, and that array is what is written to
<task-dir>/acceptance.json:
[{"ac_id": "<id>", "status": "pass"|"fail", "evidence": "<file:line or quote>"}]
```

Parity comparison: join the two acceptance.json arrays on ac_id; verdicts
must match (both pass or both fail) for every ac_id. On mismatch: first
rule out instruction divergence (byte-identical instruction = ruled out),
then read the divergence against flip-trigger FT-1 (invocation-semantics
fork → reopen the architecture decision, ADR 0001).
