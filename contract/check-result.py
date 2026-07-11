#!/usr/bin/env python3
"""Standalone task-result validator (spec AC-5). Python 3 stdlib ONLY.

Validates a result.json against the vendored schema file
(task-result.schema.json, loaded from this script's own directory):
required fields, field types, closed value sets, unknown fields.

Usage: python3 check-result.py <result.json>
Exit 0 + "VALID", or exit 1 + one "INVALID: <field>: <reason>" line per
problem ("<document>" is the pseudo-field for file-level problems).
"""
import json
import os
import sys

TYPES = {
    "string": str,
    "array": list,
    "object": dict,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def fail(lines):
    for line in lines:
        print(line)
    sys.exit(1)


def type_ok(value, names):
    for t in names:
        if t in ("integer", "number") and isinstance(value, bool):
            continue  # bool is an int subclass; a boolean is never a number
        if isinstance(value, TYPES[t]):
            return True
    return False


def main():
    if len(sys.argv) != 2:
        print("usage: check-result.py <result.json>")
        sys.exit(2)

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "task-result.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)

    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail([f"INVALID: <document>: JSON parse error: {e}"])
    except OSError as e:
        fail([f"INVALID: <document>: cannot read file: {e}"])

    if not isinstance(data, dict):
        fail([f"INVALID: <document>: top level must be an object, got {type(data).__name__}"])

    problems = []
    props = schema["properties"]
    required = set(schema.get("required", []))

    for name, spec in props.items():
        if name not in data:
            if name in required:
                problems.append(f"INVALID: {name}: required field missing")
            continue
        value = data[name]
        allowed = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
        if not type_ok(value, allowed):
            problems.append(
                f"INVALID: {name}: expected type {'|'.join(allowed)}, got {type(value).__name__}"
            )
            continue
        if "enum" in spec and value not in spec["enum"]:
            problems.append(f"INVALID: {name}: value {value!r} not in {spec['enum']}")
        if "items" in spec and isinstance(value, list):
            raw = spec["items"]["type"]
            item_types = raw if isinstance(raw, list) else [raw]
            for i, item in enumerate(value):
                if not type_ok(item, item_types):
                    problems.append(
                        f"INVALID: {name}[{i}]: expected item type {'|'.join(item_types)}, got {type(item).__name__}"
                    )
                    continue
                if isinstance(item, dict) and "properties" in spec["items"]:
                    ispec = spec["items"]
                    for req in ispec.get("required", []):
                        if req not in item:
                            problems.append(f"INVALID: {name}[{i}].{req}: required field missing")
                    for k, v in item.items():
                        if k not in ispec["properties"]:
                            if ispec.get("additionalProperties") is False:
                                problems.append(f"INVALID: {name}[{i}].{k}: unknown field")
                            continue
                        kspec = ispec["properties"][k]
                        kallowed = kspec["type"] if isinstance(kspec["type"], list) else [kspec["type"]]
                        if not type_ok(v, kallowed):
                            problems.append(
                                f"INVALID: {name}[{i}].{k}: expected type {'|'.join(kallowed)}, got {type(v).__name__}"
                            )
                            continue
                        if "enum" in kspec and v not in kspec["enum"]:
                            problems.append(f"INVALID: {name}[{i}].{k}: value {v!r} not in {kspec['enum']}")

    for name in data:
        if name not in props:
            problems.append(f"INVALID: {name}: unknown field (schema v1.1 field set is closed)")

    if problems:
        fail(problems)
    print("VALID")
    sys.exit(0)


if __name__ == "__main__":
    main()
