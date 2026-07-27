# Orchestration Mode — Doctrine (L1)

Single home for mode behavior: the commander judges, decomposes, dispatches,
integrates — and never executes the grunt work personally. This layer is
harness-neutral: it speaks only in capability tiers and one dispatch
primitive. Adapters bind these abstractions to a concrete harness; an adapter
may cite this doctrine, never restate it.

**commander** — the orchestrating model instance (synonym: orchestrator).
**worker** — a model instance executing exactly one task contract.
**human** — the adjudication layer above the commander; the last word on
entry, permission, contract changes, and quality.

Judgment routes to one of two homes — **frozen ahead** (the task contract) or
**mechanized** (a checker / tier-0 script). What neither home absorbs is the
commander's own load, and inside it the reserved set (§ Judgment reservation)
always terminates at the human.

## Routing header (workstation → section)

This file is one deep module; read the section your workstation needs.

| You are… | Read |
|---|---|
| deciding whether the mode applies at all / declaring entry / choosing topology | § Entry gate |
| pricing an offload, choosing worker count | § Amortization brake |
| grading a subtask or citing a role card | § Complexity tiering |
| resolving a tier to a model, ratio, or generation tag | the harness binding table (L3) |
| at a judgment moment mid-run | § Judgment moments |
| writing or sending a dispatch | § Dispatch primitive, § Dispatch contract |
| harvesting a worker result | § Report contract, § Escalation ladder |
| accepting deliverables | § Verification, § Judgment reservation |
| deciding whether this run is instrumented, or writing its journal | § Audit surface |
| closing the run | § Audit surface (close event), § Durable records |

## Design principles

- **Pay at first dispatch.** The mode's obligations attach to a *dispatch*, not
  to an invocation. Coordination machinery exists to make delegation safe, so
  work that delegates nothing owes it nothing: a run that never reaches a
  dispatch decision is not orchestration, and this doctrine asks nothing of it.
  The normative form of this principle is § Entry gate.
- **Instrumentation-conditioned ceremony.** The always-on interface of a
  dispatch is exactly what the two contexts need to transact: a contract, a
  result, a checker verdict. The self-audit surface — journal, computed brake
  terms, probe record, close chain — is *instrumentation*: it exists to make a
  measurement trustworthy, and it is switched on by a named trigger, not by
  every run. The normative form is § Audit surface.
- **Thin prompts, thick artifacts + context.** The mode's paperwork records
  only decisions that change downstream behavior. Everything else lives in
  artifacts (contracts, results, journals) written once and referenced,
  never restated — narration in a mechanism document taxes every run that
  loads it.
- **Thin skills.** This doctrine is the deep module — one semantically dense
  file, navigated by the routing header. Harness-facing exposure (skill
  files, prompt fragments) is the ADAPTER layer's responsibility and stays
  thin: route and cite, never restate.
- **Decisions are token-priced.** Brake decisions are made entirely in token
  space against the artifacts in hand (through the binding's conversion
  anchors); currency belongs to the reporting layer only.

## Entry gate

**The mode begins at the first dispatch decision.** A run that never reaches
one never enters the mode: it owes no declaration, writes no contract, no
result, and no journal, and it leaves no artifact behind. Nothing in this
doctrine obliges any artifact or declaration before that moment. Whether to
delegate at all remains the operator's call (the same locus as § Judgment
reservation); a dispatch decision answered "no" is a legal answer that leaves
the run outside the mode, with nothing owed for having asked.

**Mid-run entry is forward-only.** A run may begin with the commander working
inline and later reach a dispatch decision; the mode begins at that moment.
Contract and result artifacts — and instrumentation, iff a § Audit surface
trigger holds — materialize from that point forward. No retroactive backfill
of the pre-dispatch history is owed, and none may be written: a record that
narrates a past it did not observe is evidence manufactured after the fact.

At that first dispatch decision the gate's output is a **declaration** — task
family, write shape, read breadth, execution config, named grounds — plus the
human veto record. Grading covers both self-decomposed work and pre-planned
work (an externally supplied plan is graded per task, never re-decomposed for
its own sake). Predictable + mechanically acceptable is where the safety net
is strongest and cheap tiers are most legal.

**Write shape** (where the pen lives — the gate's primary output):

| Shape | Meaning |
|---|---|
| inline | the commander keeps the pen. Work that stays inline reaches no dispatch decision and therefore sits outside the mode entirely — no declaration, no contract, no result, no journal. A run whose inline stretch later reaches a dispatch decision enters the mode there, forward-only (above). |
| 1-worker | one dispatched writer, serialized. |
| disjoint-write | multiple writers on non-overlapping write surfaces, one writer per surface. An isolated working copy (e.g. a separate worktree) is one mechanical carrier; the merge-back is itself a single-writer step. |

**Read breadth** (orthogonal dial): 0..k read-only workers, attachable to ANY
write shape. Every offload — read breadth, 1-worker, disjoint-write alike —
passes the brake (§ Amortization brake); parallel dispatch additionally cites
its necessity ground there.

**Execution config recommendation:** alongside the write shape the gate
names read breadth, worker count, and worker tiers.

**Task family (declared ex-ante):** derived from the deliverable's write
surface at gate time — empty or report-only write surface → `read-heavy`;
anything else → `write-heavy`. Indeterminate write-surface semantics →
conservatively `write-heavy`, plus a typed signal on an instrumented run (the
family key may need splitting; the flip-trigger registry is the project's
assay record). On an instrumented run that completes delivery the declaration
is audited two-way (audit domain = the working tree OUTSIDE the
contract-declared output paths and the mode's own artifacts): declared
write-heavy with zero new commits or uncommitted changes in the declared write
surface is an untrue declaration — unless the run's reasoned, recorded
conclusion was "no change needed"; declared read-heavy with ANY new commit or
uncommitted change in the audit domain is an untrue declaration (under-
declaring to dodge a positive price is the economically tempting gaming
direction; both directions carry equal audit weight). The consequence is a
signal, not a stop — a `declaration-audit` deviation line, never a block —
except on measurement-bearing runs, where it escalates. Blocked/failed terminals are
exempt.

**Mechanical task class (declared at the gate):** a task is *declared
mechanical* when every acceptance criterion of the work the run executes —
the acceptance sources named in the declaration's grounds (an accepted
contract's criteria, a frozen test suite, a written brief) — carries a
runnable, builder-independent check artifact: a frozen test suite, an
exit-code script, a byte comparison. The mechanical/taste boundary itself is
§ Complexity tiering's taste criterion and is not restated here. The
declaration cites the check artifacts themselves — the frozen suite's path —
never a contract document, so it is declarable before any contract file
exists.

Declaring the class binds a frozen default set — decided once, at the
declaration, instead of re-judged at each station:

| Dial | Frozen default for a declared-mechanical task |
|---|---|
| write shape | inline, WHILE the corpus fits one context |
| acceptance | per check artifact (§ Verification); no verification dispatch is owed |
| entry-gate judgment check | pre-answered no-match — the class declaration IS that station's required line (§ Judgment moments) |

Each is a default, not a handcuff: any of them is overridable with a
recorded reason, and that reason is what the audit reads. A mechanical task
whose corpus exceeds one context overrides the write-shape default on the
standard necessity ground (§ Amortization brake), recorded like any other
override. A pre-answered station is answered, not deleted — an adapter's
enumeration of it still stands.

On an instrumented run the class rides the typed `entry` event: `class`
(`mechanical`, or absent = unclassified, the behavior above) and
`class_default` (`cited`, or `overridden(<reason>)`) — additive fields under
§ Audit surface's additive-fields rule. Declaring a `class` and omitting
`class_default`, or overriding with an empty reason, are both semantic
VIOLATIONs (§ Audit surface, semantic rule S4): the class is declarable for
free, the departure from what it binds is not.

The entry declaration is still a judgment moment (decision_type
`entry-gate`) — and for a declared-mechanical task it is the ONE remaining
entry judgment, everything downstream of it being table lookup. For an
unclassified task the topology choice — where the pen lives, how much read
breadth, which tiers — is judged, not defaulted; for a declared-mechanical
task that ruling is cached at class level, the declaration itself being the
judged act. The gate consults no price table and weighs no price; every
economic question about a concrete offload belongs to the brake
(§ Amortization brake), per dispatch, at dispatch time.

On an uninstrumented run the declaration is exercised in-session and not
recorded: the gate's questions are answered where they are asked, and the
absence of a record is the point of the cut, not an omission. On an
instrumented run it is recorded in full as the typed `entry` event
(§ Audit surface): family + write shape + read breadth + execution config +
named grounds. A human veto is recorded — who, changed to what, why — and
governs on either kind of run.

## Amortization brake

Moving work off the commander is an economic act with computable costs. One
inequality, in token space, carries the whole test:

```
offload pays ⟺ Σi W_i × (1−r_i) > C_reread + C_brief_cmd + Σi r_i × (C_fresh + C_brief_worker)
```

- `W_i` — order-of-magnitude estimate of the output offloaded to worker i:
  the brake's ONLY on-the-spot estimate. It is made in units the estimator
  can feel (file count, line count) and converted to token space through the
  same conversion anchors as everything else.
- `r_i` — worker i's tier price relative to the commander tier, from the
  binding's ratio table (L3, with the unit weights). Same tier ⇒ r = 1.0 by
  construction — same tier, same price is a definition, not an approximation
  — so the saving term is zero and a same-tier offload can never pass on
  economics. That consequence emerges from the formula; no per-tier or
  per-model exception clause exists or may be added.
- `C_brief_cmd`, `C_reread` (commander-side) and `C_brief_worker`, the
  corpus term of `C_fresh` (worker-side, per offload) — derived from the
  actual byte sizes of the artifacts in hand (the contract file and prompt,
  the corpus files the worker must read, the expected re-read set) through
  the binding's **conversion anchors** — the binding's declared bytes→token-
  equivalent rates per content class, with their correction factor. The
  mechanism is named here; the anchor VALUES live only in the binding,
  changelog-governed like its ratio table. Mixed tiers compute each offload
  item separately.
- `C_fresh` — a worker's cold-start cost, decomposed into a **boot term**
  (the harness's fixed context-establishment overhead) plus the **corpus
  term** (the artifacts the worker must read).

**Two forms, one rule.** The inequality is the same on every run; what
changes is whether it is *evidenced*.

- **Ordinary (uninstrumented) run:** the commander applies the inequality
  qualitatively — reasoning in token space from the artifacts in front of it —
  and launches or does not. Nothing is computed into a record, no probe record
  is read or written, and the boot term is not priced at all: the commander
  weighs a cold start it cannot quantify. That is a deliberate, named
  consequence of paying at first dispatch, not an unstated gap.
- **Instrumented run (§ Audit surface):** the same inequality is computed and
  recorded as a typed `brake` event, every term carrying its basis (file refs
  + bytes + content class) so a tier-0 auditor can recompute both sides; the
  boot term is read from the probe record and cited by probe row, never
  computed from bytes and never estimated. Here a computed value without a
  basis is an invented constant — an audit FAIL.

The launch rule binds identically on both: **an economics-failing dispatch
without a necessity ground does not launch.** Instrumentation buys the
evidence, never the obligation.

EVERY dispatch that moves work off the commander — the serial 1-worker shape
included (a write-shape choice needs no necessity ground) — carries a typed
brake event on an instrumented run. Parallel dispatch, and any dispatch whose
economics fail, additionally names its **necessity ground** from a closed
enum of four, each an override with its own citation duty:

| Ground | Citation duty |
|---|---|
| `wall-clock` | cite the concrete deadline |
| `corpus` | the corpus exceeds one context — cite the corpus-size evidence |
| `disjoint-write` | list the non-overlapping write surfaces |
| `verification-mandated` | this doctrine itself mandates the dispatch away from the commander — cite the mandating rule |

`verification-mandated` is the non-discretionary ground: the launch bar
governs DISCRETIONARY offload of the commander's own work, so a dispatch this
doctrine mandates is accounted for (its brake event is still written on an
instrumented run; k and tier are still bounded) but an economics fail does not
block it. The fresh-context verifier (§ Verification — the builder may not
hold it) is the ONLY such mandate in this doctrine; extending the class is an
edit to this sentence, gated like any doctrine-default change (§ Durable
records). Under any override the brake's job shifts to bounding k and tier:
each added worker still pays its marginal r_i × (C_fresh + C_brief_worker),
and the recorded basis for k is what an auditor reads.

Cold start is conservative-closed on an instrumented run: no boot-probe value
obtainable (the probe failed, or the binding declares no probe procedure) or
no conversion-anchor table in the binding → the economics leg cannot be
computed, the brake verdict is `not-computable`, offload is legal on necessity
grounds only, and the gap lands in the deviation log. The next instrumented
entry retries the probe.

**Boot-probe record (instrumentation only; cache semantics, never a feedback
loop):** the boot term's evidenced source is a per-project,
append-only probe record written ONLY by the binding's probe procedure, and
read ONLY on an instrumented run. The first dispatch of an instrumented run
takes the probe if no usable row exists — a cheap-tier one-question boot whose
measured context-establishment cost IS the value — and entry continues
regardless of its outcome. The consumable row is the latest row matching the
current harness, configuration hash, and model generation (three axes, equal
weight); any mismatch is a deterministic re-probe — append a new row, never
edit or delete old ones. A run's own measurements NEVER write back into the
probe record: a stale stamp means the cached value is invalid and must be
re-measured by the probe, never adjusted in place from a run's own numbers.
Probe-row selection is a tier-0 decision (hit | reprobe | error); a malformed
or unreadable record is an error and follows the cold-start path above — a
suspicious row is never consumed. An ordinary run neither reads nor writes
this record.

Estimate drift — the measured output (delivered diff bytes, converted through
the same anchors) versus the brake event's estimate — is journaled at close on
an instrumented run as a typed `estimate-drift` deviation. It is evidence for
a later change to the binding's anchors, which travels the evidence path of
§ Durable records; W is per-task and never becomes a stored constant.

## Complexity tiering

Grade every subtask BEFORE its wave dispatches, on three axes:

| Axis | Question | Toward cheap/mechanized | Toward frontier/human |
|---|---|---|---|
| verifiability | is acceptance mechanical — a written, runnable check? | check artifact exists; exit code decides | taste verdict; no check writable |
| recovery cost | if the worker is wrong, what does detection + undo cost? | reversible via version control; blast radius one file | irreversible or outward-facing; cross-file invariants |
| context economics | does the work fit one context? what re-reading tax does each extra context pay? | small closed corpus; recipe known | corpus exceeds context; path-dependent exploration |

The context-economics axis grades; its go/no-go wiring lives in
§ Amortization brake.

Planning may roll forward in waves — plan → dispatch → harvest → re-judge;
grade and route each wave before it launches; later waves may evolve from
earlier waves' findings. The wave boundary is where judgment moments live.

Grading output per subtask: capability tier (§ Capability tiers), read-only
or write role within the chosen write shape, and a `why-not-a-script` answer
(anything gradeable to tier-0 is a script, never a model dispatch).

**Role cards (grading cache):** a role card (contract layer, `roles/`) is a
three-axis grading result cached at design time for a shape-constant
dispatch. Citing a card on the dispatch line replaces the grade axes — but only
after checking the card's `graded_under` stamp against the doctrine revision
this run runs under and the binding's current model-generation tag; any
mismatch means the card is stale and the citation is a miss, recorded as
`card=none(<reason>)` with full three-axis grading as the fallback. Judgment
duties never appear on a card (§ Judgment reservation); the boundary is
mechanically scanned at the contract layer.

Concurrency hard cap: **5 simultaneous workers** (default; 3–5 recommended
operating band).

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

## Capability tiers

Routing speaks ONLY in tiers. A concrete model name never appears at this
layer; each harness's binding table maps every model tier to ≥1 concrete
model, and also carries each tier's price ratio r, the unit weights
(output / cache-write / input), and a model-generation tag (`model_gen`,
used by card staleness checks and boot-probe row selection). L1 embeds no ratio,
weight, or price value.

| Tier | Task shape |
|---|---|
| tier-0 (deterministic script) | acceptance, counting, format checks, any decision already expressible as a written command with an exit code. Not a model. Cheapest, fully auditable — always preferred where it exists. |
| frontier | judgment, decomposition, integration, first-time diagnosis, architecture trade-offs, cross-file invariants (usually the commander itself) |
| mid | clear-spec implementation, search/inventory, multi-source research, review lenses (default worker) |
| cheap | batch application of an already-solved pattern; format conversion; mechanical enumeration |

Cheap-tier red line: work needing judgment, first encounters, or a fuzzy
recipe never goes to cheap.

**Worker tier default:** default one tier below the commander, and choose the
cheapest tier expected to pass acceptance in ONE dispatch — a cheaper tier
that needs a retry has already spent the saving (§ Escalation ladder prices
the retry). Each harness binding homes the concrete tier→model mapping and any
tier-specific admissibility conditions that follow from it.

## Judgment moments

A judgment moment is a decision point the commander RECOGNIZES as a decision.
Recognition is the first capability to fail as commander tier drops, so the
moments are enumerated rather than left to notice: at each of the five call
sites below, the commander writes exactly ONE line, in the form the adapter
enumerates, carrying one of the three station answers defined below.

**Call sites (closed enum):** `entry-gate | grading-dispute | worker-blocked
| acceptance-ambiguity | scope-change-preview`.

**The station's three answers** (distinct from the journal line's
`disposition` field, which records where the moment was ROUTED — see the
mapping below):

- **match** — this moment fits a call site and the commander's own ruling is
  not self-evident: **surface it to the human.** Surfacing is NON-BLOCKING —
  the commander states the moment and its own ruling in-channel and proceeds.
  It is a disclosure, not a request for permission; the one exception is a
  moment in the reserved set (§ Judgment reservation), which terminates at the
  human regardless of how this station answered.
- **no-match** — no call site fits. The line still owes its one-line why:
  "the doctrine covers this" / "it is deterministic" is a no-match *claim*,
  not an answer.
- **misfit-but-uncertain** — no site fits AND the commander does not trust its
  own ruling. This **is** a surface trigger; uncertainty about the shape of a
  decision is the strongest signal that a human should see it.

**Where the station lives.** On an instrumented run each moment lands as a
typed `judgment_moment` line carrying the written answer in `check` and, in
`disposition`, where the moment was routed: `frozen` (the contract already
decided it), `mechanized` (a checker or tier-0 script decides it), `surfaced`
(stated to the human and proceeded past), or `blocked` (reserved set — it
terminates at the human, and a `blocked_to_human` line carries it). The two
vocabularies answer different questions: the station's answer is *did this
need a second pair of eyes*, the disposition is *who actually decided it*.
Every answer has a destination, and the mapping is total:

| Station answer | Disposition |
|---|---|
| `no-match` — resolved where it stood | `frozen` when the answer was already decided before this moment and the commander is reading it off: the task contract, a declaration made at the gate (the mechanical class), or a cited role card (§ Complexity tiering — a card is a grading decided at design time, which is frozen-ahead by the same logic even though it is not the contract). `mechanized` when a checker or tier-0 script produces the answer — the commander is not deciding, it is running something and reading the exit code |
| `match` | `surfaced` |
| `misfit-but-uncertain` | `surfaced` |
| any answer, when the moment is in the reserved set | `blocked` — the reserved set overrides every other row, and a `blocked_to_human` line carries the moment verbatim (§ Judgment reservation) |

A `no-match` answer that can name neither a freezing source nor a mechanizing
check has not resolved the moment — it has skipped it, and the honest answer
was `misfit-but-uncertain` (§ Audit surface). On an ordinary run the station is guidance: it is
exercised — the commander answers it — and not recorded. The station's value
is the forced enumeration, which costs nothing to keep and is measurable
(a +1.0 judgment-quality lift when it was first instrumented); the record is
what instrumentation adds.

Unrecognized moments (the commander never saw the decision point) are the
fourth class, and no audit can see them either: they are governed by the
containment statement on a write-role dispatch (§ Audit surface), not by any
audit of the judgment stream. This boundary is honest, not accidental.

**I3 boundary:** surfacing a moment is disclosure. Permission grants,
contract changes, and final quality verdicts do not move because a moment was
surfaced (§ Judgment reservation).

## Dispatch primitive

**dispatch** := write a task-contract file into the task directory → start
one worker on it through the harness mechanism → wait for result.json to land
and validate it with the contract checker. Only the middle step is
harness-bound (adapter territory); the first and last steps are pure file
operations, identical everywhere.

**Filename convention (contractual — audits pair artifacts against records by
it):** within a task directory the contract file is named `task-contract.md`,
or `task-contract-<suffix>.md` where one directory holds several; the result
is named `result.json`. A dispatch record's contract path and the file on disk
must be the same path in both directions — an artifact no record names, and a
record naming no artifact, are equally reconciliation failures (§ Audit
surface). Renaming an artifact does not excuse it from the pairing.

Every dispatch is cold: the worker starts with no state from any earlier
dispatch, and its cost is accounted as a cold start. There is no continuation
channel at this layer — a later wave that needs earlier context passes it as
artifacts (§ Report contract), which is the mode's only communication surface.

## Dispatch contract

Every dispatch carries four elements, mapped to task-contract fields. A
dispatch missing any element is defective — fix it before sending. The four
elements are authored PER TASK; the implementer behavioral contract they sit
above is cited from its single home (the contract layer's task-contract
template), never copied per instance — "written once and referenced, never
restated" (§ Design principles) extends to the dispatched contract, so a
per-subtask instance carries its task-specific fields plus a citation to that
home, not a duplicate of the invariant boilerplate.

| Element | Contract field |
|---|---|
| objective & motivation | Scope |
| output format | Acceptance Criteria — each criterion quoting its written acceptance source verbatim (with a source reference), or marked `self-authored` where no written source exists (§ Verification) |
| tool & source guidance | Commands to Run + Read-Only Boundaries |
| task boundary | Do Not Touch + Owned Files |

## Report contract

Artifacts over relay: worker products land on the filesystem; result.json
carries light references (paths), never bulk content. The filesystem is the
ONLY commander↔worker communication surface. A worker's report is its
result.json — summary, files_changed, commands_run (with exit codes), risks,
and observations.

One named exception: where a binding's read-only worker type structurally
cannot write files, its report rides the harness channel and the commander
persists it VERBATIM into the task directory, provenance-noted — the channel
is a carrier, never a second home; the task directory remains the record of
record. The transcription is mechanical for findings; any doctrine-vocabulary
field a worker self-reports enters the record only after the commander's own
judgment.

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
- A grading dispute the ladder cannot settle is a judgment moment
  (`grading-dispute`, § Judgment moments), not an infinite retry.
- De-escalation: a solved pattern gets written as an exact recipe (with
  verification commands) and demoted to mid/cheap batch application — or to
  tier-0 where a script can carry it.

## Single-writer rule

One pen per write surface. Parallel READ breadth is always legal (read-only
workers); parallel WRITES are legal only on non-overlapping write surfaces
(disjoint-write shape), one writer per surface, and the merge-back of
isolated working copies is itself a single-writer step. The inline and
1-worker shapes satisfy this trivially.

Adapters SHALL enable preventive enforcement where the harness supports it
(read-only worker toolsets, read-only sandbox modes) and SHALL record that
configuration in every dispatch record they write. **The preventive rule binds
every dispatch run, instrumented or not** — it is procedure, not paperwork,
and it is the leg that actually prevents the damage. The post-hoc audit is a
detective addition available on instrumented runs: worker records of every
parallel phase show zero file writes outside the writer's own surface.

## Judgment reservation

Permission grants, contract changes, and quality verdicts are NEVER delegated
to workers or automation. The commander holds them; the human overrules the
commander.

- A result.json with a non-empty scope_change_request stops that line of work
  immediately. The commander escalates the request verbatim to the human —
  never approves in the human's stead, never re-dispatches enlarged work
  before the ruling. (A `scope-change-preview` moment may inform the
  commander's framing; it never substitutes for the human ruling.)
- Quality verdicts on deliverables terminate at the human.

## Verification

The builder never accepts its own work. Acceptance of a mechanical AC is its
check artifact (tier-0). Acceptance of a taste AC goes to the named verifier —
default a fresh-context worker sharing no conversation state with the
builder, which judges each criterion against the artifacts, citing evidence
(file:line or command output). That verifier dispatch is the one this doctrine
mandates: it does not need to pass the brake's economics leg, and it names
`verification-mandated` as its ground (§ Amortization brake). The criterion
the verifier binds to is the contract's quoted acceptance source — the
original written assertion, not a paraphrase — so the judgment tracks the
source of truth rather than a lossy projection; a `self-authored` criterion
(no written source upstream) is judged on its own terms, there being no source
text to quote against. "Reads as correct" is not evidence; execution output is.

## Audit surface

Everything in this section is **instrumentation**. It exists on a run whose
numbers or whose conformance a reader will trust, and it is absent otherwise
(§ Design principles). An ordinary dispatch run produces exactly three kinds
of artifact — task-contract instance(s), a result.json per executed worker,
and the checker verdict per result — and nothing here.

**Measurement-bearing (the trigger enum — the single extension point; a
future measurement need appends a trigger here rather than re-hardwiring
ceremony):** a run is instrumented iff at least one of

- **(a) benchmark arm** — the run is a cell of a comparison whose numbers are
  published or compared (arm, parity run, ablation).
- **(b) explicit human request** — the human asks for an instrumented run.

Every other run is uninstrumented, and that is the default. **Both triggers
are deliberate: no run becomes instrumented without someone choosing it.**
That property is load-bearing downstream — it is why a missing telemetry
export is a close-chain FAILURE rather than a tolerated state (below). Whoever
chose to measure owes the evidence the measurement depends on.

**A named gap, stated rather than papered over.** An earlier revision of this
enum carried a third, automatic trigger: the first dispatch run after a
doctrine or model-generation change was instrumented without anyone asking, so
that drift nobody noticed would still be caught. It was removed on evidence
that it did not do that. Its model-generation leg keyed on a
human-maintained tag, so it fired only after a human had already noticed the
change — a trigger that requires you to notice cannot catch what you did not
notice. Its doctrine-revision leg had no payload: nearly every close-chain
member audits an artifact that exists only because the run was instrumented,
and the one member whose referent is outside this mode — the conformance
join of recorded model against execution telemetry — needs a telemetry export
that no binding currently produces. **So: nothing automatic now watches for a
silent model-generation change.** Closing that gap starts with a binding that
produces telemetry; an automatic trigger is worth re-adding to this enum only
once there is something for it to trigger. The brake's
computed and typed form — the probe record, the typed `brake` event — is
instrumentation by this rule; its qualitative launch rule survives on every
run as commander guidance (§ Amortization brake, "Two forms, one rule").

**Run semantics:** one instrumented run = one mode entry over one contract
scope (first dispatch decision → waves → harvest → close), producing exactly
one journal file. The journal opens on `commander_stamp` and closes on the
typed `close` event. A new run = a new journal file; counters reset by
construction; the append-only journal is simultaneously the audit surface and
the counter — no second, driftable state exists.

**Journal event vocabulary (JSONL, one event per line; examples use tier
names and placeholders — a real journal carries the binding-resolved ids):**

```jsonl
{"event":"commander_stamp","model":"<self-reported model id>","doctrine_rev":"<revision short-hash>","model_gen":"<binding gen-tag>","vocab":3}
{"event":"entry","family":"read-heavy|write-heavy","write_shape":"inline|1-worker|disjoint-write","read_breadth":0,"config":{"tiers":"<free>"},"grounds":"<free text>","veto":null}
{"event":"probe","action":"hit|probed|reprobed|failed","row":"<config_hash>@<ts>|null"}
{"event":"brake","wave":1,"offload":[{"tier":"mid","w_est":0,"r":0.0,"C_brief_worker":{"tok":0,"basis":{"refs":["<path>"],"bytes":0,"class":"prose|code|cjk|mixed"}},"corpus":{"tok":0,"basis":{"refs":["<path>"],"bytes":0,"class":"prose|code|cjk|mixed"}},"boot":0}],"save":0,"pay":0,"verdict":"pass|fail|not-computable","ground":"wall-clock|corpus|disjoint-write|verification-mandated|none","inputs":{"C_brief_cmd":{"tok":0,"basis":{"refs":["<path>"],"bytes":0,"class":"prose|code|cjk|mixed"}},"C_reread":{"tok":0,"basis":{"refs":["<path>"],"bytes":0,"class":"prose|code|cjk|mixed"}}},"probe_ref":"<config_hash>@<ts>|null","anchor_rev":"<binding changelog rev>","r_rev":"<binding changelog rev>","k_note":"<free>"}
{"event":"deviation","kind":"escalation|scope-change|estimate-drift|declaration-audit|aborted-dispatch|<open set>","note":"<free>","contract":"<task-contract path, optional — e.g. with kind aborted-dispatch>"}
{"event":"dispatch","task_id":"<id>","tier":"mid","resolved_model":"<from the binding table>","read_only":true,"wave":1,"contract":"<path>","containment":"<free>","doubt":"<free>"}
{"event":"judgment_moment","moment_id":1,"decision_type":"entry-gate|grading-dispute|worker-blocked|acceptance-ambiguity|scope-change-preview","disposition":"frozen|mechanized|surfaced|blocked","check":"<the station's one written line>"}
{"event":"blocked_to_human","moment_id":2,"reason":"judgment-reserved|worker-blocked","payload":"<verbatim>"}
{"event":"dispatch_result","task_id":"<id>","checker":"VALID|INVALID","usage":{"<harness-reported worker token counts, verbatim>":0}}
{"event":"dispatch_result","task_id":"<id>","checker":"VALID|INVALID","usage":"unavailable"}
{"event":"close","terminal":"done|failed|blocked","members":[{"name":"<member>","status":"pass|fail(<rc>)|dropped(trigger-absent)"}]}
```

Every line carries `ts` (ISO8601 UTC) in addition to the fields shown.

The first journal line is ALWAYS `commander_stamp` — the commander
self-reports its model id, the doctrine revision it runs under, the binding's
model-generation tag, and `vocab`, the journal vocabulary version (an integer;
this revision's vocabulary is version 3). Auditors key their dialect on the
vocab stamp, NEVER on event presence — presence inference would let a
drifting commander escape full audit by writing old-form events, which is
exactly the drift the stamp exists to kill. **A journal an audit is invoked on
that carries no stamp, or a stamp below the current vocabulary, FAILS that
audit.** There is no legacy dialect and no fallback: the scope of every audit
is the journal its own close chain hands it, so a stamp-less journal is not an
honest old record being misread — it is a current record that failed to
declare itself. Historical journals from earlier vocabularies are simply never
re-invoked.

**Additive fields** — a new optional field or a new open-set enum value, never
a shrink of the vocabulary above, never a change to an existing event's
required set, never a `vocab` bump — may extend ANY event. On the `dispatch`
line: `card:"<role>@<graded_under>"` — or `"none(<reason>)"` on a miss/stale
citation — when role cards are in play, `grade` (the three tiering axes, when
no valid card is cited), `why_not_script`, `contract_family` (a stable id
shared by same-family waves), `write_surface` (a digest of the contract's
Owned Files, or `read-only`), `brief_tokens_est`, and `w_est`. The first
non-dispatch example: a `deviation` line of `kind:"aborted-dispatch"` (an
open-set value) carries an optional `contract` field naming the task-contract
path a decided-but-unlaunched dispatch left behind — a STRUCTURED field, not
free-text `note` parsing, is what a reconciliation audit pairs the orphan
artifact against. The `dispatch_result` line (harvest side) records the
checker verdict and the worker usage; `usage` is an ENUM — an object of
harness-channel-reported token counts, verbatim, or the typed degradation
marker `"unavailable"`. A prose pointer (a see-elsewhere note) is not a legal
value.

**Two folded judgment fields on the `dispatch` line.** Both were standalone
events in earlier vocabularies and carry the same content on a field:

- `containment` — owed on EACH write-role dispatch line: expected drift
  exposure (duration × scope × novelty proxies) vs containment capacity
  (mechanical-acceptance coverage × recovery cost).
- `doubt` — owed on the dispatch line of the affected moment when an entry or
  grading `judgment_moment` lands with disposition ≠ `frozen`: what the
  commander is least sure about. One per recurrence, not one per run.

On an uninstrumented run both are exercised and not recorded, like the
stations they follow.

**Computed-term object (one shape, four stations):** every computed brake
input — offload `C_brief_worker`, offload `corpus`, inputs `C_brief_cmd`,
inputs `C_reread` — is `{"tok":<int>,"basis":{"refs":[...],"bytes":<int>,
"class":"prose|code|cjk|mixed"}}`. An auditor recomputes `tok` from
`basis.bytes` × the anchor rate for `class` at `anchor_rev`; a computed item
without a basis is an invented value — FAIL (recomputability is this
event's reason to exist). The `boot` term is an integer, NOT a computed
term: its value comes from the probe record and is verified by resolving
`probe_ref`, never by byte recomputation. Recompute identities:
`save = Σ w_est × (1−r)`;
`pay = C_reread.tok + C_brief_cmd.tok + Σ r × (C_brief_worker.tok + boot + corpus.tok)`.
Worker-side items ride per-offload (mixed tiers each computed separately).
Probe value unobtainable ⇒ `verdict:"not-computable"` (§ Amortization
brake's conservative-closed path, in typed form).

**Semantic validity (the four rules, enforced on every stamped journal):**
typed carriers kill format drift; these kill semantic drift:

1. **S1 — moment_id uniqueness.** One `judgment_moment` per `moment_id` per
   journal; a paired reference (a `blocked_to_human` echoing its moment) is
   not a re-use.
2. **S2 — referential pairing.** Every `dispatch_result.task_id` must resolve
   to an EARLIER `dispatch.task_id` in the SAME journal. A result attributed
   to a dispatch this journal never recorded is unattributable work.
3. **S3 — usage enum.** `dispatch_result.usage` is a token-count object or the
   typed marker `"unavailable"`; prose is illegal.
4. **S4 — override reason.** An `entry` event whose `class_default` is an
   override (§ Entry gate, mechanical task class) must carry a non-empty
   recorded reason inside it; an empty reason is a VIOLATION. The default
   set is overridable precisely because the reason is recorded, so an
   override that records nothing has taken the licence without paying for
   it. An event that declares a `class` and omits `class_default` entirely
   is the same VIOLATION by the shorter route — omission is the cheapest
   way to leave the default set unrecorded, so the audit reads a declared
   class as owing its `class_default`. This rule is the enforcement path —
   not the family declaration-audit in § Entry gate, which reads a different
   field.

**Typed-event coverage (owed-when triggers):** on an instrumented run the
`entry` event and the `close` event are unconditional — one of each per run,
the gate's declaration in full and the chain's terminal digest. Each
remaining event is owed ONLY when its trigger fires; an absent event with no
trigger is compliant, and "owed but missing" is decidable from the journal
alone:

- `probe` — owed before the first dispatch: the row selection's outcome.
- `brake` — owed per wave when any offload is planned or executed. A journal
  containing dispatch events but no brake event is an audit FAIL — the plan's
  absence is no escape hatch.
- Subtask grading — carried on each `dispatch` line's additive fields
  (grade or card citation, why_not_script); a valid card citation replaces
  the grade axes, and a stale card is `card:"none"` plus full grading
  (§ Complexity tiering).
- `containment` / `doubt` — dispatch-line fields, triggers as above.
- `judgment_moment` — one per recognized moment (§ Judgment moments).
- `blocked_to_human` — owed when a `judgment_moment` carries
  `disposition: "blocked"`, carrying that moment verbatim. Listed here because
  a duty stated only in prose sits outside the "owed but missing is decidable
  from the journal alone" property this section claims for itself, and a
  decidable duty nobody wrote down is decidable by nobody.
- `deviation` — opens at the first deviation event (escalation, scope-change
  ruling, estimate drift, declaration-audit flag, aborted dispatch).

**The close event and its chain.** Close runs the project's canonical audit
set as ONE invocation and records the outcome in the `close` event: each
member by name with one of three statuses — `pass`, `fail(<rc>)`,
`dropped(trigger-absent)`. Neither of the two that are not a pass may be
collapsed into `pass`; that collapse is the silent false-green this whole
surface is built to catch:

- **`dropped(trigger-absent)`** — the member's trigger did not fire, so it was
  not run. Dropped ≠ run ≠ passed.
- **`fail(<rc>)`** — the member ran and did not conclude in the affirmative,
  named with its exit code. Batching may not hide WHICH member failed.
  **A member that ran and could not conclude for want of evidence fails here,
  and it is meant to.** The canonical case is the conformance join with no
  execution telemetry: every instrumented run is deliberately triggered
  (§ trigger enum above), so somebody chose to measure, and the evidence a
  measurement depends on is owed rather than hoped for. A close that read
  green while the model-conformance join established nothing would let a
  published tier claim rest on a record that verified none of it.

Every member is run and recorded: a chain that stops at the first failure
produces a close record with holes in it, and the record's completeness is
what it is for. The members' list and their order are the adapter's single
home, cited by anything that says "the close audits" rather than
re-enumerated. The journal closes on this event.

Judgment-bearing fields (grounds, doubt text, containment statements) are
free-text one-liners BY DESIGN: the typed carrier changes the surface, not
the judgment's nature — an enum there would be the schema overreaching into
the judgment itself.

**dispatch-plan.md (optional render, no audit standing):** the journal is
the sole legal home of machine-consumed record fields. A dispatch-plan.md
may still be written — or generated from the journal — for human reading,
but no auditor may take it as a source of record; where render and journal
disagree, the journal governs, and the disagreement is a signal with no audit
consequence. Journal events land at their moment and are never
rewritten — a rewrite is audit history destroyed.

## Durable records

The mode's durable records are append-only and project-local, never shipped:
an instrumented run's journal, and the project's boot-probe record
(§ Amortization brake). Never rewrite an existing line: history is evidence,
and a diff showing an existing line changed is itself a violation. Runs that
are not instrumented leave no durable record, by design — the deliverable and
version control are the record of what happened.

**Default-change governance (doctrine defaults AND binding values):** a
change to a default in this doctrine, or to a value the binding owns (a
conversion anchor, a ratio row, a tier mapping), is legal ONLY when the
changing spec or commit cites regression evidence that **predates the text
change** — evidence gathered under the pre-change behavior, naming what the
candidate change was expected to do. A change whose only evidence is
collected after the fact has assumed its own conclusion. No ledger mechanism
carries this rule; the citation lives in the spec or commit that makes the
change, where a reviewer reads it.
