---
x_provenance:
  source_repo: touchstone
  source_path: skills/epic-driven-roadmap/templates/task-contract.md
  source_commit: 627524633d2215fa139291109345d4196c4fd00b
  template_version: "1.1"
  vendored_date: 2026-07-10
  modifications:
    - "runtime enum genericized to <harness-id> (neutrality invariant I1)"
    - "behavioral-contract intro: harness-specific aside genericized"
    - "Scope-Change Protocol adjudication aligned to governing spec AC-11/I3: all requests escalate to the human; no orchestrator auto-approval"
    - "seam sentence: harness noun genericized"
    - "dropped tool-internal cross-reference (CONTEXT.md pointer)"
    - "scope-changes ledger path made workspace-convention-relative"
    - "source_repo recorded by repo identity, not local disk path: the checkout path contains a term this repo's neutrality scan bans; full local path in the vendor commit message (outside scan scope)"
    - "Do Not Touch category example generalized: 'vendored crates' → 'vendored deps' (language-ecosystem-specific noun removed)"
    - "Expected Output normalized: schema version stated as 1.1 (source text said '1' while the source schema file is 1.1 — source-internal inconsistency resolved toward the file); 'review.md' → 'review file'"
    - "reversibility_basis example wording: 'git-recoverable' → 'recoverable via version control' (tool-neutral phrasing, same spirit as the seam-sentence modification)"
    - "behavioral-contract rule 5 (result discipline: commands_run recording + failure-still-writes-valid-result) added: the vendor source leaves these worker duties implicit; the single-home requirement moved them from adapter worker prompts into this contract (human ruling D1, 2026-07-10)"
    - "2026-07-11 (v2 spec REQ-2/REQ-3): AC mechanical/taste marking convention added (taste criterion home: doctrine § Capability tiers); optional Advisor Scope section added (worker tactical consult declaration + disclosure duty)"
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
- Globs and individual files are both legal. Implementer may create new files inside Scope without listing them upfront.

## Read-Only Boundaries
- <existing contracts the implementer reads but must not modify>
- Category: cross-team APIs, public traits, schema definitions, vendored deps in this repo.
- If AC appears to require modifying anything here, implementer must fail with `risks` naming the path and the AC that conflicts.

## Do Not Touch
- <hard safety boundary; off-limits even if technically reachable>
- Stronger than Read-Only — implementer should not even read these for context.
- Category: `.git/`, sibling-team directories, vendored deps outside Scope.
- Always in force: build artifacts and caches (egg-info, __pycache__, dist/, coverage files) are never part of the delivery — do not commit them, whatever the write surface says.

## Acceptance Criteria
- <testable outcomes; load-bearing source of truth for "done">
- ACs from the spec/plan; implementer's job is to satisfy these, not to match a file list.
- Mark each AC `mechanical:` (attach the runnable check — pattern match / exit code; claiming mechanical without a written check is a grading defect) or `taste:` (name the verifier route: fresh-context worker, orchestrator, or human). Unmarked = taste (fail-safe default).

## Commands to Run
- <verification commands; exit codes captured in result.json>

## Advisor Scope (worker tactical) (optional)
- tactical_consults_declared: <n> (omit section entirely when the worker gets no advisor)
- Worker-layer consults are tactical ONLY. Contract-interpretation or acceptance-interpretation questions escalate through the status protocols (rules 2/3), never through the advisor. Every consult is disclosed in result.json `judgment_events`; disclosed overage beyond <n> is calibration data; undisclosed use is a violation.

## Owned Files (optional)
- Use ONLY when you need to pin exact files — e.g., parallel implementer dispatch with non-overlapping ownership, or an intentionally narrow refactor.
- When present, narrows Scope further: implementer must touch only these files.
- Default: omit. Scope + AC + Read-Only Boundaries + Do Not Touch are sufficient for most contracts.

## Expected Output
- result.json (schema version 1.1) at this task-dir
- (optional) review file if cross-provider review attached

---

**Implementer behavioral contract** (applies to all runtimes; canonical — harness-specific role prompts defer here):

1. **Free movement within Scope** — create, modify, or delete files inside Scope without consulting the planner, as long as AC is met. Every path actually written goes into `files_changed`.
2. **Hard stop at Read-Only Boundaries and Do Not Touch** — if AC appears to require modifying any of these, do **not** modify. Set `status: failed` with `risks` naming the path and the AC that conflicts.
3. **Outside-scope necessity → needs-scope-expansion** — if AC requires touching a repo or module outside Scope (not in Read-Only Boundaries / Do Not Touch — i.e. the planner missed it), do **not** modify it. Set `status: needs-scope-expansion`, fill `scope_change_request` (see § Scope-Change Protocol), and return. (Read-Only / Do Not Touch conflicts are different — those mean the AC itself is wrong → rule 2 `failed`.)
4. **Use `observations`** for any context that doesn't fit summary/risks/handoff_notes — unexpected codebase shape, ambiguities resolved by judgment, related issues out of scope, design questions, anything you'd tell the next implementer if you could chat. Don't pre-filter; the orchestrator skims.
5. **Result discipline** — record every command you ran with its exit code in `commands_run`. If the contracted Commands to Run fail, still write a schema-valid result at the task dir — `status: failed`, `risks` and/or `fallback_reason` filled — never crash, never leave the task dir without a result artifact.

---

## Scope-Change Protocol

When rule 3 fires, the implementer emits a `scope_change_request` in result.json.

**`scope_change_request` (implementer fills):**

| Field | Value |
|---|---|
| `target` | Out-of-scope **repo or module/directory** needed (matches Scope granularity; never a single file). |
| `ac_ref` | AC **ID** that forces this (pointer only — do not restate the AC). |
| `rationale` | The runtime discovery the contract author could not foresee; why `target` is needed. Do not restate `ac_ref`. |
| `reversibility` | `reversible` or `irreversible`. If you cannot determine it, classify `irreversible`. |
| `reversibility_basis` | Why classed so (e.g. "in-project edit, recoverable via version control" / "force-push, history rewrite"). |
| `alternatives_considered` | In-scope routes tried and rejected, or `none`. |

**Adjudication policy (orchestrator):** every scope-change request stops that line of work and is escalated to the human with the request verbatim. The orchestrator never approves on the human's behalf and never re-dispatches enlarged work before the human rules. After a human ruling: approved → amend Scope + re-dispatch; denied → the task stays `needs-scope-expansion` and the orchestrator re-plans within the original Scope.

**Ledger:** every request + decision appends one line to `<workspace>/epics/<slug>/scope-changes.jsonl` (audit + epic-close retro):

```
{"ts","task_id","request":{…verbatim…},"decision":"approved|denied","decided_by":"human","decision_reason","scope_amendment","outcome":"redispatched|abandoned|<task_id>"}
```

**Seam:** this protocol organizes intent + auditability only. Preventing an unauthorized irreversible action is the harness's permission layer / sandbox / version control (operator-configured), not this protocol.
