"""Lean-based statement-fidelity auditor for openai/math (design: LEAN_FIDELITY_AUDITOR_PLAN.md).

Plan: docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md

Phases 0 and 1, and the preparation of phase 2, are implemented so far:

    python scripts/benchmarks/openai_math_lean_fidelity.py env-check    --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_fidelity.py controls     --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_fidelity.py screen-sheet --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_fidelity.py screen-score
    python scripts/benchmarks/openai_math_lean_fidelity.py formalize    --math-root /path/to/openai-math --dry-run
    python scripts/benchmarks/openai_math_lean_fidelity.py formalize    --math-root /path/to/openai-math
        --model <tag> --base-url <OpenAI-compatible endpoint> [--resume]

`env-check` (phase 0): for each of the 19 pilot pairs it checks that the statement extraction is sound on the
real challenge file (balanced, found exactly once, same theorem name) and that the challenge elaborates with
`lake env lean`. It writes docs/reference/benchmarks/lean_fidelity_env_check.json.

`controls` (phase 1, no model): for the target theorem of each challenge it tries to prove, with a fixed tactic
script, that the statement is equivalent to itself (must succeed), to each mutant (must fail) and to a set of
meaning-preserving rewrites (prover recall). Generated files go to private/lean_fidelity/ (git-ignored); the
results go to docs/reference/benchmarks/lean_fidelity_phase1_controls.json.

`screen-sheet` writes one Markdown sheet per reader to docs/reference/benchmarks/lean_fidelity_screen/; each
reader ticks whether the prose determines the statement. `screen-score` combines the sheets (agreement, Cohen's
kappa, the families both readers marked determined). `formalize` asks a model for a Lean statement from the prose
and the challenge file without its target theorem, and stores the raw replies as JSONL; `--dry-run` only writes
the prompts. No Lean is needed for these three.

env-check and controls need Lean and the Mathlib cache (`lake exe cache get` in openai-math/lean), but not
Comparator, so they also run on Windows.
"""

import argparse
import hashlib
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
sys.path.insert(0, str(ROOT))
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
    # `lake env lean` does not apply the project's `autoImplicit false`; without it an unknown name in a candidate
    # would become a bound variable, and the statement would elaborate with a different meaning.
    header = (
        f"-- fidelity check {check_id}\nset_option autoImplicit false in\n"
        f"set_option maxHeartbeats {HEARTBEATS} in\nexample :\n"
    )
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


def run_check_file(family: str, check_file: Path, ranges: list[dict], lean_root: Path, timeout: int):
    """Runs one generated file through Lean; returns (outcome per check id, seconds)."""
    code, output, seconds = _run(["lake", "env", "lean", str(check_file)], lean_root, timeout)
    if code is None:
        outcomes = {r["id"]: {"outcome": "timeout", "messages": []} for r in ranges}
    else:
        outcomes, outside = classify(output, ranges)
        problem = trusted(outcomes, outside, f"F{family}_{SENTINEL[0]}")
        if problem:
            outcomes = {r["id"]: {"outcome": "setup_error", "messages": [problem]} for r in ranges}
    print(f"F{family}: {len(ranges)} checks ({seconds:.0f} s)", flush=True)
    return outcomes, seconds


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
        outcomes, seconds = run_check_file(pair["family"], check_file, ranges, lean_root, timeout)
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


# ---------------------------------------------------------------- phase 2: shared inputs


def load_targets(math_root: Path) -> list[dict]:
    """For each pilot pair: prose, challenge file, Comparator config and the target theorem's statement."""
    targets = []
    for pair in json.loads(DATASET.read_text(encoding="utf-8"))["pairs"]:
        path = math_root / pair["challenge"]
        lean = path.read_text(encoding="utf-8")
        config_path = path.with_suffix(".json")
        config = config_path.read_text(encoding="utf-8") if config_path.exists() else None
        parsed = pilot.theorem_statement(lean, pilot.challenge_target(config))
        if not parsed:
            raise SystemExit(f"F{pair['family']}: target theorem not found in {pair['challenge']}")
        name, stmt, start, end = parsed
        targets.append(
            {
                "family": pair["family"],
                "title": pair["title"],
                "scope": pair["scope"],
                "challenge": pair["challenge"],
                "theorem": name,
                "statement": stmt.strip(),
                "lean": lean,
                "start": start,
                "end": end,
            }
        )
    return targets


# ---------------------------------------------------------------- phase 2: prose screen

SCREEN_DIR = ROOT / "docs" / "reference" / "benchmarks" / "lean_fidelity_screen"
READERS = ("A", "B")
VERDICTS = ("determined", "underdetermined")
# Shown above the definition of a wrapper statement; parse_sheet reads it back to mark the family.
WRAPPER_NOTE = "The statement is a named proposition defined in the challenge file. Judge its definition:"
SCREEN_RULES = """\
For each family, read the prose and the formal statement, then tick exactly one box.

- **determined**: a competent mathematician who reads only the prose, and is told the theorem's name and given
  the definitions in the challenge file, would write a statement with the same mathematical content: the same
  objects, quantifiers, hypotheses, constants and bounds, up to notation. If the prose describes several
  results, it is determined when one of them is this statement and the name is enough to pick it.
- **underdetermined**: the statement contains something the prose does not fix. Examples: it is a lemma the
  prose does not state, it has a constant, bound or hypothesis the prose does not give, or it combines results
  of which the prose mentions only some.

When unsure, choose underdetermined. Decide alone: do not discuss with the other reader and do not look at any
model output. Add a short note when the choice is not obvious."""


def wrapper_definition(target: dict) -> str | None:
    """The definition when the conclusion is one Prop-valued constant of the challenge file applied to variables.

    Such a statement carries its content in that definition, which stays in the formalizer's context, so a
    model can restate the name without formalizing anything.
    """
    stmt = target["statement"]
    concl = stmt[pilot._top_level_colon(stmt) + 1 :].strip()
    m = re.fullmatch(r"([\w.']+)(?:\s+[\w.']+)*", concl)
    if not m:
        return None
    short = re.escape(m.group(1).rsplit(".", 1)[-1])
    lean = target["lean"]
    d = re.search(rf"^(?:noncomputable\s+)?(?:def|abbrev)\s+(?:[\w.]+\.)?{short}\b[^\n]*", lean, re.M)
    if not d:
        return None
    text = lean[d.start() : declaration_end(lean, d.end())].strip()
    return text if re.search(r":\s*Prop\b", text[: text.find(":=") if ":=" in text else len(text)]) else None


def screen_sheet(targets: list[dict], reader: str, commit: str) -> str:
    """The Markdown sheet one reader fills in."""
    lines = [
        f"# Prose screen for the Lean fidelity auditor: reader {reader}",
        "",
        "Plan: [LEAN_FIDELITY_AUDITOR_PLAN.md](../LEAN_FIDELITY_AUDITOR_PLAN.md), phase 2. Reader name: ",
        "",
        f"Source: [openai/math](https://github.com/openai/math) at commit `{commit[:12]}`, Apache-2.0.",
        "",
        "## Rules",
        "",
        SCREEN_RULES,
        "",
    ]
    for t in targets:
        url = f"https://github.com/openai/math/blob/{commit}/{t['challenge']}"
        lines += [
            f"## F{t['family']}: {t['title']}",
            "",
            f"Challenge file: [{t['challenge']}]({url}). Theorem: `{t['theorem']}`.",
            "",
            "**Prose**",
            "",
            *[f"> {line}" if line else ">" for line in t["scope"].splitlines()],
            "",
            "**Formal statement**",
            "",
            "```lean",
            t["statement"],
            "```",
            "",
        ]
        wrapper = wrapper_definition(t)
        if wrapper:
            lines += [
                WRAPPER_NOTE,
                "",
                "```lean",
                wrapper,
                "```",
                "",
            ]
        lines += [
            *[f"- [ ] {v}" for v in VERDICTS],
            "",
            "Note: ",
            "",
        ]
    return "\n".join(lines)


def parse_sheet(text: str) -> dict[str, dict]:
    """Verdict and note per family from a filled sheet; verdict None when not exactly one box is ticked."""
    out = {}
    for m in re.finditer(r"^## F(\d+):.*?(?=^## F\d+:|\Z)", text, re.M | re.S):
        section = m.group(0)
        ticked = [v for v in VERDICTS if re.search(rf"^- \[[xX]\] {v}\s*$", section, re.M)]
        note = re.search(r"^Note:[ \t]*(.*)$", section, re.M)
        out[m.group(1)] = {
            "verdict": ticked[0] if len(ticked) == 1 else None,
            "note": note.group(1).strip() if note else "",
            "wrapper": WRAPPER_NOTE in section,
        }
    return out


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    observed = sum(x == y for x, y in zip(a, b)) / n
    expected = sum((a.count(v) / n) * (b.count(v) / n) for v in VERDICTS)
    return None if expected == 1 else round((observed - expected) / (1 - expected), 3)


def screen_score(sheets: dict[str, str]) -> dict:
    """Combines the readers' sheets. A family is scored only when every reader marked it determined.

    Wrapper families (the statement is one named proposition of the challenge file) are kept out of the headline
    set and listed separately: their definition stays in the formalizer's context, so a match can be a restated
    name rather than a formalization.
    """
    parsed = {reader: parse_sheet(text) for reader, text in sheets.items()}
    families = sorted(set().union(*(p.keys() for p in parsed.values())))
    missing = [f"{r}:F{f}" for r, p in parsed.items() for f in families if not p.get(f, {}).get("verdict")]
    if missing:
        return {"complete": False, "missing": missing}
    wrappers = {f for f in families if any(parsed[r][f]["wrapper"] for r in parsed)}
    rows = [{"family": f, "wrapper": f in wrappers, **{r: parsed[r][f] for r in parsed}} for f in families]
    verdicts = {r: [parsed[r][f]["verdict"] for f in families] for r in parsed}
    a, b = (verdicts[r] for r in READERS)
    determined = [f for f, x, y in zip(families, a, b) if x == y == "determined"]
    return {
        "complete": True,
        "rule": "scored only when both readers marked the family determined",
        "agreement": round(sum(x == y for x, y in zip(a, b)) / len(families), 3),
        "cohen_kappa": cohen_kappa(a, b),
        "determined": determined,
        "headline": [f for f in determined if f not in wrappers],
        "wrappers_reported_separately": [f for f in determined if f in wrappers],
        "rows": rows,
    }


# Numbers that are structural in most statements (bounds such as 0 < ε or 1 ≤ k), not content the prose must give.
STRUCTURAL_NUMBERS = {"0", "1", "2"}


def auto_screen_row(target: dict) -> dict:
    """Mechanical, reproducible screen of one family: wrapper or not, and its numeric anchoring.

    A family is numerically anchored when every number in its statement (or in its wrapper definition), other
    than 0, 1 and 2, also occurs in the prose. It replaces no judgment about meaning; it only marks families
    whose constants the prose cannot have supplied.
    """
    wrapper = wrapper_definition(target)
    text = target["statement"] + ("\n" + wrapper if wrapper else "")
    prose_numbers = set(pilot.NUM.findall(target["scope"]))
    missing = sorted({n for n in pilot.NUM.findall(text) if n not in prose_numbers and n not in STRUCTURAL_NUMBERS})
    return {"family": target["family"], "wrapper": wrapper is not None, "anchored": not missing, "missing": missing}


def auto_screen(targets: list[dict]) -> dict:
    rows = [auto_screen_row(t) for t in targets]
    headline = [r["family"] for r in rows if not r["wrapper"]]
    return {
        "rule": "headline = every family that is not a wrapper; anchored is a secondary stratum",
        "structural_numbers": sorted(STRUCTURAL_NUMBERS),
        "headline": headline,
        "headline_anchored": [r["family"] for r in rows if not r["wrapper"] and r["anchored"]],
        "wrappers_reported_separately": [r["family"] for r in rows if r["wrapper"]],
        "rows": rows,
    }


def cmd_screen_auto(math_root: Path) -> int:
    result = {"openai_math_commit": oracle.check_commit(math_root), **auto_screen(load_targets(math_root))}
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREEN_DIR / "auto_screen.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))
    print(f"Wrote {path}")
    return 0


def cmd_screen_sheet(math_root: Path, force: bool) -> int:
    commit = oracle.check_commit(math_root)
    targets = load_targets(math_root)
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    for reader in READERS:
        path = SCREEN_DIR / f"reader_{reader}.md"
        if path.exists() and not force and any(v["verdict"] for v in parse_sheet(path.read_text("utf-8")).values()):
            print(f"{path} already has verdicts; not overwritten (use --force).")
            continue
        path.write_text(screen_sheet(targets, reader, commit), encoding="utf-8")
        print(f"Wrote {path}")
    return 0


def cmd_screen_score() -> int:
    sheets = {r: (SCREEN_DIR / f"reader_{r}.md").read_text(encoding="utf-8") for r in READERS}
    result = screen_score(sheets)
    (SCREEN_DIR / "screen_result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))
    return 0 if result["complete"] else 1


# ---------------------------------------------------------------- phase 2: formalize

PROMPT_VERSION = "fidelity-formalize-v1"
MARKER = "-- [statement to formalize]"
SYSTEM_PROMPT = (
    "You are an expert in Lean 4 and Mathlib. You turn a mathematical claim written in prose into a Lean 4 "
    "theorem statement. You never write proofs."
)
USER_PROMPT = """\
Below is a Lean 4 file and a claim in prose. Write one Lean 4 theorem named `{name}` that states exactly the \
result described in the prose, using the definitions in the file where they apply. It will be inserted at the \
line `{marker}`, so it can use everything defined before that line.

Rules:
- State the claim; do not prove it. End the theorem with `:= by sorry`.
- Do not add hypotheses, constants or conclusions that the prose does not give.
- Reply with a single ```lean code block that contains only that theorem.

Prose:
{prose}

File:
```lean
{context}
```"""


def prompt_sha256() -> str:
    return hashlib.sha256((PROMPT_VERSION + SYSTEM_PROMPT + USER_PROMPT + MARKER).encode("utf-8")).hexdigest()


def declaration_end(lean: str, end: int) -> int:
    """End of the declaration whose statement ends at end: the next line that starts at column 0."""
    m = re.compile(r"^\S", re.M).search(lean, lean.find("\n", end) + 1 if "\n" in lean[end:] else len(lean))
    return m.start() if m else len(lean)


def build_context(target: dict) -> str:
    """The challenge file without the target theorem, its docstring and its proof; a marker takes their place."""
    lean = target["lean"]
    start = _insertion_point(lean, target["start"])
    stop = declaration_end(lean, target["end"])
    return lean[:start] + MARKER + "\n\n" + lean[stop:]


def build_messages(target: dict) -> list[dict[str, str]]:
    user = USER_PROMPT.format(
        name=target["theorem"], marker=MARKER, prose=target["scope"].strip(), context=build_context(target)
    )
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def parse_candidate(output: str, name: str) -> tuple[str, str | None]:
    """(status, statement) from a model reply: parsed, wrong_name (another theorem was stated) or no_theorem."""
    block = re.search(r"```(?:lean4?|)\s*\n(.*?)```", output, re.S)
    code = block.group(1) if block else output
    parsed = pilot.theorem_statement(code, name)
    if parsed:
        return "parsed", parsed[1].strip()
    other = pilot.theorem_statement(code)
    if other:
        return "wrong_name", other[1].strip()
    return "no_theorem", None


def _context_full(client) -> bool | None:
    """True when the prompt filled the model's context, so Ollama may have cut it."""
    tokens, limit = getattr(client, "last_prompt_tokens", None), getattr(client, "num_ctx", None)
    return None if tokens is None or limit is None else tokens >= limit - 16


class OllamaClient:
    """Ollama's native chat API, which, unlike its OpenAI-compatible endpoint, accepts a context length per call.

    Ollama truncates a prompt longer than its context silently, so every reply also records how many prompt
    tokens the model read (`last_prompt_tokens`); `formalize` flags a reply whose prompt filled the context.
    """

    def __init__(self, model: str, base_url: str | None = None, num_ctx: int = 32768, timeout: float = 1800.0):
        self.model, self.num_ctx, self.timeout = model, num_ctx, timeout
        self.base_url = (base_url or "http://localhost:11434").rstrip("/")
        self.last_prompt_tokens = None

    def digest(self) -> str | None:
        import httpx

        models = httpx.get(f"{self.base_url}/api/tags", timeout=60).json().get("models", [])
        return next((m.get("digest") for m in models if m.get("name") == self.model), None)

    def complete(self, messages, temperature: float = 0.0, seed: int = 0) -> str:
        import httpx

        options = {"temperature": temperature, "seed": seed, "num_ctx": self.num_ctx}
        body = {"model": self.model, "messages": messages, "stream": False, "options": options}
        response = httpx.post(f"{self.base_url}/api/chat", json=body, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        self.last_prompt_tokens = data.get("prompt_eval_count")
        return data["message"]["content"]


class OpenAICompatClient:
    """An OpenAI-compatible endpoint such as LM Studio's. The context length is set when the model is loaded
    there, so it is passed in as num_ctx only to flag replies whose prompt filled it (`usage.prompt_tokens`)."""

    def __init__(self, model: str, base_url: str, num_ctx: int, timeout: float = 1800.0):
        self.model, self.base_url, self.num_ctx, self.timeout = model, base_url.rstrip("/"), num_ctx, timeout
        self.last_prompt_tokens = None

    def complete(self, messages, temperature: float = 0.0, seed: int = 0) -> str:
        import httpx

        body = {"model": self.model, "messages": messages, "temperature": temperature, "seed": seed}
        response = httpx.post(f"{self.base_url}/chat/completions", json=body, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        self.last_prompt_tokens = (data.get("usage") or {}).get("prompt_tokens")
        return data["choices"][0]["message"]["content"]


def cmd_formalize(math_root: Path, out: Path, client, resume: bool, dry_run_dir: Path | None) -> int:
    commit = oracle.check_commit(math_root)
    targets = load_targets(math_root)
    if dry_run_dir is not None:
        dry_run_dir.mkdir(parents=True, exist_ok=True)
        for t in targets:
            messages = build_messages(t)
            text = "\n\n".join(f"## {m['role']}\n\n{m['content']}" for m in messages)
            (dry_run_dir / f"F{t['family']}_prompt.md").write_text(text, encoding="utf-8")
            print(f"F{t['family']}: {len(text)} chars, about {len(text) // 3} tokens")
        print(f"Prompts in {dry_run_dir}; no model was called. Prompt {PROMPT_VERSION} {prompt_sha256()[:12]}")
        return 0

    kept = {}
    if resume and out.exists():
        previous = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
        kept = {x["family"]: x for x in previous if x.get("kind") != "meta" and not x.get("transport_error")}
    meta = {
        "kind": "meta",
        "plan": "docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md (phase 2)",
        "model": client.model,
        "base_url_host": client.base_url.split("//")[-1].split("/")[0],
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": prompt_sha256(),
        "openai_math_commit": commit,
        "temperature": 0.0,
        "seed": 0,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if isinstance(client, OllamaClient):
        # Ollama tags are aliases: several names can point at one model, so the digest identifies it.
        meta.update(client="ollama-native", model_digest=client.digest(), num_ctx=client.num_ctx)
    elif isinstance(client, OpenAICompatClient):
        meta.update(client="openai-compatible", num_ctx=client.num_ctx)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(meta) + "\n")
        for t in targets:
            if t["family"] in kept:
                fh.write(json.dumps(kept[t["family"]], ensure_ascii=False) + "\n")
                continue
            messages = build_messages(t)
            t0 = time.time()
            try:
                output, error = client.complete(messages, temperature=0.0, seed=0), ""
            except Exception as exc:  # A transport failure is recorded, not retried silently; --resume redoes it.
                output, error = "", f"{type(exc).__name__}: {exc}"
            status, candidate = parse_candidate(output, t["theorem"]) if output else ("no_output", None)
            row = {
                "family": t["family"],
                "theorem": t["theorem"],
                "wrapper": wrapper_definition(t) is not None,
                "prompt_chars": sum(len(m["content"]) for m in messages),
                "prompt_tokens": getattr(client, "last_prompt_tokens", None),
                "context_full": _context_full(client),
                "output": output,
                "transport_error": error,
                "status": status,
                "candidate": candidate,
                "seconds": round(time.time() - t0, 2),
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"F{t['family']}: {status}{' ERROR ' + error if error else ''}", flush=True)
    print(f"Wrote {out}")
    return 0


# ---------------------------------------------------------------- phase 2: compare


def family_verdict(original: dict | None, mutants: list[dict]) -> dict:
    """Auditor verdict for one family from its check outcomes.

    abstain: no candidate, or the candidate did not elaborate. Otherwise the original is faithful when proved
    equivalent; each mutant is flagged unless proved equivalent; the family discriminates when the original is
    faithful and every mutant is flagged.
    """
    if original is None or original["outcome"] in ("invalid", "setup_error"):
        reason = "no candidate" if original is None else original["outcome"]
        return {"verdict": "abstain", "reason": reason, "mutants": len(mutants), "mutants_flagged": 0}
    faithful = original["outcome"] == "proved"
    flagged = sum(m["outcome"] in ("not_shown", "timeout") for m in mutants)
    return {
        "verdict": "faithful" if faithful else "flagged",
        "mutants": len(mutants),
        "mutants_flagged": flagged,
        "discriminating": faithful and flagged == len(mutants),
    }


def phase2_summary(verdicts: dict[str, dict], families: list[str]) -> dict:
    sub = [verdicts[f] for f in families if f in verdicts]
    n = len(families)
    elaborated = [v for v in sub if v["verdict"] != "abstain"]
    faithful = sum(v["verdict"] == "faithful" for v in elaborated)
    mutants = sum(v["mutants"] for v in elaborated)
    flagged = sum(v["mutants_flagged"] for v in elaborated)
    return {
        "families": n,
        "elaborated": len(elaborated),
        "faithful": faithful,
        "faithful_rate_of_all": round(faithful / n, 3) if n else None,
        "specificity_of_elaborated": round(faithful / len(elaborated), 3) if elaborated else None,
        "mutants": mutants,
        "mutants_flagged": flagged,
        "discriminating_families": sum(v.get("discriminating", False) for v in elaborated),
    }


def compare(math_root: Path, responses: Path, out_dir: Path, timeout: int, jobs: int) -> int:
    commit = oracle.check_commit(math_root)
    lean_root = oracle.lean_dir(math_root)
    lines = [json.loads(line) for line in responses.read_text(encoding="utf-8").splitlines() if line]
    meta = next(x for x in lines if x.get("kind") == "meta")
    replies = {x["family"]: x for x in lines if x.get("kind") != "meta"}
    label = re.sub(r"[^A-Za-z0-9._-]", "_", meta["model"])
    work = out_dir / f"compare_{label}"
    work.mkdir(parents=True, exist_ok=True)
    targets = load_targets(math_root)
    screen = auto_screen(targets)

    jobs_list = []
    for t in targets:
        reply = replies.get(t["family"], {})
        candidate = reply.get("candidate") if reply.get("status") in ("parsed", "wrong_name") else None
        if candidate is None:
            jobs_list.append((t, reply, []))
            continue
        cand = statement_prop(candidate)
        checks = [(f"F{t['family']}_original", cand, statement_prop(t["statement"]))]
        for code, mutant in sorted(pilot.mutate(t["statement"]).items()):
            checks.append((f"F{t['family']}_{code}", cand, statement_prop(mutant)))
        checks.append((f"F{t['family']}_{SENTINEL[0]}", SENTINEL[1], SENTINEL[2]))
        jobs_list.append((t, reply, checks))

    def run_one(job):
        t, reply, checks = job
        if not checks:
            return t, reply, [], {}
        text, ranges = build_check_file(t["lean"], t["start"], checks)
        check_file = work / f"F{t['family']}.lean"
        check_file.write_text(text, encoding="utf-8")
        outcomes, _ = run_check_file(t["family"], check_file, ranges, lean_root, timeout)
        return t, reply, checks, outcomes

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        finished = list(pool.map(run_one, jobs_list))

    verdicts, rows = {}, []
    for t, reply, checks, outcomes in finished:
        fam = t["family"]
        original = outcomes.get(f"F{fam}_original")
        mutants = [outcomes[c[0]] for c in checks if c[0] not in (f"F{fam}_original", f"F{fam}_{SENTINEL[0]}")]
        verdicts[fam] = family_verdict(original, mutants)
        rows.append(
            {
                "family": fam,
                "theorem": t["theorem"],
                "status": reply.get("status", "missing"),
                "candidate": reply.get("candidate"),
                **verdicts[fam],
                "checks": {c[0]: outcomes[c[0]] for c in checks},
            }
        )
    result = {
        "plan": "docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md (phase 2)",
        "formalizer": {k: meta.get(k) for k in ("model", "model_digest", "client", "num_ctx", "prompt_sha256")},
        "openai_math_commit": commit,
        "heartbeats": HEARTBEATS,
        "tactic": TACTIC,
        "headline": phase2_summary(verdicts, screen["headline"]),
        "headline_anchored": phase2_summary(verdicts, screen["headline_anchored"]),
        "wrappers_reported_separately": phase2_summary(verdicts, screen["wrappers_reported_separately"]),
        "rows": rows,
    }
    headline = result["headline"]
    result["go"] = bool(headline["families"]) and headline["faithful"] / headline["families"] >= 0.3
    out = ROOT / "docs" / "reference" / "benchmarks" / "lean_fidelity_phase2" / f"compare_{label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("headline", "headline_anchored", "wrappers_reported_separately", "go")}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "step", choices=["env-check", "controls", "screen-auto", "screen-sheet", "screen-score", "formalize", "compare"]
    )
    parser.add_argument("--math-root", type=Path, help="Path to an openai/math checkout (all steps but screen-score)")
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds per Lean file or model call")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "private" / "lean_fidelity", help="Generated files")
    parser.add_argument("--jobs", type=int, default=4, help="Lean processes in parallel (controls)")
    parser.add_argument("--force", action="store_true", help="Overwrite screen sheets that already have verdicts")
    parser.add_argument("--model", help="Model name at the endpoint (formalize)")
    parser.add_argument("--base-url", help="Endpoint (formalize; default localhost:11434 or localhost:1234/v1)")
    parser.add_argument("--out", type=Path, help="Raw outputs, JSONL (formalize)")
    parser.add_argument("--responses", type=Path, help="formalize output to check with Lean (compare)")
    parser.add_argument("--resume", action="store_true", help="Keep finished families from --out (formalize)")
    parser.add_argument("--dry-run", action="store_true", help="Write the prompts only; call no model (formalize)")
    parser.add_argument(
        "--backend", choices=["ollama", "openai"], default="ollama", help="ollama: native API; openai: e.g. LM Studio"
    )
    parser.add_argument("--num-ctx", type=int, default=32768, help="Context length (set per call with ollama)")
    args = parser.parse_args()
    if args.step == "screen-score":
        return cmd_screen_score()
    if args.math_root is None:
        parser.error("--math-root is required for this step")
    math_root = args.math_root.resolve()
    if args.step == "env-check":
        return env_check(math_root, args.timeout)
    if args.step == "controls":
        return controls(math_root, args.out_dir.resolve(), args.timeout, args.jobs)
    if args.step == "compare":
        if args.responses is None:
            parser.error("--responses is required for compare")
        return compare(math_root, args.responses.resolve(), args.out_dir.resolve(), args.timeout, args.jobs)
    if args.step == "screen-auto":
        return cmd_screen_auto(math_root)
    if args.step == "screen-sheet":
        return cmd_screen_sheet(math_root, args.force)
    if args.dry_run:
        return cmd_formalize(math_root, Path(), None, False, args.out_dir.resolve() / "prompts")
    if not args.model:
        parser.error("--model is required for formalize")
    if args.backend == "ollama":
        client = OllamaClient(args.model, args.base_url, args.num_ctx, args.timeout)
    else:
        client = OpenAICompatClient(args.model, args.base_url or "http://localhost:1234/v1", args.num_ctx, args.timeout)
    out = args.out or args.out_dir / f"formalize_{re.sub(r'[^A-Za-z0-9._-]', '_', client.model)}.jsonl"
    return cmd_formalize(math_root, out.resolve(), client, args.resume, None)


if __name__ == "__main__":
    sys.exit(main())
