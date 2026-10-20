"""Falsifiability pilot v2: prompts frozen in the protocol, validity, measurement and analysis (model injected)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_falsifiability_pilot_v2 as v2  # noqa: E402

PROTOCOL_TEXT = v2.PROTOCOL.read_text(encoding="utf-8")


def _section(number: str) -> str:
    start = PROTOCOL_TEXT.index(f"## {number}.")
    end = PROTOCOL_TEXT.find("\n## ", start + 1)
    return PROTOCOL_TEXT[start : end if end != -1 else None].split("\n", 1)[1]


def _norm(text: str) -> str:
    return " ".join(text.split())


def test_generator_prompt_is_the_frozen_text_of_section_7():
    assert _norm(v2.GENERATE_PROMPT.format(question="{question}")) == _norm(_section("7"))


def test_rubric_prompt_is_the_frozen_text_of_section_8():
    assert _norm(v2.RUBRIC_PROMPT.format(question="{question}", hypothesis="{hypothesis}")) == _norm(_section("8"))


VALID = {
    "hypothesis_id": "H",
    "variables": [{"name": "group", "domain": ["a", "b"]}, {"name": "outcome", "domain": ["x", "y"]}],
    "assumptions": ["group == 'a'"],
    "claims": ["outcome == 'x'"],
}


def test_validity_accepts_formal_objects_and_names_failures():
    assert v2.validate(VALID)[0] == "VALID"
    assert v2.validate(None) == ("INVALID", None, "NO_JSON")
    status, hypothesis, reason = v2.validate({**VALID, "claims": ["outcome is a real number"]})
    assert status == "INVALID" and hypothesis is None and reason
    big = {
        "hypothesis_id": "B",
        "variables": [{"name": f"v{i}", "domain": list(range(10))} for i in range(7)],
        "assumptions": [],
        "claims": ["v0 >= 0"],
    }
    assert v2.validate(big)[0] == "BLOCKED"


def test_generation_records_parse_status_and_fixed_seeds():
    questions = [
        {"id": "Q1", "domain": "d", "text": "Does a predict b?"},
        {"id": "Q2", "domain": "d", "text": "Does c?"},
    ]
    seeds = []

    def complete(prompt, seed):
        seeds.append(seed)
        return json.dumps(VALID) if seed == 63000 else "no object here"

    rows = v2.generate(questions, complete)
    assert [r["parsed"] for r in rows] == [True, False]
    assert seeds == [63000, 63001] and rows[0]["formal"]["hypothesis_id"] == "H"


def test_measure_counts_every_exclusion_and_scores_valid_ones_with_three_reviews():
    rows = [
        {"question_id": "Q1", "domain": "d", "question": "q", "parsed": True, "formal": VALID},
        {
            "question_id": "Q2",
            "domain": "d",
            "question": "q",
            "parsed": True,
            "formal": {**VALID, "claims": ["outcome is a real number"]},
        },
        {"question_id": "Q3", "domain": "d", "question": "q", "parsed": False, "formal": None},
    ]
    scores = iter(['{"falsifiability": 6}', '{"falsifiability": 8}', '{"falsifiability": 7}'])
    out = v2.measure(rows, lambda p, s: next(scores))
    assert [r["formalization"] for r in out] == ["VALID", "INVALID", "INVALID"]
    assert out[0]["exact"]["verdict"] == "FALSIFIABLE" and out[0]["rubric"]["median"] == 7.0
    assert out[1]["exact"] is None and out[2]["reason"] == "NO_JSON"


def test_analysis_states_its_scope_and_uses_the_v1_criteria():
    rows = []
    for i in range(40):
        falsifiable = bool(i % 2)
        score = 7 if falsifiable else 3
        rows.append(
            {
                "question_id": f"Q{i}",
                "domain": "d",
                "formalization": "VALID",
                "reason": "",
                "exact": {
                    "status": "DECIDED",
                    "verdict": "FALSIFIABLE" if falsifiable else "UNFALSIFIABLE",
                    "excluded_fraction": 0.3 if falsifiable else 0.0,
                },
                "rubric": {"reviews": [score] * 3, "median": float(score)},
            }
        )
    result = v2.analyse(rows)
    assert result["criteria"]["A_agreement"]["met"] and result["criteria"]["I_informativeness"]["met"]
    assert "formal hypotheses" in result["scope"] and result["q3"]["status"] == "not run"


def test_score_refuses_measures_from_another_protocol(tmp_path, monkeypatch):
    monkeypatch.setattr(v2, "MEASURES", tmp_path / "m.jsonl")
    monkeypatch.setattr(v2, "RESULTS", tmp_path / "r.json")
    v2._write(
        v2.MEASURES,
        [
            {
                "question_id": "Q",
                "protocol_sha256": "0" * 64,
                "formalization": "INVALID",
                "reason": "NO_JSON",
                "exact": None,
                "rubric": None,
            }
        ],
    )
    with pytest.raises(SystemExit):
        v2.cmd_score()
