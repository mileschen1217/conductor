# Orchestration Mode — Doctrine (L1)

Single home for mode behavior: the commander judges, decomposes, dispatches,
integrates — and never executes the grunt work personally. This layer is
harness-neutral: it speaks only in capability tiers and one dispatch
primitive. Adapters bind those two abstractions to a concrete harness; an
adapter may cite this doctrine, never restate it.

**commander** — the orchestrating model instance (synonym: orchestrator).
**worker** — a model instance executing exactly one task contract.
**human** — the adjudication layer above the commander; the last word on
entry, permission, contract changes, and quality.

## Entry gate

Mode entry is a judged decision, never a default. Before ANY dispatch, the
commander evaluates two disqualifiers and presents the call to the human:

1. **Predictable decomposition** — the complete subtask list can be enumerated
   before any worker runs, AND no subtask depends on another subtask's
   findings. If true: do NOT open the mode; run the light path (direct
   execution or a scripted batch).
2. **Insufficient value** — the mode's token premium (research reference:
   ~15× a single-context run) is not repaid by the task's value. No
   quantitative coefficient exists yet; the decidable form is: the commander
   states a named reason, and the human can veto.

Record every entry decision in the audit surface (§ Audit surface): open or
not-open, plus named reasons against BOTH disqualifiers ("open" must state why
neither disqualifier holds). "Not-open" produces zero worker dispatches. A
human veto is recorded — who, changed to what, why — and governs: act on the
human's ruling, not the original recommendation.

## Complexity tiering

Grade every subtask BEFORE its wave dispatches. Planning may roll forward in
waves — grade and route each wave before it launches; later waves may evolve
from earlier waves' findings (that evolution is exactly the mode's home turf —
a plan fully writable upfront belongs to the light path).

Grading signals: breadth of files/sources touched, degree of path-dependency,
output shape.

| Grade | Meaning | Spawns per subtask |
|---|---|---|
| simple | single-fact lookup; one known target | 1 |
| comparative | multi-source cross-check | 2–4 |
| complex | open-ended, multi-file / multi-domain | 10+ |

Concurrency hard cap: **5 simultaneous workers** (default; 3–5 is the
recommended operating band). The cap bounds simultaneous workers; a complex
subtask's 10+ spawns queue through it.

## Capability tiers

Routing speaks ONLY in tiers: **frontier / mid / cheap**. A concrete model
name never appears at this layer; each harness's binding table maps every
tier to ≥1 concrete model.

| Task shape | Tier |
|---|---|
| judgment, decomposition, integration, first-time diagnosis, architecture trade-offs, cross-file invariants | frontier (usually the commander itself) |
| clear-spec implementation, search/inventory, multi-source research, review lenses | mid (default worker) |
| batch application of an already-solved pattern; format conversion; mechanical enumeration | cheap |

Cheap-tier red line: work needing judgment, first encounters, or a fuzzy
recipe never goes to cheap. Cheap's correct use is: frontier/mid has solved
the pattern into an exact recipe → cheap applies it in batch.

## Dispatch primitive

**dispatch** := write a task-contract file into the task directory → start
one worker on it through the harness mechanism → wait for result.json to land
and validate it with the contract checker. Only the middle step is
harness-bound (adapter territory); the first and last steps are pure file
operations, identical everywhere.

## Dispatch contract

Every dispatch carries four elements, mapped to task-contract fields. A
dispatch missing any element is defective — fix it before sending.

| Element | Contract field |
|---|---|
| objective & motivation | Scope |
| output format | Acceptance Criteria |
| tool & source guidance | Commands to Run + Read-Only Boundaries |
| task boundary | Do Not Touch + Owned Files |

## Report contract

Artifacts over relay: worker products land on the filesystem; result.json
carries light references (paths), never bulk content. The filesystem is the
ONLY commander↔worker communication surface. A worker's report is its
result.json — summary, files_changed, commands_run (with exit codes), risks,
observations.

## Escalation ladder

- Cheap errs once on a subtask → escalate that subtask to mid. No retry at cheap.
- Mid errs twice on the same subtask → escalate to frontier WITH the full
  failure trail: what was tried, exact commands, exact errors, hypotheses
  already excluded. An escalation without the trail makes frontier guess from
  zero — wasted.
- Same approach: at most 3 attempts total (initial + 2 retries) per
  subtask × approach. A genuinely different approach resets the count.
- Timeout / no response counts as an error at that tier.
- De-escalation: a solved pattern gets written as an exact recipe (with
  verification commands) and demoted to mid/cheap batch application.

## Single-writer rule

Parallel fan-out is read-only; ALL writes are single-threaded. No two workers
ever hold write access to the same working tree at the same time.

Adapters SHALL enable preventive enforcement where the harness supports it
(read-only worker toolsets, read-only sandbox modes) and SHALL record that
configuration in each run's dispatch records. The portable acceptance check
is post-hoc audit: worker transcripts of every parallel phase show zero file
writes; all writes trace to single-threaded phases.

## Judgment reservation

Permission grants, contract changes, and quality verdicts are NEVER delegated
to workers or automation. The commander holds them; the human overrules the
commander.

- A result.json with a non-empty scope_change_request stops that line of work
  immediately. The commander escalates the request verbatim to the human —
  never approves in the human's stead, never re-dispatches enlarged work
  before the ruling.
- Quality verdicts on deliverables terminate at the human.

## Verification

The builder never accepts its own work. Acceptance goes to a fresh-context
worker — one sharing no conversation state with the builder — which reads the
contract's acceptance criteria and judges each against the artifacts,
citing evidence (file:line or command output). "Reads as correct" is not
evidence; execution output is.

## Audit surface (dispatch-plan)

The commander keeps `dispatch-plan.md` in the task directory:

1. **Entry decision** — open/not-open, named reasons against both
   disqualifiers, human veto record if any (who / changed-to / reason).
2. **Subtask table** — one row per dispatched subtask:
   `| subtask | grade | tier | resolved model | contract path | wave |`
   (resolved model comes from the harness binding table at dispatch time).
3. **Deviation log** — entry misjudgments (e.g. decomposition turned out
   predictable → fall back to the light path, don't force the mode),
   escalations, scope-change rulings.
