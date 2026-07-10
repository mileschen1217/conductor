# conductor

Portable orchestration doctrine for frontier-model commanders — the model judges,
decomposes, dispatches, and synthesizes; workers execute.

Three-layer shape:

- **L1 Doctrine** (`doctrine/`) — vendor-neutral markdown: commander posture,
  entry economic gate, complexity tiering, dispatch contract, report contract,
  escalation ladder, single-writer rule, verification-not-self-verification.
- **L2 Contract** (`contract/`) — files as the interface: task-contract template,
  result schema v1.1, stdlib-only validator + fallback-result generator.
  The filesystem is the only channel every harness shares.
- **L3 Adapters** (`adapters/<harness>/`) — one thin binding per harness:
  dispatch primitive → harness mechanism, capability tier → concrete model.
  New harness = one new adapter; L1/L2 untouched.

## Install

**Claude Code** (official plugin route — the plugin copy carries `doctrine/`
and `contract/` with it):

```
/plugin marketplace add mileschen1217/conductor
/plugin install conductor@conductor
```

Then invoke with `/orchestration-mode`. Alternative for a single project from
a local checkout: `./install.sh claude-code <project-dir>` (symlinks the
adapter as a project skill).

**Codex CLI** (AGENTS.md fragment; needs a local checkout on disk):

```
git clone https://github.com/mileschen1217/conductor && cd conductor
./install.sh codex [path/to/AGENTS.md]     # default: ./AGENTS.md; idempotent
```

The commander-side forwarder recipe lives in `adapters/codex/README.md`.

**What the scripts are** — `scripts/` holds the repo's own quality gates, not
runtime dependencies: `check-neutrality.sh` (vendor-neutrality scan over
doctrine/ + contract/), `test-check-result.sh` (validator fixture suite),
`audit-single-writer.sh` (post-hoc single-writer audit for live runs). Nothing
in `scripts/` needs installing; the pieces adapters call at runtime are
`contract/check-result.py` and `contract/make-fallback-result.py`, which
travel with the repo/plugin copy.

Related: [touchstone](https://github.com/mileschen1217/touchstone) — honesty
overlay on V&V. conductor deliberately lives outside it: dispatch doctrine and
honesty gates are orthogonal concerns.
