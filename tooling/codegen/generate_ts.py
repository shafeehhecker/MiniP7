#!/usr/bin/env python3
"""Generate TypeScript types from the canonical Pydantic schema (ADR-0003).

The domain model is defined exactly once, in ``packages/schema``. This script
introspects those Pydantic models and emits ``packages/client/src/models.ts``
so Python and TypeScript can never disagree about the model.

Usage
-----
    python tooling/codegen/generate_ts.py          # (re)generate the file
    python tooling/codegen/generate_ts.py --check  # exit 1 if the committed
                                                   # file is stale (CI drift gate)

Design notes
------------
- Pure Python, no Node toolchain (consistent with the zero-build approach).
- Deterministic output: same input always produces byte-identical output, so
  the CI drift check is a plain file comparison.
- Enums become TypeScript string enums; models become interfaces. Fields with
  defaults are optional (``?``) on the TypeScript side, mirroring what a JSON
  payload may omit.
"""
from __future__ import annotations

import argparse
import enum
import sys
import types
import typing
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "schema" / "src"))

from pydantic import BaseModel  # noqa: E402
from pydantic_core import PydanticUndefined  # noqa: E402

import schema  # noqa: E402

OUTPUT = REPO_ROOT / "packages" / "client" / "src" / "models.ts"

HEADER = """\
/* AUTO-GENERATED — DO NOT EDIT.
 *
 * Generated from packages/schema (the single source of truth, ADR-0003) by
 * tooling/codegen/generate_ts.py. Regenerate with:
 *
 *     python tooling/codegen/generate_ts.py
 *
 * CI regenerates and diffs this file; any drift fails the build.
 */
"""

PRIMITIVES = {
    str: "string",
    int: "number",
    float: "number",
    bool: "boolean",
}


def _ts_type(annotation: object) -> str:
    """Map a Python annotation to a TypeScript type expression."""
    if annotation in PRIMITIVES:
        return PRIMITIVES[annotation]  # type: ignore[index]
    if annotation is type(None):
        return "null"
    if isinstance(annotation, type):
        if issubclass(annotation, enum.Enum):
            return annotation.__name__
        if issubclass(annotation, BaseModel):
            return annotation.__name__

    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin in (list, typing.List):
        inner = _ts_type(args[0]) if args else "unknown"
        return f"{inner}[]"
    if origin in (dict, typing.Dict):
        k = _ts_type(args[0]) if args else "string"
        v = _ts_type(args[1]) if len(args) > 1 else "unknown"
        return f"Record<{k}, {v}>"
    if origin in (typing.Union, types.UnionType):
        return " | ".join(sorted({_ts_type(a) for a in args}, key=lambda s: s == "null"))
    raise TypeError(f"Cannot map annotation to TypeScript: {annotation!r}")


def _emit_enum(e: type[enum.Enum]) -> str:
    doc = (e.__doc__ or "").strip().splitlines()
    lines = []
    if doc:
        lines.append(f"/** {doc[0]} */")
    lines.append(f"export enum {e.__name__} {{")
    for member in e:
        lines.append(f'  {member.name} = "{member.value}",')
    lines.append("}")
    return "\n".join(lines)


def _emit_model(m: type[BaseModel]) -> str:
    doc = (m.__doc__ or "").strip().splitlines()
    lines = []
    if doc:
        lines.append(f"/** {doc[0]} */")
    lines.append(f"export interface {m.__name__} {{")
    for name, field in m.model_fields.items():
        required = field.default is PydanticUndefined and field.default_factory is None
        opt = "" if required else "?"
        ts = _ts_type(field.annotation)
        desc = field.description
        if desc:
            lines.append(f"  /** {desc} */")
        lines.append(f"  {name}{opt}: {ts};")
    lines.append("}")
    return "\n".join(lines)


def generate() -> str:
    """Build the full models.ts content from the schema package's public API."""
    enums: list[type[enum.Enum]] = []
    models: list[type[BaseModel]] = []
    for name in schema.__all__:
        obj = getattr(schema, name)
        if isinstance(obj, type) and issubclass(obj, enum.Enum):
            enums.append(obj)
        elif isinstance(obj, type) and issubclass(obj, BaseModel):
            models.append(obj)
        # Non-type exports (e.g. COMMON_CURRENCIES) are runtime values served
        # by the API (`GET /api/currencies`), not part of the type contract.

    blocks = [HEADER]
    blocks += [_emit_enum(e) for e in enums]
    blocks += [_emit_model(m) for m in models]
    return "\n\n".join(blocks) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail (exit 1) if the committed file is stale")
    args = parser.parse_args()

    content = generate()
    if args.check:
        current = OUTPUT.read_text() if OUTPUT.exists() else ""
        if current != content:
            sys.stderr.write(
                f"DRIFT: {OUTPUT.relative_to(REPO_ROOT)} is stale.\n"
                "The schema changed without regenerating the TypeScript types.\n"
                "Run: python tooling/codegen/generate_ts.py\n")
            return 1
        print("TypeScript types are in sync with the schema.")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content)
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
