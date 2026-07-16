# Four-arm dev-benchmark — distill kernel Phase 1 (2026-07-16)

**What this is.** An external, real-task ablation of conductor's orchestration mode. Four
independent implementations built the *same frozen spec* (a ~1500-line deterministic,
zero-LLM ingest kernel) by four different development methodologies, headless, one at a
time, every arm's commander pinned to `opus`. One held-out pytest suite, four fresh-context
code judges, and one three-source cost ledger graded all four; a final independent model
adjudicated the suite's own failures and ranked the arms.

The benchmark harness and its full method are the single home at
`distill` repo → `benchmark/README.md`. This document is the **findings handoff for
conductor** — it carries the numbers, the analysis, and the direction for v3. It is retained
deliberately: **the distill kernel task is now a regression baseline. When conductor v3
exists, re-run the same four arms against the same frozen spec and compare.**

Everything below is n=1 per arm. Confidence in the ranking is **low** by the synthesizer's
own ruling. Read it as a direction-finder, not a verdict.

---

## The four arms

| arm | methodology | what it isolates |
|---|---|---|
| `inline` | main thread, ad-hoc subagents, no orchestration mechanism | the floor |
| `inline-v2form` | conductor v2, full mechanism, **0 workers** (commander keeps the pen) | the naked price of the discipline, with fan-out removed |
| `anvil-sdd` | `/touchstone:anvil` SDD, its reviewers billed (incl. cross-vendor Codex) | the incumbent methodology, honestly costed |
| `conductor` | conductor v2, commander-worker, topology chosen by the entry gate | the challenger on its home ground |

`inline` vs `inline-v2form` is the load-bearing pair: **same commander, same model, same pen,
0 workers on both — the only difference is whether the conductor v2 mechanism was running.**
That pair isolates the price of the discipline itself, with fan-out held out.

---

## Complete data

All numbers measured by the harness itself, not read from the CLI (see "Measurement" below
for why that distinction is load-bearing). `cost_total` = billed Claude cost + estimated
Codex cost; only `anvil-sdd` used Codex.

| arm | suite | correctness¹ | quality¹ | cost_total | wall (min) | turns | subagents | out tokens | cache-read |
|---|---|---|---|---|---|---|---|---|---|
| `inline` | 132/135 | 2 | 4 | **$11.38** | 37.5 | 76 | 1 | 155,611 | 11.5M |
| `inline-v2form` | 132/135 | **4** | 4 | $16.07 | **32.3** | 74 | 1 | 140,271 | 13.8M |
| `anvil-sdd` | 131/135 | 4 | **5** | $73.32 | 233.4 | 135 | 48 | 932,608 | 87.9M |
| `conductor` | 130/135 | 3 | 4 | $32.84 | 87.7 | 79 | 9 | 512,883 | 45.3M |

¹ correctness/quality = the final synthesizer's 1–5 scores, *after* adjudicating suite
failures (raw suite pass-count is not the correctness score — see next section).

**Per-model output-token split** (where the work physically ran):

| arm | opus out | sonnet out | codex(gpt-5.5) out | main-thread share | subagent share |
|---|---|---|---|---|---|
| `inline` | 94,034 | 61,577 | — | 60% | **39%** (a sonnet reviewer) |
| `inline-v2form` | 140,271 | **0** | — | **87%** | 12% |
| `anvil-sdd` | 264,488 | 640,084 | 28,036 | 28% | 68% |
| `conductor` | 100,856 | **412,027** | — | 19% | **80%** |

**Judge sheet** (fresh context per arm, code-only, not told which arm or methodology):
all four **verdict = sound**, **zero I-1/I-3 invariant violations, zero gaming**. Honesty
findings: `inline` 1, `inline-v2form` 1, `anvil-sdd` 0, `conductor` 0.

---

## Headline: the ruler was wrong more often than the arms were

Ranking (synthesizer): **`inline-v2form` > `anvil-sdd` > `conductor` > `inline`.**

The **raw suite pass-count was overturned by adjudication** — which is the entire reason the
suite was ruled one lens of three, not the verdict. Of the 3 distinct failing ACs, **2 were
the grader or the spec, not the code**:

- **AC-42** (failed by `inline-v2form`, `anvil-sdd`, `conductor` — 3 of 4) → **grader
  artifact**. The fixture title is `"What is AI Ethics?"`; the frozen safe-title rule maps
  `?`→`-`, so a compliant arm writes `<date> What is AI Ethics-.md`. The suite planted the
  colliding note at `<date> What is AI Ethics.md` (no `-`). The two filenames never collide,
  so *not* appending the video id is correct — which is what the 3 "failing" arms did.
  `inline` "passes" only because it strips trailing `-` as edge punctuation, a deviation from
  the frozen rule that strips only `.` and whitespace. **The ruler rewarded the one arm that
  broke the frozen rule and penalized three faithful ones.** This reading was not even in the
  suite's own `INTERPRETATIONS.json` — the suite author never noticed they'd picked a reading.
- **AC-25** (2 arms) → **spec self-contradiction**. The ownership table omits `title` but
  AC-25 asserts on it; the arms that "pass" do so by clobbering human-edited titles, which
  both their own judges flagged as a defect.
- **AC-47** (2 arms: `inline`, `conductor`) → **the one real defect**: `<vault>/.distill/`
  pollution. The other two arms read the same clause and complied.

Plus a 4/4 signal outside the failure set: **AC-43** — all four arms independently hit the
same spec contradiction (`"///"`→`"---"` is non-empty, but AC-43 pins it to the video id)
and all four documented inventing the same workaround. **4/4 correlation = the spec is
broken, not the arms.**

**Three spec self-contradictions (AC-42/AC-25/AC-43 + the quote-predicate hole anvil found)
must be fixed before any branch merges.** This is a distill action item, noted here only
because it explains why the correctness spread is smaller than the raw suite suggests.

---

## The discipline price (the load-bearing finding)

The isolated pair, `inline` → `inline-v2form` (fan-out held out on both):

| | billed | wall clock | turns | cache-write | opus out |
|---|---|---|---|---|---|
| `inline` | $11.38 | 37.5 min | 76 | 325k | 94k |
| `inline-v2form` | $16.07 | 32.3 min | 74 | 581k | 140k |
| **delta** | **+$4.68 (+41%)** | ~~−14% (no time penalty)~~ *(wall-clock claim retracted — did not reproduce; see ADDENDUM)* | flat | **+79%** | +49% |

**~$5 bought spec fidelity** *(the original "no wall-clock penalty" half of this
headline is retracted — r2 measured +44%; see ADDENDUM)*. On this one run the mechanism made
the commander *read the contract more carefully*, not work faster or split work up:
`inline-v2form` honoured the AC-47 clause (its `vaultio.py:106` cites AC-47 by name) where
the floor polluted the vault, and it shipped no undisclosed deviation under a
"full conformance" commit message. Same judge quality (4), same invariant sheet.

**This is a real and cheap effect — and it is n=1, with an effect size of one minor defect
plus one honesty finding.** Do not over-read it.

---

## Why v2 cost *more*, not less (the question this benchmark was really about)

The expectation "v2 should reduce cost" is correct in principle, so the +41% has a specific
cause. **v2 has exactly one cost-reduction mechanism: fan-out work to cheaper model tiers.**
It has no other. With that in hand, both anomalies resolve:

**`inline-v2form` (0 workers): paid the discipline tax, got no tier rebate.**
- 87% of its output stayed on the commander **at opus** (140k opus / 0 sonnet). The floor,
  by contrast, offloaded 39% of its work — and did so to a **sonnet** reviewer.
- So the *undisciplined* arm accidentally did the cost-saving thing (delegate review to a
  cheaper tier) that the disciplined-but-0-worker arm structurally could not.
- The discipline's paperwork is the visible cost: **cache-write +79%** vs the floor. About
  **$3.7 of the $4.68 delta is cache-write/read, not output** — it is the mechanism's
  documents (plan / ledger / phase docs) being written and then re-read every turn.

**`conductor` (with workers): fan-out worked per-token, but got swamped by task size.**
- Fan-out functioned: 80% of output on subagents, **412k on sonnet** vs 100k opus. The
  theory held at the per-token level.
- But **total output ballooned to 512k — 3.3× the floor's 155k** — because coordination
  generates its own volume (worker briefs, plan handoffs, review rounds). Per-token was
  cheaper; token *count* was 3.3× higher. Net: 2.9× the floor's cost.

### The amortization law underneath

> v2 saves money ⟺ (offloaded work × tier discount) > (fixed coordination overhead)

Coordination overhead is roughly **fixed per task** — plan written once, ledger once, review
rounds run regardless of size — so it amortizes only when the parallelizable work is large
enough. **A single ~1500-line kernel is too small; the fixed tax dominates.** This task sits
near the *pessimal* size for fan-out: small enough that overhead dominates, yet the mechanism
still charges full price.

**The benchmark did not show conductor is worthless. It showed conductor is worthless *at
this task size*.** That is a scope finding, not a death sentence.

### Context drag — prose accumulation is a measured cost driver

cache-read tokens re-read per output token produced (high = each unit of work drags a big
accumulated context behind it):

| arm | cache-read / output | cache-write / output |
|---|---|---|
| `inline` | 74.0× | 2.09× |
| **`inline-v2form`** | **98.4× (highest in field)** | **4.14× (2× the floor)** |
| `conductor` | 88.4× | 3.10× |
| `anvil-sdd` | 94.2× | 4.07× |

`inline-v2form` spawned **zero** workers yet carries the heaviest context drag in the whole
field. The only possible source is the mechanism's own prose accumulating and being re-read
each turn. **The prose is the cost driver in the 0-worker case, empirically.** The
discipline's *value* (AC-47 caught) came from a few load-bearing decisions being recorded,
not from document volume — so document volume is a lever with slack in it.

---

## How conductor currently decides fan-out (and the missing brake)

Read from `doctrine/orchestration-mode.md` as of `build/orchestration-mode-v2` @ `30a7cf0`.

**The gate outputs a topology, two orthogonal dials** (§ lines 32–44):
- **Write shape** — `inline` (0-worker) / `1-worker` / `disjoint-write`. Where the pen lives.
- **Read breadth** — `0..k` read-only workers, attachable to any write shape.

**Parallel dispatch has exactly two legal grounds** (line 41–43), cited per dispatch:
`(a) wall-clock`, or `(b) corpus exceeds a single context`. disjoint-write additionally
requires non-overlapping write surfaces.

**The sole refusal ground** (lines 49–55) is *task value below the measured discipline
price* — the ablation-measured overhead of the 0-worker form vs bare inline. **And,
critically: "Before that number exists, refusal is disabled"** — the gate may only annotate
`[pending-measurement]`, never refuse.

### Finding 1 — the cost brake was disabled for lack of a number, and we just produced it

conductor fanned out on a task where it shouldn't have, and the doctrine explains why: its
economic brake requires a *measured* discipline price to cite, that number did not exist, so
refusal was forbidden by the doctrine's own rule. **This benchmark is precisely the ablation
the doctrine asks for: the measured 0-worker discipline price is +$4.68 / +41% on this task.**
Feed it back so the gate can begin refusing sub-threshold tasks instead of running them.

### Finding 2 — there is no brake on fan-out *itself*, only on running the mode

The refusal ground measures whether to run the **mode** (0-worker discipline price). It does
**not** test whether to **fan out**. The two legal grounds for parallel dispatch (wall-clock,
corpus) are **not cost tests** — so a fan-out can be justified "for wall-clock" and open N
workers with nothing checking that the tier discount exceeds the coordination overhead. The
`context economics` axis already exists (line 69: "what re-reading tax does each extra
context pay?") but it is wired only into *tier grading* (frontier vs cheap), **not into the
fan-out go/no-go decision.** This is the exact gap the amortization law above describes.

### Finding 3 — fan-out *scale* has no size-coupling

Scale is bounded by the 5-worker concurrency cap (lines 79–80) and each subtask's tiering
grade, but there is **no formula tying total worker count to task size**. Worker count
emerges from decomposition, so a small task decomposed into N subtasks pays N fresh-context
loads regardless of whether N was worth it.

---

## Would a persistent agent / agent-team help?

The idea: a warm agent that stays resident avoids paying the full fresh-spawn context load on
every dispatch. The data backs the premise hard — **cache-read is 74–98× output**, and a
large fraction of each worker spawn is re-loading spec + plan + codebase orientation into a
cold context.

**It helps in one narrow place, and it is not free.**

- **Where it genuinely helps: the read-breadth dial.** Repeated queries against the *same
  corpus* — a warm reader that loaded the corpus once beats k fresh spawns each loading it.
  This maps directly onto conductor's "corpus exceeds context" ground, but pays the corpus
  load *once*. The harness already supports it (the Agent tool's SendMessage continues a
  spawned agent with context intact).
- **It does not eliminate context drag — it relocates it.** `inline-v2form`'s pathology *was*
  a single warm context (the commander) accumulating prose and re-reading it at 98×. A
  persistent worker does the same thing: its context grows monotonically as it takes on
  tasks, and its per-turn cache-read climbs. It is the amortization law one level down —
  **fresh spawn is expensive-per-spawn but bounded; warm agent is cheap-per-spawn but
  monotonically growing.** Many small same-corpus tasks → warm wins; few large or unrelated
  tasks → fresh wins.
- **It costs the fresh-context independence the safety net is built on.** conductor's
  verification value comes from workers sharing no state with the commander (lines 210–212,
  270: "a fresh-context worker sharing no conversation state") — a fresh reader cannot inherit
  the commander's assumptions, so its judgment is an *independent* vote. A warm agent starts
  inheriting history, and that independence — and the audit model of "artifacts over relay" —
  degrades.

**Recommendation on this:** adopt persistent agents as a *bounded* optimization for
read-heavy, same-corpus phases only (read breadth), never as a general replacement for the
fresh write/verify workers where independence is the point. If adopted, cap accumulated
context with an explicit "discard-and-reopen past threshold N" rule, or it becomes a second
`inline-v2form`.

---

## Recommendations for conductor v3

1. **Wire the measured discipline price into the gate.** +$4.68 / +41% is the number the
   doctrine's refusal ground was waiting for. Enable refusal; route sub-threshold tasks to
   the light path.
2. **Add a fan-out amortization brake.** Beyond wall-clock/corpus, a parallel dispatch should
   pass `(offloaded work × tier discount) > (k × fresh-context load)`. Promote the existing
   `context economics` axis from tier-grading input to a fan-out go/no-go gate.
3. **Put document volume on a diet.** cache-write/read is the 0-worker cost driver; the
   discipline's value came from a few recorded load-bearing decisions, not volume. Trim
   plan/ledger prose to "records only decisions that change downstream behaviour."
4. **Persistent reader for read-breadth**, bounded by a context-discard threshold (above).
5. **Default small tasks to the 0-worker form.** It won this run outright, and dominated the
   worker-fan-out arm on every axis. Fan-out should be opt-in above a size threshold, not the
   default topology.

---

## Honest caveats

- **n=1 per arm. This run does not settle anything.** The whole discipline-price finding
  rests on one minor defect (AC-47) plus one commit-message honesty flag, in a single pair of
  runs.
- **Two observations would overturn the ranking:** (1) re-run `inline` and `inline-v2form`
  once each — if the floor lands AC-47-clean or v2form lands polluted, the $4.68 bought
  nothing measurable and the ranking collapses to pure cost order (floor on top). (2) A spec
  too big for one opus context — fan-out is being judged here on a task one commander can hold
  entirely in context, which is *precisely where fan-out should not pay*. On a larger spec,
  conductor/anvil coordination overhead may invert into an advantage. **This is the primary
  reason to retain the benchmark and re-run at larger scale.**
- **The measurement itself had to be rebuilt to be trusted.** Three of the ranking axes were
  caught reporting silently-wrong numbers from the CLI (cost estimate 5× high; `duration_ms`
  8× low on one arm and correct on another; `num_turns` 7× low on that same arm), each caught
  only because the number was *absurd*. The harness now measures every ranked quantity two
  independent ways and BLOCKs on disagreement. A conductor v3 re-run must keep that discipline
  — a plausible wrong number from a single instrument is unfalsifiable. Detail:
  `distill` repo → `benchmark/README.md` § "The cross-check".

---

## Regression-test protocol for v3

The distill kernel task is retained as a baseline. To re-test v3:

1. From the distill repo, the four arm worktrees branch from `arm-base` (the frozen contract,
   no `benchmark/` dir). Rebuild the `conductor` arm's brief against the v3 mechanism.
2. Run headless, one arm at a time (`benchmark/scripts/run-arm.sh`), same as this run.
3. Grade with the same held-out suite + judges + cost ledger, adjudicate, synthesize.
4. Compare against this document's numbers. **The specific v3 questions:** did the fan-out
   amortization brake (rec 2) stop conductor fanning out on the small kernel task? Did the
   prose diet (rec 3) close the cache-write gap between the 0-worker form and the floor? If
   yes to both, `conductor` and `inline-v2form` should converge toward the floor's cost while
   keeping the +correctness the discipline bought. If they don't, the discipline is not
   paying its way on tasks this size and should default off below the size threshold.

---

## ADDENDUM — confirm re-run (2026-07-16, same day): the discipline finding REPRODUCED

Overturn condition (1) from "Honest caveats" was executed: `inline` and
`inline-v2form` re-run once each as fresh arms (`inline-r2`, `inline-v2form-r2`),
same frozen `arm-base` (a43c48a), same harness, commander pinned opus, advisor
absent, one at a time. Results in distill `benchmark/results/<arm>-r2/`.

| arm | suite | real defect (AC-47) | AC-42 (grader artifact) | cost | wall | subagents |
|---|---|---|---|---|---|---|
| `inline-r2` | 131/135 | **FAILED again — vault polluted 2/2** | failed (= faithful to frozen rule) | $11.91 | 32.6 min | 0 |
| `inline-v2form-r2` | 132/135 | **clean again — 2/2** | failed (same) | $16.33 | 47.1 min | 1 (opus general-purpose) |

- **The load-bearing pair holds at n=2 per side**: the floor pollutes
  `<vault>/.distill/` in 2/2 runs; the v2-form commander honours the clause in
  2/2 runs. Overturn condition (1) did NOT fire.
- **The discipline price reproduced almost exactly: +$4.42 / +37%** (r1:
  +$4.68 / +41%).
- **The wall-clock claim did NOT reproduce**: r1 showed −14% (v2form faster);
  r2 shows +44% (v2form slower, 47.1 vs 32.6 min). Wall clock is noisy across
  runs — drop "no time penalty" from the sellable claim; the stable claims are
  the price and the fidelity.
- Behavioral variance note: the floor's ad-hoc delegation is itself unstable
  (r1: 1 sonnet reviewer, 39% of output; r2: zero subagents). The mechanism's
  behavior was comparatively stable across runs.
- Cross-check: one WARN on `inline-v2form-r2` num_turns (clocked 66 vs CLI 91;
  clocked value ranked). All other instruments agree.
- AC-42 failed in 3 of these 4 re-run/original cells — further reinforcing the
  synthesis ruling that AC-42 is the ruler's defect, not the arms'.
