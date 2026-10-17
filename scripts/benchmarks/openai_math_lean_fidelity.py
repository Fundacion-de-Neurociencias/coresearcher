"""Lean-based statement-fidelity auditor for openai/math (design: LEAN_FIDELITY_AUDITOR_PLAN.md).

Plan: docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md

Phases 0 and 1 are implemented so far:

    python scripts/benchmarks/openai_math_lean_fidelity.py env-check --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_fidelity.py controls  --math-root /path/to/openai-math

`env-check` (phase 0): for each of the 19 pilot pairs it checks that the statement extraction is sound on the
real challenge file (balanced, found exactly once, same theorem name) and that the challenge elaborates with
`lake env lean`. It writes docs/reference/benchmarks/lean_fidelity_env_check.json.

`controls` (phase 1, no model): for the target theorem of each challenge it tries to prove, with a fixed tactic
script, that the statement is equivalent to itself (must succeed), to each mutant (must fail) and to a set of
meaning-preserving rewrites (prover recall). Generated files go to private/lean_fidelity/ (git-ignored); the
results go to docs/reference/benchmarks/lean_fidelity_phase1_controls.json.

Both need Lean and the Mathlib cache (`lake exe cache get` in openai-math/lean), but not Comparator, so they
also run on Windows.
"""

import argparse
import importlib.util
import json
import platform
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATASET = ROOT / "docs" / "reference" / "benchmarks" / "openai_math_pilot_dataset.json"
ENV_CHECK_OUT = ROOT / "docs" / "reference" / "benchmarks" / "lean_fidelity_env_check.json"
CONTROLS_OUT = ROOT / "docs" / "reference" / "benchmarks" / "lean_fidelity_phase1_controls.json"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pilot = _load("openai_math_pilot")
oracle = _load("openai_math_lean_oracle")


def extraction_check(pair: dict, lean: str) -> dict:
    """Checks the statement extraction of one pilot pair against its real challenge file."""
    parsed = pilot.theorem_statement(lean)
    if not parsed:
        return {"ok": False, "reason": "no theorem found"}
    name, stmt, _, _ = parsed
    checks = {
        "same_theorem": name == pair["theorem"],
        "balanced": pilot._balanced(stmt),
        "found_once": lean.count(stmt) == 1,
    }
    return {"ok": all(checks.values()), **checks, "matches_frozen_statement": stmt == pair["statement"]}


def _run(cmd: list[str], cwd: Path, timeout: int) -> tuple[int | None, str, float]:
    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "", time.monotonic() - start
    except OSError as exc:
        return -1, str(exc), time.monotonic() - start
    return proc.returncode, proc.stdout + proc.stderr, time.monotonic() - start


def elaboration_errors(output: str) -> list[str]:
    """Lean error lines; `sorry` warnings are expected in a challenge file and are not errors."""
    return [line for line in output.splitlines() if ": error" in line]


def lean_version_line(output: str) -> str:
    """The `Lean (version ...)` line; Lake may print dependency warnings around it."""
    return next((line.strip() for line in output.splitlines() if line.startswith("Lean (version")), output.strip())


def env_check(math_root: Path, timeout: int) -> int:
    commit = oracle.check_commit(math_root)
    lean_root = oracle.lean_dir(math_root)
    pairs = json.loads(DATASET.read_text(encoding="utf-8"))["pairs"]
    _, version_output, _ = _run(["lake", "env", "lean", "--version"], lean_root, 600)
    lean_version = lean_version_line(version_output)

    rows = []
    for pair in pairs:
        path = math_root / pair["challenge"]
        row = {"family": pair["family"], "challenge": pair["challenge"]}
        if not path.exists():
            rows.append({**row, "extraction": {"ok": False, "reason": "challenge file not found"}})
            continue
        row["extraction"] = extraction_check(pair, path.read_text(encoding="utf-8"))
        rel = path.relative_to(lean_root).as_posix()
        code, output, seconds = _run(["lake", "env", "lean", rel], lean_root, timeout)
        errors = elaboration_errors(output)
        row["elaboration"] = {
            "ok": code == 0 and not errors,
            "exit_code": code,
            "timed_out": code is None,
            "seconds": round(seconds, 1),
            "errors": errors[:5],
        }
        rows.append(row)
        status = "ok" if row["elaboration"]["ok"] and row["extraction"]["ok"] else "PROBLEM"
        print(f"{pair['family']} {status} ({seconds:.0f} s)", flush=True)

    elaborated = sum(r.get("elaboration", {}).get("ok", False) for r in rows)
    extracted = sum(r["extraction"]["ok"] for r in rows)
    result = {
        "plan": "docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md (phase 0)",
        "openai_math_commit": commit,
        "lean_version": lean_version,
        "os": platform.platform(),
        "timeout_seconds": timeout,
        "summary": {"pairs": len(rows), "extraction_ok": extracted, "elaboration_ok": elaborated},
        "rows": rows,
    }
    ENV_CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"extraction ok {extracted}/{len(rows)}, elaboration ok {elaborated}/{len(rows)} -> {ENV_CHECK_OUT}")
    return 0 if extracted == elaborated == len(rows) else 1


# ---------------------------------------------------------------- phase 1: prover controls

HEARTBEATS = 400000
# Tuned on the equivalent rewrites only (plan, phase 1). Iff.rfl closes definitional rewrites; the simp only
# line normalizes ∧/∨ order and double negation on both sides; the rest needs a proof in each direction.
# Baseline without the simp only line, for the record: prover recall 37/44 (swap 2/6, double negation 16/19).
TACTIC = (
    "  first\n"
    "  | exact Iff.rfl\n"
    "  | (simp only [not_not, and_comm, and_left_comm, and_assoc, or_comm, or_left_comm, or_assoc]; done)\n"
    "  | (constructor <;> intro h <;> first | exact h | simpa using h | aesop | tauto)\n"
)
IDENT = r"[^\W\d][\w'₀-₉!?]*"
# Constructs that bind or have lower precedence than ∨, so a split at a depth-0 ∨, ∧ or → would be wrong.
_LOW = re.compile(r"[↔,∀∃λ∑∏⋃⋂∫⨆⨅∮$]|<\||\b(?:fun|if|then|else|match|let|have|show|by|do)\b")


def statement_prop(stmt: str) -> str:
    """The statement `theorem name binders : concl` as one proposition, `∀ binders, concl`."""
    m = re.match(r"\s*theorem\s+[^\s(:{\[]+", stmt)
    rest = stmt[m.end() :] if m else stmt
    colon = pilot._top_level_colon(rest)
    binders, concl = rest[:colon].strip(), rest[colon + 1 :].strip()
    return f"∀ {binders}, {concl}" if binders else concl


def _depth0(text: str, token: str) -> list[int]:
    """Positions of token at bracket depth 0."""
    out, depth = [], 0
    for i, ch in enumerate(text):
        if ch in "([{⟨⦃":
            depth += 1
        elif ch in ")]}⟩⦄":
            depth -= 1
        elif depth == 0 and text.startswith(token, i):
            out.append(i)
    return out


def _peel(prop: str) -> tuple[str, str]:
    """Splits leading quantifiers and one pair of enclosing parentheses off prop: (prefix, body)."""
    prefix, body = "", prop.strip()
    while True:
        if body[:1] in "∀∃" and not body.startswith("∃!"):
            binders = pilot._binder_list(body, 0)
            cut = 1 + len(binders) + 1
            if cut > len(body):
                return prefix, body
            prefix, body = prefix + body[:cut] + " ", body[cut:].strip()
        elif body.startswith("(") and body.endswith(")") and pilot._balanced(body[1:-1]):
            inner = body[1:-1]
            if _depth0(inner, ",") or _LOW.search(_strip_brackets(inner)):
                return prefix, body
            body = inner.strip()
        else:
            return prefix, body


def _strip_brackets(text: str) -> str:
    """text with every bracketed span removed, so a search sees only depth 0."""
    out, depth = [], 0
    for ch in text:
        if ch in "([{⟨⦃":
            depth += 1
        elif ch in ")]}⟩⦄":
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _split(body: str, token: str) -> list[str] | None:
    """body split at depth-0 token, when no lower-precedence construct is at depth 0."""
    flat = _strip_brackets(body)
    if _LOW.search(flat) or (token != "→" and "→" in flat):
        return None
    if token == "∧" and "∨" in flat:
        return None
    cuts = _depth0(body, token)
    if not cuts:
        return None
    parts, last = [], 0
    for c in cuts:
        parts.append(body[last:c].strip())
        last = c + len(token)
    parts.append(body[last:].strip())
    return parts if all(parts) else None


def _rename(prop: str) -> str | None:
    """Renames the bound variables of the first binder list (alpha-equivalent)."""
    if prop[:1] not in "∀∃":
        return None
    binders = pilot._binder_list(prop, 0)
    groups = re.findall(r"[(\{⦃]\s*([^:(){}⦃⦄\[\]]+?)\s*:", binders) or [re.split(r"[:,]", binders)[0]]
    names = [n for g in groups for n in g.split() if re.fullmatch(IDENT, n) and n != "_"]
    if not names:
        return None
    out = prop
    for n in names:
        out = re.sub(rf"(?<![\w'.₀-₉]){re.escape(n)}(?![\w'₀-₉!?])(?!\s*:=)", f"{n}_r", out)
    return out


def _flip_lt(prop: str) -> str | None:
    """`a < b` to `b > a` (and ≤ to ≥) at the first place where both sides are single atoms."""
    atom = r"-?[\w'₀-₉.]+"
    for m in re.finditer(rf"({atom})\s*([<≤])\s*({atom})", prop):
        before, after = prop[: m.start()].rstrip(), prop[m.end() :].lstrip()
        if (not before or before[-1] in "(,∧∨→↔¬:") and (not after or after[0] in ")∧∨→↔,"):
            flipped = {"<": ">", "≤": "≥"}[m.group(2)]
            return prop[: m.start()] + f"{m.group(3)} {flipped} {m.group(1)}" + prop[m.end() :]
    return None


def _swap(prop: str) -> str | None:
    """Swaps the two sides of the top-level ∨, or else ∧, under the leading quantifiers."""
    prefix, body = _peel(prop)
    for token in ("∨", "∧"):
        parts = _split(body, token)
        if parts:
            return f"{prefix}(({f' {token} '.join(parts[1:])}) {token} ({parts[0]}))"
    return None


def _curry(prop: str) -> str | None:
    """`A → B → C` to `A ∧ B → C` under the leading quantifiers."""
    prefix, body = _peel(prop)
    parts = _split(body, "→")
    if not parts or len(parts) < 3:
        return None
    return f"{prefix}((({parts[0]}) ∧ ({parts[1]})) → {' → '.join(parts[2:])})"


REWRITES = {
    "rename": _rename,
    "flip_lt": _flip_lt,
    "swap": _swap,
    "curry": _curry,
    "double_negation": lambda prop: f"¬¬({prop})",
}


def rewrites(prop: str) -> dict[str, str]:
    """Meaning-preserving rewrites of prop that apply to it."""
    out = {}
    for code, rule in REWRITES.items():
        new = rule(prop)
        if new and new != prop:
            out[code] = new
    return out


def _insertion_point(lean: str, start: int) -> int:
    """Start of the theorem's modifiers, attributes and docstring, so checks can go just before them."""
    line_start = lean.rfind("\n", 0, start) + 1
    i = line_start if re.fullmatch(r"[\w\s]*", lean[line_start:start]) else start
    while True:
        head = lean[:i].rstrip()
        last = head[head.rfind("\n") + 1 :]
        if head.endswith("-/") and "/--" in head:
            i = head.rindex("/--")
        elif last.lstrip().startswith("@["):
            i = head.rfind("\n") + 1
        else:
            return i


def check_block(check_id: str, left: str, right: str, line: int) -> tuple[str, dict]:
    """One `example` that tries to prove left ↔ right; returns the text and its line ranges."""
    header = f"-- fidelity check {check_id}\nset_option maxHeartbeats {HEARTBEATS} in\nexample :\n"
    # `:= by` gets a line of its own: Lean reports failed tactics at `by`, so that line belongs to the proof.
    stmt = f"    ({left}) ↔\n    ({right})\n"
    text = header + stmt + "    := by\n" + TACTIC + "\n"
    proof_line = line + header.count("\n") + stmt.count("\n")
    return text, {"id": check_id, "first_line": line, "proof_line": proof_line, "last_line": line + text.count("\n")}


def build_check_file(lean: str, start: int, checks: list[tuple[str, str, str]]) -> tuple[str, list[dict]]:
    """The challenge file with the checks inserted before the target theorem."""
    at = _insertion_point(lean, start)
    head = lean[:at]
    if not head.endswith("\n"):
        head += "\n"
    line = head.count("\n") + 1
    blocks, ranges = [], []
    for check_id, left, right in checks:
        text, rng = check_block(check_id, left, right, line)
        blocks.append(text)
        ranges.append(rng)
        line = rng["last_line"]
    return head + "".join(blocks) + lean[at:], ranges


OUTCOMES = ("proved", "not_shown", "invalid", "timeout", "setup_error")
SENTINEL = ("sentinel", "(2 : ℕ) + 2 = 4", "(2 : ℕ) + 2 = 5")


def classify(output: str, ranges: list[dict]) -> tuple[dict[str, dict], list[str]]:
    """Outcome per check: proved, not_shown (tactic failed or timed out) or invalid (did not elaborate).

    Also returns errors outside every check, which mean the context itself failed and no outcome can be trusted.
    """
    result = {r["id"]: {"outcome": "proved", "messages": []} for r in ranges}
    outside = []
    for m in re.finditer(r"^[^\n]*?:(\d+):\d+: error:?\s*(.*)$", output, re.M):
        line, message = int(m.group(1)), m.group(2).strip()
        owner = next((r for r in ranges if r["first_line"] <= line < r["last_line"]), None)
        if owner is None:
            outside.append(f"{line}: {message}"[:300])
            continue
        entry = result[owner["id"]]
        entry["messages"].append(f"{line}: {message}"[:300])
        timeout = "timeout" in message or "heartbeats" in message
        if line >= owner["proof_line"] or timeout:
            if entry["outcome"] == "proved":
                entry["outcome"] = "not_shown"
        else:
            entry["outcome"] = "invalid"
    return result, outside


def family_checks(pair: dict, lean: str, config: str | None) -> tuple[dict, list[tuple[str, str, str, str]]]:
    """Statement info and (id, kind, left, right) checks for one family; uses the challenge's target theorem."""
    parsed = pilot.theorem_statement(lean, pilot.challenge_target(config))
    if not parsed:
        return {"error": "target theorem not found"}, []
    name, stmt, start, _ = parsed
    prop = statement_prop(stmt)
    checks = [(f"F{pair['family']}_identity", "identity", prop, prop)]
    for code, mutant in sorted(pilot.mutate(stmt).items()):
        checks.append((f"F{pair['family']}_{code}", "mutant", prop, statement_prop(mutant)))
    for code, rewritten in rewrites(prop).items():
        checks.append((f"F{pair['family']}_{code}", "rewrite", prop, rewritten))
    # A false equivalence that must come out not_shown; otherwise the output was not read correctly.
    checks.append((f"F{pair['family']}_{SENTINEL[0]}", SENTINEL[0], SENTINEL[1], SENTINEL[2]))
    return {"theorem": name, "start": start}, checks


def trusted(outcomes: dict[str, dict], outside: list[str], sentinel_id: str) -> str | None:
    """None when a family's outcomes can be trusted, else the reason they cannot."""
    if outside:
        return "errors outside the checks: " + "; ".join(outside[:3])
    if outcomes.get(sentinel_id, {}).get("outcome") != "not_shown":
        return "the sentinel check did not fail as expected"
    return None


def controls(math_root: Path, out_dir: Path, timeout: int, jobs: int) -> int:
    commit = oracle.check_commit(math_root)
    lean_root = oracle.lean_dir(math_root)
    pairs = json.loads(DATASET.read_text(encoding="utf-8"))["pairs"]
    _, version_output, _ = _run(["lake", "env", "lean", "--version"], lean_root, 600)
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs_list = []
    for pair in pairs:
        path = math_root / pair["challenge"]
        lean = path.read_text(encoding="utf-8")
        config_path = path.with_suffix(".json")
        config = config_path.read_text(encoding="utf-8") if config_path.exists() else None
        info, checks = family_checks(pair, lean, config)
        if not checks:
            jobs_list.append((pair, info, [], None, []))
            continue
        text, ranges = build_check_file(lean, info["start"], [(c[0], c[2], c[3]) for c in checks])
        check_file = out_dir / f"F{pair['family']}.lean"
        check_file.write_text(text, encoding="utf-8")
        jobs_list.append((pair, info, checks, check_file, ranges))

    def run_one(job):
        pair, info, checks, check_file, ranges = job
        if not checks:
            return pair["family"], info, [], None, 0.0
        code, output, seconds = _run(["lake", "env", "lean", str(check_file)], lean_root, timeout)
        if code is None:
            outcomes = {r["id"]: {"outcome": "timeout", "messages": []} for r in ranges}
        else:
            outcomes, outside = classify(output, ranges)
            problem = trusted(outcomes, outside, f"F{pair['family']}_{SENTINEL[0]}")
            if problem:
                outcomes = {r["id"]: {"outcome": "setup_error", "messages": [problem]} for r in ranges}
        print(f"F{pair['family']}: {len(checks)} checks ({seconds:.0f} s)", flush=True)
        return pair["family"], info, checks, outcomes, seconds

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        finished = list(pool.map(run_one, jobs_list))

    rows = []
    for family, info, checks, outcomes, seconds in finished:
        for check_id, kind, left, right in checks:
            rows.append(
                {"family": family, "id": check_id, "kind": kind, "right": right, **outcomes[check_id]}
                | {"theorem": info.get("theorem")}
            )
        if not checks:
            rows.append({"family": family, "id": f"F{family}", "kind": "setup", "outcome": "invalid", **info})

    def tally(kind: str) -> dict:
        sub = [r for r in rows if r["kind"] == kind]
        counts = {o: sum(r["outcome"] == o for r in sub) for o in OUTCOMES}
        return {"n": len(sub), **counts}

    by_rule = {}
    for code in REWRITES:
        sub = [r for r in rows if r["kind"] == "rewrite" and r["id"].endswith("_" + code)]
        by_rule[code] = {o: sum(r["outcome"] == o for r in sub) for o in OUTCOMES}
    rewrite = tally("rewrite")
    # Invalid rewrites (the rule produced text that does not elaborate) and untrusted families are not prover
    # failures; timeouts are, since the budget is part of the prover.
    valid = rewrite["n"] - rewrite["invalid"] - rewrite["setup_error"]
    summary = {
        "families": len(finished),
        "families_untrusted": sorted({r["family"] for r in rows if r["outcome"] == "setup_error"}),
        "identity": tally("identity"),
        "mutant": tally("mutant"),
        "rewrite": rewrite,
        "rewrite_by_rule": by_rule,
        "sentinel": tally("sentinel"),
        "prover_recall": round(rewrite["proved"] / valid, 3) if valid else None,
    }
    summary["go"] = (
        not summary["families_untrusted"]
        and summary["identity"]["proved"] == summary["identity"]["n"]
        and summary["mutant"]["proved"] == 0
        and (summary["prover_recall"] or 0) >= 0.8
    )
    result = {
        "plan": "docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md (phase 1)",
        "openai_math_commit": commit,
        "lean_version": lean_version_line(version_output),
        "os": platform.platform(),
        "heartbeats": HEARTBEATS,
        "tactic": TACTIC,
        "summary": summary,
        "rows": rows,
    }
    CONTROLS_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["env-check", "controls"])
    parser.add_argument("--math-root", required=True, type=Path, help="Path to an openai/math checkout")
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds per Lean file")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "private" / "lean_fidelity", help="Generated files")
    parser.add_argument("--jobs", type=int, default=4, help="Lean processes in parallel (controls)")
    args = parser.parse_args()
    if args.step == "env-check":
        return env_check(args.math_root.resolve(), args.timeout)
    return controls(args.math_root.resolve(), args.out_dir.resolve(), args.timeout, args.jobs)


if __name__ == "__main__":
    sys.exit(main())
