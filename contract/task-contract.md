---
x_provenance:
  source_repo: touchstone
  source_path: skills/epic-driven-roadmap/templates/task-contract.md
  source_commit: 627524633d2215fa139291109345d4196c4fd00b
  template_version: "1.1"
  vendored_date: 2026-07-10
  modifications: see git history of this file
task_id: <id>
epic: <slug>
role: <role-name>
runtime: <harness-id>
status: pending
created: YYYY-MM-DD
---

# Task Contract: <title>

## Scope
- <repos / directories / modules the implementer may freely modify to satisfy AC>
- Globs and individual files are both legal. New files may be created inside
  Scope without listing them upfront.

## Read-Only Boundaries
- <existing contracts the implementer reads but must not modify>
- Typical: cross-team APIs, public traits, schema definitions, vendored deps.
- If AC appears to require modifying anything here, fail with `risks` naming the
  path and the AC that conflicts.

## Do Not Touch
- <hard safety boundary; off-limits even if technically reachable>
- Stronger than Read-Only: do not even read these for context.
- Typical: `.git/`, sibling-team directories, vendored deps outside Scope.
- Always in force: build artifacts and caches (egg-info, __pycache__, dist/,
  coverage files) are never part of the delivery.

## Acceptance Criteria
- <testable outcomes; the load-bearing source of truth for "done">
- Satisfy these, not a file list.
- Mark each `mechanical:` (attach the runnable check — claiming mechanical
  without a written check is a grading defect) or `taste:` (name the verifier
  route). Unmarked reads as taste.
- **Quote the acceptance source.** Where an AC has a written source, quote its
  operative assertion verbatim and cite it (`source: <file:line>`); excerpt a
  long source and mark the elision, but never paraphrase the operative
  assertion. Where no written source exists, mark the AC `self-authored`.

## Commands to Run
- <verification commands; exit codes captured in result.json>

## Owned Files (optional)
- Use ONLY to pin exact files — parallel implementer dispatch with
  non-overlapping ownership, or an intentionally narrow refactor.
- When present, narrows Scope further: touch only these.
- Default: omit.

## Expected Output
- result.json (schema version 1.1) at this task-dir
- (optional) review file if cross-provider review attached
- **Length.** `summary` is 3–8 sentences. `observations` is unbounded (rule 4).
  A file written to disk matches the length of the artifacts beside it in the
  same directory; where none exist, the Acceptance Criteria set the floor and
  nothing rewards exceeding it.

---

**Implementer behavioral contract** (applies to all runtimes; canonical —
harness-specific role prompts defer here).

**Delivery rule — cite, don't copy.** This contract and the § Scope-Change
Protocol below are invariant boilerplate whose single home is this template. A
per-subtask instance CITES this home by path and never reproduces its text;
every task-specific difference lives in the instance fields. No instance
rewrites, negates, or overrides a numbered rule — a rule that genuinely cannot
fit a task is a doctrine-level change, never a per-instance override.

1. **Free movement within Scope** — create, modify, or delete files inside Scope
   without consulting the planner, as long as AC is met. Every path actually
   written goes into `files_changed`.
2. **Hard stop at Read-Only Boundaries and Do Not Touch** — if AC appears to
   require modifying any of these, do not. Set `status: failed` with `risks`
   naming the path and the AC that conflicts.
3. **Outside-scope necessity → needs-scope-expansion** — if AC requires touching
   a repo or module outside Scope and outside those boundaries (the planner
   missed it), do not modify it. Set `status: needs-scope-expansion`, fill
   `scope_change_request`, and return.
4. **Use `observations`** for any context that doesn't fit
   summary/risks/handoff_notes — unexpected codebase shape, ambiguities resolved
   by judgment, related issues out of scope, design questions. Don't pre-filter;
   the orchestrator skims.
5. **Result discipline** — record every command you ran with its exit code in
   `commands_run`. If the contracted Commands to Run fail, still write a
   schema-valid result at the task dir — `status: failed`, `risks` and/or
   `fallback_reason` filled. Never crash, never leave the task dir without a
   result artifact.

---

## Scope-Change Protocol

When rule 3 fires, the implementer emits a `scope_change_request` in result.json.

| Field | Value |
|---|---|
| `target` | Out-of-scope **repo or module/directory** needed (matches Scope granularity; never a single file). |
| `ac_ref` | AC **ID** that forces this (pointer only — do not restate the AC). |
| `rationale` | The runtime discovery the contract author could not foresee; why `target` is needed. Do not restate `ac_ref`. |
| `reversibility` | `reversible` or `irreversible`. If undeterminable, classify `irreversible`. |
| `reversibility_basis` | Why classed so (e.g. "in-project edit, recoverable via version control" / "force-push, history rewrite"). |
| `alternatives_considered` | In-scope routes tried and rejected, or `none`. |

**Adjudication (orchestrator):** every request stops that line of work and is
escalated to the human verbatim. The orchestrator never approves on the human's
behalf and never re-dispatches enlarged work before the ruling. Approved → amend
Scope and re-dispatch; denied → the task stays `needs-scope-expansion` and the
orchestrator re-plans within the original Scope.

**Ledger:** every request and decision appends one line to
`<workspace>/epics/<slug>/scope-changes.jsonl`:

```
{"ts","task_id","request":{…verbatim…},"decision":"approved|denied","decided_by":"human","decision_reason","scope_amendment","outcome":"redispatched|abandoned|<task_id>"}
```
