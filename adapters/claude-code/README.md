# Claude Code adapter — verification record

This file records which commander×topology combinations have **completed a
protocol run** (`benchmark/protocol.md`): acceptance pass by a
fresh-context judge plus clean isolation/conformance audits, evidenced by
a ledger run_id. **It is a verification record, not a capability claim** —
each line means "this combination ran validly under the protocol at least
once", nothing more. A combination without such evidence never appears
(claim ≤ evidence).

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
```

haiku appears in no line: both haiku cells failed acceptance on this run,
and the M9 judgment-parity matrix independently placed it outside the
validated commander set under both doctrine-only and skill-loaded
conditions.

Binding of dispatch primitives and capability tiers: `binding.md`.
