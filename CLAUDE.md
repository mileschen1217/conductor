# conductor — Project Instructions

Portable orchestration doctrine: a frontier-model commander judges, decomposes,
dispatches, and integrates; workers execute. Three layers, file contracts between
them (see README.md):

- `doctrine/orchestration-mode.md` — L1, vendor-neutral single home of mode
  behavior. Adapters cite it; nothing restates it.
- `contract/` — L2, the only commander↔worker data interface: task-contract
  template, result schema v1.1, `check-result.py` (stdlib-only validator; run
  `bash scripts/test-check-result.sh` for its fixture suite).
- `adapters/<harness>/` — L3, one thin binding per harness: dispatch primitive →
  harness mechanism, capability tier → concrete model (`binding.md`). Harness
  nouns are legal ONLY here.

## Hard rules

- **Vendor neutrality (invariant I1):** `doctrine/` and `contract/` must contain
  zero harness-specific nouns. Gate: `bash scripts/check-neutrality.sh` (must
  print CLEAN; `--self-test` proves the scanner is alive). The banned-term list
  lives only in that script; changing it is a spec-level decision.
- **Single-writer (I2):** parallel fan-out is read-only; all writes single-
  threaded. Post-hoc check: `bash scripts/audit-single-writer.sh <journal.jsonl>`.
- **Judgment reservation (I3):** permission, contract changes, and quality
  verdicts stay with the commander/human — never delegated to workers.
- L1/L2 are the single homes; edit them there, never in an adapter.
