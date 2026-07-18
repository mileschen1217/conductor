#!/usr/bin/env python3
"""audit-brake-lines.py — brake audit, journal typed-event dialect primary
(v3.1 REQ-9 / AC-19); prose-plan dialect retained as LEGACY for historical
runs (v3 AC-7 behavior, frozen — new rules land in the journal dialect only).

Dialect selection is keyed on the INPUT + the vocab stamp, never on event
presence:
  - input parses as a JSONL journal (first non-empty line is a JSON object)
    AND commander_stamp.vocab >= 2  → journal dialect: read typed `brake`
    events, recompute both sides from the events' own computed-term bases,
    resolve probe_ref/anchor_rev/r_rev references. A vocab >= 2 journal with
    dispatch events but NO brake event = FAIL (owed-but-missing; the prose
    plan has no audit standing and is no fallback escape).
  - input is a JSONL journal WITHOUT the vocab stamp → named LEGACY output,
    exit 0 (the prose-plan dialect applies to that run's plan file; an honest
    old journal never eats a false VIOLATION).
  - input is a markdown plan → legacy prose dialect (below), unchanged.

Journal-dialect per-event checks:
  - verdict enum pass|fail|not-computable
  - r membership in the allowed set (--r-values / --commander-r as below)
  - computed-term stations (inputs.C_brief_cmd, inputs.C_reread, and per
    offload C_brief_worker + corpus) each carry a recomputable basis
    {refs, bytes, class}; a station without one is an INVENTED VALUE (FAIL)
  - warm offload items carry boot=0 and corpus.tok=0
  - save = Σ w_est×(1−r); pay = C_reread.tok + C_brief_cmd.tok +
    Σ r×(C_brief_worker.tok + boot + corpus.tok) (5% tolerance)
  - with --anchors prose=<r>,code=<r>,cjk=<r>[,correction=<f>]: each
    computed term's tok is band-checked against basis.bytes through the
    anchor rates (order-of-magnitude tolerance — anchor-table precision)
  - EVERY cold offload on a computed verdict (pass|fail) owes a non-null
    probe_ref — boot:0 without one is an invented zero (the honest no-probe
    state is verdict=not-computable); with --probe <probe.jsonl> the
    reference must resolve to a row (config_hash@ts), and ANY malformed
    line in the probe record makes every probe_ref unverifiable
    (whole-record suspicion, conservative-closed); anchor_rev and r_rev
    must be present (bad-ref FAIL otherwise)
  - verdict=not-computable with a non-empty offload and ground=none = FAIL
    (conservative-closed: economics leg uncomputable ⇒ necessity ground only)

Legacy prose dialect (frozen): checks every `brake:` line in a dispatch plan
against the constants table and an allowed r-value set.

Usage:
  audit-brake-lines.py <journal.jsonl> [--anchors ...] [--probe <probe.jsonl>] \
      [--r-values 1.0,0.4,0.2,0.1,0.5] [--commander-r 0.2,0.1]
  audit-brake-lines.py <dispatch-plan.md> --table <constants.jsonl> \
      [--r-values 1.0,0.4,0.2,0.1,0.5] [--commander-r 0.2,0.1]

--commander-r narrows the legal set to the given commander's OWN column of
the binding's per-pair table (plus 1.0, always legal for same-model). Without
it the audit can only check set membership, not pair correctness — a live
witness run (MR7) wrote r=0.2 for a same-model offload (true value 1.0) and
set-membership alone passed it. CAVEAT: even with --commander-r the
protection is commander-dependent, not general pair-correctness — the
offload's tier label is not cross-checked against r, so a mislabeled r that
coincides with another legitimate value in the SAME commander's column
(e.g. 0.2 under an opus commander, where 0.2 is the legitimate haiku rate)
still passes. Full pair verification needs the worker's resolved model,
which brake lines do not carry.

Per-line verdicts:
  CONFORMANT — parses, r values allowed, citation resolves, arithmetic checks
  DEVIATION  — parses loosely but off the documented format (e.g. verdict off
               enum, save/pay declared uncomputable, cold-start citation) —
               calibration data, not a violation
  VIOLATION  — an invented constant: numeric save/pay inconsistent (>5%) with
               W/r and the cited row; an r outside the allowed set; or a row
               citation that does not resolve in the table

Exit: 0 = no VIOLATION (deviations reported); 1 = any VIOLATION; 2 = env/usage.
"""
import argparse
import json
import os
import re
import sys

OFFLOAD_RE = re.compile(r"\{tier:([^,}]+),W≈(\d+),r=([0-9.]+)[^}]*\}")
FIELD_RE = {
    "save": re.compile(r"save=(\S+)"),
    "pay": re.compile(r"pay=(\S+)"),
    "verdict": re.compile(r"verdict=(\S+)"),
    "ground": re.compile(r"ground=(\S+)"),
    "constants_row": re.compile(r"constants_row=(\S+)"),
}


def load_table(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("kind") == "constants":
                rows.append(r)
    return rows


def resolve_citation(cite, rows):
    """A citation resolves iff its run_id (the @<run_id>/ part) matches a
    constants row's provenance.run_id and every key token embedded in the
    cite's key part appears among that row's key values."""
    m = re.match(r"(.+)@([^/]+)/(.+)", cite)
    if not m:
        return None
    keystr, run_id, _ts = m.group(1), m.group(2), m.group(3)
    for r in rows:
        if r.get("provenance", {}).get("run_id") != run_id:
            continue
        vals = set(str(v) for v in r.get("key", {}).values())
        tokens = [t for t in re.split(r"[,:|{}\s]+", keystr) if t]
        embedded = [t for t in tokens if t in vals]
        if embedded:
            return r
    return None


CLASS_ENUM = ("prose", "code", "cjk", "mixed")


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


def journal_dialect(events, args, allowed_r):
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

    violations = 0
    if dispatches and not brakes:
        print(f"VIOLATION: journal carries {len(dispatches)} dispatch event(s) but NO brake event — "
              "owed-but-missing (vocab >= 2 owes a typed brake event per offload wave; "
              "a prose plan has no audit standing and is no fallback)")
        print("RESULT: 1 violation(s) in 0 brake event(s)")
        return 1
    if not brakes:
        print("NO-BRAKE-EVENTS: journal carries none (legal for a zero-offload inline run)")
        return 0

    for n, (ln, e) in enumerate(brakes, 1):
        problems = []
        verdict = e.get("verdict")
        if verdict not in ("pass", "fail", "not-computable"):
            problems.append(f"verdict off enum: {verdict!r}")
        offloads = e.get("offload") or []
        ground = e.get("ground")
        if verdict == "not-computable" and offloads and ground in (None, "none"):
            problems.append(
                "not-computable economics with a non-empty offload and ground=none — "
                "conservative-closed breach (necessity ground required)")
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
            warm = o.get("warm") is True
            boot = o.get("boot")
            cbw = check_term(f"offload[{i}].C_brief_worker", o.get("C_brief_worker"), anchors, problems)
            corpus = check_term(f"offload[{i}].corpus", o.get("corpus"), anchors, problems)
            if not is_int(boot):
                problems.append(f"offload[{i}]: boot missing or non-integer (probe-record value, cited via probe_ref)")
                boot = 0
            if warm and (boot != 0 or (isinstance(corpus, int) and corpus != 0)):
                problems.append(f"offload[{i}]: warm=true but boot={boot}, corpus.tok={corpus} — warm zeroes both terms")
            if not warm and verdict in ("pass", "fail"):
                # EVERY cold offload on a computed verdict owes a probe-cited
                # boot value — boot:0 without a probe_ref would be a free pass
                # for an invented zero (fail-open); the honest no-probe state
                # is verdict=not-computable, never a computed verdict.
                needs_probe_ref = True
            if cbw is None or corpus is None:
                pay_computable = False
            else:
                pay_offload += float(r) * (cbw + boot + corpus)
        if needs_probe_ref:
            pref = e.get("probe_ref")
            if not pref:
                problems.append("cold offload on a computed verdict but probe_ref is null/absent — bad-ref (the boot value has no cited source; no-probe economics is verdict=not-computable)")
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
    print(f"RESULT: CLEAN ({len(brakes)} brake event(s), journal dialect)")
    return 0


def try_load_journal(path):
    """Return list of (lineno, event-dict) if the file reads as JSONL, else None."""
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
    ap.add_argument("plan", help="journal.jsonl (primary dialect) or dispatch-plan.md (legacy)")
    ap.add_argument("--table", default=None)
    ap.add_argument("--anchors", default=None,
                    help="journal dialect: prose=<r>,code=<r>,cjk=<r>[,correction=<f>] for tok band recompute")
    ap.add_argument("--probe", default=None,
                    help="journal dialect: probe.jsonl to resolve probe_ref citations against")
    ap.add_argument("--r-values", default="1.0,0.4,0.2,0.1,0.5")
    ap.add_argument("--commander-r", default=None,
                    help="the commander's own column of the per-pair r table; narrows the legal set (1.0 stays legal)")
    args = ap.parse_args()

    if not os.path.isfile(args.plan):
        print(f"usage error: plan not found: {args.plan}", file=sys.stderr)
        return 2
    allowed_r = {float(x) for x in args.r_values.split(",")}
    if args.commander_r:
        allowed_r = {1.0} | {float(x) for x in args.commander_r.split(",")}

    events = try_load_journal(args.plan)
    if events is not None:
        stamp = next((e for _, e in events if e.get("event") == "commander_stamp"), None)
        vocab = (stamp or {}).get("vocab")
        if isinstance(vocab, int) and not isinstance(vocab, bool) and vocab >= 2:
            return journal_dialect(events, args, allowed_r)
        print("LEGACY: journal carries no vocab stamp (pre-v3.1 dialect) — typed brake events "
              "not owed by this journal; the prose-plan dialect applies to that run's plan file "
              "(visible degradation, never a false VIOLATION)")
        return 0

    if not args.table:
        print("usage error: prose-plan dialect requires --table", file=sys.stderr)
        return 2
    rows = load_table(args.table)

    plan = open(args.plan, encoding="utf-8").read()
    # A brake record is LOGICAL: it starts at `brake:` (possibly
    # backtick-wrapped) and runs until a blank line, a heading, or end of
    # text — live plans wrap and continue lines. Collapse to one string.
    lines = [
        re.sub(r"\s+", " ", m.group(0).replace("`", "")).strip()
        for m in re.finditer(r"`?brake:\s*offload=.*?(?=\n\s*\n|\n#|\Z)", plan, re.DOTALL)
    ]
    if not lines:
        print("NO-BRAKE-LINES: plan carries none (legal for a zero-offload inline run)")
        return 0

    violations = 0
    for n, line in enumerate(lines, 1):
        problems, deviations = [], []
        offloads = [(t.strip(), int(w), float(r)) for t, w, r in OFFLOAD_RE.findall(line)]
        if not offloads:
            deviations.append("no parseable offload entries")
        for _t, _w, r in offloads:
            if r not in allowed_r:
                problems.append(f"r={r} outside the allowed binding set {sorted(allowed_r)}")
        f = {k: (rx.search(line).group(1) if rx.search(line) else None) for k, rx in FIELD_RE.items()}
        if f["verdict"] not in ("pass", "fail"):
            deviations.append(f"verdict off enum: {f['verdict']}")
        cite = f["constants_row"] or ""
        cited_row = None
        if cite.startswith("none(") or "pending-measurement" in cite:
            deviations.append(f"cold-start citation: {cite}")
        elif cite:
            cited_row = resolve_citation(cite, rows)
            if cited_row is None:
                problems.append(f"constants_row citation does not resolve in table: {cite}")
        else:
            deviations.append("constants_row field absent")

        def as_int(s):
            try:
                return int(s)
            except (TypeError, ValueError):
                return None

        save, pay = as_int(f["save"]), as_int(f["pay"])
        if save is None or pay is None:
            deviations.append(f"save/pay non-numeric ({f['save']}/{f['pay']}) — economics leg declared uncomputable")
        elif offloads:
            exp_save = sum(w * (1 - r) for _t, w, r in offloads)
            if abs(exp_save - save) > max(5, 0.05 * max(exp_save, 1)):
                problems.append(f"save={save} inconsistent with Σ W·(1−r)={exp_save:.0f}")
            if cited_row:
                c = cited_row["const"]
                exp_pay = c["C_reread"] + c["C_brief_cmd"] + sum(
                    r * (c["C_fresh"] + c["C_brief_worker"]) for _t, _w, r in offloads
                )
                if abs(exp_pay - pay) > max(5, 0.05 * max(exp_pay, 1)):
                    problems.append(f"pay={pay} inconsistent with table row arithmetic {exp_pay:.0f}")

        if problems:
            violations += 1
            print(f"VIOLATION line {n}: " + "; ".join(problems))
        elif deviations:
            print(f"DEVIATION line {n}: " + "; ".join(deviations))
        else:
            print(f"CONFORMANT line {n}")

    if violations:
        print(f"RESULT: {violations} violation(s) in {len(lines)} brake line(s)")
        return 1
    print(f"RESULT: CLEAN ({len(lines)} brake line(s); deviations are calibration data)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
