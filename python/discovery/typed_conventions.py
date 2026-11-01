"""
python/discovery/typed_conventions.py - Conventions compared by meaning, not by wording (ADR-DISCOVERY-087).

The re-run of the openai/math time-travel benchmark with the full chain (OPENAI_MATH_CHAIN_RESULTS.md) found that
the seams step of ADR-083 compared conventions as normalized strings. Two texts that name the same convention in
different words were a MISMATCH, so the step flagged about a third of all citations wherever they were, and a real
mismatch could not be told from a rewording.

A convention value can now be typed. Besides its text, it may carry:

- `fields`: named atoms (a string, number or boolean). A field present on both sides is compared after
  normalization; a difference is a decided MISMATCH that names the field.
- `signs`: named sign or normalization quantities, each an arithmetic formula over integer parameters
  (`"(-1)**(k-1)"`, `"-1"`, `"2*pi"` is not allowed: only integers and the declared parameters). A quantity present
  on both sides is compared by exhaustive evaluation over the parameters' declared ranges (default 0..16 each, at
  most 20,000 points); a difference is a decided MISMATCH with the first counterexample.
- `params`: `{name: [low, high]}`, the integer ranges of the formulas' parameters.

Outcomes for one convention:

- MATCH: at least one typed item was compared and all agreed, or the two texts are equal after normalization.
- MISMATCH: a typed item differs. This is decided, with the item and the values (or the counterexample).
- UNCOMPARED: the two sides have nothing typed in common and their texts differ. A different wording is not
  evidence of a different convention, so this is a non-verdict: the citation check is INCOMPLETE, not FINDINGS.

Typed items present on one side only are listed as unspecified on the other. The biomedical kinds of ADR-086 keep
their canonical-value and unit-algebra comparison; this module covers every other tag.
"""

from __future__ import annotations

import ast
import itertools
import operator
import re
from typing import Any, Dict, List

MATCH, MISMATCH, UNCOMPARED = "MATCH", "MISMATCH", "UNCOMPARED"
DEFAULT_RANGE = (0, 16)
MAX_POINTS = 20_000
MAX_EXPONENT = 512
MAX_FORMULA_CHARS = 200
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow}


class ConventionError(ValueError):
    """A typed convention is malformed."""


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower().replace("_", " "))


def is_typed(value: Any) -> bool:
    return isinstance(value, dict)


def text_of(value: Any) -> str:
    return str(value.get("text", "")) if is_typed(value) else str(value)


def validate(value: Any) -> Any:
    """A convention value: a string, or an object with optional text, fields, signs and params."""
    if not is_typed(value):
        return str(value)
    unknown = set(value) - {"text", "fields", "signs", "params"}
    if unknown:
        raise ConventionError(f"Unknown keys in a typed convention: {sorted(unknown)}.")
    fields = value.get("fields") or {}
    signs = value.get("signs") or {}
    params = value.get("params") or {}
    if not all(isinstance(d, dict) for d in (fields, signs, params)):
        raise ConventionError("'fields', 'signs' and 'params' must be objects.")
    for k, v in fields.items():
        if not isinstance(v, (str, int, float, bool)):
            raise ConventionError(f"Field {k!r} must be a string, number or boolean.")
    for name, rng in params.items():
        if not (isinstance(rng, (list, tuple)) and len(rng) == 2 and all(isinstance(x, int) for x in rng)
                and rng[0] <= rng[1]):
            raise ConventionError(f"Parameter {name!r} needs an integer range [low, high].")
    for k, f in signs.items():
        if not isinstance(f, str) or len(f) > MAX_FORMULA_CHARS:
            raise ConventionError(f"Sign formula {k!r} must be a string of at most {MAX_FORMULA_CHARS} characters.")
        _parse(f)
    return {"text": str(value.get("text", "")), "fields": dict(fields), "signs": dict(signs),
            "params": {k: [int(a), int(b)] for k, (a, b) in params.items()}}


def _parse(formula: str) -> ast.AST:
    try:
        tree = ast.parse(formula.strip(), mode="eval")
    except SyntaxError as exc:
        raise ConventionError(f"Invalid sign formula {formula!r}: {exc.msg}") from exc
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and not isinstance(node.value, int):
            raise ConventionError(f"Only integer constants are allowed in {formula!r}.")
        if not isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.USub, ast.UAdd, ast.Constant, ast.Name,
                                 ast.Load, *_BIN)):
            raise ConventionError(f"Unsupported construct {type(node).__name__} in {formula!r}.")
    return tree.body


def _eval(node: ast.AST, env: Dict[str, int]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise ConventionError(f"Undeclared parameter {node.id!r}.")
        return env[node.id]
    if isinstance(node, ast.UnaryOp):
        v = _eval(node.operand, env)
        return -v if isinstance(node.op, ast.USub) else v
    left, right = _eval(node.left, env), _eval(node.right, env)
    if isinstance(node.op, ast.Pow):
        if abs(right) > MAX_EXPONENT:
            raise ConventionError(f"Exponent {right} is too large.")
        if right < 0 and left not in (1, -1):
            raise ConventionError("A negative exponent is allowed only on 1 or -1.")
        if right < 0:
            return left ** (-right)  # (+-1)^-n == (+-1)^n
    return _BIN[type(node.op)](left, right)


def compare_formulas(a: str, b: str, params: Dict[str, List[int]]) -> Dict[str, Any]:
    """Exhaustive comparison of two integer formulas over the parameters' ranges."""
    ta, tb = _parse(a), _parse(b)
    names = sorted({n.id for t in (ta, tb) for n in ast.walk(t) if isinstance(n, ast.Name)})
    ranges = [range(params.get(n, DEFAULT_RANGE)[0], params.get(n, DEFAULT_RANGE)[1] + 1) for n in names]
    total = 1
    for r in ranges:
        total *= len(r)
    if total > MAX_POINTS:
        return {"outcome": UNCOMPARED, "detail": f"{total} parameter points exceed the limit of {MAX_POINTS}"}
    for point in itertools.product(*ranges):
        env = dict(zip(names, point))
        try:
            va, vb = _eval(ta, env), _eval(tb, env)
        except (ZeroDivisionError, ConventionError) as exc:
            return {"outcome": UNCOMPARED, "detail": f"not evaluable at {env}: {exc}"}
        if va != vb:
            return {"outcome": MISMATCH, "counterexample": {"at": env, "cited": va, "citing": vb}}
    scope = ", ".join(f"{n} in {list(params.get(n, DEFAULT_RANGE))}" for n in names) or "no parameters"
    return {"outcome": MATCH, "scope": scope}


def compare(cited: Any, citing: Any) -> Dict[str, Any]:
    """MATCH, MISMATCH or UNCOMPARED for one convention, with the items compared."""
    a, b = validate(cited), validate(citing)
    items: List[Dict[str, Any]] = []
    unspecified: List[str] = []
    if is_typed(a) and is_typed(b):
        params = {**a["params"], **b["params"]}
        for k in sorted(set(a["fields"]) | set(b["fields"])):
            if k in a["fields"] and k in b["fields"]:
                same = _norm(a["fields"][k]) == _norm(b["fields"][k])
                items.append({"item": f"field {k}", "outcome": MATCH if same else MISMATCH,
                              "cited": a["fields"][k], "citing": b["fields"][k]})
            else:
                unspecified.append(f"field {k} ({'citing' if k in a['fields'] else 'cited'} side silent)")
        for k in sorted(set(a["signs"]) | set(b["signs"])):
            if k in a["signs"] and k in b["signs"]:
                res = compare_formulas(a["signs"][k], b["signs"][k], params)
                items.append({"item": f"sign {k}", "cited": a["signs"][k], "citing": b["signs"][k], **res})
            else:
                unspecified.append(f"sign {k} ({'citing' if k in a['signs'] else 'cited'} side silent)")
    decided = [i for i in items if i["outcome"] in (MATCH, MISMATCH)]
    if any(i["outcome"] == MISMATCH for i in items):
        outcome, by = MISMATCH, "typed items"
    elif decided:
        outcome, by = MATCH, "typed items"
    elif _norm(text_of(a)) and _norm(text_of(a)) == _norm(text_of(b)):
        outcome, by = MATCH, "normalized string"
    else:
        outcome, by = UNCOMPARED, "nothing typed in common; the texts differ"
    return {"outcome": outcome, "compared_by": by, "items": items, "unspecified": unspecified}


def describe(value: Any) -> str:
    """One line for reports: the text, then the typed items."""
    if not is_typed(value):
        return str(value)
    parts = [str(value.get("text", ""))] if value.get("text") else []
    parts += [f"{k}={v}" for k, v in sorted((value.get("fields") or {}).items())]
    parts += [f"{k}: {v}" for k, v in sorted((value.get("signs") or {}).items())]
    return "; ".join(parts)


def schema() -> Dict[str, Any]:
    return {
        "text": "the convention as the source states it (optional)",
        "fields": "{name: string | number | boolean}, compared after normalization",
        "signs": "{quantity: integer formula over the params}, compared exhaustively over their ranges",
        "params": "{name: [low, high]}, integer ranges (default [0, 16]); at most 20,000 points",
        "outcomes": [MATCH, MISMATCH, UNCOMPARED],
    }


__all__ = ["compare", "compare_formulas", "validate", "is_typed", "text_of", "describe", "schema", "ConventionError",
           "MATCH", "MISMATCH", "UNCOMPARED"]
