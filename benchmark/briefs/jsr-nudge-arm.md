# Arm brief — jsr nudge arm (native-turn economy, no mode)

Protocol row: `benchmark/protocol.md` § judgment-surface-reduction re-run.
This arm measures harness-side turn economy on the bare floor task. It runs
NO orchestration mode: no journal, no entry gate, no ceremony.

## Task

The frozen distill-kernel Phase 1 task, byte-identical to the floor arm
(distill repo's `benchmark/`, frozen held-out pytest suite, 133 assertions).

## The nudge (the only delta vs the floor arm)

<!-- nudge:batch-v1 -->
You MAY batch independent tool calls (reads, non-dependent writes) into one
turn; never batch across a dependency.

The marker line above ships with the nudge so its presence is mechanically
greppable. It appears in this file and nowhere else: any other arm brief
matching it — or carrying the same guidance in any paraphrase — is a
pollution defect that voids the mode-vs-floor comparison.

## What is measured

- `billed_cc_usd` against the reused floor.
- Unique API calls, deduped by message id — the mechanism witness, gated
  separately from the cost outcome, so a cost win with no turn cut is
  visible as such rather than credited to batching.
- The frozen suite result.
- An offline batching-integrity review of the transcript: every multi-call
  turn's calls verified pairwise independent. An ambiguous group counts as a
  violation, and any violation is reported with its turn id — a green suite
  does not excuse a batch that crossed a dependency.
