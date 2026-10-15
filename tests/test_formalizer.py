"""Tests for the prose-to-formal formalizer and its benchmark scorer (ADR-DISCOVERY-061). No model is called."""

import json
import sys
from pathlib import Path

from python.discovery.formalizer import (
    FormalizationStatus,
    build_messages,
    extract_json,
    formalize_and_evaluate,
    parse_formalization,
    prompt_sha256,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "benchmarks"))
import formalizer_bench  # noqa: E402

SCHEMA = [{"name": "x", "domain": [0, 1, 2]}]
GOOD = {"variables": SCHEMA, "scope": None, "assumptions": [], "claims": ["x <= 1"]}


def test_extracts_json_from_fence_and_from_chatty_text():
    assert extract_json("Here:\n```json\n" + json.dumps(GOOD) + "\n```\nDone.") == GOOD
    assert extract_json("Note {not json}. Answer: " + json.dumps(GOOD) + " end") == GOOD
    assert extract_json('{"claims": ["s == \'}\'"]}') == {"claims": ["s == '}'"]}
    assert extract_json("no object here") is None


def test_parse_statuses():
    assert parse_formalization("plain text").status == FormalizationStatus.NO_JSON
    bad = dict(GOOD, claims=["__import__('os')"])
    assert parse_formalization(json.dumps(bad)).status == FormalizationStatus.INVALID
    assert parse_formalization(json.dumps(dict(GOOD, claims="x <= 1"))).status == FormalizationStatus.INVALID
    other = dict(GOOD, variables=[{"name": "x", "domain": [0, 1]}])
    assert parse_formalization(json.dumps(other), variable_schema=SCHEMA).status == FormalizationStatus.SCHEMA_MISMATCH
    parsed = parse_formalization(json.dumps(GOOD), "H-1", SCHEMA)
    assert parsed.status == FormalizationStatus.PARSED and parsed.hypothesis.hypothesis_id == "H-1"


def test_prompt_is_frozen_and_carries_the_schema():
    messages = build_messages("x stays low", SCHEMA)
    assert '"name": "x"' in messages[1]["content"]
    assert len(prompt_sha256()) == 64


class _FakeClient:
    def __init__(self, output):
        self.output = output

    def complete(self, messages):
        return self.output


def test_end_to_end_with_a_fake_model():
    payload = formalize_and_evaluate("x stays low", _FakeClient(json.dumps(GOOD)), "H-E2E", SCHEMA)
    assert payload["status"] == "PARSED"
    assert payload["evaluation"]["content_verdict"] == "FALSIFIABLE"


def test_gold_formalizations_have_their_intended_verdicts():
    assert formalizer_bench.gold_check(formalizer_bench.load_items()) == []


def test_scorer_on_gold_answers_is_perfect():
    items = formalizer_bench.load_items()
    rows = [formalizer_bench.score_item(i, json.dumps(i["gold"]), True) for i in items]
    summary = formalizer_bench.summarize(rows)
    assert summary["parse_rate"] == 1.0
    assert summary["equivalent_to_gold_rate"] == 1.0
    assert summary["verdict_agreement_with_gold"] == 1.0
    assert summary["spurious_defects"] == 0 and summary["missed_defects"] == 0


def test_scorer_detects_a_translation_that_adds_a_defect():
    item = next(i for i in formalizer_bench.load_items() if i["id"] == "F06")
    tautology = dict(item["gold"], claims=["prey >= 0"])  # Always true given the bounds: unfalsifiable.
    row = formalizer_bench.score_item(item, json.dumps(tautology), True)
    assert row["verdict"] == "UNFALSIFIABLE" and row["spurious_defect"] is True
    assert row["relation_to_gold"] == "WEAKER"
