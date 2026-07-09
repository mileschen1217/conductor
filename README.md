# conductor

Portable orchestration doctrine for frontier-model commanders — the model judges,
decomposes, dispatches, and synthesizes; workers execute.

Three-layer shape (contract to be settled via design spec; see founding research):

- **L1 Doctrine** — vendor-neutral markdown: commander posture, dispatch contract,
  report contract, escalation, verification-not-self-verification, plus the three
  rules external research adds (spawn tiering, single-writer, economic gate).
- **L2 Contract** — files as the interface: task contract + result schema.
  The filesystem is the only channel every harness shares.
- **L3 Adapters** — one thin shell per harness (Claude Code skill, Codex CLI
  TOML/AGENTS.md, …). New harness = one new adapter; L1/L2 untouched.

Founding research (aim, boundaries, construction guidance, portability evidence):
`.touchstone/research/2026-07-09-orchestration-mode.md` (local, not committed).

Related: [touchstone](https://github.com/mileschen1217/touchstone) — honesty
overlay on V&V. conductor deliberately lives outside it: dispatch doctrine and
honesty gates are orthogonal concerns. Reference direction between the two repos
is a design decision, settled in the contract stage.
