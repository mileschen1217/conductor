---
role: mech-writer
duties:
  - apply an already-solved, written recipe to the targets enumerated in the
    contract, inside the contract's owned files only
  - run every contracted verification command and record exit codes in the
    result artifact
grade:
  verifiability: mechanical — the recipe ships with runnable checks; exit
    codes decide acceptance
  recovery: low — version-control revert; blast radius bounded to the
    contract's owned files
  context: small closed corpus; recipe known; zero exploration
tier: cheap
capability_surface:
  read_only: false
  tools: [read, edit, run-contracted-commands]
io:
  input: task contract (Scope carries the exact recipe with its verification
    commands; Owned Files enumerates the write surface)
  expected_output: result artifact with files_changed and commands_run (exit
    codes); recipe applied to every enumerated target or the miss reported
when_not:
  - the recipe is fuzzy, partial, or first-encounter (cheap-tier red line —
    escalate the grading, not the worker)
  - targets are not enumerable in advance
  - the change spans cross-file invariants that the recipe does not already
    encode
  - any duty in the doctrine's reserved set (RT-8)
graded_under:
  doctrine_rev: "9b59741"
  model_gen: "g2026.07"
---

# mech-writer — cached grading: recipe application

One shape, graded once: batch application of a solved pattern whose checks
are written before dispatch (doctrine § Defaults — solved pattern, its
de-escalation endpoint). Citing this card replaces the three-axis grade
columns (RT-4 @ role-card); any `graded_under` mismatch is a miss and full grading is owed.
