# conductor — Project Instructions

Portable orchestration doctrine (L1 doctrine / L2 file contracts / L3 per-harness
adapters). Inherits all rules from `~/.claude/CLAUDE.md`.

## Status: pre-contract

No contract accepted yet. Next steps, in order:

1. `/touchstone:init` (sets up doc routing for this repo)
2. `/touchstone:crucible` — forge the contract. Primary input: founding research at
   `.touchstone/research/2026-07-09-orchestration-mode.md` (+ worknotes subdir).
3. Build in a fresh session after human accept.

## Standing requirements (from the founding session, 2026-07-10)

- **Portability is the point.** Built first as a Claude Code skill, but L1/L2 must
  stay vendor-neutral so Codex CLI (or another harness) can run the mode with only
  a new L3 adapter. Portability AC shape: same task contract run through the CC
  adapter and the Codex adapter, both producing schema-valid results with the same
  acceptance verdict.
- **Author skills against touchstone's standards**: follow
  `~/claude_code/touchstone/docs/skill-authoring-template.md` and reuse/refer the
  task-contract + result-schema templates in
  `~/claude_code/touchstone/skills/epic-driven-roadmap/templates/`
  (task-contract.md, task-result.json). Whether conductor *refers to* or *vendors
  a provenance-stamped copy of* those templates is a crucible-stage decision — do
  not pick silently.
- **Do not pre-build structure.** The three-layer directory shape in README.md is
  a proposal, not a decision; let the contract settle it.
