"""Falsifiability pilot, version 2 (docs/reference/benchmarks/FALSIFIABILITY_PILOT_V2_PROTOCOL.md).

    python scripts/benchmarks/run_falsifiability_pilot_v2.py generate   # one formal hypothesis per bank question
    python scripts/benchmarks/run_falsifiability_pilot_v2.py measure    # validity, exact measure, rubric (3 reviews)
    python scripts/benchmarks/run_falsifiability_pilot_v2.py score      # Q1, Q2 and their criteria

Each hypothesis is written directly as a formal object. There is no prose translation and no consistency gate. Every
model call is injectable, so the logic is tested without a model. Version 1 (run_falsifiability_pilot.py) is unchanged.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_falsifiability_pilot as v1  # noqa: E402

from python.discovery.formal_hypothesis import (  # noqa: E402
    FormalHypothesisError,
    ThresholdExceeded,
    hypothesis_from_dict,
)

BENCH = ROOT / "docs" / "reference" / "benchmarks"
PILOT = BENCH / "falsifiability_v2"
BANK = BENCH / "inspiration" / "question_bank.json"
PROTOCOL = BENCH / "FALSIFIABILITY_PILOT_V2_PROTOCOL.md"
HYPOTHESES = PILOT / "hypotheses.jsonl"
MEASURES = PILOT / "measures.jsonl"
RESULTS = PILOT / "falsifiability_v2_results.json"
GENERATOR_MODEL = "qwen2.5:14b-instruct-q4_K_M"
JUDGE_MODEL = "qwen2.5-coder:32b"
GENERATOR_SEED = 63000
RUBRIC_SEED = 64000

# Frozen texts, identical to sections 7 and 8 of the v2 protocol (checked by the tests).
GENERATE_PROMPT = (
    "Write one scientific hypothesis for the research question below, as a JSON object with these keys: "
    "`hypothesis_id` (string), `variables` (a list of objects with `name` and `domain`, where the domain is a list of at "
    "most 10 values), `assumptions` (a list of predicates), `claims` (a list of predicates, at least one). "
    "A predicate is a string that uses only: comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`), `and`, `or`, `not`, "
    "parentheses, arithmetic, and `in` with a literal list. Write implication as `(not A) or B`. Do not use quantifiers, "
    "subscripts, function calls other than the listed operators, or prose inside a predicate. "
    "Answer only with the JSON object. "
    "Research question: {question}"
)
RUBRIC_PROMPT = (
    "You review a scientific hypothesis, given here as a formal object. Rate its falsifiability on a scale from 1 (no "
    "observation could refute it) to 10 (it names a precise observation that would refute it). Answer only with JSON: "
    '{{"falsifiability": <integer 1-10>}} '
    "Research question: {question} "
    "Hypothesis (formal object): {hypothesis}"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _protocol_sha() -> str:
    return _sha256(PROTOCOL)


def _load(path: Path) -> list:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write(path: Path, rows) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


# --------------------------------------------------------------------------- generation


def generate(questions: list, complete) -> list:
    """`complete(prompt, seed)` returns the model's text. The parse status is recorded; nothing is retried."""
    from python.discovery.formalizer import extract_json

    rows = []
    for index, q in enumerate(questions):
        text = complete(GENERATE_PROMPT.format(question=q["text"]), GENERATOR_SEED + index)
        obj = extract_json(text)
        rows.append(
            {
                "question_id": q["id"],
                "domain": q["domain"],
                "question": q["text"],
                "raw_output": text[:8000],
                "parsed": obj is not None,
                "formal": obj,
            }
        )
    return rows


# --------------------------------------------------------------------------- measurement


def validate(obj):
    """(status, hypothesis or None, reason). A space above the threshold is BLOCKED, anything malformed is INVALID."""
    if obj is None:
        return "INVALID", None, "NO_JSON"
    try:
        return "VALID", hypothesis_from_dict(obj), ""
    except ThresholdExceeded as exc:
        return "BLOCKED", None, str(exc)[:200]
    except (FormalHypothesisError, ValueError, TypeError, KeyError) as exc:
        return "INVALID", None, str(exc)[:200]


def rubric(question: str, obj: dict, complete) -> dict:
    """Three reviews from the judge, each with its own seed; the median of the valid scores is the score."""
    body = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    scores = [
        v1.parse_score(complete(RUBRIC_PROMPT.format(question=question, hypothesis=body), RUBRIC_SEED + k))
        for k in range(v1.REVIEWS)
    ]
    valid = sorted(s for s in scores if s is not None)
    return {"reviews": scores, "median": float(sorted(valid)[len(valid) // 2]) if len(valid) == v1.REVIEWS else None}


def measure(rows: list, complete) -> list:
    out = []
    for row in rows:
        status, hypothesis, reason = validate(row["formal"]) if row["parsed"] else ("INVALID", None, "NO_JSON")
        record = {"question_id": row["question_id"], "domain": row["domain"], "formalization": status, "reason": reason}
        if hypothesis is None:
            record.update({"exact": None, "rubric": None})
        else:
            record["exact"] = v1.exact_measure(hypothesis)
            record["rubric"] = rubric(row["question"], row["formal"], complete)
        out.append(record)
    return out


# --------------------------------------------------------------------------- analysis


def analyse(measures: list) -> dict:
    """The v1 analysis, applied to v2 measures. Each excluded item is counted with its reason."""
    result = v1.analyse(measures)
    result["protocol"] = PROTOCOL.name
    result["scope"] = (
        "formal hypotheses generated by the pinned model; prose hypotheses are not covered (see v1 results)"
    )
    return result


# --------------------------------------------------------------------------- commands


def _models():
    from python.discovery.formalizer import ChatClient

    return ChatClient(model=GENERATOR_MODEL), ChatClient(model=JUDGE_MODEL)


def cmd_generate() -> int:
    PILOT.mkdir(parents=True, exist_ok=True)
    if HYPOTHESES.exists():
        raise SystemExit("hypotheses.jsonl exists; the generated set is frozen and is not regenerated.")
    questions = json.loads(BANK.read_text(encoding="utf-8"))["questions"]
    generator, _ = _models()
    rows = generate(
        questions, lambda p, s: generator.complete([{"role": "user", "content": p}], temperature=0.0, seed=s)
    )
    for row in rows:
        row["protocol_sha256"] = _protocol_sha()
    _write(HYPOTHESES, rows)
    print(f"Wrote {len(rows)} rows to {HYPOTHESES.relative_to(ROOT)}, sha256 {_sha256(HYPOTHESES)}")
    return 0


def cmd_measure() -> int:
    rows = _load(HYPOTHESES)
    if not rows:
        raise SystemExit("Run 'generate' first.")
    _, judge = _models()
    out = measure(rows, lambda p, s: judge.complete([{"role": "user", "content": p}], seed=s))
    for row in out:
        row["protocol_sha256"] = _protocol_sha()
    _write(MEASURES, out)
    print(f"Wrote {len(out)} measures to {MEASURES.relative_to(ROOT)}, sha256 {_sha256(MEASURES)}")
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
