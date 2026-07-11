# Orchestration Mode — Doctrine (L1)

Single home for mode behavior: the commander judges, decomposes, dispatches,
integrates — and never executes the grunt work personally. This layer is
harness-neutral: it speaks only in capability tiers, one dispatch primitive,
and one advisor primitive. Adapters bind these abstractions to a concrete
harness; an adapter may cite this doctrine, never restate it.

**commander** — the orchestrating model instance (synonym: orchestrator).
**worker** — a model instance executing exactly one task contract.
**advisor** — a frontier-tier model instance the commander (or, within a
declared tactical scope, a worker) consults for a ruling at an enumerated
judgment moment. A ruling is an input to the caller, never a verdict.
**human** — the adjudication layer above the commander; the last word on
entry, permission, contract changes, and quality.

Judgment has three homes, and every judgment moment is routed to one of them:
**frozen ahead** (the task contract), **mechanized** (a checker / tier-0
script), or **purchased on demand** (the advisor). What remains after routing
is exactly the commander's own load — and the reserved set (§ Judgment
reservation) that always terminates at the human.

## Entry gate

Mode entry is a judged decision, never a default — but the gate's output is a
**topology**, not a yes/no on task shape. Grading covers both self-decomposed
work and pre-planned work (an externally supplied plan is graded per task,
never re-decomposed for its own sake). Predictable decomposition is NOT a
refusal ground: predictable + mechanically acceptable is where the safety net
is strongest and cheap tiers are most legal.

**Write shape** (where the pen lives — the gate's primary output):

| Shape | Meaning |
|---|---|
| inline | the commander keeps the pen. This is the mode's 0-worker form: contract, entry gate, journal, checker, and result discipline still apply. |
| 1-worker | one dispatched writer, serialized. |
| disjoint-write | multiple writers on non-overlapping write surfaces, one writer per surface. An isolated working copy (e.g. a separate worktree) is one mechanical carrier; the merge-back is itself a single-writer step. |

**Read breadth** (orthogonal dial): 0..k read-only workers, attachable to ANY
write shape. Paying k fresh contexts is legal ONLY for (a) wall-clock, or
(b) the corpus exceeds a single context. Every parallel dispatch cites its
legal ground in the dispatch plan — wall-clock or corpus for read breadth,
non-overlapping write surfaces for disjoint-write.

**Execution config recommendation:** alongside the write shape the gate
names read breadth, worker count, worker tiers, and the advisor setup.

**The sole refusal ground** is task value below the measured discipline
price — the ablation-measured unit price of the mode's own overhead
(contract + gate + journal + checker + result discipline, measured as the
cost delta between the mode's 0-worker form and bare inline on the same
task). A refusal cites the measured number and routes to the light path.
Before that number exists, refusal is disabled: the gate may only annotate
`[pending-measurement]`, never refuse.

Record every entry decision in the audit surface (§ Audit surface):
topology + execution config + named grounds. A human veto is
recorded — who, changed to what, why — and governs.

## Complexity tiering

Grade every subtask BEFORE its wave dispatches, on three axes:

| Axis | Question | Toward cheap/mechanized | Toward frontier/human |
|---|---|---|---|
| verifiability | is acceptance mechanical — a written, runnable check? | check artifact exists; exit code decides | taste verdict; no check writable |
| recovery cost | if the worker is wrong, what does detection + undo cost? | reversible via version control; blast radius one file | irreversible or outward-facing; cross-file invariants |
| context economics | does the work fit one context? what re-reading tax does each extra context pay? | small closed corpus; recipe known | corpus exceeds context; path-dependent exploration |

Planning may roll forward in waves — plan → dispatch → harvest → re-judge;
grade and route each wave before it launches; later waves may evolve from
earlier waves' findings. The wave boundary is where judgment moments live.

Grading output per subtask: capability tier (§ Capability tiers), read-only
or write role within the chosen write shape, and a `why-not-a-script` answer
(anything gradeable to tier-0 is a script, never a model dispatch).

Concurrency hard cap: **5 simultaneous workers** (default; 3–5 recommended
operating band).

## Capability tiers

Routing speaks ONLY in tiers. A concrete model name never appears at this
layer; each harness's binding table maps every model tier to ≥1 concrete
model.

| Tier | Task shape |
|---|---|
| tier-0 (deterministic script) | acceptance, counting, format checks, any decision already expressible as a written command with an exit code. Not a model. Cheapest, fully auditable — always preferred where it exists. |
| frontier | judgment, decomposition, integration, first-time diagnosis, architecture trade-offs, cross-file invariants (usually the commander itself, or the advisor) |
| mid | clear-spec implementation, search/inventory, multi-source research, review lenses (default worker) |
| cheap | batch application of an already-solved pattern; format conversion; mechanical enumeration |

Cheap-tier red line: work needing judgment, first encounters, or a fuzzy
recipe never goes to cheap.

**Taste criterion (the mechanical/taste boundary):** an acceptance criterion
is *mechanical* iff a runnable check (pattern match / exit code) is actually
written for it. Claiming mechanical without the check artifact is a grading
defect. The default direction is taste (fail-safe): an AC without a check
artifact routes to a named verifier — fresh-context worker, commander, or
human — recorded in the contract. Grading is an authoring act: where
a runnable check is writable, the grader writes it at grading time and
the criterion is mechanical — a criterion never passes as mechanical on
promise alone. Taste is the terminal grade only where no runnable check
can be written (the judgment itself is the acceptance).

## Advisor primitive

The advisor call is the dispatch primitive's inverse: dispatch pushes frozen
judgment down into a fresh small context (cheap, scalable); an advisor call
sends the caller's full context up for a ruling (expensive, rationed by
accounting). Transport is a binding concern — this layer never names it.

**Call sites (closed enum):** `entry-gate | grading-dispute | worker-blocked
| acceptance-ambiguity | scope-change-preview`.

**Protocol (commander side):** for every RECOGNIZED judgment moment the
commander writes a `judgment_moment` journal line — `moment_id` monotonically
increasing — with a disposition: `frozen | mechanized | advisor | blocked`.

- disposition `advisor` → write `advisor_intent` (decision_type + why)
  BEFORE the call; the ruling lands as an `advisor_ruling` line whose payload
  validates against the contract layer's advisor-ruling schema. One consult
  per `moment_id`; a second consult on the same moment is a protocol
  violation (the runaway loop's only true form — killed here, no global
  limiter needed). Pairing in every audit is by `moment_id`, never adjacency.
- disposition `blocked` → `blocked_to_human` line; the moment terminates at
  the human (§ Judgment reservation).
- Transport not attached / pairing illegal → `advisor_unavailable` line +
  confidence-degraded note; the commander proceeds on its own judgment
  (delivery-first), never silently. If the moment is itself
  judgment-reserved, it goes to the human regardless of advisor state.

Unrecognized moments (the commander never saw the decision point) are the
fourth class: no journal line exists, so no audit can see them — they are
governed by containment (the containment-check line, § Audit surface),
not by the judgment-flow audit. This boundary is honest, not
accidental.

**Attention threshold** (default **3**; a dispatch plan may override it in
writing): the counter is the count of `advisor_intent` lines in the current
run journal — the journal IS the counter; no second mutable state exists.
Crossing NEVER blocks a call or delivery: the call executes, an
`advisor_threshold` line lands at the crossing, and the harvest report
surfaces it as a calibration signal. Budget governance is accounting +
calibration; the only mandatory mid-run stop is a judgment-reserved moment.

**I3 boundary:** a ruling is an input. Permission grants, contract changes,
and final quality verdicts do not move because an advisor exists.

**Worker→advisor path (contract-governed):** the task contract declares the
worker's tactical advisor scope; the worker discloses every consult in
result.json `judgment_events`. The worker layer may consult tactically ONLY —
contract-interpretation and acceptance-interpretation moments escalate
(blocked / scope protocols), never consult. Worker consults do NOT count
against the commander's per-run threshold (different context, different
economics); harvest folds their counts into the run report as a separate
worker-consult metric feeding calibration. Disclosed overage beyond the
declared scope is calibration data; undisclosed use is a VIOLATION — the
honesty red line, audited post-hoc against the harness's observation surface
where the binding has one (a binding without one degrades that check to
UNVERIFIABLE, never CLEAN).

## Dispatch primitive

**dispatch** := write a task-contract file into the task directory → start
one worker on it through the harness mechanism → wait for result.json to land
and validate it with the contract checker. Only the middle step is
harness-bound (adapter territory); the first and last steps are pure file
operations, identical everywhere.

**Attributability (a duty of every dispatch, not a nicety):** what starts the
worker must carry its `task_id` in a form the harness's own execution record
preserves — so that after the run, anything the worker did can be joined back
to the task it did it for. Without that carrier the worker's advisor use
cannot be attributed to any task, and the disclosure audit is UNVERIFIABLE by
construction: not "probably fine", *unauditable*. The concrete carrier is
adapter territory (a marker line in the worker's brief, a structured field,
whatever the harness records); the duty is not.

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
observations, and (when the contract declares an advisor scope)
judgment_events.

## Escalation ladder

Escalation is signal-driven: the contract checker's INVALID, a failed
contracted command, or a timeout is the trigger. Two triggers are "the same
error" when their signatures match — exit code + a fingerprint of the error's
first distinctive line.

- Cheap errs once on a subtask → escalate that subtask to mid. No retry at cheap.
- Mid errs twice on the same subtask (same signature) → escalate to frontier
  WITH the full failure trail: what was tried, exact commands, exact errors,
  hypotheses already excluded.
- Same approach: at most 3 attempts total per subtask × approach. A genuinely
  different approach resets the count.
- Timeout / no response counts as an error at that tier.
- A grading dispute the ladder cannot settle is an advisor call site
  (`grading-dispute`), not an infinite retry.
- De-escalation: a solved pattern gets written as an exact recipe (with
  verification commands) and demoted to mid/cheap batch application — or to
  tier-0 where a script can carry it.

## Single-writer rule

One pen per write surface. Parallel READ breadth is always legal (read-only
workers); parallel WRITES are legal only on non-overlapping write surfaces
(disjoint-write shape), one writer per surface, and the merge-back of
isolated working copies is itself a single-writer step. The inline and
1-worker shapes satisfy this trivially — the journal still records the
configuration (the audit surface degrades to the judgment stream, not to
nothing).

Adapters SHALL enable preventive enforcement where the harness supports it
(read-only worker toolsets, read-only sandbox modes) and SHALL record that
configuration in each run's dispatch records. The portable acceptance check
is post-hoc audit: worker transcripts of every parallel phase show zero file
writes outside the writer's own surface.

## Judgment reservation

Permission grants, contract changes, and quality verdicts are NEVER delegated
to workers, automation, or the advisor. The commander holds them; the human
overrules the commander.

- A result.json with a non-empty scope_change_request stops that line of work
  immediately. The commander escalates the request verbatim to the human —
  never approves in the human's stead, never re-dispatches enlarged work
  before the ruling. (A `scope-change-preview` advisor consult may inform the
  commander's framing; it never substitutes for the human ruling.)
- Quality verdicts on deliverables terminate at the human.

## Verification

The builder never accepts its own work. Acceptance of a mechanical AC is its
check artifact (tier-0). Acceptance of a taste AC goes to the named verifier —
default a fresh-context worker sharing no conversation state with the
builder, which judges each criterion against the artifacts, citing evidence
(file:line or command output). "Reads as correct" is not evidence; execution
output is.

## Audit surface

**Run semantics:** one run = one mode invocation over one contract scope
(entry gate → dispatch plan → waves → harvest → close), producing exactly one
journal file. The journal opens on `commander_stamp` and closes on the
precedent append (§ Precedent & eval loop). A new run = a new journal file;
counters reset by construction; the append-only journal is simultaneously the
audit surface and the counter — no second, driftable state exists.

**Journal event vocabulary (JSONL, one event per line; examples use tier
names and placeholders — a real journal carries the binding-resolved ids):**

```jsonl
{"event":"commander_stamp","model":"<self-reported model id>","doctrine_rev":"<revision short-hash>"}
{"event":"dispatch","task_id":"<id>","tier":"mid","resolved_model":"<from the binding table>","read_only":true,"wave":1,"contract":"<path>"}
{"event":"judgment_moment","moment_id":1,"decision_type":"entry-gate|grading-dispute|worker-blocked|acceptance-ambiguity|scope-change-preview","disposition":"frozen|mechanized|advisor|blocked"}
{"event":"advisor_intent","moment_id":1,"decision_type":"<echoes its judgment_moment's decision_type>","why":"<1 line>"}
{"event":"advisor_ruling","moment_id":1,"decision_type":"<echoes the paired advisor_intent's decision_type>","ruling":"<verdict>","rationale":"<1-3 lines>","confidence":"high|medium|low","what_would_change_my_mind":"<1 line>","digest_ref":"<path or null>"}
{"event":"advisor_threshold","moment_id":4,"threshold":3,"consults_so_far":4}
{"event":"advisor_unavailable","moment_id":2,"note":"transport not attached / pairing illegal — commander proceeds on own judgment, confidence degraded"}
{"event":"blocked_to_human","moment_id":2,"reason":"judgment-reserved|worker-blocked","payload":"<verbatim>"}
{"event":"calibration_notify","calibration_id":"<stable proposal key>","channel":"<binding-named channel, or report-only>","status":"sent|report-only|failed","error":null}
```

The first journal line is ALWAYS `commander_stamp` — the commander
self-reports its model id and the doctrine revision it runs under. Every
dispatch line carries the binding-resolved model actually passed to the
harness mechanism; the conformance audit joins these against execution
telemetry after the run.

**dispatch-plan.md** (the commander keeps it in the task directory):

1. **Entry decision** — write shape + execution config (read breadth, worker
   count, tiers, advisor setup) + named grounds; the refusal number or
   `[pending-measurement]`; human veto record if any.
2. **Task-shape declaration** (machine-readable; the precedent lookup key):
   `task-shape: kind=<kind>, write_surface=<surface>`
3. **Precedent line** (§ Precedent & eval loop):
   `precedent: cited <run_id>` | `precedent: deviation — <written reason>` |
   `precedent: no-match`
4. **Subtask table** — one row per dispatched subtask:
   `| subtask | grade (3 axes) | tier | resolved model | why-not-a-script | contract path | wave |`
5. **Containment check** — one line: expected drift exposure (duration ×
   scope × novelty proxies) vs containment capacity (mechanical-acceptance
   coverage × recovery cost). This is the plan-time answer to the drift the
   judgment-flow audit cannot see (unrecognized moments).
6. **Doubt surfacing** — what the commander is least sure about in this plan.
7. **Deviation log** — entry misjudgments, escalations, scope-change rulings,
   threshold crossings, advisor-unavailable degradations.

## Precedent & eval loop

**Ledger:** a per-project append-only ledger records every run (line formats:
the contract layer's precedent schema; the file path is named by each
harness binding). Append after EVERY run, including failed and
blocked-to-human terminals — the outcome verdict records the terminal state.
Never rewrite an existing line: history is evidence; the ledger is a
version-controlled file, and a diff showing an existing line changed is
itself a violation.

**Pre-dispatch duty (cite-or-deviate):** before dispatching, query the ledger
for lines matching the declared task shape (`task_shape.kind` +
`write_surface` equality). A match must be either cited in the dispatch plan
(by `run_id`) or deviated from with a written reason. Querying is a duty;
following is not. No match is a vacuous pass, recorded as `no-match`.

**Calibration loop:** at run close, run the deterministic trigger check
(tier-0): ≥3 same-shape runs carrying a consistent typed `deviation_signal`
→ append a `calibration/v1` `status=proposed` line, list it in the run
report's pending-calibrations section, and emit a promote-pending
notification through the binding-named channel (a harness without one
degrades to the report floor; emission failure is journaled and never blocks
run close). An open proposed line suppresses duplicate triggers for the same
rule. Promotion or rejection is human-only, recorded by APPEND (a new line
superseding the proposed one — never in-place).

**Maintenance rule (doctrine-default changes):** a change to any doctrine
default (e.g. the attention threshold value, or a calibration rule
promotion) is legal ONLY when it cites a parity-regression run whose record
(a) predates the text change, (b) carries `doctrine_rev` equal to the
pre-change revision, and (c) carries a `candidate_delta` naming the proposed
change — i.e. the regression executed the pre-change doctrine PLUS the
candidate override, never old behaviour alone. The promoting `calibration/v1`
line cites that run via its `m9_run` field, joining the ledger to the
regression record. A change missing any leg is rejected on review.
