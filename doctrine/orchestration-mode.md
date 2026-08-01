# Orchestration Mode — Doctrine (L1)

Single home of mode behavior. Harness-neutral: it speaks only in capability
tiers and one dispatch primitive.
**commander** — the orchestrating model instance. **worker** — a model instance
executing exactly one task contract. **human** — the adjudication layer above
the commander; the last word on entry, permission, contract changes, and quality.
Three parts: roots hold every force; the application slab anchors roots to
sites; definitions, defaults and machine pointers close the file.

## Roots

Every root is in force at every moment of a run. Nothing outside this section
adds force; the rest of the file only anchors, defines, or mechanizes what is
stated here.

- **RT-1 — the cut.** The mode begins at the first dispatch: deciding not to
  dispatch is an answer, not an entry, and a run that never dispatches stays
  outside the mode, owing no declaration, contract, result, or journal.
- **RT-2 — paid or named.** The brake inequality authorizes a serial offload
  that pays, and nothing else: any other launch — one whose economics fail, or
  concurrency the inequality does not price — names a necessity ground from
  the closed set and pays that ground's citation duty.
- **RT-3 — claim ≤ evidence.** A value or claim enters the record only with
  its basis; a recorded value with no basis is an invented value.
- **RT-4 — scoped validity.** A cached judgment or measurement is valid only
  for the configuration it was made under; a mismatch is a miss, never a
  fallback, and a run never writes back into the cache it read from.
- **RT-5 — consumer gate.** An artifact exists only when it is about to be
  consumed — a contract file is written when a worker is about to consume it,
  never pre-written per planned subtask — and an invariant is cited from its
  single home, never copied per instance.
- **RT-6 — one pen per surface.** Parallel reads are always legal; parallel
  writes are legal only on non-overlapping surfaces, one writer each, and a
  merge-back of isolated working copies is itself a single-writer step.
- **RT-7 — builder ≠ acceptor.** The builder never accepts its own work: a
  mechanical criterion is accepted by its runnable check artifact, and a taste
  criterion by a named verifier sharing no conversation state with the
  builder, whose dispatch names `verification-mandated` as its ground.
- **RT-8 — judgment reserved; surfaced, not asked.** Permission grants,
  contract changes, and quality verdicts are never delegated to workers or
  automation — the commander holds them, the human overrules the commander,
  and a reserved moment terminates at the human however its station answered;
  surfacing is disclosure, not a request for permission — the commander
  states the moment and its own ruling and proceeds, a no-match owes its
  one-line why, and "the doctrine covers this" is a claim, not an answer.
- **RT-9 — instrumentation is external.** A run is instrumented iff the
  operator set the switch the harness binding names — existence, not content,
  readability never consulted, absence reads as off, and off is the default;
  no property of the run makes it instrumented — not its purpose, not who
  will compare its numbers, not what its brief says about it; whoever armed
  the switch owes the evidence the measurement depends on; and an
  uninstrumented run exercises every station and records nothing —
  instrumentation buys the evidence, never the obligation.
- **RT-10 — records append-only.** The mode's durable records — an
  instrumented run's journal and the project's boot-probe record — are
  append-only, project-local, and never ship: an existing line is never
  rewritten, and a diff showing one changed is itself the violation.

**Growth law.** A new case under an existing root adds at most one site anchor
to the slab and zero new normative text; a case no root can generate is a
spec-level event, never a new entry.

## Application slab

A line anchors one root at one site and adds no force of its own; the section
it sits in names the moment a commander loads it.

### At entry — loaded while ruling on whether and how the run enters the mode

- RT-2 @ entry-gate: the gate weighs no price — every economic question about
  a concrete offload belongs to the brake, at dispatch time.

### At plan — loaded while a wave is graded and priced, before anything launches

- RT-3 @ brake-terms: every recorded brake term names its basis — the
  binding's anchors, the probe row, or the single on-the-spot `W` estimate.
- RT-3 @ grading: a criterion is mechanical only when its runnable check is
  actually written; where one is writable, the grader writes it at grading
  time.
- RT-4 @ role-card: a card citation replaces the grading axes only while its
  `graded_under` stamp matches this run's doctrine revision and the binding's
  generation tag; a mismatch is a miss and full grading is owed.

### At dispatch — loaded at the moment a worker is actually about to start

- RT-9 @ switch: the switch is read when a dispatch is actually happening,
  then latched — no later wave and no consumer re-derives it.
- RT-9 @ switch-writer: the commander never creates, modifies, or deletes the
  switch; its writer is the operator or the harness.
- RT-6 @ dispatch-record: the preventive write-restriction configuration is
  recorded on every dispatch record — on every dispatch run, instrumented or
  not.
- RT-5 @ artifact-naming: a record and its artifact name each other in both
  directions; renaming does not excuse an artifact from the pairing.

### At harvest — loaded when worker output returns and acceptance is ruled

- RT-8 @ scope-change: a non-empty `scope_change_request` stops that line of
  work — escalated verbatim, never approved in the human's stead, never
  re-dispatched enlarged before the ruling.
- RT-3 @ acceptance: "reads as correct" is not evidence; execution output is.
- RT-3 @ worker-report: a doctrine-vocabulary field a worker self-reports
  enters the record only after the commander's own judgment.

### At close — loaded when an instrumented run's audits run and its journal closes

- RT-4 @ audit-dialect: an auditor keys its dialect on the `vocab` stamp,
  never on event presence; a journal with no stamp, or a stamp below the
  current vocabulary, fails the audit it was invoked on.
- RT-3 @ close-verdict: a member that ran and could not conclude for want of
  evidence is a fail — the evidence a measurement depends on is owed, not
  hoped for.
- RT-4 @ drift: `W` is per-task and never becomes a stored constant;
  estimated output against delivered output is journaled as drift.

## Definitions, defaults and machine pointers

A definition carries no force of its own and inherits the consumer of the
rules that use it.

### Definitions

- **Entry declaration** — task family, write shape, read breadth, execution
  config, named grounds, and the human veto when one lands.
- **Topology** — two orthogonal dials: where the pen lives, and how many
  read-only workers attach (0..k). Topology is judged for an unclassified
  task and read off the class for a declared-mechanical one.

  | write shape | meaning |
  |---|---|
  | `inline` | the commander keeps the pen |
  | `1-worker` | one dispatched writer, serialized |
  | `disjoint-write` | multiple writers on non-overlapping surfaces, one per surface |

- **Task family** — follows the deliverable's write surface: empty or
  report-only is `read-heavy`, anything else is `write-heavy`.
- **Declared mechanical** — a task is declared mechanical when every
  acceptance criterion of the work the run executes carries a runnable,
  builder-independent check artifact; the declaration cites those artifacts,
  never a contract document.
- **The brake** — computed separately per offload:

  ```
  Σi W_i × (1−r_i)  >  C_reread + C_brief_cmd + Σi r_i × (C_fresh + C_brief_worker)
  ```

  `W` is the only quantity estimated at the moment of decision; every other
  term derives from artifact bytes through the binding's conversion anchors,
  whose values live only in the binding. `r` is the ratio of posted prices,
  worker to commander. `C_fresh` is what a cold context costs before it has
  read anything: the harness's establishment overhead plus the corpus it must
  read.
- **Necessity grounds** — the closed set:

  | ground | citation duty |
  |---|---|
  | `wall-clock` | the concrete deadline |
  | `corpus` | the corpus-size evidence |
  | `disjoint-write` | the non-overlapping write surfaces |
  | `verification-mandated` | the rule in this doctrine that mandates it |

- **Grading** — every subtask is graded before its wave dispatches:

  | axis | question |
  |---|---|
  | verifiability | is acceptance a written, runnable check? |
  | recovery cost | if the worker is wrong, what does detection plus undo cost? |
  | context economics | does the work fit one context, and what re-reading tax does each extra context pay? |

  Output per subtask: capability tier, read-only or write role, and a
  `why-not-a-script` answer.
- **Capability tiers** — routing speaks only in tiers; a concrete model name
  never appears at this layer. Each harness binding maps every tier to at
  least one model and carries its price ratio, unit weights, and generation
  tag.

  | tier | task shape |
  |---|---|
  | tier-0 (deterministic script) | acceptance, counting, format checks — any decision already expressible as a command with an exit code. Always preferred where it exists; anything gradeable to tier-0 is a script. |
  | frontier | judgment, decomposition, integration, first-time diagnosis, architecture trade-offs, cross-file invariants |
  | mid | clear-spec implementation, search, inventory, multi-source research, review lenses |
  | cheap | batch application of an already-solved pattern; format conversion; mechanical enumeration — never judgment, a first encounter, or a fuzzy recipe |

- **Judgment stations** — a judgment moment is a decision point the commander
  recognizes as a decision; the sites are enumerated:
  `entry-gate | grading-dispute | worker-blocked | acceptance-ambiguity |
  scope-change-preview`.
- **The judgment line** — at each site the commander writes one line carrying
  one of three answers: **match** (a site fits and the ruling is not
  self-evident), **no-match** (no site fits), **misfit-but-uncertain** (no
  site fits and the commander does not trust its own ruling). Match and
  misfit-but-uncertain both surface. The answer records whether a second pair
  of eyes was needed; the disposition records who decided:

  | answer | disposition |
  |---|---|
  | `no-match`, already decided elsewhere | `frozen` — the contract, a gate declaration, or a cited role card |
  | `no-match`, a checker produces the answer | `mechanized` |
  | `match` / `misfit-but-uncertain` | `surfaced` |
  | any answer, moment in the reserved set | `blocked` — overrides every row above |

  A `no-match` that can name neither a freezing source nor a mechanizing
  check has skipped the moment, and the honest answer was
  `misfit-but-uncertain`.
- **A dispatch** — write a task-contract file into the task directory, start
  one worker on it through the harness mechanism, wait for `result.json` and
  validate it with the contract checker; only the middle step is
  harness-bound. Every dispatch is cold: a later wave that needs earlier
  context receives it as artifacts. Within a task directory the contract is
  `task-contract.md` (or `task-contract-<suffix>.md`) and the result is
  `result.json`. Four elements, one missing makes the dispatch defective:

  | element | contract field |
  |---|---|
  | objective & motivation | Scope |
  | output format | Acceptance Criteria |
  | tool & source guidance | Commands to Run + Read-Only Boundaries |
  | task boundary | Do Not Touch + Owned Files |

- **Worker report** — a worker's report is its `result.json`: summary,
  files_changed, commands_run with exit codes, risks, observations. It
  carries paths, never bulk content, and the filesystem is the only
  commander↔worker communication surface. Where a binding's read-only worker
  type structurally cannot write files, the commander persists its channel
  report verbatim into the task directory with a provenance note — the
  channel is a carrier, never a second home.
- **Escalation signals** — the checker's INVALID, a failed contracted
  command, or a timeout; two triggers are the same error when their
  signatures match — exit code plus a fingerprint of the error's first
  distinctive line — and a genuinely different approach resets the count. An
  escalation carries the full failure trail: what was tried, exact commands,
  exact errors, hypotheses already excluded.
- **Close law** — close runs every member of the canonical audit set as one
  invocation, each recorded by name as `pass`, `fail(<rc>)`, or
  `dropped(trigger-absent)`, and no status that is not `pass` collapses into
  `pass`. The member set and its order are named by the adapter's close tool,
  which is cited, never re-enumerated.

### Defaults

- **Task family fail-safe** — what cannot be determined resolves to
  `write-heavy`.
- **Declared-mechanical set** — inline while the corpus fits one context;
  acceptance per check artifact; the entry judgment station pre-answered —
  each overridable with a recorded reason.
- **Worker tier** — one tier below the commander: the cheapest tier expected
  to pass acceptance in one dispatch.
- **Taste fail-safe** — taste is the terminal grade only where no runnable
  check can be written, and it is the fail-safe default.
- **Retry budget** — a retry is legal only while it stays cheaper than the
  escalation it defers: cheap escalates on its first error; at mid one retry
  on the same signature is legal and a second is escalation.
- **Solved pattern** — written as an exact recipe with its verification
  commands and demoted to the cheapest tier that can carry it.

### Machine pointers

- **Journal** — one instrumented run is one mode entry over one contract
  scope and produces exactly one journal, opening on `commander_stamp` and
  closing on `close`; `commander_stamp`, `entry` and `close` are unconditional
  and appear once each; every other event is owed only when its trigger fires,
  and "owed but missing" is decidable from the journal alone. Event vocabulary, required sets, value
  enums, the additive-fields rule, the computed-term shape, and the owed-when
  map: `contract/journal-event.schema.json`.
- **Cross-line journal rules** — `moment_id` uniqueness, `dispatch_result`
  pairing to a dispatch the same journal recorded, and a declared class owing
  its `class_default`: the schema and the journal auditors.
- **Record↔artifact reconciliation** — `scripts/audit-artifact-reconciliation.py`.
- **Brake-line shape and the launch rule** — `scripts/audit-brake-lines.py`.
- **Vendor neutrality** — `scripts/check-neutrality.sh`.
- **Preventive single-writer enforcement** — the harness binding.
- **Boot-probe record** — `contract/probe.schema.json`; the probe procedure is
  the binding's.
- **Contract template rules** — the acceptance-source quoting rule (verbatim
  quote with reference, else `self-authored`) and the behavioral-contract cite
  rule: `contract/task-contract.md`.
