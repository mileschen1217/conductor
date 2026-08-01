#!/usr/bin/env python3
"""Validate a journal (JSONL) against contract/journal-event.schema.json.

Stdlib only, like every other checker in this layer — `jsonschema` is not a
dependency this repo takes.

The point of this file is what it does NOT contain: the event vocabulary. It is
a generic validator for the JSON Schema subset the journal schema uses, and it
READS that schema at run time. Hand-writing the vocabulary here in Python would
rebuild the exact drift surface the schema was created to remove — truth in two
places, prose and code, free to diverge.

Supported keywords: $ref (into #/definitions), type, enum, const, required,
properties, additionalProperties (boolean), dependencies, oneOf, pattern,
minimum, minLength, items. Anything else in the schema is ignored rather than silently treated as
satisfied — see `unsupported_keywords()`, which reports them, so a schema that
grows a keyword this validator cannot enforce is visible instead of quietly
under-checked.

Usage:
  check-journal-event.py <journal.jsonl> [<journal.jsonl> ...]
  check-journal-event.py --schema-audit        # list unenforced schema keywords
Exit: 0 = every line valid; 1 = at least one line invalid; 2 = usage/environment.
"""
import json
import re
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("journal-event.schema.json")

SUPPORTED = {
    "$ref", "type", "enum", "const", "required", "properties",
    "additionalProperties", "oneOf", "pattern", "minimum", "minLength", "items",
    "dependencies",
    # metadata, deliberately inert
    "$schema", "title", "description", "x_notes", "definitions",
}

TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "null": type(None),
}


def _is_type(value, name):
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "boolean":
        return isinstance(value, bool)
    py = TYPES.get(name)
    if py is None:
        return True                      # unknown type name: not enforced
    if py is dict or py is list or py is str:
        return isinstance(value, py)
    return isinstance(value, py)


def resolve(schema, root):
    seen = 0
    while "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise ValueError(f"unsupported $ref target: {ref}")
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        schema = node
        seen += 1
        if seen > 10:
            raise ValueError("$ref cycle")
    return schema


def validate(value, schema, root, path="$"):
    """Return a list of human-readable violation strings."""
    schema = resolve(schema, root)
    errs = []

    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, n) for n in names):
            return [f"{path}: expected type {'|'.join(names)}, got {type(value).__name__}"]

    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} not in enum {schema['enum']}")

    if "pattern" in schema and isinstance(value, str):
        if not re.search(schema["pattern"], value):
            errs.append(f"{path}: {value!r} does not match /{schema['pattern']}/")

    if "minLength" in schema and isinstance(value, str) and len(value) < schema["minLength"]:
        errs.append(f"{path}: shorter than minLength {schema['minLength']}")

    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema["minimum"]:
            errs.append(f"{path}: {value} below minimum {schema['minimum']}")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errs.append(f"{path}: missing required field {key!r}")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in value:
                errs.extend(validate(value[key], sub, root, f"{path}.{key}"))
        for trigger, needed in (schema.get("dependencies") or {}).items():
            if trigger in value:
                for k in needed:
                    if k not in value:
                        errs.append(f"{path}: {trigger!r} present, so {k!r} is required")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errs.append(f"{path}: additional property {key!r} not allowed")

    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errs.extend(validate(item, schema["items"], root, f"{path}[{i}]"))

    if "oneOf" in schema:
        matches = [b for b in schema["oneOf"] if not validate(value, b, root, path)]
        if len(matches) != 1:
            # Report the branch that got furthest, not a wall of every branch's
            # complaints: with a `const` discriminator exactly one branch is the
            # intended one, and its errors are the useful ones.
            if not matches:
                best, best_errs = None, None
                for b in schema["oneOf"]:
                    b_errs = validate(value, b, root, path)
                    disc = resolve(b, root).get("properties", {}).get("event", {})
                    if isinstance(value, dict) and disc.get("const") == value.get("event"):
                        best, best_errs = b, b_errs
                        break
                    if best_errs is None or len(b_errs) < len(best_errs):
                        best, best_errs = b, b_errs
                errs.extend(best_errs or [f"{path}: matched no oneOf branch"])
            else:
                titles = [resolve(b, root).get("title", "?") for b in matches]
                errs.append(f"{path}: matched {len(matches)} oneOf branches ({', '.join(titles)}); exactly one is required")

    return errs


def unsupported_keywords(node, out, where="#"):
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("x_"):
                continue          # annotation block: prose, never a constraint
            if k == "dependencies":
                # property-dependency form: values are arrays of field names, so
                # its KEYS are fields and recursing would report them as unknown
                # keywords. The schema-dependency form (a subschema as the value)
                # is NOT enforced by validate(), so it must still be reported.
                for dep_name, dep_val in (v or {}).items():
                    if not (isinstance(dep_val, list)
                            and all(isinstance(x, str) for x in dep_val)):
                        out.add(f"{where}/dependencies/{dep_name}: schema-dependency form")
                continue
            if k in ("properties", "definitions"):
                for name, sub in (v or {}).items():
                    unsupported_keywords(sub, out, f"{where}/{k}/{name}")
                continue
            if k not in SUPPORTED:
                out.add(f"{where}: {k}")
            if isinstance(v, (dict, list)):
                unsupported_keywords(v, out, f"{where}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            unsupported_keywords(v, out, f"{where}[{i}]")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    try:
        root = json.loads(SCHEMA_PATH.read_text())
    except Exception as exc:                                  # noqa: BLE001
        print(f"ERROR: cannot read {SCHEMA_PATH}: {exc}", file=sys.stderr)
        return 2

    if argv[0] == "--schema-audit":
        out = set()
        unsupported_keywords(root, out)
        if out:
            print("UNENFORCED schema keywords (present in the schema, not checked here):")
            for line in sorted(out):
                print(f"  {line}")
            return 1
        print("CLEAN: every keyword the schema uses is enforced by this validator")
        return 0

    bad = 0
    for arg in argv:
        p = Path(arg)
        if not p.is_file():
            print(f"ERROR: not a file: {p}", file=sys.stderr)
            return 2
        for n, raw in enumerate(p.read_text().splitlines(), 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                print(f"INVALID {p}:{n}: not JSON ({exc.msg})")
                bad += 1
                continue
            errs = validate(event, root, root, f"{p.name}:{n}")
            for e in errs:
                print(f"INVALID {e}")
            bad += 1 if errs else 0
    if bad:
        print(f"INVALID: {bad} line(s) failed")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
