# Claude Code adapter — verification record

This file records which commander×topology combinations have **completed a
protocol run** (`benchmark/protocol.md`): acceptance pass by a
fresh-context judge plus clean isolation/conformance audits, evidenced by
a ledger run_id. **It is a verification record, not a capability claim** —
each line means "this combination ran validly under the protocol at least
once", nothing more. A combination without such evidence never appears
(claim ≤ evidence).

**Every line below predates the pay-at-first-dispatch cut (0.7.0)** and is
written in the vocabulary of the doctrine revision it ran under — including
forms such as the "0-worker" ceremony-bearing run, which no longer exists (a
run that never dispatches does not enter the mode). A verification record is
history: it is never rewritten to match current vocabulary, and the
measurements remain valid measurements of what they measured.

Scope honestly stated: the evidence below is n=1 per cell, one task family
(read-heavy repository audit), one date. The protocol's comparative cost
formula (R3) **failed for every v2-form pair on this run** — v2-form cost
2–5× its inline counterpart at not-worse quality; the human rulings are in
the run ledger. The ledger itself (`benchmark/ledger.jsonl`) is maintained
locally by each operator and does not ship (its rows reference local
artifacts).

```
verified-run: sonnet×inline — ledger bench-audit-002-2026-07-12
verified-run: fable×inline — ledger bench-audit-002-2026-07-12
verified-run: opus×inline — ledger bench-audit-002-2026-07-12
verified-run: fable×v2-form — ledger bench-audit-002-2026-07-12
verified-run: opus×v2-form — ledger bench-audit-002-2026-07-12
verified-run: sonnet×v2-form — ledger bench-audit-002-2026-07-12
verified-run: opus×inline+v3form — doctrine 33ec134 — ledger v3-regression-2026-07-17
verified-run: opus×conductor-v3 — doctrine 33ec134 — ledger v3-regression-2026-07-17
verified-run: opus×forced-1-worker — doctrine 33ec134 — ledger v3-regression-2026-07-17
verified-run: opus×inline+v4form — doctrine e7f60ae — ledger v4pair-2026-07-18
verified-run: opus×inline+v5form — doctrine 2434baf — ledger cgc-rerun-2026-07-23
verified-run: opus×inline+v5form+verifier — doctrine 2434baf — ledger cgc-rerun-2026-07-23
```

The three v3 lines (arm names as in `benchmark/protocol.md` § v3
regression) ran a write-heavy task family (distill kernel build, frozen
spec) under plugin 0.3.0 installed from the published marketplace;
judgment claims do not cross doctrine revisions, hence the explicit rev
stamp. Stamp provenance disclosed: the runs' own commander_stamp lines
recorded the plugin version (`0.3.0`), not the doctrine commit — the
installed plugin carries no git history, a known binding gap queued in
the run's findings; `33ec134` was resolved from the publishing repo's
history and byte-matches the doctrine file the plugin shipped. The
1-worker line is a veto-forced topology (governed operator override
recorded in the run's brief and in its dispatch-plan deviation log,
entry DEV-2), verified as a run record like any other — its
fresh-context judge verdict (flawed: one gaming finding in the worker's
output) ships with the ledger row, not hidden by the line.

The v4pair line ran the same write-heavy task family twice (interleaved
pairs against a bare-inline floor) under plugin 0.4.0 from the published
marketplace; `e7f60ae` is the shipped `doctrine/REV` stamp, byte-matched
in the installed plugin cache before launch. On this run the protocol's
fresh-context comparison judge was replaced by the deterministic held-out
suite (judge pass skipped by ruling — see the findings doc). It is a
verification record, not a capability claim: that run measured a POSITIVE discipline price
(+33%/+62% over the floor, one real held-out test lost per form arm) —
the finding and its cost decomposition live in
`benchmark/findings/2026-07-18-distill-kernel-v4pair-discipline-price.md`.

The two v5form lines ran the same write-heavy task family under plugin
0.5.0 from the published marketplace; `2434baf` is the shipped
`doctrine/REV` stamp, verified in the install before launch. They are two
DIFFERENT topologies, not two samples of one: the first is the compliant
0-worker consumer-gated form (zero write dispatch, no contract or result
paper, reconciliation vacuous); the second adds one read-only
fresh-context acceptance verifier on a task whose acceptance criteria are
all mechanical — a dispatch the doctrine does not mandate there. Both held
the frozen suite at 133/0. Verification record, not capability claim: the
compliant form measured **+22.2%** over the floor and the over-verifying
one **+80.1%** — a documented band miss, accepted as an honest negative;
the accounting is in
`benchmark/findings/2026-07-23-consumer-gated-ceremony-rerun.md`.

haiku appears in no line: both haiku cells failed acceptance on this run,
and the M9 judgment-parity matrix independently placed it outside the
validated commander set under both doctrine-only and skill-loaded
conditions.

Binding of dispatch primitives and capability tiers: `binding.md`.
