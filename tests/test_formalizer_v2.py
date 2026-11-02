"""Formalizer v2 (ADR-DISCOVERY-093): surface repair, schema restoration, self-repair round. No network."""

import json

from python.discovery import formalizer as fz

SCHEMA = [
    {"name": "growing", "domain": [True, False]},
    {"name": "R", "continuous": True, "lower": 0, "upper": 20},
]


class FakeClient:
    """Returns scripted outputs in order and records the messages it received."""

    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def complete(self, messages, temperature=0.0, seed=0, json_mode=False):
        self.calls.append({"messages": messages, "json_mode": json_mode})
        return self.outputs.pop(0)


def test_surface_repair_rewrites_notation_only():
    assert fz.repair_predicate("(a == 1) implies (b > 2)") == "not ((a == 1)) or ((b > 2))"
    assert fz.repair_predicate("x && !y || z") == "x and not y or z"
    assert fz.repair_predicate("bleaching == true") == "bleaching"
    assert fz.repair_predicate("flag == False") == "not flag"
    assert fz.repair_predicate("x = 3") == "x == 3"
    assert fz.repair_predicate("ph ≥ 7 and ph ≠ 8") == "ph >= 7 and ph != 8"
    assert fz.repair_predicate("name == 'x' => y") == "not (name == 'x') or (y)"


def test_surface_repair_never_changes_valid_predicates_or_comparisons():
    for expr in ["a != b", "x >= 3", "x <= 3", "x < 3", "not (p) or (q)", "s in ('a', 'b')"]:
        assert fz.repair_predicate(expr) == expr
    assert fz.repair_predicate("p -> q -> s") == "p -> q -> s"  # a chain is ambiguous; left for the validator


def test_schema_domains_restored_only_when_names_match():
    data = {
        "variables": [{"name": "growing", "domain": ["yes", "no"]}, {"name": "R", "continuous": True}],
        "claims": ["not growing or R > 1"],
    }
    assert fz.repair_data(data, SCHEMA)["variables"] == SCHEMA
    renamed = {"variables": [{"name": "grows", "domain": [True, False]}], "claims": ["grows"]}
    assert fz.repair_data(renamed, SCHEMA)["variables"] == renamed["variables"]


def test_v2_parses_after_surface_repair_without_a_second_call():
    out = json.dumps({"variables": SCHEMA, "scope": "", "assumptions": None, "claims": ["growing implies R > 1"]})
    client = FakeClient([out])
    result = fz.formalize_v2("An outbreak grows only if R exceeds 1.", client, "H", SCHEMA)
    assert result.status == fz.FormalizationStatus.PARSED
    assert result.attempts == 1 and len(client.calls) == 1 and client.calls[0]["json_mode"] is True
    assert result.data["claims"] == ["not (growing) or (R > 1)"]
    assert "claims" in result.repaired_fields


def test_v2_self_repair_round_sends_the_validator_error_back_once():
    bad = json.dumps({"variables": SCHEMA, "claims": ["growing or unknown_var > 1"]})
    good = json.dumps({"variables": SCHEMA, "claims": ["not growing or R > 1"]})
    client = FakeClient([bad, good])
    result = fz.formalize_v2("An outbreak grows only if R exceeds 1.", client, "H", SCHEMA)
    assert result.status == fz.FormalizationStatus.PARSED and result.attempts == 2
    feedback = client.calls[1]["messages"][-1]["content"]
    assert feedback.startswith("The validator rejected that output:")


def test_v2_gives_up_after_one_self_repair_and_reports_the_failure():
    bad = json.dumps({"variables": SCHEMA, "claims": ["growing or unknown_var > 1"]})
    client = FakeClient([bad, bad])
    result = fz.formalize_v2("x", client, "H", SCHEMA)
    assert result.status == fz.FormalizationStatus.INVALID and result.attempts == 2
    assert len(client.calls) == 2


def test_v2_prompt_is_fingerprinted_and_v1_is_unchanged():
    assert fz.PROMPT_VERSION == "formalizer-v1" and fz.PROMPT_VERSION_V2 == "formalizer-v2"
    assert len(fz.prompt_sha256_v2()) == 64 and fz.prompt_sha256_v2() != fz.prompt_sha256()
    messages = fz.build_messages_v2("p", SCHEMA)
    assert messages[0]["content"] == fz.SYSTEM_PROMPT_V2
    assert len(messages) == 2 + 2 * len(fz.FEW_SHOT_V2)
    # Worked examples never reuse benchmark prose.
    bench = json.load(open("docs/reference/benchmarks/formalizer_dataset.json", encoding="utf-8"))["items"]
    held = json.load(open("docs/reference/benchmarks/formalizer_dataset_heldout_v2.json", encoding="utf-8"))["items"]
    proses = {i["prose"] for i in bench + held}
    assert not any(e["prose"] in proses for e in fz.FEW_SHOT_V2)


def test_few_shot_answers_are_valid_formal_objects():
    from python.discovery.formal_hypothesis import hypothesis_from_dict

    for example in fz.FEW_SHOT_V2:
        hypothesis_from_dict({**example["answer"], "hypothesis_id": "example"})
