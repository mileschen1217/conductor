#!/usr/bin/env python3
"""estimate-tokens.py — tier-0 bytes→tok-eq conversion helper (v3.1 REQ-3 / AC-5).

Python 3 stdlib ONLY. Pure arithmetic: the script embeds NO anchor values —
every rate comes in through --anchors (the binding's conversion-anchor table
is the single home of the values; this helper is the mechanism).

Model: a file's characters are split into two buckets — CJK characters
(ideographs, kana, hangul, CJK punctuation, fullwidth forms) and everything
else. The non-CJK bucket is charged at the file's extension class rate
(prose or code, chars per tok-eq); the CJK bucket at the cjk rate. The
optional correction factor multiplies the total (tokenizer correction; the
binding names its value). tok-eq = round(correction × (base_chars/base_rate
+ cjk_chars/cjk_rate)).

Extension→class map (embedded here as the classification RULE; the binding's
anchor-table section names it): code = {py sh bash js ts jsx tsx json jsonl
yaml yml toml c h cpp hpp cc rs go java rb pl swift kt sql}; everything else
(md, txt, no extension, …) = prose.

Usage:
  estimate-tokens.py --anchors prose=<r>,code=<r>,cjk=<r>[,correction=<f>] <file>...

Output: one line per file `<path> <bytes> <tok-eq>` + a final
`TOTAL <bytes> <tok-eq>` line.
Exit: 0 = computed; 2 = usage error (bad anchors, unreadable file).
"""
import argparse
import os
import sys

CODE_EXTS = {
    "py", "sh", "bash", "js", "ts", "jsx", "tsx", "json", "jsonl", "yaml",
    "yml", "toml", "c", "h", "cpp", "hpp", "cc", "rs", "go", "java", "rb",
    "pl", "swift", "kt", "sql",
}

CJK_RANGES = (
    (0x3000, 0x303F),   # CJK symbols & punctuation
    (0x3040, 0x30FF),   # hiragana + katakana
    (0x3400, 0x4DBF),   # CJK ext A
    (0x4E00, 0x9FFF),   # CJK unified ideographs
    (0xAC00, 0xD7AF),   # hangul syllables
    (0xF900, 0xFAFF),   # CJK compatibility ideographs
    (0xFF00, 0xFFEF),   # halfwidth/fullwidth forms
)


def is_cjk(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in CJK_RANGES)


def parse_anchors(spec):
    rates = {}
    for part in spec.split(","):
        k, _, v = part.partition("=")
        k, v = k.strip(), v.strip()
        if not k or not v:
            raise ValueError(f"malformed anchor entry: {part!r}")
        rates[k] = float(v)
    for req in ("prose", "code", "cjk"):
        if req not in rates:
            raise ValueError(f"anchor {req!r} missing from --anchors")
        if rates[req] <= 0:
            raise ValueError(f"anchor {req!r} must be positive")
    rates.setdefault("correction", 1.0)
    return rates


def classify(path):
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    return "code" if ext in CODE_EXTS else "prose"


def estimate(path, rates):
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", errors="replace")
    base_rate = rates[classify(path)]
    cjk_chars = sum(1 for ch in text if is_cjk(ch))
    base_chars = len(text) - cjk_chars
    tok = round(rates["correction"] * (base_chars / base_rate + cjk_chars / rates["cjk"]))
    return len(raw), tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchors", required=True,
                    help="prose=<r>,code=<r>,cjk=<r>[,correction=<f>] — chars per tok-eq per class")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    try:
        rates = parse_anchors(args.anchors)
    except ValueError as err:
        print(f"usage error: {err}", file=sys.stderr)
        return 2

    total_bytes = total_tok = 0
    for path in args.files:
        try:
            nbytes, tok = estimate(path, rates)
        except OSError as err:
            print(f"usage error: cannot read {path}: {err}", file=sys.stderr)
            return 2
        total_bytes += nbytes
        total_tok += tok
        print(f"{path} {nbytes} {tok}")
    print(f"TOTAL {total_bytes} {total_tok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
