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

## Routing header (workstation → section)

This file is one deep module; read the section your workstation needs.

| You are… | Read |
|---|---|
| deciding open / refuse / topology | § Entry gate |
| pricing an offload, choosing worker count | § Amortization brake |
| grading a subtask or citing a role card | § Complexity tiering |
| resolving a tier to a model, ratio, or generation tag | the harness binding table (L3) |
| at a judgment moment mid-run | § Advisor primitive |
| writing or sending a dispatch | § Dispatch primitive, § Dispatch contract |
| harvesting a worker result | § Report contract, § Escalation ladder |
| accepting deliverables | § Verification, § Judgment reservation |
| writing the plan or journal | § Audit surface |
| closing the run (ledgers, calibration) | § Precedent & eval loop |

## Design principles

- **Thin prompts, thick artifacts + context.** The mode's paperwork records
  only decisions that change downstream behavior. Everything else lives in
  artifacts (contracts, results, journals) written once and referenced,
  never restated — narration in a mechanism document taxes every run that
  loads it.
- **Thin skills.** This doctrine is the deep module — one semantically dense
  file, navigated by the routing header. Harness-facing exposure (skill
  files, prompt fragments) is the ADAPTER layer's responsibility and stays
  thin: route and cite, never restate.
- **Decisions are token-priced.** Gate and brake decisions are made entirely
  in token space against measured, operator-local numbers; currency belongs
  to the reporting layer only.

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
write shape. Every offload — read breadth, 1-worker, disjoint-write alike —
passes the brake (§ Amortization brake); parallel dispatch additionally cites
its necessity ground there.

**Execution config recommendation:** alongside the write shape the gate
names read breadth, worker count, worker tiers, and the advisor setup.

**Task family (declared ex-ante):** derived from the deliverable's write
surface at gate time — empty or report-only write surface → `read-heavy`;
anything else → `write-heavy`. Indeterminate write-surface semantics →
conservatively `write-heavy`, plus a typed journal signal (the family key may
need splitting; the flip-trigger registry is the project's assay record).
The declaration is audited two-way on runs that complete delivery (audit
domain = the working tree OUTSIDE the contract-declared output paths and the
mode's own artifacts): declared write-heavy with zero new commits or
uncommitted changes in the declared write surface is an untrue declaration —
unless the run's reasoned, recorded conclusion was "no change needed";
declared read-heavy with ANY new commit or uncommitted change in the audit
domain is an untrue declaration (under-declaring to dodge a positive price is
the economically tempting gaming direction; both directions carry equal
audit weight). The consequence is advisory — a journal audit-flag plus a
deviation-log line feeding calibration, never a block — except on
measurement-bearing runs, where it escalates. Blocked/failed terminals are
exempt.

**The sole refusal ground** is task value below the task family's measured
discipline price — the row in the operator's constants table matching the
declared family (row kind `discipline-price`; produced only by an ablation
pair, § Precedent & eval loop). The weighing is a judgment moment
(decision_type `entry-gate`), never a formula: the commander judges the
task's recovery-cost class and its need for mechanical acceptance (the
tiering axes) — the price row is the cited evidence, the value side is the
recorded judgment. Dispositions:

- **Row value non-positive → open without weighing** (discipline is free or
  better). This binds to the row's sign, never the family name: a family
  whose later measurement turns positive automatically rejoins the weighing
  path.
- **Row value positive → open** when the judged value covers the price (high
  recovery-cost class — irreversible or outward-facing surface, cross-file
  invariants — or mechanical acceptance is needed), and on a tie (price ≈
  value undecidable → open: the discipline side's cost is bounded; record
  the tie→open basis).
- **No row for the family → refusal is disabled**; the gate may only
  annotate `[pending-measurement]`, never refuse.
- **Refusal → the light path:** a minimal journal (commander_stamp, the
  entry judgment_moment, and the entry decision citing the refused row by
  row identity) closes the run. The task then proceeds outside the mode —
  no contract, no dispatch plan, no precedent append (precedent lines belong
  to mode runs only).

Every table citation — here and in the brake — is by ROW IDENTITY
(`<key>@<run_id>/<ts>`; an append-only table holds many rows per key), and
rows are consumed per the table's reading state machine (§ Precedent & eval
loop).

Record every entry decision in the audit surface (§ Audit surface):
topology + execution config + named grounds + family + the cited row or
`[pending-measurement]`. A human veto is recorded — who, changed to what,
why — and governs.

## Amortization brake

Moving work off the commander is an economic act with measured costs. One
inequality, in token space, carries the whole test:

```
offload pays ⟺ Σi W_i × (1−r_i) > C_reread + C_brief_cmd + Σi r_i × (C_fresh + C_brief_worker)
```

- `W_i` — order-of-magnitude estimate of the output offloaded to worker i:
  the brake's ONLY on-the-spot value. Every other number is read from a
  table; inventing a constant on the spot is an audit FAIL.
- `r_i` — worker i's tier price relative to the commander tier, from the
  binding's ratio table (L3, with the unit weights). Same tier ⇒ r = 1.0 by
  construction — same tier, same price is a definition, not an approximation
  — so the saving term is zero and a same-tier offload can never pass on
  economics. That consequence emerges from the formula; no per-tier or
  per-model exception clause exists or may be added.
- `C_*` — burner-tagged constants (burner = commander | worker) from the
  operator's constants table, cited by row identity.

EVERY dispatch that moves work off the commander — the serial 1-worker shape
included (a write-shape choice needs no necessity ground) — carries a brake
line in the dispatch plan (format: § Audit surface). Parallel dispatch
additionally cites its necessity ground — a closed triple, each an override
with its own citation duty: **wall-clock** (cite the concrete deadline),
**corpus exceeds one context** (cite the corpus-size evidence),
**disjoint-write** (list the non-overlapping write surfaces). An
economics-failing dispatch without a necessity ground does not launch. Under
an override the brake's job shifts to bounding k and tier: each added worker
still pays its marginal r_i × (C_fresh + C_brief_worker), and the brake line
records the basis for k.

Cold start is conservative-closed: no C_* rows for the family, or no ratio
table in the binding → the economics leg cannot be computed, offload is
legal on necessity grounds only, and the gap lands in the deviation log. The
run's own close bootstraps the first constants row (§ Precedent & eval
loop).

Boundary: the launch bar governs DISCRETIONARY offload of the commander's
own work. A dispatch this doctrine itself mandates away from the commander
is not discretionary: its brake line is still written (accounting; k and
tier still bounded), but an economics fail does not block it. The fresh-
context verifier (§ Verification — the builder may not hold it) is the ONLY
such mandate in this doctrine; extending the class is an edit to this
sentence, gated like any doctrine-default change.

Estimate drift — measured W versus the brake line's estimate — is journaled
at close as a typed deviation signal feeding calibration; it never enters
the constants table (W is per-task, not a family constant).

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
dispatch. Citing a card in the plan replaces the grade columns — but only
after checking the card's `graded_under` stamp against this run's
`commander_stamp.doctrine_rev` and the binding's current model-generation
tag; any mismatch means the card is stale and the citation is a miss,
recorded as `card=none(<reason>)` with full three-axis grading as the
fallback. Judgment duties never appear on a card (§ Judgment reservation);
the boundary is mechanically scanned at the contract layer.

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
used by card staleness checks and constants-table keys). L1 embeds no ratio,
weight, or price value.

| Tier | Task shape |
|---|---|
| tier-0 (deterministic script) | acceptance, counting, format checks, any decision already expressible as a written command with an exit code. Not a model. Cheapest, fully auditable — always preferred where it exists. |
| frontier | judgment, decomposition, integration, first-time diagnosis, architecture trade-offs, cross-file invariants (usually the commander itself, or the advisor) |
| mid | clear-spec implementation, search/inventory, multi-source research, review lenses (default worker) |
| cheap | batch application of an already-solved pattern; format conversion; mechanical enumeration |

Cheap-tier red line: work needing judgment, first encounters, or a fuzzy
recipe never goes to cheap.

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

Two limits on that audit, because an honesty rule that overreaches buys
nothing and costs a great deal:

- **The mode binds a harness's interface, never its internals.** An adapter may
  build an observation surface only from what its harness *offers* — a
  documented log, an exported metric, a supported API. It may not reach into
  formats the harness never promised to keep stable (session transcripts,
  on-disk state, private files). Such a binding is not portability, it is a
  guess about someone else's implementation, and it will break silently on
  their next release. Where no offered surface exists, the correct answer is
  UNVERIFIABLE — not a cleverer excavation. **A harness that reports a worker
  ran on tier X while running it on tier Y is that harness's defect, not this
  mode's threat model.**
- **The check is scoped to measurement-bearing runs.** Undisclosed advisor use
  corrupts exactly one thing: a claim that attributes work to a tier. It is
  therefore REQUIRED for runs whose output is such a claim (benchmark cells,
  parity runs, ablations — anything whose numbers a reader would trust) and NOT
  required for ordinary orchestration, where UNVERIFIABLE is a legal resting
  state and the disclosure duty stands on the contract alone. Verifying a
  measurement-bearing run is a bounded, one-off act (its cost is known in
  advance); it does not license a standing mechanism in the mode.

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
observations, and (when the contract declares an advisor scope)
judgment_events.

One named exception: where a binding's read-only worker type structurally
cannot write files, its report rides the harness channel and the commander
persists it VERBATIM into the task directory, provenance-noted — the channel
is a carrier, never a second home; the task directory remains the record of
record. The transcription is mechanical for findings; worker-self-reported
doctrine-vocabulary fields (e.g. judgment_events) enter the record only
after the commander's own judgment.

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
{"event":"dispatch_result","task_id":"<id>","checker":"VALID|INVALID","usage":{"<harness-reported worker token counts, verbatim>":0}}
```

The first journal line is ALWAYS `commander_stamp` — the commander
self-reports its model id and the doctrine revision it runs under. Every
dispatch line carries the binding-resolved model actually passed to the
harness mechanism; the conformance audit joins these against execution
telemetry after the run. Additive fields (never a shrink of the vocabulary
above): a `dispatch` line carries `card:"<role>|none"` when role cards are
in play; the `dispatch_result` line (harvest side) records the checker
verdict and the harness-channel-reported worker usage verbatim — the
collector's per-worker input at close.

**dispatch-plan.md** (the commander keeps it in the task directory).
Mandatory fields — exactly three, unconditional:

1. **Entry decision** — write shape + execution config (read breadth, worker
   count, tiers, advisor setup) + named grounds + task family + the cited
   price row (by row identity) or `[pending-measurement]`; human veto record
   if any.
2. **Shape & precedent** (machine-readable; the precedent lookup key):
   `task-shape: kind=<kind>, write_surface=<surface>` + the family line +
   `precedent: cited <run_id>` | `precedent: deviation — <written reason>` |
   `precedent: no-match`.
3. **Subtask table** — one row per dispatched subtask:
   `| subtask | grade (3 axes) or card=<role>@<graded_under> | tier | resolved model | why-not-a-script | contract path | wave |`
   (a valid card citation replaces the grade columns; miss/stale =
   `card=none(<reason>)` + full grading).

Conditional fields — each owed ONLY when its trigger fires; an absent field
with no trigger is compliant, and "owed but missing" is decidable from
journal events:

- **Brake line** — owed when any offload is planned or executed (a
  zero-dispatch inline run owes none). One line per wave:
  `brake: offload=[{tier:<t>,W≈<int>,r=<ratio>}...] save=<int> pay=<int>
  verdict=pass|fail ground=<wall-clock|corpus|disjoint-write|none>
  constants_row=<key>@<run_id>/<ts> r_rev=<binding changelog rev>
  k_note="<optional>"`.
- **Containment check** — owed when any write-role dispatch exists: expected
  drift exposure (duration × scope × novelty proxies) vs containment
  capacity (mechanical-acceptance coverage × recovery cost).
- **Doubt surfacing** — owed when an entry or grading `judgment_moment`
  lands with disposition ≠ frozen: what the commander is least sure about.
- **Deviation log** — opens at the first deviation event (escalation,
  scope-change ruling, threshold crossing, advisor-unavailable degradation).

**Persistence:** dispatch-plan.md is append-per-wave. Each wave appends its
own section — including its brake line — and NEVER rewrites an earlier
wave's section: the brake-line audit presumes this; a rewrite is audit
history destroyed.

## Precedent & eval loop

Two ledger tiers, both append-only, both operator-local, neither shipped.

**Project tier — journal + precedent ledger:** a per-project append-only
ledger records every run (line formats: the contract layer's precedent
schema; the file path is named by each harness binding). Append after EVERY
run, including failed and blocked-to-human terminals — the outcome verdict
records the terminal state. Never rewrite an existing line: history is
evidence; the ledger is a version-controlled file, and a diff showing an
existing line changed is itself a violation.

**Operator tier — constants table:** one table per operator, keyed
`task_family × harness × model_gen` (path named by each binding at the
operator level; row schemas live in the contract layer). It ships EMPTY — no
seeded values; every family starts `[pending-measurement]`, and the numbers
can only come from that operator's own runs. Row kinds:

- `constants` rows (C_fresh / C_brief_cmd / C_brief_worker / C_reread —
  burner-tagged raw tokens, with a fidelity mark naming the source surface):
  appended by the binding's tier-0 collector at precedent-append time,
  reading ONLY the run journal and the binding's declared offered surfaces
  (the interface-not-internals rule of § Advisor primitive governs;
  transcripts and on-disk internal formats are illegal sources). Missing
  usage events or no offered surface → the collector appends an
  UNVERIFIABLE row and the run closes normally; collector degradation never
  blocks a run.
- `discipline-price` rows: produced ONLY by an ablation pair (same task,
  0-worker form vs bare) — a single run's collector never produces one.

Reading state machine (consumers: gate + brake): per key, the FIRST measured
row is consumable (bootstrap — first use needs no ruling); every later
change lands as `proposed` (not consumable) until a human promotes it
(supersede-by-append, never in-place). Price rows skip `proposed`: each
ablation pair appends `measured` directly, and a re-measurement replaces the
old row only on human promote. Concurrent same-key first rows serialize on
the file lock; "first" = file order. Appends are lock-serialized single-line
atomic writes (cross-project concurrency safe).

**Pre-dispatch duty (cite-or-deviate):** before dispatching, query the
project ledger for lines matching the declared task shape (`task_shape.kind`
+ `write_surface` equality). A match must be either cited in the dispatch
plan (by `run_id`) or deviated from with a written reason. Querying is a
duty; following is not. No match is a vacuous pass, recorded as `no-match`.

**Calibration loop:** at run close, run the deterministic trigger check
(tier-0): ≥3 same-shape runs carrying a consistent typed `deviation_signal`
(estimate-drift from the brake's W comparison included) → append a
`calibration/v1` `status=proposed` line, list it in the run report's
pending-calibrations section, and emit a promote-pending notification
through the binding-named channel (a harness without one degrades to the
report floor; emission failure is journaled and never blocks run close). An
open proposed line suppresses duplicate triggers for the same rule.
Promotion or rejection is human-only, recorded by APPEND (a new line
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
