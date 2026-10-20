"""Falsifiability pilot: generation, measurement and analysis, with the model injected (no Ollama needed)."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_falsifiability_pilot as fp  # noqa: E402

from python.discovery.formal_hypothesis import hypothesis_from_dict  # noqa: E402

FALSIFIABLE = hypothesis_from_dict(
    {
        "hypothesis_id": "F",
        "variables": [{"name": "group", "domain": ["a", "b"]}, {"name": "outcome", "domain": ["x", "y"]}],
        "assumptions": ["group == 'a'"],
        "claims": ["outcome == 'x'"],
    }
)
UNFALSIFIABLE = hypothesis_from_dict(
    {
        "hypothesis_id": "U",
        "variables": [{"name": "group", "domain": ["a", "b"]}],
        "assumptions": [],
        "claims": ["group == 'a' or group == 'b'"],
    }
)


def test_parse_score_accepts_only_integers_in_range():
    assert fp.parse_score('{"falsifiability": 7}') == 7
    assert fp.parse_score('```json\n{"falsifiability": 10}\n```') == 10
    assert fp.parse_score('{"falsifiability": 11}') is None
    assert fp.parse_score('{"falsifiability": true}') is None
    assert fp.parse_score('{"falsifiability": "7"}') is None
    assert fp.parse_score("no json here") is None


def test_rubric_uses_three_seeded_reviews_and_the_median():
    answers = iter(['{"falsifiability": 4}', '{"falsifiability": 9}', '{"falsifiability": 6}'])
    seeds = []

    def complete(prompt, seed):
        seeds.append(seed)
        return next(answers)

    result = fp.rubric_score("a claim", complete)
    assert result == {"reviews": [4, 9, 6], "median": 6.0} and len(set(seeds)) == 3


def test_rubric_without_three_valid_reviews_has_no_median():
    result = fp.rubric_score("a claim", lambda p, s: '{"falsifiability": 5}' if s == 64000 else "junk")
    assert result["median"] is None


def test_exact_measure_reports_verdict_and_forbidden_fraction():
    measured = fp.exact_measure(FALSIFIABLE)
    assert measured["status"] == "DECIDED" and measured["verdict"] == "FALSIFIABLE"
    assert 0 < measured["excluded_fraction"] <= 1
    assert fp.exact_measure(UNFALSIFIABLE)["verdict"] == "UNFALSIFIABLE"


def test_measure_records_formalization_exclusions_with_reasons():
    hypotheses = [
        {"question_id": "Q1", "domain": "d", "prose": "p1"},
        {"question_id": "Q2", "domain": "d", "prose": "p2"},
    ]

    def formalize(prose, qid):
        return ("PASSED_GATE", FALSIFIABLE, "") if qid == "Q1" else ("EXCLUDED", None, "FORMALIZATION_AMBIGUOUS")

    rows = fp.measure(hypotheses, formalize, lambda p, s: '{"falsifiability": 8}')
    assert rows[0]["exact"]["verdict"] == "FALSIFIABLE" and rows[0]["rubric"]["median"] == 8.0
    assert rows[1]["exact"] is None and rows[1]["reason"] == "FORMALIZATION_AMBIGUOUS"


def test_cohen_kappa_matches_the_textbook_values():
    assert fp.cohen_kappa([1, 1, 0, 0], [1, 1, 0, 0]) == pytest.approx(1.0)
    assert fp.cohen_kappa([1, 1, 0, 0], [1, 0, 1, 0]) == pytest.approx(0.0)


def synthetic_rows(n, correlated=True):
    rng = np.random.default_rng(1)
    rows = []
    for i in range(n):
        falsifiable = bool(i % 2)
        score = (7 if falsifiable else 3) if correlated else int(rng.integers(1, 11))
        fraction = 0.3 if falsifiable else 0.0
        rows.append(
            {
                "question_id": f"Q{i}",
                "domain": "d",
                "formalization": "PASSED_GATE",
                "reason": "",
                "exact": {
                    "status": "DECIDED",
                    "verdict": "FALSIFIABLE" if falsifiable else "UNFALSIFIABLE",
                    "excluded_fraction": fraction,
                },
                "rubric": {"reviews": [score] * 3, "median": float(score)},
            }
        )
    return rows


def test_analysis_on_correlated_measures_meets_both_criteria():
    result = fp.analyse(synthetic_rows(40))
    assert result["q1"]["kappa"] == pytest.approx(1.0)
    assert result["q1"]["kappa_95"][0] > 0.40
    assert result["q2"]["informative"] == result["q2"]["exact_falsifiable"] == 20
    assert result["criteria"]["A_agreement"]["met"] and result["criteria"]["I_informativeness"]["met"]
    assert result["q3"]["status"] == "not run"


def test_blocked_and_unscored_items_are_excluded_with_a_reason():
    rows = synthetic_rows(10)
    rows[0]["exact"] = {"status": "BLOCKED", "verdict": None, "excluded_fraction": None}
    rows[1]["rubric"] = {"reviews": [None, 3, 3], "median": None}
    result = fp.analyse(rows)
    assert result["excluded"] == 2 and result["analysed"] == 8
    assert set(result["excluded_reasons"]) == {
        "exact evaluator blocked: state space above max_states",
        "rubric scores incomplete",
    }


def test_informative_criterion_fails_when_falsifiable_items_exclude_nothing():
    rows = synthetic_rows(40)
    for row in rows:
        row["exact"]["excluded_fraction"] = 0.01
    result = fp.analyse(rows)
    assert result["q2"]["informative"] == 0 and result["criteria"]["I_informativeness"]["met"] is False


def test_generation_is_one_hypothesis_per_question_with_fixed_seeds():
    questions = [
        {"id": "Q-1", "domain": "d", "text": "Does a predict b?"},
        {"id": "Q-2", "domain": "d", "text": "Does c?"},
    ]
    seeds = []

    def complete(prompt, seed):
        seeds.append(seed)
        return " a hypothesis "

    rows = fp.generate(questions, complete)
    assert [r["question_id"] for r in rows] == ["Q-1", "Q-2"] and rows[0]["prose"] == "a hypothesis"
    assert seeds == [63000, 63001]


def test_score_refuses_measures_from_another_protocol(tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "MEASURES", tmp_path / "m.jsonl")
    monkeypatch.setattr(fp, "RESULTS", tmp_path / "r.json")
    rows = synthetic_rows(4)
    for row in rows:
        row["protocol_sha256"] = "0" * 64
    fp.MEASURES.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    with pytest.raises(SystemExit):
        fp.cmd_score()
