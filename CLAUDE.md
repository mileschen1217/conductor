# conductor — Project Instructions

Portable orchestration doctrine (L1 doctrine / L2 file contracts / L3 per-harness
adapters). Inherits all rules from `~/.claude/CLAUDE.md`.

## Status: contract accepted — ready for Build

Contract accepted 2026-07-10 (crucible complete: assay → design-spec →
2-round cross-provider design-review C+H=0 → human accept).

**Next step (fresh session): `/touchstone:anvil` on the accepted spec:**
`.touchstone/specs/2026-07-10-orchestration-mode-design.md`
(3 stories → 7 REQs → 13 ACs; live-bearing: AC-2/6/7/8/10/12/13)

Companion records:
- ADR 0001 (three-layer file-contract architecture, accepted):
  `.touchstone/docs/adr/0001-three-layer-file-contract-architecture.md`
- Assay record (guardrail block, flip-triggers FT-1/2/3, deferred D-1/2/3):
  `.touchstone/epics/orchestration-mode/assay-2026-07-10-orchestration-mode.md`
- Design-review trail: `.touchstone/epics/orchestration-mode/design-review-2026-07-10/`
- Epic tracker: `.touchstone/epics/orchestration-mode/index.md` (Phase 2 = Build)

## Doc Routing

Workspace root `.touchstone/` (see `.claude/touchstone.yaml`): specs →
`.touchstone/specs/`, ADR drafts → `.touchstone/docs/adr/`, epics →
`.touchstone/epics/`, plans → `.touchstone/plans/`, research →
`.touchstone/research/`.

## Standing requirements (from the founding session, 2026-07-10)

- **Portability is the point.** Built first as a Claude Code skill, but L1/L2 must
  stay vendor-neutral so Codex CLI (or another harness) can run the mode with only
  a new L3 adapter. Portability AC shape: same task contract run through the CC
  adapter and the Codex adapter, both producing schema-valid results with the same
  acceptance verdict.
- **Author skills against touchstone's standards**: follow
  `~/claude_code/touchstone/docs/skill-authoring-template.md`. The task-contract +
  result-schema templates from
  `~/claude_code/touchstone/skills/epic-driven-roadmap/templates/` are **vendored**
  (provenance-stamped copy in `contract/`) — decided at assay 2026-07-10, do not
  revert to refer-by-path.
- **Structure is settled**: three-layer shape (L1 `doctrine/` / L2 `contract/` /
  L3 `adapters/` + `benchmark/`, `scripts/`) is now contractual — ADR 0001 +
  accepted spec § Scope are authoritative, not README.md.
