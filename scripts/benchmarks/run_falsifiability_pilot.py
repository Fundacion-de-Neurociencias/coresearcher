"""Falsifiability pilot (docs/reference/benchmarks/FALSIFIABILITY_PILOT_PROTOCOL.md). Questions 1 and 2 only.

    python scripts/benchmarks/run_falsifiability_pilot.py generate   # one hypothesis per bank question (Ollama)
    python scripts/benchmarks/run_falsifiability_pilot.py measure    # formalize, exact measure, rubric scores (Ollama)
    python scripts/benchmarks/run_falsifiability_pilot.py score      # analysis, writes falsifiability_results.json

Models are fixed by the protocol: the formalizer and the C1 generator are qwen2.5:14b-instruct-q4_K_M, and the rubric
judge is qwen2.5-coder:32b. Both are reached through Ollama's OpenAI-compatible API at FORMALIZER_BASE_URL. Every step
is injectable, so the logic is tested without a model.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.formal_hypothesis import (  # noqa: E402
    ContentVerdict,
    HypothesisEvaluator,
    ThresholdExceeded,
)

BENCH = ROOT / "docs" / "reference" / "benchmarks"
PILOT = BENCH / "falsifiability"
BANK = BENCH / "inspiration" / "question_bank.json"
PROTOCOL = BENCH / "FALSIFIABILITY_PILOT_PROTOCOL.md"
HYPOTHESES = PILOT / "hypotheses.jsonl"
MEASURES = PILOT / "measures.jsonl"
RESULTS = PILOT / "falsifiability_results.json"
GENERATOR_MODEL = "qwen2.5:14b-instruct-q4_K_M"
JUDGE_MODEL = "qwen2.5-coder:32b"
REVIEWS = 3
INFORMATIVE_THRESHOLD = 0.05
BOOT_SEED = 62001
BOOT_RESAMPLES = 10_000
KAPPA_CRITERION = 0.40
INFORMATIVE_CRITERION = 0.70

GENERATE_PROMPT = (
    "Write one testable scientific hypothesis that answers the research question below. State the claim, the "
    "comparison or measurement that would test it, and what outcome would refute it. Use at most 120 words.\n\n"
    "Question: {question}"
)
RUBRIC_PROMPT = (
    "You review a scientific hypothesis. Rate its falsifiability on a scale from 1 (no observation could refute it) to "
    "10 (it names a precise observation that would refute it). Answer only with JSON: "
    '{{"falsifiability": <integer 1-10>}}\n\nHypothesis: {hypothesis}'
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _append(path: Path, rows) -> None:
    with path.open("a", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load(path: Path) -> list:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------- generation


def generate(questions: list, complete) -> list:
    """`complete(prompt, seed)` returns the model's text. One hypothesis per question, seed fixed by question index."""
    rows = []
    for index, q in enumerate(questions):
        prose = complete(GENERATE_PROMPT.format(question=q["text"]), 63000 + index).strip()
        rows.append({"question_id": q["id"], "domain": q["domain"], "prose": prose})
    return rows


# --------------------------------------------------------------------------- measurement


def exact_measure(hypothesis) -> dict:
    """Content verdict and forbidden fraction from the formal evaluator. A space above the threshold is BLOCKED, not
    estimated."""
    try:
        report = HypothesisEvaluator.evaluate(hypothesis, max_examples=3)
    except ThresholdExceeded:
        return {"status": "BLOCKED", "verdict": None, "excluded_fraction": None}
    return {
        "status": "DECIDED",
        "verdict": report.content_verdict.value,
        "excluded_fraction": report.excluded_fraction_of_applicable,
    }


def parse_score(text: str):
    """The integer falsifiability score from a judge's answer, or None. Anything outside 1-10 is None."""
    from python.discovery.formalizer import extract_json

    data = extract_json(text)
    if not data or not isinstance(data.get("falsifiability"), int) or isinstance(data.get("falsifiability"), bool):
        return None
    value = data["falsifiability"]
    return value if 1 <= value <= 10 else None


def rubric_score(prose: str, complete) -> dict:
    """Three separate reviews, each with its own seed; the median of the valid scores is the score."""
    scores = [parse_score(complete(RUBRIC_PROMPT.format(hypothesis=prose), 64000 + k)) for k in range(REVIEWS)]
    valid = sorted(s for s in scores if s is not None)
    median = float(np.median(valid)) if len(valid) == REVIEWS else None
    return {"reviews": scores, "median": median}


def measure(hypotheses: list, formalize, complete) -> list:
    """`formalize(prose, hypothesis_id)` returns (status, hypothesis or None, reason). Every exclusion is recorded."""
    rows = []
    for h in hypotheses:
        status, hypothesis, reason = formalize(h["prose"], h["question_id"])
        row = {"question_id": h["question_id"], "domain": h["domain"], "formalization": status, "reason": reason}
        if hypothesis is None:
            row.update({"exact": None, "rubric": None})
        else:
            row["exact"] = exact_measure(hypothesis)
            row["rubric"] = rubric_score(h["prose"], complete)
        rows.append(row)
    return rows


def formalize_with_model(prose: str, question_id: str):
    """Formalizer path: the consistency gate of ADR-DISCOVERY-064 with the pinned model. Requires a running Ollama."""
    from python.discovery.formalization_gate import formalize_gated
    from python.discovery.formalizer import ChatClient

    client = ChatClient(model=GENERATOR_MODEL)
    result = formalize_gated(prose, {GENERATOR_MODEL: client}, hypothesis_id=question_id)
    formal = result.formalization
    if result.passes and formal is not None and formal.hypothesis is not None:
        return "PASSED_GATE", formal.hypothesis, ""
    return "EXCLUDED", None, result.status.value


# --------------------------------------------------------------------------- analysis


def wilson(successes: int, trials: int):
    if trials == 0:
        return [float("nan"), float("nan")]
    z = 1.959963984540054
    p = successes / trials
    centre = (p + z * z / (2 * trials)) / (1 + z * z / trials)
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / (1 + z * z / trials)
    return [centre - half, centre + half]


def cohen_kappa(a, b) -> float:
    a, b = np.asarray(a, dtype=bool), np.asarray(b, dtype=bool)
    observed = float(np.mean(a == b))
    expected = float(np.mean(a) * np.mean(b) + (1 - np.mean(a)) * (1 - np.mean(b)))
    return 1.0 if expected == 1.0 else (observed - expected) / (1 - expected)


def bootstrap_interval(values_fn, n: int, rng) -> list:
    """Percentile interval of a statistic over hypotheses, resampled with replacement."""
    stats = []
    for _ in range(BOOT_RESAMPLES):
        idx = rng.integers(0, n, size=n)
        stats.append(values_fn(idx))
    stats = [s for s in stats if s is not None and not math.isnan(s)]
    return [float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))]


def analyse(rows: list) -> dict:
    from scipy.stats import spearmanr

    def reason_for(r):
        if r["exact"] is None:
            return r["reason"] or r["formalization"]
        if r["exact"]["status"] == "BLOCKED":
            return "exact evaluator blocked: state space above max_states"
        if r["rubric"] is None or r["rubric"]["median"] is None:
            return "rubric scores incomplete"
        return None

    excluded = [r for r in rows if reason_for(r) is not None]
    usable = [r for r in rows if reason_for(r) is None]
    n = len(usable)
    result = {
        "questions": len(rows),
        "excluded": len(excluded),
        "excluded_reasons": sorted({reason_for(r) for r in excluded}),
        "analysed": n,
        "q1": {"status": "not analysed"},
        "q2": {"status": "not analysed"},
        "q3": {"status": "not run", "reason": "no revision pairs exist (protocol section 5.3)"},
        "criteria": {},
    }
    if n < 2:
        return result

    exact = [r["exact"]["verdict"] == ContentVerdict.FALSIFIABLE.value for r in usable]
    scores = np.array([r["rubric"]["median"] for r in usable], dtype=float)
    cut = float(np.median(scores))
    rubric = [s > cut for s in scores]
    kappa = cohen_kappa(exact, rubric)
    fractions = np.array([r["exact"]["excluded_fraction"] or 0.0 for r in usable], dtype=float)
    constant = np.ptp(fractions) == 0 or np.ptp(scores) == 0
    rho = None if constant else float(spearmanr(fractions, scores).statistic)
    rng = np.random.default_rng(BOOT_SEED)
    kappa_ci = bootstrap_interval(lambda idx: cohen_kappa(np.asarray(exact)[idx], np.asarray(rubric)[idx]), n, rng)
    result["q1"] = {
        "kappa": kappa,
        "kappa_95": kappa_ci,
        "spearman_fraction_vs_rubric": rho,
        "rubric_cut_at_median": cut,
    }

    falsifiable = [i for i, e in enumerate(exact) if e]
    informative = [i for i in falsifiable if fractions[i] >= INFORMATIVE_THRESHOLD]
    result["q2"] = {
        "exact_falsifiable": len(falsifiable),
        "informative": len(informative),
        "informative_share_95": wilson(len(informative), len(falsifiable)),
        "threshold": INFORMATIVE_THRESHOLD,
    }
    result["criteria"] = {
        "A_agreement": {"met": kappa_ci[0] > KAPPA_CRITERION, "required_lower_bound": KAPPA_CRITERION},
        "I_informativeness": {
            "met": (len(informative) / len(falsifiable) >= INFORMATIVE_CRITERION) if falsifiable else False,
            "required_share": INFORMATIVE_CRITERION,
        },
    }
    return result


# --------------------------------------------------------------------------- commands


def _protocol_sha() -> str:
    return _sha256(PROTOCOL)


def cmd_generate() -> int:
    from python.discovery.formalizer import ChatClient

    PILOT.mkdir(parents=True, exist_ok=True)
    if HYPOTHESES.exists():
        raise SystemExit("hypotheses.jsonl exists; the generated set is frozen and is not regenerated.")
    questions = json.loads(BANK.read_text(encoding="utf-8"))["questions"]
    client = ChatClient(model=GENERATOR_MODEL)
    rows = generate(
        questions,
        lambda prompt, seed: client.complete([{"role": "user", "content": prompt}], temperature=0.0, seed=seed),
    )
    for row in rows:
        row["protocol_sha256"] = _protocol_sha()
    _append(HYPOTHESES, rows)
    print(f"Wrote {len(rows)} hypotheses to {HYPOTHESES.relative_to(ROOT)}, sha256 {_sha256(HYPOTHESES)}")
    return 0


def cmd_measure() -> int:
    from python.discovery.formalizer import ChatClient

    hypotheses = _load(HYPOTHESES)
    if not hypotheses:
        raise SystemExit("Run 'generate' first.")
    judge = ChatClient(model=JUDGE_MODEL)
    rows = measure(
        hypotheses,
        formalize_with_model,
        lambda prompt, seed: judge.complete([{"role": "user", "content": prompt}], seed=seed),
    )
    for row in rows:
        row["protocol_sha256"] = _protocol_sha()
    MEASURES.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"Wrote {len(rows)} measures to {MEASURES.relative_to(ROOT)}")
    return 0


def cmd_score() -> int:
    rows = _load(MEASURES)
    if not rows:
        raise SystemExit("Run 'measure' first.")
    stale = {r["protocol_sha256"] for r in rows} - {_protocol_sha()}
    if stale:
        raise SystemExit(f"Measures were produced under another protocol version: {sorted(stale)}")
    result = analyse(rows)
    result["protocol_sha256"] = _protocol_sha()
    RESULTS.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["generate", "measure", "score"])
    args = parser.parse_args(argv)
    return {"generate": cmd_generate, "measure": cmd_measure, "score": cmd_score}[args.step]()


if __name__ == "__main__":
    sys.exit(main())
