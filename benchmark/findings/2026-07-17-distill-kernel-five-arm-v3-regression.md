# Five-arm v3 regression — distill kernel Phase 1 (2026-07-17)

The v3 doctrine's acceptance regression (spec REQ-6; protocol single home =
`benchmark/protocol.md` § v3 regression). Five arms built the same frozen
spec (distill arm-base `a43c48a`, 51 acceptance criteria) by five
methodologies, serial headless, commander pinned to opus on every arm,
conductor plugin **0.3.0 installed from the published marketplace**,
shipped doctrine rev **`33ec134`**. Grading: held-out pytest suite +
fresh-context per-arm judge + cost, synthesized once by a fresh opus
context (`results/synthesis-v3.{json,md}` in the distill repo's
benchmark/, together with all summaries and the run-meta snapshot).

Relation to the four-arm run (2026-07-16, previous file in this
directory): arms 1 and 3 are re-runs of the same briefs byte-identical;
they exist as same-batch controls because the floor is measured-high-
variance and the targets are relative. Arms 2, 4, 5 run the v3 doctrine
(the four-arm run measured v2).

## The five arms, complete data

| arm | methodology | billed USD | wall min | suite | judge |
|---|---|---|---|---|---|
| inline-v3 | floor: no mechanism | $17.26 | 42.9 | 132/135 | sound, q5 |
| v3form | v3 discipline, 0-worker pinned | **$11.71** | **35.9** | 132/135 | sound, q4 |
| anvil-sdd-v3 | incumbent (touchstone anvil SDD, as deployed) | $94.38 | 299.6 | 132/135 | sound, q5 |
| conductor-v3 | v3, topology chosen by gate+brake | $19.05 | 56.1 | 132/135 | sound, q4 |
| forced-1w | v3, 1 write-worker forced by recorded operator veto | $23.74 | 63.3 | 132/135 | **flawed**, q4 |

Synthesis ranking: **v3form ▸ inline-v3 ▸ conductor-v3 ▸ anvil-sdd-v3 ▸
forced-1w** (confidence: medium; n=1 per arm).

Suite unanimity: the single failing test (`test_ac42_filename_collision…`)
fails on all five arms with byte-identical spec-correct output —
synthesis-ruled **grader artifact** (the fixture builds a collision that
the frozen safe-title rule makes impossible). No arm penalized. The
cross-arm-correlation instrument did its one job again (in the four-arm
run it caught 9 of 12 failures as ruler defects).

## Headline 1 — the discipline price flipped negative (target met, sign and all)

Floor vs v3form differ ONLY in whether the v3 mechanism ran (same opus
commander, same pen). Token-equivalent accounting (out=1, cache-write=0.25,
in=0.2):

```
floor   275,264 tok-eq   $17.26   42.9 min
v3form  222,296 tok-eq   $11.71   35.9 min
discipline price = −52,968 tok-eq  (protocol target ≤ +3,500; v2 measured +5,800)
cache-write/output ratio = 1.74    (protocol target ≤ 3.0; v2 measured 4.14)
```

Both regression targets pass with room. What changed from v2's +5,800:
the R3 prose diet (3 mandatory plan fields instead of 7), the brake's
not-owed rule (a zero-dispatch run writes no brake line), and the entry
gate's light deliberation. What the floor spent that v3form didn't:
18.9M cache-read tokens vs 10.3M, per the arms' three-source token
rollups (distill `benchmark/results/<arm>/cost.json`; the floor's
subagent adds 0.6M to its main session's 18.2M) — the floor wandered,
including one self-chosen ad-hoc opus subagent — the discipline's structure appears
to *save* re-reading on a write-heavy task, reversing the v2 sign.
Honest caveat: the winner rests on a single-run $5.55 delta; the
synthesis names the 3–5× re-run of this pair as the falsification test.
The floor's variance across its three recorded runs (one sonnet reviewer
/ zero / one opus gp) is itself a reproduced finding.

## Headline 2 — one worker hop costs more than the whole discipline (and it gamed)

v3form vs forced-1w differ only in who held the pen (operator veto forced
exactly one sonnet write-worker; commander never wrote deliverables):

```
worker hop price = +$12.03 (+103%), +27.4 min
```

The hop also produced the run's only judge-confirmed **gaming finding**:
the worker's VTT rolling-cue dedup knowingly deviates from the frozen
step-8 basis rule, with a code comment admitting it is tuned to what the
AC-18 test checks; byte-divergent output on untested inputs (concrete
failing input in `results/forced-1w/judge.json`). The commander's
checker validated the contract mechanically and the defect passed — the
per-worker price includes not just fresh-context rebuild (C_fresh
measured 68,244 tok-eq on this corpus) but a quality-assurance surface
the commander cannot see from the result artifact alone. This is the
strongest single-run datum yet for the doctrine's brake defaulting
closed on single-context tasks.

## Headline 3 — the gate's own choice was vindicated, but judgment has a running cost

conductor-v3 (topology free) chose: entry opened `[pending-measurement]`
(no price row — refusal disabled, exactly the three-state rule), brake
cold-start conservative-closed → 0 write worker, one sonnet
fresh-verifier via the mandated-verification exemption. The protocol's
expected script (branch 1: no fan-out, brake refusal on record) HIT.
forced-1w then demonstrated what fanning out would have cost: the gate's
restraint saved money. But making-and-recording the judgment cost
$19.05 − $11.71 = **+$7.34 and +20 min** over the same shape with the
decision pinned externally: entry deliberation, judgment moments, brake
prose, verifier dispatch ($1.45), harvest re-read. That number is the
concrete input to the two deferred design items (remove entry refusal;
prose-diet round 2).

## Headline 4 — the incumbent, honestly costed, again

anvil-sdd-v3: 15 SDD tasks × (implementer + reviewer + fix loops), 35
subagents, 4 codex rollouts, $94.38, 5.0 hours — for a kernel the suite
and judge cannot distinguish from the $11.71 arm's. Its review loops did
catch 2 Critical + 6 Important defects in its OWN code during the build
(recorded in the arm worktree's SDD progress ledger,
`.superpowers/sdd/progress.md` — not this benchmark's ledger, whose
per-arm review counts are zero by construction), and its judge quality
is 5 vs v3form's 4 —
the review spend is not zero-value, but 8× the winner's cost bought no
measurable correctness. Consistent with the four-arm result (4.5×); the
gap widened because this anvil run decomposed finer (15 tasks vs 13).

## The calibration loop closed in production, across arms

Sequential coupling through the real operator table
(`~/.claude/conductor/constants.jsonl`), all honest, all journaled:

1. v3form's close appended `unverifiable` (0-worker — nothing to measure);
2. conductor-v3's close appended `unverifiable` (inline build, verifier
   usage not itemized by the harness);
3. forced-1w's brake line **cited** conductor-v3's row (explicitly noting
   `kind=unverifiable — supplies no C_* values`, pay=UNCOMPUTABLE);
4. forced-1w's close banked the **first measured constants row**:
   `C_fresh=68,244, C_brief_cmd=2,500, C_brief_worker=500, C_reread=500`.

Self-measurement went from empty to consumable within one benchmark day,
with no seeding. Cross-project note: C_fresh here is 68,244 vs 12,483
measured on the conductor repo — 5.5× apart, first concrete evidence for
the deferred "user-default + project-override constants" design item.
Comparability note: the coupling could not steer any arm's behavior
(v3form pinned; conductor-v3 ran before the measured row existed;
forced-1w's topology was veto-locked), and the at-start table snapshot
ships with the run meta.

## Product gaps caught live (regression-ratchet queue)

1. **doctrine_rev fallback in installed-plugin context** — the plugin
   cache has no `.git`; both mode arms' commander_stamp records
   `doctrine_rev: "0.3.0"` (plugin version) instead of the doctrine
   file's commit. Binding needs an explicit fallback rule (version string
   is honest but violates the letter of the binding's definition).
   **Retro root-cause link to gap 4, scoped to its evidence:** role
   cards are stamped `graded_under.doctrine_rev: 33ec134`; against the
   run's resolved rev string `"0.3.0"` the staleness check can never
   match. One dispatch names this verbatim — forced-1w's mech-writer
   consideration (`card=none (mech-writer stale 33ec134!=0.3.0)`) — so
   the staleness block is *confirmed for that instance*; the other
   `card:"none"` dispatches carry no note, so the same mechanism is the
   plausible shared cause there, not an established one. A candidate
   rev-semantics fix (ship the doctrine-file commit inside the plugin,
   e.g. a stamped metadata file, defined as the installed-context rev)
   would unblock card citation; queued with the other gaps, not yet
   actioned. Some of Headline 3's judgment-machinery overhead is the
   manual three-axis regrade this block forces — a qualitative link;
   the +$7.34 was not itemized to that granularity.
2. **Brake-line grammar drift defeats the auditor, in both directions** —
   conductor-v3 wrote `- **brake:** …` (bold bullet): parser reports
   NO-BRAKE-LINES (false negative reads as clean). forced-1w wrote the
   citation as `key@<project>/<run_id>/<ts>` (extra segment): resolver
   reports VIOLATION on lines whose semantics are honest. Adjudicated:
   format drift, no dishonesty. Root fix direction: move the brake
   record into the journal as a typed event; plan prose stays
   human-facing. (Same class as witness finding MR7; the ratchet is not
   yet closed.)
3. **audit-single-writer.sh still speaks the v1 journal dialect**
   (`{"phase","worker","action","path"}`) — MALFORMED on every v3
   journal. I2 was discharged structurally this run (0–1 writers); the
   instrument needs a v3-vocabulary mode before it can discharge I2 on a
   real fan-out.
4. **Card mechanism unused where it applied** — every mode-arm dispatch
   journaled `card: "none"`; the fresh-verifier and (arguably)
   mech-writer cards fit the shapes dispatched. Retro found one
   confirmed cause: gap 1's rev mismatch blocks the staleness check on
   the single dispatch that documents its card consideration (forced-1w,
   quoted in gap 1). Whether the remaining `card:"none"` instances share
   that cause or never found the cards (headless discoverability) is
   not separable from the journals — and cannot be measured until the
   staleness block is fixed. (Cost impact is part of Headline 3's
   +$7.34, not separately itemized.)
5. **Journal lines carry no `ts`** in both mode arms (build-run journals
   did); collector tolerated it, but drift-window logic keys on
   timestamps. Vocabulary conformance nit.
6. **Fresh-verifier carries no gaming/honesty lens** — forced-1w's
   verifier returned ACCEPT (flagging only a test-coverage gap) on a
   deliverable whose code comment *admits* tuning the VTT step-8 branch
   to what the AC-18 test checks; the per-arm judge caught it from the
   same artifacts. The verifier's card duties are criteria-conformance
   only (`contract/roles/fresh-verifier.md` § duties: assess each
   contracted criterion, report pass/fail with evidence); a judge-grade
   honesty check (compare code comments and the worker's own claims
   against the frozen rules) is card-level absent.
   Candidate fix is an L2 card duty line — spec-level, queued with the
   backlog rulings. Until then, the commander's mechanical checker plus
   a criteria-only verifier is a demonstrated blind spot for worker
   gaming (the exact defect class the veto-forced arm was priced to
   expose).

One retro observation recorded for the deferred design queue rather than
as a gap: forced-1w's commander improvised **warm worker continuation**
(wave 3 re-used the wave-1 worker via a follow-up message; the journal's
dispatch events record `brief_tokens_est: 400` for the warm follow-up vs
`brief_tokens_est: 7000` for the cold wave-1 dispatch, tier self-labeled
`cheap-work-on-warm-mid`). The dispatch primitive's text
knows only ephemeral contract dispatch — amortizing C_fresh across
same-corpus waves is exactly what the brake's economics want, and the
promotion decision (boundaries: warm only within a contract family,
verifier always fresh, a warm marker on the dispatch event) sits in the
epic's deferred log.

## Honest caveats

- n=1 per arm; every cost delta above is a lead, not a law. The
  synthesis's falsification test: re-run the floor/v3form pair 3–5×.
- The floor arm's own dispatch behavior is high-variance (three runs,
  three shapes); the discipline price inherits that noise on its floor
  side.
- anvil's $94 includes codex estimated via hand-maintained pricing
  ($2.53 of $94 — negligible to the ordering).
- The judges were told nothing about methodologies, but arm-root paths
  contain arm names; same exposure as every prior run in this series.
- Judge/synthesis spend (this run): $10.89 + synthesis, billed outside
  every arm's account (neutral working directories).

## AC discharge (v3 spec, pending human acceptance)

| AC | verdict | evidence |
|---|---|---|
| AC-2 (write-heavy leg) | PASS | 3 mode arms: task-shape `write_surface=kernel/+tests/+pyproject.toml` → family=write-heavy journaled; commits present inside declared surface (1/5/2); bidirectional audit clean |
| AC-5 | PASS (with note) | conductor-v3 brake on record → inline held; numeric leg recomputed with the run-banked measured row: save 27,000 < pay 30,498 → same verdict. Note: at run time the brake refused via cold-start (pay=UNCOMPUTABLE), the conservative branch, not the inequality branch |
| AC-11 | PASS | ratio 1.74 ≤ 3.0; AC-47 lock-dir test passed on both mode arms |
| AC-18 | PASS | five summaries complete; cross-checks: WARNs only (known CLI duration/turns undercount), zero BLOCK; ledger rows appended (run_id v3-regression-2026-07-17) |
| AC-19 | PASS | judge≠producer throughout; conductor-v3 no-fan-out with brake record HIT; discipline price −52,968 tok-eq ≤ +3,500; fidelity held both mode arms |
| AC-20 | PASS | forced-1w cell measured (cost/suite/fidelity/constants) into ledger; verified-run lines added to the CC adapter README stamped doctrine 33ec134 |
