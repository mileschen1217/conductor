# v4pair — discipline-price sign confirmation at 0.4.0 (2026-07-18)

Purpose: the v3 regression's headline discipline price (v3form −$5.55 vs
the inline floor) was a single pair inside cache/warmth noise — its own
synthesis said so. This run asks one question with enough repetition to
answer it: **what is the SIGN of the discipline price on a write-heavy
task at plugin 0.4.0** (doctrine rev `e7f60ae`, installed from the
published marketplace)? Design: interleaved serial pairs on the same day
(floor, form, floor, form…), same frozen spec (distill arm-base
`a43c48a`, 51 acceptance criteria), commander pinned to opus, held-out
pytest suite + cost lenses (judge pass skipped by ruling — the suite
already decided the quality question). Planned 3 pairs; stopped after 2
by stop-loss rule: two same-sign pairs over a low-variance floor decide
the sign, and the human had asked whether two sufficed before the second
pair landed.

## The four arms, complete data

| arm | methodology | billed USD | wall min | suite |
|---|---|---|---|---|
| inline-b1 | floor: no mechanism | $11.27 | 27.4 | 132/135 |
| v4form-b1 | 0.4.0 mode, 0-worker inline form | $18.23 | 43.9 | **131/135** |
| inline-b2 | floor: no mechanism | $10.75 | 27.3 | 132/135 |
| v4form-b2 | 0.4.0 mode, 0-worker inline form | $14.35 | 33.7 | **131/135** |

(ac42 fails on all four arms — the known grader artifact, never
penalized. The 131s are one REAL failure each, distinct: v4form-b1
mis-serializes yaml-special-character titles (ac25); v4form-b2 reroutes
the lock dir but leaves `.distill` staging in the vault (ac47). Both are
implemented-but-wrong, not missing. Both inline arms are clean.)

## Verdict

**The discipline price on this task family is POSITIVE: +$6.97 (+62%)
and +$3.60 (+33%).** The floor is low-variance ($11.27/$10.75, same
27 min, same suite result), so the sign is decided at n=2. The v3
regression's −$5.55 is ruled a cache-noise outlier, as its synthesis
already suspected. Quality does not compensate: the form arms each lost
one real held-out test that the floor arms passed.

## Where the money goes (decomposition)

Per-turn token attribution over all four transcripts (single home:
`benchmark/results/_v4pair-run-meta/delta-decomposition.md` in the
distill repo). Basis note: the bucket figures and percentages below are
on the **estimated** (tokens × pricing) basis, whose deltas are $6.65
and $3.07 — diverging from the billed headline deltas by ~5% (pair 1)
and ~17% (pair 2), a gap the decomposition file discloses and cannot
attribute. The qualitative split holds on either basis:

- **Mode boot** (SKILL + doctrine + haiku boot probe, ~14.7K tok): ~10%
  of the delta — a fixed cost worth 3–6% of the floor. Not the problem.
  (And the benchmark overstates it: every arm worktree is a fresh
  project, so every run pays cold boot; a long-lived repo pays it once.)
- **Ceremony: 68–117% of the delta.** ~30 commander turns writing the
  journal (21/29 lines), six task contracts, six result.json, checker and
  audit runs. The damning detail: in the 0-worker form, T1–T5's
  result.json were batch-self-written by the commander in the same
  minute — **no second context ever read them**. The only contract with
  a consumer was T6's, read by the verification subagent.
- **Subagent: negative** (−$0.34/−$0.76) — the mode dispatched a sonnet
  verifier where the floor used opus. The one structural choice the mode
  made paid for itself.
- **Residual: context-carry tax** — per-turn cache_read +41%/+24% once
  boot+ceremony inflate the context.

## Product finding — candidate REQ (not yet filed)

`doctrine/orchestration-mode.md:72` mandates the ceremony: the inline
form is defined as "contract, entry gate, journal, checker, and result
discipline still apply." The decomposition shows the contract/result
discipline only creates value when a second context consumes the
artifact (a worker brief, a fresh verifier); a self-written result.json
is paperwork with no evidentiary value — the producer is the judge.
**Candidate REQ: consumer-gated ceremony** — contracts and result files
are produced only for dispatched or verified tasks; the journal remains
(it has a consumer: the audit scripts and the human). Estimated recovery
$3.5–5.5 of the delta, landing overhead at ~9–15% — inside the stated
acceptable band (human ruling, this run: 10–15% is the tolerable
imagination space; +50% is not "imperceptibly thin"). Spec-level change
(L1); goes through crucible, not a patch.

Two regimes, restated honestly: this run measures the fits-in-one-context
write-heavy regime only. The read-heavy regime where dispatch is forced
anyway measured NEGATIVE discipline price (−$2.27, T16 2026-07-13) and is
not contradicted by this run.

## Run integrity notes

- Plugin cache verified pre-launch: installed 0.4.0, gitCommitSha
  `658d384…`, cached `doctrine/REV` = `e7f60ae` (run-meta snapshot in the
  distill repo's `benchmark/results/_v4pair-run-meta/`).
- Both v4form arms' `.conductor/` run records (journal, probe file)
  archived under `benchmark/results/<arm>/conductor-run/` before worktree
  teardown.
- n=2 pairs decides the sign, not the magnitude; both pairs same-day
  serial, pricing and model constant, cache warmth interleaved across
  both arms rather than loaded onto one.
