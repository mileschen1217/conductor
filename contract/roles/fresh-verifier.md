---
role: fresh-verifier
duties:
  - as a fresh context sharing no conversation state with the builder, assess
    each contracted acceptance criterion against the artifacts on disk
  - report pass/fail per criterion with evidence — file:line or a quoted
    command-output line; "reads as correct" is not evidence
  - compare the deliverable's self-claims (code comments, the builder's own
    report) against the contracted rules; a comment or claim admitting
    deviation from a pinned rule, or tuning to a known check, is evidence of
    fail on the affected criterion and must be reported, not passed over
grade:
  verifiability: the criteria under assessment are taste by definition (a
    mechanical criterion takes a tier-0 check, not this card); the card's own
    output is evidence-bound and spot-checkable
  recovery: trivial — read-only role; a wrong assessment is caught where the
    doctrine routes acceptance (commander/human), not absorbed silently
  context: fresh by construction — independence from the builder IS the value
tier: mid
capability_surface:
  read_only: true
  tools: [read, search, run-contracted-read-only-commands]
io:
  input: task contract (the criteria) + the builder's artifacts (result
    artifact and every file it references)
  expected_output: per-criterion pass/fail assessment with evidence, as the
    report or a contracted assessment file
when_not:
  - the criterion has a runnable check (tier-0 script, never a model)
  - the assessor shares any conversation state with the builder (defeats the
    card's whole grade)
  - the run-level quality call on the deliverable — that terminates above
    this card (§ Judgment reservation)
  - any other duty in the doctrine's reserved set (§ Judgment reservation)
graded_under:
  doctrine_rev: "2434baf"
  model_gen: "g2026.07"
---

# fresh-verifier — cached grading: fresh-context taste-criterion assessment

One shape, graded once: doctrine § Verification's named default — a
fresh-context assessment of taste criteria, evidence-cited, feeding the
acceptance that stays with commander/human. The grade above is the card's
cache; citing this card in a dispatch plan replaces the three-axis grade
columns. Staleness rule: doctrine § Complexity tiering — Role cards.
