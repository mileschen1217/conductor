---
role: read-scout
duties:
  - locate, inventory, and summarize material inside the contract's read
    boundaries; every claim cited as file:line or a quoted command-output line
  - return findings in the report (result artifact); a findings file is an
    optional extra, never the required delivery path
grade:
  verifiability: findings are spot-checkable against cited sources; acceptance
    is a coverage + citation check, writable as a runnable check per contract
  recovery: trivial — read-only role, nothing to undo; worst case is a wasted
    dispatch
  context: fresh small context over a contract-bounded corpus subset; no
    path-dependent exploration
tier: mid  # not cheap despite the cheap-leaning axes: finding classification
  # needs reading comprehension, not pattern match (why-not-a-script's answer
  # is also why-not-cheap); search/inventory is the tier table's mid row
capability_surface:
  read_only: true
  tools: [read, search, list, run-contracted-read-only-commands]
io:
  input: task contract (Scope + Read-Only Boundaries name the corpus subset
    and the questions to answer)
  expected_output: result artifact whose summary carries the findings with
    citations; files_changed empty
when_not:
  - any write to any surface is required
  - first-time diagnosis of an unknown failure (path-dependent exploration →
    full grading, frontier-leaning)
  - the question needs a pass/fail call on someone else's deliverable (that
    is fresh-verifier's shape, or the doctrine's reserved set)
  - any duty in the doctrine's reserved set (§ Judgment reservation)
graded_under:
  doctrine_rev: "978f98c"
  model_gen: "g2026.07"
---

# read-scout — cached grading: read-only reconnaissance

One shape, graded once: a bounded read-only sweep (search, inventory,
multi-source lookup) whose findings are evidence-cited and whose acceptance
can be checked against the citations. The grade above is the card's cache;
citing this card in a dispatch plan replaces the three-axis grade columns
for the subtask (doctrine § Complexity tiering — Role cards). Staleness rule
lives there: any `graded_under` mismatch = miss = full grading.
