---
task_id: example-1
epic: consumer-gated-ceremony
role: mech-writer
runtime: <harness-id>
status: pending
created: 2026-07-22
---

# Task Contract: apply the recipe to scripts/x.py

## Scope
- scripts/ — the enumerated targets only

## Read-Only Boundaries
- doctrine/, contract/ — read for context, do not modify

## Do Not Touch
- .git/

## Acceptance Criteria
- mechanical: `bash scripts/test-x.sh` exits 0
  > every target file ends with a trailing newline
  source: .touchstone/specs/2026-07-21-example.md AC-3

## Commands to Run
- bash scripts/test-x.sh

## Owned Files
- scripts/x.py

## Expected Output
- result.json (schema version 1.1) at this task-dir

---

**Implementer behavioral contract:** cited, not copied — obey the canonical
rules at `<conductor>/contract/task-contract.md § Implementer behavioral
contract` (and its § Scope-Change Protocol). Not reproduced in this instance.
