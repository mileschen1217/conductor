# Arm brief — jsr form arm (mode 0-worker form, re-run against the floor)

Protocol row: `benchmark/protocol.md` § judgment-surface-reduction re-run.
This file is the arm's brief; it carries no batching or turn-economy guidance
of any kind (the nudge is confined to its own arm — cross-arm pollution voids
the mode-vs-floor delta).

## Task

The frozen distill-kernel Phase 1 task, byte-identical to the arm the floor
was measured on (distill repo's `benchmark/`, frozen held-out pytest suite,
133 assertions). No task text is added, removed, or reworded here.

## How this arm runs

- conductor installed from the published marketplace at the shipped revision
  under test; the mode is entered, not simulated.
- Commander = frontier tier, sequential, no parallelism.
- The entry gate declares the task's class. Every acceptance criterion of the
  kernel task carries a runnable, builder-independent check artifact (the
  frozen suite), so the expected declaration is `class: "mechanical"` with
  `class_default: "cited"` — recorded, not assumed: whatever the gate rules
  is what the journal carries, and an override records its reason.
- Acceptance is the frozen suite's execution (doctrine § Verification). The
  task carries zero taste criteria, so no verification dispatch is owed; a
  verifier dispatch here would be the over-verify shape this epic exists to
  remove.

## What is measured

- `billed_cc_usd` from the arm's summary, against the reused floor.
- Unique API calls, deduped by message id from the session transcript — the
  canonical turn metric. Summary `num_turns` / `num_turns_reported` fields
  are advisory only and are not evidence.
- Ceremony invocation count (membership rule in the protocol row).
- The frozen suite result, and the close audits over the arm's journal.
