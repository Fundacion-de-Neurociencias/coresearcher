"""openai/math statement-fidelity pilot (Task A), implementing
docs/reference/benchmarks/OPENAI_MATH_PILOT_PROTOCOL.md.

Usage:
    python scripts/benchmarks/openai_math_pilot.py

Downloads the needed files of openai/math at a pinned commit (cached in private/cache/, which is
git-ignored), builds 20 prose/Lean pairs with syntactic mutants, evaluates the systems and writes
docs/reference/benchmarks/openai_math_pilot_dataset.json and openai_math_pilot_results.json.
"""

import hashlib
import json
import math
import random
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.semantic_bijectivity_auditor import SemanticBijectivityAuditor  # noqa: E402

COMMIT = "1581d4cbdd69a0faf34b2089614fe2a814316a6a"
RAW = f"https://raw.githubusercontent.com/openai/math/{COMMIT}/"
CACHE = ROOT / "private" / "cache" / "openai_math" / COMMIT
OUT_DIR = ROOT / "docs" / "reference" / "benchmarks"
PROTOCOL = OUT_DIR / "OPENAI_MATH_PILOT_PROTOCOL.md"
SAMPLE_SEED = 20261013
SAMPLE_SIZE = 20
BOOT_SEED = 20261013
BOOT_RESAMPLES = 2000
NULL_SEED = 7013
Z95 = 1.959963984540054


def fetch(path: str) -> str | None:
    """Returns the file at the pinned commit, using the local cache. None when it does not exist."""
    target = CACHE / path
    if target.exists():
        return target.read_text(encoding="utf-8")
    try:
        with urllib.request.urlopen(RAW + path, timeout=60) as resp:
            text = resp.read().decode("utf-8")
    except Exception:
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------- extraction


def eligible_families(contents: str) -> list[str]:
    return sorted(set(re.findall(r"\(\[Lean\]\(lean/docs/(\d{3})\.md\)\)", contents)))


def scope_section(note: str) -> str:
    m = re.search(r"^## Scope\s*\n(.*?)(?=^## |\Z)", note, re.S | re.M)
    return m.group(1).strip() if m else ""


def first_challenge_path(note: str) -> str | None:
    m = re.search(r"\]\(\.\./ComparatorChallenges/([^)]+\.lean)\)", note)
    return f"lean/ComparatorChallenges/{m.group(1)}" if m else None


def theorem_statement(lean: str) -> tuple[str, str, int, int] | None:
    """Returns (name, statement_text, start, end) for the first theorem; statement ends before ':= by'.

    Only a ':=' outside brackets ends the statement; one inside brackets belongs to a named argument such
    as (k := k) or to a binder default value.
    """
    m = re.search(r"\btheorem\s+([^\s(:{\[]+)", lean)
    if not m:
        return None
    end = _top_level_assign(lean, m.end())
    if end == -1:
        return None
    return m.group(1), lean[m.start() : end], m.start(), end


def _top_level_assign(text: str, start: int) -> int:
    """Index of the first ':=' at bracket depth 0 from start, or -1."""
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch in "([{⟨⦃":
            depth += 1
        elif ch in ")]}⟩⦄":
            depth -= 1
        elif depth == 0 and text.startswith(":=", i):
            return i
    return -1


def title_of(note: str) -> str:
    m = re.match(r"#\s+(.+)", note.strip())
    return m.group(1).strip() if m else "Claim"


# ---------------------------------------------------------------- mutations


def _top_level_colon(stmt: str) -> int:
    """Index of the ':' that separates the binders from the conclusion (depth 0, not ':=')."""
    depth = 0
    for i, ch in enumerate(stmt):
        if ch in "([{⟨":
            depth += 1
        elif ch in ")]}⟩":
            depth -= 1
        elif ch == ":" and depth == 0 and not stmt.startswith(":=", i):
            return i
    return -1


def _balanced(text: str) -> bool:
    """True when every bracket in text is closed in order."""
    pairs = {")": "(", "]": "[", "}": "{", "⟩": "⟨"}
    stack = []
    for ch in text:
        if ch in "([{⟨":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def _binder_list(stmt: str, i: int) -> str:
    """Text between the quantifier at i and the ',' that ends its binder list (depth 0)."""
    depth = 0
    for j in range(i + 1, len(stmt)):
        ch = stmt[j]
        if ch in "([{⟨⦃":
            depth += 1
        elif ch in ")]}⟩⦄":
            depth -= 1
        elif ch == "," and depth == 0:
            return stmt[i + 1 : j]
    return stmt[i + 1 :]


def mutate(stmt: str) -> dict[str, str]:
    mutants = {}
    colon = _top_level_colon(stmt)
    concl_start = colon + 1 if colon != -1 else None

    m = re.search(r"(?<![\w.])(\d+)(?![\w.])", stmt)
    if m:
        mutants["M1"] = stmt[: m.start()] + str(int(m.group(1)) + 1) + stmt[m.end() :]

    swaps = {"<": "≤", "≤": "<", ">": "≥", "≥": ">"}
    for i, ch in enumerate(stmt):
        if ch not in swaps:
            continue
        prev_ch = stmt[i - 1] if i > 0 else ""
        next_ch = stmt[i + 1] if i + 1 < len(stmt) else ""
        # Skip Lean syntax that is not an order relation: =>, ->, <|, |>, <;>, <-, ⟨ ⟩ are not touched.
        if ch == ">" and prev_ch in "=-|":
            continue
        if ch == "<" and next_ch in "|;-":
            continue
        mutants["M2"] = stmt[:i] + swaps[ch] + stmt[i + 1 :]
        break

    for i, ch in enumerate(stmt):
        if ch in "∀∃":
            # ∃ takes no instance or implicit binders ([Fintype F], {x}, ⦃x⦄), and ∃! has no ∀ form.
            if stmt.startswith("∃!", i) or re.search(r"[\[{⦃]", _binder_list(stmt, i)):
                continue
            mutants["M3"] = stmt[:i] + ("∃" if ch == "∀" else "∀") + stmt[i + 1 :]
            break

    if colon != -1:
        binders = list(re.finditer(r"\((?:[^()]|\([^()]*\))*\)", stmt[:colon]))
        # Hypothesis binders follow the Lean convention of a name starting with "h", e.g. (hn : 0 < n).
        explicit = [b for b in binders if re.match(r"\(\s*h\w*\s*:", b.group(0))]
        if explicit:
            b = explicit[-1]
            mutants["M4"] = stmt[: b.start()] + stmt[b.end() :]

    # An unbalanced conclusion means the statement was cut at an inner ':=' (a named argument such as
    # (k := k)); wrapping it in ¬ ( ... ) would leave a parenthesis open, so M5 does not apply.
    if concl_start is not None and stmt[concl_start:].strip() and _balanced(stmt[concl_start:]):
        conclusion = stmt[concl_start:].rstrip()
        mutants["M5"] = stmt[:concl_start] + " ¬ (" + conclusion.strip() + ")\n    "
    return {k: v for k, v in mutants.items() if v != stmt}


# ---------------------------------------------------------------- systems


def s1_coresearcher(prose: str, title: str, lean: str, name: str) -> tuple[bool, float]:
    prose_spec = SemanticBijectivityAuditor.extract_prose_specifications(prose, title)
    lean_spec = SemanticBijectivityAuditor.extract_lean_specifications(lean, name)
    verdict = SemanticBijectivityAuditor.audit_bijective_alignment(prose_spec, lean_spec)
    return (not verdict.is_bijective), float(verdict.drift_score)


NUM = re.compile(r"(?<![\w.])\d+(?:/\d+)?(?![\w.])")


def b1_numeric(prose: str, stmt: str) -> tuple[bool, float]:
    prose_nums = set(NUM.findall(prose))
    unexplained = [n for n in NUM.findall(stmt) if n not in prose_nums]
    return bool(unexplained), float(len(unexplained))


# ---------------------------------------------------------------- statistics


def wilson(k: int, n: int) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    p, z2 = k / n, Z95**2
    c = (p + z2 / (2 * n)) / (1 + z2 / n)
    h = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return [c - h, c + h]


def auroc(scores, labels) -> float:
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def family_bootstrap(rows, key, rng) -> list[float]:
    fams = sorted({r["family"] for r in rows})
    by = {f: [r for r in rows if r["family"] == f] for f in fams}
    vals = []
    for _ in range(BOOT_RESAMPLES):
        pick = [r for f in rng.choice(fams, size=len(fams), replace=True) for r in by[f]]
        a = auroc([r[key] for r in pick], [r["label"] for r in pick])
        if not math.isnan(a):
            vals.append(a)
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if vals else [float("nan")] * 2


def null_auroc(rows, key, rng) -> float:
    fams = sorted({r["family"] for r in rows})
    labels = []
    for f in fams:
        fam_labels = [r["label"] for r in rows if r["family"] == f]
        labels += list(rng.permutation(fam_labels))
    ordered = [r for f in fams for r in rows if r["family"] == f]
    return auroc([r[key] for r in ordered], labels)


def summarize(rows, flag_key, score_key, rng) -> dict:
    muts = [r for r in rows if r["label"] == 1]
    origs = [r for r in rows if r["label"] == 0]
    tp = sum(r[flag_key] for r in muts)
    tn = sum(not r[flag_key] for r in origs)
    by_type = {}
    for code in sorted({r["mutation"] for r in muts}):
        sub = [r for r in muts if r["mutation"] == code]
        k = sum(r[flag_key] for r in sub)
        by_type[code] = {"flagged": k, "n": len(sub), "sensitivity": k / len(sub), "wilson_95": wilson(k, len(sub))}
    return {
        "sensitivity": {
            "flagged": tp,
            "n": len(muts),
            "value": tp / len(muts) if muts else None,
            "wilson_95": wilson(tp, len(muts)),
        },
        "specificity": {
            "passed": tn,
            "n": len(origs),
            "value": tn / len(origs) if origs else None,
            "wilson_95": wilson(tn, len(origs)),
        },
        "auroc": auroc([r[score_key] for r in rows], [r["label"] for r in rows]),
        "auroc_family_bootstrap_95": family_bootstrap(rows, score_key, rng),
        "auroc_null_control": null_auroc(rows, score_key, np.random.default_rng(NULL_SEED)),
        "by_mutation": by_type,
    }


# ---------------------------------------------------------------- main


def main() -> int:
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    code_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    contents = fetch("CONTENTS.md")
    if contents is None:
        print("Could not download CONTENTS.md; check network access.")
        return 1

    families = eligible_families(contents)
    sample = sorted(random.Random(SAMPLE_SEED).sample(families, SAMPLE_SIZE))

    pairs, failures = [], []
    for fam in sample:
        note = fetch(f"lean/docs/{fam}.md")
        if note is None:
            failures.append({"family": fam, "reason": "scope note not found"})
            continue
        scope = scope_section(note)
        challenge = first_challenge_path(note)
        if not scope or not challenge:
            failures.append({"family": fam, "reason": "no scope section or no Comparator statement link"})
            continue
        lean = fetch(challenge)
        parsed = theorem_statement(lean) if lean else None
        if not parsed:
            failures.append({"family": fam, "reason": f"no theorem found in {challenge}"})
            continue
        name, stmt, start, end = parsed
        pairs.append(
            {
                "family": fam,
                "title": title_of(note),
                "scope": scope,
                "challenge": challenge,
                "theorem": name,
                "lean": lean,
                "statement": stmt,
                "span": [start, end],
                "mutants": mutate(stmt),
            }
        )

    rows = []
    for p in pairs:
        variants = [("ORIGINAL", p["statement"], 0)] + [(k, v, 1) for k, v in sorted(p["mutants"].items())]
        for code, stmt, label in variants:
            lean_variant = p["lean"][: p["span"][0]] + stmt + p["lean"][p["span"][1] :]
            s1_flag, s1_score = s1_coresearcher(p["scope"], p["title"], lean_variant, p["theorem"])
            b1_flag, b1_score = b1_numeric(p["scope"], stmt)
            rows.append(
                {
                    "family": p["family"],
                    "mutation": code,
                    "label": label,
                    "s1_flag": s1_flag,
                    "s1_score": s1_score,
                    "b0_flag": False,
                    "b0_score": 0.0,
                    "b1_flag": b1_flag,
                    "b1_score": b1_score,
                }
            )

    type_coverage = {c: sum(c in p["mutants"] for p in pairs) for c in ["M1", "M2", "M3", "M4", "M5"]}
    feasibility = {
        "pairs_extracted": len(pairs),
        "extraction_failures": failures,
        "mutation_type_coverage": type_coverage,
        "criterion_pairs": len(pairs) >= 18,
        "criterion_types": sum(v >= 15 for v in type_coverage.values()) >= 3,
    }
    rng = np.random.default_rng(BOOT_SEED)
    systems = {
        "S1_coresearcher": summarize(rows, "s1_flag", "s1_score", rng),
        "B0_always_match": summarize(rows, "b0_flag", "b0_score", rng),
        "B1_numeric": summarize(rows, "b1_flag", "b1_score", rng),
    }
    h1 = systems["S1_coresearcher"]["auroc_family_bootstrap_95"][0] > 0.5

    dataset = {
        "source": {
            "repository": "https://github.com/openai/math",
            "commit": COMMIT,
            "license": "Apache-2.0",
            "attribution": "Prose scope notes and Lean statements are from openai/math (Apache-2.0).",
        },
        "sample": sample,
        "pairs": [{k: v for k, v in p.items() if k not in ("lean", "span")} for p in pairs],
    }
    results = {
        "protocol": "docs/reference/benchmarks/OPENAI_MATH_PILOT_PROTOCOL.md",
        "protocol_sha256": protocol_sha,
        "coresearcher_commit": code_commit,
        "source_commit": COMMIT,
        "feasibility": feasibility,
        "systems": systems,
        "criteria": {
            "feasibility_pairs": feasibility["criterion_pairs"],
            "feasibility_mutation_types": feasibility["criterion_types"],
            "h1_s1_auroc_lower_bound_above_half": bool(h1),
        },
        "rows": rows,
    }
    (OUT_DIR / "openai_math_pilot_dataset.json").write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "openai_math_pilot_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"protocol sha256 {protocol_sha[:16]} | coresearcher {code_commit[:7]} | source {COMMIT[:7]}")
    print(f"pairs extracted: {len(pairs)}/{SAMPLE_SIZE}; failures: {len(failures)}; mutation coverage: {type_coverage}")
    for name, s in systems.items():
        se, sp = s["sensitivity"], s["specificity"]
        print(
            f"{name:16s} sens {se['flagged']}/{se['n']}  spec {sp['passed']}/{sp['n']}  "
            f"AUROC {s['auroc']:.3f} (family bootstrap {s['auroc_family_bootstrap_95'][0]:.3f}-"
            f"{s['auroc_family_bootstrap_95'][1]:.3f}; null {s['auroc_null_control']:.3f})"
        )
    print(f"criteria: {results['criteria']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
