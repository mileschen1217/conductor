---
task_id: example-2
epic: consumer-gated-ceremony
role: mech-writer
runtime: <harness-id>
status: pending
created: 2026-07-22
---

# Task Contract: split the helper the commander carved out

## Scope
- scripts/ — the carved-out helper only

## Read-Only Boundaries
- contract/ — read for context, do not modify

## Do Not Touch
- .git/

## Acceptance Criteria
- taste: the extracted helper has one responsibility and its callers still pass (self-authored — the commander decomposed this subtask; no written upstream source to quote)

## Commands to Run
- bash scripts/test-x.sh

## Expected Output
- result.json (schema version 1.1) at this task-dir

---

**Implementer behavioral contract:** cited, not copied — see
`<conductor>/contract/task-contract.md § Implementer behavioral contract`.
