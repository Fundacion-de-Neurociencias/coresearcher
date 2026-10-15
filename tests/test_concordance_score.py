"""Tests for the concordance benchmark scorer (docs/reference/benchmarks/CONCORDANCE_BENCH_PROTOCOL.md)."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("concordance_score", ROOT / "scripts/benchmarks/concordance_score.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

EXAMPLE = ROOT / "docs/reference/benchmarks/concordance_example_task.json"
X = [{"name": "x", "domain": [0, 1, 2, 3]}]


def _task(task_id, claims, proposer="0000-0000-0000-0001"):
    return {
        "task_id": task_id,
        "proposer_orcid": proposer,
        "licence": "CC-BY-4.0",
        "confidential": False,
        "prose": {"field": "test", "statement": "A test hypothesis statement.", "context": "none"},
        "formal": {"hypothesis": {"hypothesis_id": task_id, "variables": X, "claims": claims}},
    }


def _judgment(task_id, judge, q1):
    return {"task_id": task_id, "judge_orcid": judge, "answers": {"Q1": {"value": q1}}}


def test_example_task_matches_hand_computed_answers():
    task = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert cs.coresearcher_answers(task) == task["formal"]["proposer_expected"]


def test_kappa_textbook_value():
    pairs = [("y", "y")] * 20 + [("y", "n")] * 5 + [("n", "y")] * 10 + [("n", "n")] * 15
    assert cs.cohen_kappa(pairs) == pytest.approx(0.4)


def test_kappa_perfect_and_undefined():
    assert cs.cohen_kappa([("a", "a"), ("b", "b")]) == pytest.approx(1.0)
    assert cs.cohen_kappa([("a", "a"), ("a", "a")]) is None  # one label only: kappa undefined


def test_weighted_kappa_credits_near_misses():
    order = cs.Q3_ORDER
    near = [("NOT_REFUTED", "NOT_REFUTED"), ("REFUTED", "REFUTED"), ("POSSIBLY_REFUTED", "REFUTED")]
    far = [("NOT_REFUTED", "NOT_REFUTED"), ("REFUTED", "REFUTED"), ("NOT_REFUTED", "REFUTED")]
    assert cs.cohen_kappa(near, order) > cs.cohen_kappa(far, order)


def _setup(tmp_path):
    tasks_dir, judg_dir = tmp_path / "tasks", tmp_path / "judgments"
    tasks_dir.mkdir()
    judg_dir.mkdir()
    tasks = [
        _task("T1", ["x <= 1"]),  # FALSIFIABLE
        _task("T2", ["x >= 0"], proposer="0000-0000-0000-0002"),  # UNFALSIFIABLE
        _task("T3", ["x == 1", "x == 2"], proposer="0000-0000-0000-0003"),  # SELF_CONTRADICTORY
    ]
    for t in tasks:
        (tasks_dir / f"{t['task_id']}.json").write_text(json.dumps(t), encoding="utf-8")
    judgments = [
        _judgment("T1", "1111-1111-1111-1111", "FALSIFIABLE"),
        _judgment("T1", "2222-2222-2222-2222", "FALSIFIABLE"),
        _judgment("T2", "1111-1111-1111-1111", "FALSIFIABLE"),  # judges agree, CoResearcher differs
        _judgment("T2", "2222-2222-2222-2222", "FALSIFIABLE"),
        _judgment("T3", "1111-1111-1111-1111", "SELF_CONTRADICTORY"),  # judges disagree: needs adjudication
        _judgment("T3", "2222-2222-2222-2222", "VACUOUS"),
    ]
    for i, j in enumerate(judgments):
        (judg_dir / f"j{i}.json").write_text(json.dumps(j), encoding="utf-8")
    return tasks_dir, judg_dir


def test_score_gold_disagreements_and_adjudication(tmp_path):
    tasks_dir, judg_dir = _setup(tmp_path)
    tasks = cs.load_tasks(tasks_dir)
    sealed = cs.seal(tasks)
    judgments = cs.load_judgments(judg_dir)

    without_adj = cs.score(tasks, sealed, judgments, {})
    assert without_adj["unresolved_gold"][0]["task_id"] == "T3"
    q1 = without_adj["per_question"]["Q1"]["coresearcher_gold"]
    assert q1["n"] == 2 and q1["raw_agreement"] == pytest.approx(0.5)
    assert q1["disagreements"] == [{"task_id": "T2", "gold": "FALSIFIABLE", "coresearcher": "UNFALSIFIABLE"}]

    with_adj = cs.score(tasks, sealed, judgments, {"T3": {"Q1": "SELF_CONTRADICTORY"}})
    assert with_adj["unresolved_gold"] == []
    assert with_adj["per_question"]["Q1"]["coresearcher_gold"]["n"] == 3


def test_score_refuses_a_changed_coresearcher_arm(tmp_path):
    tasks_dir, judg_dir = _setup(tmp_path)
    tasks = cs.load_tasks(tasks_dir)
    tampered = copy.deepcopy(cs.seal(tasks))
    tampered["coresearcher_answers"]["T2"]["Q1"] = "FALSIFIABLE"
    with pytest.raises(SystemExit):
        cs.score(tasks, tampered, cs.load_judgments(judg_dir), {})


def test_itemised_premise_agreement_uses_jaccard(tmp_path):
    tasks_dir, judg_dir = tmp_path / "tasks", tmp_path / "judgments"
    tasks_dir.mkdir()
    judg_dir.mkdir()
    task = _task("C1", ["x == 1"])
    task["formal"]["hypothesis"]["assumptions"] = ["x > 2", "x < 1", "x >= 0"]
    task["formal"]["assumption_labels"] = ["P1", "P2", "P3"]
    (tasks_dir / "C1.json").write_text(json.dumps(task), encoding="utf-8")
    for i, judge in enumerate(["1111-1111-1111-1111", "2222-2222-2222-2222"]):
        j = {"task_id": "C1", "judge_orcid": judge, "answers": {"Q2_items": {"value": ["P1"]}}}
        (judg_dir / f"j{i}.json").write_text(json.dumps(j), encoding="utf-8")

    tasks = cs.load_tasks(tasks_dir)
    sealed = cs.seal(tasks)
    assert sealed["coresearcher_answers"]["C1"]["Q2_items"] == ["P1", "P2"]  # P3 is not part of the conflict

    result = cs.score(tasks, sealed, cs.load_judgments(judg_dir), {})
    items = result["per_item_question"]["Q2_items"]["coresearcher_gold"]
    assert items["mean_jaccard"] == pytest.approx(0.5)  # {P1} vs {P1, P2}
    assert items["mismatches"] == [{"task_id": "C1", "gold": ["P1"], "coresearcher": ["P1", "P2"]}]


def test_preflight_accepts_the_example_task():
    assert cs.validate_task(json.loads(EXAMPLE.read_text(encoding="utf-8"))) == []


def test_preflight_catches_label_and_table_mismatches():
    task = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    broken = copy.deepcopy(task)
    broken["formal"]["assumption_labels"] = ["P1"]  # two assumptions, one label
    assert any("assumption_labels" in p for p in cs.validate_task(broken))

    broken = copy.deepcopy(task)
    broken["prose"]["observations_table"]["rows"][1]["decline"] = "slow"  # judges would see different data
    assert any("row 2 differs" in p for p in cs.validate_task(broken))


def test_open_critiques_are_collected(tmp_path):
    tasks_dir, judg_dir = _setup(tmp_path)
    critique = {"task_id": "T1", "judge_orcid": "3333-3333-3333-3333", "answers": {"Q6": [{"text": "Scope too broad"}]}}
    (judg_dir / "critique.json").write_text(json.dumps(critique), encoding="utf-8")
    tasks = cs.load_tasks(tasks_dir)
    result = cs.score(tasks, cs.seal(tasks), cs.load_judgments(judg_dir), {"T3": {"Q1": "SELF_CONTRADICTORY"}})
    assert result["open_critiques"] == [
        {"task_id": "T1", "judge_orcid": "3333-3333-3333-3333", "critiques": [{"text": "Scope too broad"}]}
    ]
