"""AI-expert concordance round 1: table ingestion and arm comparison work offline on the committed files."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import concordance_ai_round as car  # noqa: E402

ROUND = ROOT / "docs" / "reference" / "benchmarks" / "concordance_ai_round1"


def test_committed_tasks_are_valid_and_twenty():
    tasks = car.load_tasks(car.TASKS)
    assert len(tasks) == 20
    assert all(not car.validate_task(t) for t in tasks.values())


def test_sealed_answers_reproduce_from_the_tasks():
    sealed = json.loads((ROUND / "coresearcher_answers.json").read_text(encoding="utf-8"))["answers"]
    tasks = car.load_tasks(car.TASKS)
    assert {tid: car.coresearcher_answers(t) for tid, t in tasks.items()} == sealed


def test_table_reply_ingests_without_invalid_values(tmp_path, monkeypatch):
    monkeypatch.setattr(car, "ROUND", tmp_path)
    out = car.ingest_table(ROUND / "claude_science_reply.md")
    answers = json.loads(out.read_text(encoding="utf-8"))["answers"]
    assert len(answers) == 20 and "INVALID" not in json.dumps(answers)
    assert answers["AIR1-05"]["Q2_items"] == ["P1", "P2"]


def test_comparison_lists_every_disagreement():
    base = {"T1": {"Q1": "FALSIFIABLE", "Q4": "WEAKER"}}
    judge = {"T1": {"Q1": "FALSIFIABLE", "Q4": "STRONGER"}}
    original = car.load_tasks
    try:
        car.load_tasks = lambda _: {"T1": {}}
        report = car.compare({"coresearcher": base, "judge": judge})
    finally:
        car.load_tasks = original
    pair = report["pairs"]["judge"]
    assert pair["per_question"]["Q1"]["agree"] == 1 and pair["per_question"]["Q4"]["agree"] == 0
    assert pair["disagreements"] == [{"task": "T1", "question": "Q4", "coresearcher": "WEAKER", "judge": "STRONGER"}]
