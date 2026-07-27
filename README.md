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
- **Surface** — the residual judgment moments are enumerated rather than left
  to notice, and the commander states each one and its own ruling where a
  human can see it (the escalation ladder).
- **Contain** — the moments nobody notices are the irreducible residue; they
  are not judged but insured: bounded scope, mechanical acceptance nets, cheap
  recovery, honest failure (the insurance).

Most systems only define in-scope behavior and leave out-of-scope to luck.
conductor's distinguishing bet is that **out-of-scope events get defined
behavior too** — a hard stop, an honest `failed`, an escalation to a human,
never a silent improvisation. Shrink the world; price the exits.

## The value claim — and its honest status

conductor's founding claim: **a commander that judges, plus cheaper workers
that execute, delivers the same quality at lower cost** than one strong model
doing everything inline. This claim is the project's fixed star. Every
mechanism, epic, and benchmark must name how it serves the claim — anything
that serves only the mode's own bookkeeping does not enter.

Its honest status, kept under this project's own rule (claim ≤ evidence):
**pursued, not yet achieved.** The claim can only win where delegated volume
is high and workers are genuinely cheaper — `saving = Σ Wᵢ × (1 − rᵢ)`: a run
that dispatches nothing saves nothing by construction, and a low-volume
dispatch prices as a loss before quality enters. The measured record so far
covers exactly those two losing regions; the high-volume region is the open
frontier being built toward. The first structural consequence has already
landed: **a run that never dispatches is not in the mode**, so it pays
nothing — coordination machinery is charged to delegation, which is the only
thing it can pay for. That the claim is reachable at all has an
external existence proof: Anthropic reports an orchestrator/worker split
(strong-model commander, one-tier-down workers) retaining ~96% of quality at
~46% of cost on a search benchmark.

## Implementation ethos — thin skill, thin prompt, thick artifact

Three commitments that decide what gets built — and what gets deleted:

- **Thin skill.** An adapter binds the dispatch primitive to a harness
  mechanism and resolves tiers to concrete models — nothing else. Procedure
  that accretes in an adapter is debt, not capability.
- **Thin prompt.** Ceremony is priced in round-trips, not bytes, and every
  piece of bookkeeping must have a consumer. Bookkeeping without a consumer
  is deleted, not discounted.
- **Thick artifact and context.** The weight belongs in the files that cross
  context boundaries — task contracts, results, the journal. They carry the
  full context a worker needs and the full evidence an auditor needs; the
  prompts around them stay thin precisely because the artifacts are thick.

Drift check: a change that fattens a skill or prompt while thinning the
artifacts is moving backward, whatever else it improves.

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
doctrine/ + contract/), `check-role-cards.sh` (judgment-face scan over the L2
role cards), `check-doctrine-rev.sh` (guards that the shipped `doctrine/REV`
stamp matches the doctrine file's last-change commit), `test-check-result.sh`
(validator fixture suite), `audit-single-writer.sh` (post-hoc single-writer
audit over an instrumented run's journal), and `test-close-chain.sh` (proves
the close audit chain reports the same per-member exit codes under bash and
zsh). Nothing
in `scripts/` needs installing; the pieces adapters call at runtime are
`contract/check-result.py` and `contract/make-fallback-result.py`, which
travel with the repo/plugin copy.

Related: [touchstone](https://github.com/mileschen1217/touchstone) — honesty
overlay on V&V. conductor deliberately lives outside it: dispatch doctrine and
honesty gates are orthogonal concerns.
