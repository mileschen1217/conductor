#!/usr/bin/env python3
"""audit-brake-lines.py — brake audit over an instrumented run journal.

Python 3 stdlib ONLY. Input is always a journal: the brake's computed, typed
form is instrumentation (doctrine § Amortization brake, "Two forms, one rule"),
so an audit of it has a journal or it has nothing.

Stamp gate (fail-closed, same polarity as every stamp-keyed audit): a journal
handed to this audit that carries no commander_stamp, or a stamp below VOCAB,
FAILS. There is no legacy dialect and no fallback — a journal from an earlier
vocabulary belongs to a run that has closed, and is never re-invoked.

Per-event checks:
  - verdict enum pass|fail|not-computable
  - ground enum wall-clock|corpus|disjoint-write|verification-mandated|none
    (the four necessity grounds plus the absent marker) — an unrecognized
    ground is a VIOLATION, not free text
  - LAUNCH RULE (doctrine § Amortization brake): an economics-failing brake
    whose wave actually dispatched must name a necessity ground. verdict=fail
    or not-computable, a non-empty offload, a dispatch in the same wave, and
    ground none/absent = VIOLATION. This is the mechanical enforcement of "an
    economics-failing dispatch without a necessity ground does not launch";
    planning an offload and then NOT launching it is the rule working, and is
    clean.
  - r membership in the allowed set (--r-values / --commander-r as below)
  - computed-term stations (inputs.C_brief_cmd, inputs.C_reread, and per
    offload C_brief_worker + corpus) each carry a recomputable basis
    {refs, bytes, class}; a station without one is an INVENTED VALUE (FAIL)
  - save = Σ w_est×(1−r); pay = C_reread.tok + C_brief_cmd.tok +
    Σ r×(C_brief_worker.tok + boot + corpus.tok) (5% tolerance)
  - with --anchors prose=<r>,code=<r>,cjk=<r>[,correction=<f>]: each
    computed term's tok is band-checked against basis.bytes through the
    anchor rates (order-of-magnitude tolerance — anchor-table precision)
  - EVERY offload on a computed verdict (pass|fail) owes a non-null
    probe_ref — boot:0 without one is an invented zero (the honest no-probe
    state is verdict=not-computable); with --probe <probe.jsonl> the
    reference must resolve to a row (config_hash@ts), and ANY malformed
    line in the probe record makes every probe_ref unverifiable
    (whole-record suspicion, conservative-closed); anchor_rev and r_rev
    must be present (bad-ref FAIL otherwise)

Usage:
  audit-brake-lines.py <journal.jsonl> [--anchors ...] [--probe <probe.jsonl>] \
      [--r-values 1.0,0.4,0.2,0.1,0.5] [--commander-r 0.2,0.1]

--commander-r narrows the legal set to the given commander's OWN column of
the binding's per-pair table (plus 1.0, always legal for same-model). Without
it the audit can only check set membership, not pair correctness — a live
witness run (MR7) wrote r=0.2 for a same-model offload (true value 1.0) and
set-membership alone passed it. CAVEAT: even with --commander-r the
protection is commander-dependent, not general pair-correctness — the
offload's tier label is not cross-checked against r, so a mislabeled r that
coincides with another legitimate value in the SAME commander's column still
passes. Full pair verification needs the worker's resolved model, which brake
events do not carry.

Exit: 0 = no VIOLATION; 1 = any VIOLATION; 2 = env/usage error.
"""
import argparse
import json
import os
import sys

VOCAB = 3
CLASS_ENUM = ("prose", "code", "cjk", "mixed")
VERDICT_ENUM = ("pass", "fail", "not-computable")
# The four necessity grounds (doctrine § Amortization brake) plus the marker
# for "no ground named". `none` is legal only where no ground is owed.
NECESSITY_GROUNDS = ("wall-clock", "corpus", "disjoint-write", "verification-mandated")
GROUND_ENUM = NECESSITY_GROUNDS + ("none",)


def parse_anchor_arg(spec):
    """Mirror estimate-tokens.py's validation: prose/code/cjk required, all
    positive. Raises ValueError (caller maps to exit 2 usage error)."""
    rates = {}
    for part in spec.split(","):
        k, _, v = part.partition("=")
        k, v = k.strip(), v.strip()
        if not k or not v:
            raise ValueError(f"malformed anchor entry: {part!r}")
        try:
            rates[k] = float(v)
        except ValueError:
            raise ValueError(f"non-numeric anchor value: {part!r}")
    for req in ("prose", "code", "cjk"):
        if req not in rates:
            raise ValueError(f"anchor {req!r} missing from --anchors")
        if rates[req] <= 0:
            raise ValueError(f"anchor {req!r} must be positive")
    rates.setdefault("correction", 1.0)
    return rates


def is_int(v):
    """True for int, excluding bool (bool is an int subtype in Python)."""
    return isinstance(v, int) and not isinstance(v, bool)


def check_term(name, term, anchors, problems):
    """Validate one computed-term station; return tok (or None)."""
    if not isinstance(term, dict) or not is_int(term.get("tok")):
        problems.append(f"{name}: INVENTED VALUE — not a computed-term object (no recomputable tok)")
        return None
    basis = term.get("basis")
    if (not isinstance(basis, dict)
            or not isinstance(basis.get("refs"), list) or not basis.get("refs")
            or not is_int(basis.get("bytes"))
            or basis.get("class") not in CLASS_ENUM):
        problems.append(f"{name}: INVENTED VALUE — basis missing or malformed (refs/bytes/class required)")
        return term["tok"]
    if anchors:
        b, cls, corr = basis["bytes"], basis["class"], anchors.get("correction", 1.0)

        def exp_for(c):
            if c == "cjk":
                return corr * (b / 3.0) / anchors["cjk"]  # UTF-8 CJK ≈ 3 bytes/char
            return corr * b / anchors[c]

        if cls == "mixed":
            cands = [exp_for(c) for c in ("prose", "code", "cjk")]
            lo, hi = min(cands), max(cands)
        else:
            lo = hi = exp_for(cls)
        tok = term["tok"]
        if b == 0:
            if tok != 0:
                problems.append(f"{name}: tok={tok} from a zero-byte basis")
        elif not (0.5 * lo <= tok <= 2.0 * hi):
            problems.append(
                f"{name}: tok={tok} outside anchor band [{0.5 * lo:.0f}, {2.0 * hi:.0f}] for {b} bytes class={cls}")
    return term["tok"]


def load_probe_rows(path):
    """Returns (rows, malformed_lines). A malformed line in the probe record
    makes every probe_ref against it unverifiable — conservative-closed: the
    caller flags it, never silently skips (a suspicious record is never
    consumed; same polarity as probe-select's ERROR state)."""
    rows, malformed = [], []
    if not path or not os.path.isfile(path):
        return rows, malformed
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                malformed.append(n)
                continue
            rows.append(r)
    return rows, malformed


def audit(events, args, allowed_r):
    try:
        anchors = parse_anchor_arg(args.anchors) if args.anchors else None
    except ValueError as err:
        print(f"usage error: {err}", file=sys.stderr)
        return 2
    probe_rows, probe_malformed = load_probe_rows(args.probe)
    probe_ids = {
        f"{r.get('config_hash')}@{(r.get('provenance') or {}).get('ts')}"
        for r in probe_rows
    }
    brakes = [(ln, e) for ln, e in events if e.get("event") == "brake"]
    dispatches = [(ln, e) for ln, e in events if e.get("event") == "dispatch"]
    dispatched_waves = {e.get("wave") for _, e in dispatches}

    violations = 0
    if dispatches and not brakes:
        print(f"VIOLATION: journal carries {len(dispatches)} dispatch event(s) but NO brake event — "
              "owed-but-missing (an instrumented run owes a typed brake event per offload wave)")
        print("RESULT: 1 violation(s) in 0 brake event(s)")
        return 1
    if not brakes:
        print("NO-BRAKE-EVENTS: journal carries none (legal for a run that dispatched nothing)")
        return 0

    for n, (ln, e) in enumerate(brakes, 1):
        problems = []
        verdict = e.get("verdict")
        if verdict not in VERDICT_ENUM:
            problems.append(f"verdict off enum: {verdict!r}")
        offloads = e.get("offload") or []
        ground = e.get("ground")
        if ground is not None and ground not in GROUND_ENUM:
            problems.append(
                f"ground off enum: {ground!r} not in {list(GROUND_ENUM)} — the necessity "
                "grounds are a closed enum, not free text")
        # The launch rule, mechanized. A brake whose economics did not clear,
        # on a wave that actually dispatched, must name one of the four
        # grounds. Deciding not to launch is the rule working — not a finding.
        launched = e.get("wave") in dispatched_waves
        if verdict in ("fail", "not-computable") and offloads and launched \
                and ground not in NECESSITY_GROUNDS:
            problems.append(
                f"verdict={verdict} with a launched offload (wave {e.get('wave')!r} has a "
                f"dispatch) and ground={ground!r} — an economics-failing dispatch without a "
                "necessity ground does not launch")
        inputs = e.get("inputs") or {}
        c_reread = check_term("inputs.C_reread", inputs.get("C_reread"), anchors, problems)
        c_brief_cmd = check_term("inputs.C_brief_cmd", inputs.get("C_brief_cmd"), anchors, problems)
        pay_offload = 0.0
        save_expected = 0.0
        pay_computable = c_reread is not None and c_brief_cmd is not None
        needs_probe_ref = False
        for i, o in enumerate(offloads):
            r = o.get("r")
            if not isinstance(r, (int, float)) or float(r) not in allowed_r:
                problems.append(f"offload[{i}]: r={r!r} outside the allowed binding set {sorted(allowed_r)}")
                continue
            w = o.get("w_est")
            if is_int(w):
                save_expected += w * (1 - float(r))
            else:
                problems.append(f"offload[{i}]: w_est missing or non-integer")
            boot = o.get("boot")
            cbw = check_term(f"offload[{i}].C_brief_worker", o.get("C_brief_worker"), anchors, problems)
            corpus = check_term(f"offload[{i}].corpus", o.get("corpus"), anchors, problems)
            if not is_int(boot):
                problems.append(f"offload[{i}]: boot missing or non-integer (probe-record value, cited via probe_ref)")
                boot = 0
            if verdict in ("pass", "fail"):
                # EVERY offload on a computed verdict owes a probe-cited boot
                # value — boot:0 without a probe_ref would be a free pass for an
                # invented zero (fail-open); the honest no-probe state is
                # verdict=not-computable, never a computed verdict.
                needs_probe_ref = True
            if cbw is None or corpus is None:
                pay_computable = False
            else:
                pay_offload += float(r) * (cbw + boot + corpus)
        if needs_probe_ref:
            pref = e.get("probe_ref")
            if not pref:
                problems.append("offload on a computed verdict but probe_ref is null/absent — bad-ref (the boot value has no cited source; no-probe economics is verdict=not-computable)")
            elif args.probe and probe_malformed:
                problems.append(
                    f"probe record has malformed line(s) {probe_malformed} — suspicious record, probe_ref {pref!r} unverifiable (conservative-closed)")
            elif args.probe and pref not in probe_ids:
                problems.append(f"probe_ref {pref!r} does not resolve in the probe record — bad-ref")
        for ref_field in ("anchor_rev", "r_rev"):
            if not e.get(ref_field):
                problems.append(f"{ref_field} missing — bad-ref (computed values cite no binding changelog rev)")
        if verdict in ("pass", "fail"):
            save, pay = e.get("save"), e.get("pay")
            if not is_int(save) or not is_int(pay):
                problems.append(f"save/pay non-numeric ({save!r}/{pay!r}) on a computed verdict")
            else:
                if offloads and abs(save_expected - save) > max(5, 0.05 * max(save_expected, 1)):
                    problems.append(f"save={save} inconsistent with Σ w_est·(1−r)={save_expected:.0f}")
                if pay_computable:
                    pay_expected = c_reread + c_brief_cmd + pay_offload
                    if abs(pay_expected - pay) > max(5, 0.05 * max(pay_expected, 1)):
                        problems.append(f"pay={pay} inconsistent with recomputed {pay_expected:.0f}")
        if problems:
            violations += 1
            print(f"VIOLATION event {n} (journal line {ln}): " + "; ".join(problems))
        else:
            print(f"CONFORMANT event {n} (journal line {ln})")

    if violations:
        print(f"RESULT: {violations} violation(s) in {len(brakes)} brake event(s)")
        return 1
    print(f"RESULT: CLEAN ({len(brakes)} brake event(s))")
    return 0


def load_journal(path):
    """Return list of (lineno, event-dict), or None if the file is not JSONL."""
    events = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                return None
            if not isinstance(obj, dict):
                return None
            events.append((n, obj))
    return events or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("journal", help="journal.jsonl of an instrumented run")
    ap.add_argument("--anchors", default=None,
                    help="prose=<r>,code=<r>,cjk=<r>[,correction=<f>] for tok band recompute")
    ap.add_argument("--probe", default=None,
                    help="probe.jsonl to resolve probe_ref citations against")
    ap.add_argument("--r-values", default="1.0,0.4,0.2,0.1,0.5")
    ap.add_argument("--commander-r", default=None,
                    help="the commander's own column of the per-pair r table; narrows the legal set (1.0 stays legal)")
    args = ap.parse_args()

    if not os.path.isfile(args.journal):
        print(f"usage error: journal not found: {args.journal}", file=sys.stderr)
        return 2
    allowed_r = {float(x) for x in args.r_values.split(",")}
    if args.commander_r:
        allowed_r = {1.0} | {float(x) for x in args.commander_r.split(",")}

    events = load_journal(args.journal)
    if events is None:
        print(f"usage error: not a JSONL journal: {args.journal}", file=sys.stderr)
        return 2

    stamp = next((e for _, e in events if e.get("event") == "commander_stamp"), None)
    vocab = (stamp or {}).get("vocab")
    if stamp is None:
        print("VIOLATION: stamp gate: journal carries no commander_stamp — a journal handed "
              f"to this audit must declare its dialect (vocab {VOCAB}); there is no legacy fallback")
        return 1
    if not (is_int(vocab) and vocab >= VOCAB):
        print(f"VIOLATION: stamp gate: commander_stamp.vocab={vocab!r} is absent or below the "
              f"current vocabulary {VOCAB} — this journal was written in a dialect whose run has "
              "closed; it is not re-audited under the current rules")
        return 1
    return audit(events, args, allowed_r)


if __name__ == "__main__":
    sys.exit(main())
