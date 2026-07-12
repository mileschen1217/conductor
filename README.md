# conductor

Portable orchestration doctrine for model commanders — the model judges,
decomposes, dispatches, and synthesizes; workers execute.

## The principle

Any finite agent's reliability is a function of one ratio: the size of the
decision space it faces over the capacity it brings. You cannot make a model
smarter at runtime — but you can shrink the world it must judge, and you can
price what happens when reality steps outside that world. conductor is
institution design applied to models, the same technology human organizations
have always used to get reliable outcomes from bounded agents:

- **Freeze** — decisions whose inputs exist at plan time are made once, ahead,
  and carried as contracts (the checklist).
- **Mechanize** — acceptance that can be written as a check is run as a check,
  never re-judged (the audit).
- **Consult** — the residual judgment moments are pulled from a stronger judge
  on demand, and journaled (the escalation ladder).
- **Contain** — the moments nobody notices are the irreducible residue; they
  are not judged but insured: bounded scope, mechanical acceptance nets, cheap
  recovery, honest failure (the insurance).

Most systems only define in-scope behavior and leave out-of-scope to luck.
conductor's distinguishing bet is that **out-of-scope events get defined
behavior too** — a hard stop, an honest `failed`, an escalation to a human,
never a silent improvisation. Shrink the world; price the exits.

## Three-layer shape

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
