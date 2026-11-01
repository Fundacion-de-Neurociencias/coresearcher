"""
python/discovery/typed_conventions.py - Conventions compared by meaning, not by wording (ADR-DISCOVERY-087, ADR-088).

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
- `where` (ADR-088): conditions on the parameters, e.g. `["n % 2 == 0", "k >= 2"]`. A sign quantity is compared only
  on the points that satisfy both sides' conditions, inside both sides' ranges. An empty shared domain is UNCOMPARED.
- `cases` and `case` (ADR-088): which case of a result is used is not a convention. The cited side lists the cases
  its statement covers (`{"homotopy_direction": ["forward", "reverse"]}`); the citing side names the case it uses
  (`{"homotopy_direction": "reverse"}`). A case the cited result does not cover is a decided MISMATCH; a covered one
  is a MATCH.

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
from typing import Any, Dict, List, Sequence

MATCH, MISMATCH, UNCOMPARED = "MATCH", "MISMATCH", "UNCOMPARED"
DEFAULT_RANGE = (0, 16)
MAX_POINTS = 20_000
MAX_EXPONENT = 512
MAX_FORMULA_CHARS = 200
_CMP = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt,
        ast.GtE: operator.ge}
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
    unknown = set(value) - {"text", "fields", "signs", "params", "where", "cases", "case"}
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
    where = value.get("where") or []
    if isinstance(where, str):
        where = [where]
    if not isinstance(where, list) or not all(isinstance(w, str) and len(w) <= MAX_FORMULA_CHARS for w in where):
        raise ConventionError(f"'where' must be a list of conditions of at most {MAX_FORMULA_CHARS} characters.")
    for w in where:
        _parse(w, condition=True)
    cases = value.get("cases") or {}
    case = value.get("case") or {}
    if not (isinstance(cases, dict) and all(isinstance(v, list) and v and all(isinstance(x, (str, int, bool))
                                                                             for x in v) for v in cases.values())):
        raise ConventionError("'cases' must be {name: [covered case, ...]}.")
    if not (isinstance(case, dict) and all(isinstance(v, (str, int, bool)) for v in case.values())):
        raise ConventionError("'case' must be {name: the case used}.")
    return {"text": str(value.get("text", "")), "fields": dict(fields), "signs": dict(signs),
            "params": {k: [int(a), int(b)] for k, (a, b) in params.items()}, "where": list(where),
            "cases": {k: list(v) for k, v in cases.items()}, "case": dict(case)}


def _parse(formula: str, condition: bool = False) -> ast.AST:
    kind = "condition" if condition else "sign formula"
    try:
        tree = ast.parse(formula.strip(), mode="eval")
    except SyntaxError as exc:
        raise ConventionError(f"Invalid {kind} {formula!r}: {exc.msg}") from exc
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.USub, ast.UAdd, ast.Constant, ast.Name, ast.Load, *_BIN)
    if condition:
        allowed += (ast.Compare, ast.BoolOp, ast.And, ast.Or, ast.Not, *_CMP)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and (isinstance(node.value, bool) or not isinstance(node.value, int)):
            raise ConventionError(f"Only integer constants are allowed in {formula!r}.")
        if not isinstance(node, allowed):
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
        if isinstance(node.op, ast.Not):
            return not v
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BoolOp):
        values = (_eval(v, env) for v in node.values)
        return all(values) if isinstance(node.op, ast.And) else any(values)
    if isinstance(node, ast.Compare):
        left = _eval(node.left, env)
        for op, comp in zip(node.ops, node.comparators):
            right = _eval(comp, env)
            if not _CMP[type(op)](left, right):
                return False
            left = right
        return True
    left, right = _eval(node.left, env), _eval(node.right, env)
    if isinstance(node.op, ast.Pow):
        if abs(right) > MAX_EXPONENT:
            raise ConventionError(f"Exponent {right} is too large.")
        if right < 0 and left not in (1, -1):
            raise ConventionError("A negative exponent is allowed only on 1 or -1.")
        if right < 0:
            return left ** (-right)  # (+-1)^-n == (+-1)^n
    return _BIN[type(node.op)](left, right)


def compare_formulas(a: str, b: str, params: Dict[str, List[int]], where: Sequence[str] = ()) -> Dict[str, Any]:
    """Exhaustive comparison of two integer formulas over the parameters' ranges, restricted to the points that
    satisfy every condition in `where` (ADR-088)."""
    ta, tb = _parse(a), _parse(b)
    conditions = [_parse(w, condition=True) for w in where]
    names = sorted({n.id for t in [ta, tb, *conditions] for n in ast.walk(t) if isinstance(n, ast.Name)})
    ranges = [range(params.get(n, DEFAULT_RANGE)[0], params.get(n, DEFAULT_RANGE)[1] + 1) for n in names]
    total = 1
    for r in ranges:
        total *= len(r)
    if total > MAX_POINTS:
        return {"outcome": UNCOMPARED, "detail": f"{total} parameter points exceed the limit of {MAX_POINTS}"}
    compared = 0
    for point in itertools.product(*ranges):
        env = dict(zip(names, point))
        try:
            if not all(_eval(c, env) for c in conditions):
                continue
            va, vb = _eval(ta, env), _eval(tb, env)
        except (ZeroDivisionError, ConventionError) as exc:
            return {"outcome": UNCOMPARED, "detail": f"not evaluable at {env}: {exc}"}
        compared += 1
        if va != vb:
            return {"outcome": MISMATCH, "counterexample": {"at": env, "cited": va, "citing": vb}}
    if not compared:
        return {"outcome": UNCOMPARED, "detail": "no parameter point satisfies both sides' ranges and conditions"}
    scope = ", ".join(f"{n} in {list(params.get(n, DEFAULT_RANGE))}" for n in names) or "no parameters"
    if where:
        scope += "; where " + " and ".join(where)
    return {"outcome": MATCH, "scope": scope, "points": compared}


def _shared_ranges(a: Dict[str, List[int]], b: Dict[str, List[int]]) -> Dict[str, List[int]]:
    """Both sides' ranges hold at once: the intersection where both declare a parameter."""
    out = {**a, **b}
    for k in set(a) & set(b):
        out[k] = [max(a[k][0], b[k][0]), min(a[k][1], b[k][1])]
    return out


def compare(cited: Any, citing: Any) -> Dict[str, Any]:
    """MATCH, MISMATCH or UNCOMPARED for one convention, with the items compared."""
    a, b = validate(cited), validate(citing)
    items: List[Dict[str, Any]] = []
    unspecified: List[str] = []
    if is_typed(a) and is_typed(b):
        params = _shared_ranges(a["params"], b["params"])
        where = a["where"] + b["where"]
        for k in sorted(set(a["fields"]) | set(b["fields"])):
            if k in a["fields"] and k in b["fields"]:
                same = _norm(a["fields"][k]) == _norm(b["fields"][k])
                items.append({"item": f"field {k}", "outcome": MATCH if same else MISMATCH,
                              "cited": a["fields"][k], "citing": b["fields"][k]})
            else:
                unspecified.append(f"field {k} ({'citing' if k in a['fields'] else 'cited'} side silent)")
        for k in sorted(set(a["signs"]) | set(b["signs"])):
            if k in a["signs"] and k in b["signs"]:
                res = compare_formulas(a["signs"][k], b["signs"][k], params, where)
                items.append({"item": f"sign {k}", "cited": a["signs"][k], "citing": b["signs"][k], **res})
            else:
                unspecified.append(f"sign {k} ({'citing' if k in a['signs'] else 'cited'} side silent)")
        for k in sorted(b["case"]):
            if k in a["cases"]:
                covered = _norm(b["case"][k]) in {_norm(x) for x in a["cases"][k]}
                item = {"item": f"case {k}", "outcome": MATCH if covered else MISMATCH, "cited": a["cases"][k],
                        "citing": b["case"][k]}
                if not covered:
                    item["detail"] = "the cited result does not cover this case"
                items.append(item)
            else:
                unspecified.append(f"case {k} (cited side lists no cases)")
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
    parts += [f"where {w}" for w in value.get("where") or []]
    parts += [f"case {k}={v}" for k, v in sorted((value.get("case") or {}).items())]
    parts += [f"cases {k} in {v}" for k, v in sorted((value.get("cases") or {}).items())]
    return "; ".join(parts)


def schema() -> Dict[str, Any]:
    return {
        "text": "the convention as the source states it (optional)",
        "fields": "{name: string | number | boolean}, compared after normalization",
        "signs": "{quantity: integer formula over the params}, compared exhaustively over their ranges",
        "params": "{name: [low, high]}, integer ranges (default [0, 16]); at most 20,000 points",
        "where": "[condition, ...] on the params; signs are compared where both sides' conditions hold",
        "cases": "cited side: {name: [cases the result covers]}",
        "case": "citing side: {name: the case used}; a case not covered is a MISMATCH",
        "outcomes": [MATCH, MISMATCH, UNCOMPARED],
    }


__all__ = ["compare", "compare_formulas", "validate", "is_typed", "text_of", "describe", "schema", "ConventionError",
           "MATCH", "MISMATCH", "UNCOMPARED"]
