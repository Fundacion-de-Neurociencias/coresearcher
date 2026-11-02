"""AI-expert concordance round 1: CoResearcher (formal arm) against AI judges reading only the prose.

The owner decided on 2026-11-01 that the expert arm is Claude Science, a desktop application no tool here can drive.
So the prose arm travels as one self-contained text that the owner pastes into Claude Science once, and its JSON
answer comes back as a file. A second judge from another model family (a local Ollama model) answers the same tasks
through the existing LLM arm, to dilute same-family circularity. Results are reported as AI-expert concordance,
never as human validation.

    python scripts/benchmarks/concordance_ai_round.py build     # write the 20 tasks
    python scripts/benchmarks/concordance_ai_round.py pack      # write the Claude Science text, print SHA-256s
    python scripts/benchmarks/concordance_ai_round.py seal      # CoResearcher's answers, sealed before any judge runs
    python scripts/benchmarks/concordance_ai_round.py ingest --raw CLAUDE_SCIENCE_REPLY.txt
    python scripts/benchmarks/concordance_ai_round.py compare   # agreement per question, disagreements listed

Tasks are built from the formalizer benchmark sets, whose gold formal objects were checked against their intended
verdicts (formalizer_bench.py gold-check). Premises, observation rows and rivals are added here: rows come from the
evaluator's own witnesses, and rivals are hand-written variants with their formal object.
"""

import argparse
import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from concordance_llm_arm import SYSTEM_PROMPT, parse_answers, prompt_sha256, questions_for, user_prompt  # noqa: E402
from concordance_score import coresearcher_answers, load_tasks, validate_task  # noqa: E402

from python.discovery.formal_hypothesis import HypothesisEvaluator, hypothesis_from_dict  # noqa: E402

ROUND = ROOT / "docs" / "reference" / "benchmarks" / "concordance_ai_round1"
TASKS = ROUND / "tasks"
BENCH = ROOT / "docs" / "reference" / "benchmarks"
SOURCES = {"main": BENCH / "formalizer_dataset.json", "heldout": BENCH / "formalizer_dataset_heldout_v2.json"}
SELECTION = ["H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08", "H09", "H10", "H11", "H12",
             "F01", "F03", "F04", "F05", "F08", "F10", "F12", "F20"]
PACK_VERSION = "claude-science-pack-v1"
SEED = 20261102

# Hand-written rivals: (prose, claims, scope or None). Same variables and domains as the hypothesis.
RIVALS = {
    "H01": ("A patient is eligible for the drug only if eGFR is above 45 mL/min.", ["not eligible or egfr > 45"], None),
    "H02": ("Whenever rainfall falls below 300 mm, the wetland dries out.", ["rain >= 300 or dry"], None),
    "H03": ("An older patient's drug clearance is strictly lower than a younger patient's.", ["cl_old < cl_young"],
            None),
    "H04": ("In adults, resting heart rate stays at or below 100 beats per minute.", ["hr <= 100"], "age >= 18"),
    "H09": ("Whenever wind speed exceeds 20 km/h, a forest fire spreads.", ["wind <= 20 or spreads"], None),
    "H10": ("In soils where pH is below 5, aluminium toxicity is at most 1 unit.", ["tox <= 1"], "ph < 5"),
    "H11": ("In treated patients, the infection rate is at most the untreated rate.",
            ["treated_rate <= untreated_rate"], None),
    "H12": ("A neuron fires whenever its membrane potential exceeds -55 mV.", ["v <= -55 or fires"], None),
}


def _items() -> dict:
    out = {}
    for path in SOURCES.values():
        for item in json.loads(path.read_text(encoding="utf-8"))["items"]:
            out[item["id"]] = item
    return out


def _grid(var: dict) -> list:
    if var.get("domain") is not None:
        return list(var["domain"])
    lo = var.get("lower") if var.get("lower") is not None else -100
    hi = var.get("upper") if var.get("upper") is not None else 100
    return sorted({lo, hi, (lo + hi) / 2, lo + (hi - lo) / 4, lo + 3 * (hi - lo) / 4, 0 if lo <= 0 <= hi else lo,
                   1 if lo <= 1 <= hi else hi})


def _rows(gold: dict, hid: str) -> list:
    """Up to two observation rows from the evaluator: one allowed state and one certain counterexample."""
    h = hypothesis_from_dict({**gold, "hypothesis_id": hid})
    names = [v["name"] for v in gold["variables"]]
    allowed = violating = None
    for values in itertools.product(*[_grid(v) for v in gold["variables"]]):
        state = dict(zip(names, values))
        if not h.applies(state):
            continue
        if h.violated_claims(state):
            violating = violating or state
        else:
            allowed = allowed or state
        if allowed and violating:
            break
    return [r for r in (allowed, violating) if r]


def _fmt(value):
    return value if not isinstance(value, float) or not value.is_integer() else int(value)


def build() -> list:
    items = _items()
    TASKS.mkdir(parents=True, exist_ok=True)
    written = []
    for n, item_id in enumerate(SELECTION, start=1):
        item, gold = items[item_id], items[item_id]["gold"]
        task_id = f"AIR1-{n:02d}"
        labels = [f"P{i + 1}" for i in range(len(gold.get("assumptions") or []))]
        hyp = {**gold, "hypothesis_id": f"{task_id}-H"}
        rows = [{k: _fmt(v) for k, v in r.items()} for r in _rows(gold, task_id)]
        # Row order and presence vary by a fixed seed, so "row 2 refutes" is not a pattern a judge can learn.
        rng = random.Random(f"{SEED}-{task_id}")
        if len(rows) == 2 and rng.random() < 0.35:
            rows = rows[:1]  # the allowed state only: the expected answer is NOT_REFUTED
        rng.shuffle(rows)
        columns = {v["name"]: (f"one of {v['domain']}" if v.get("domain") is not None else
                               f"real number in [{v.get('lower')}, {v.get('upper')}]") for v in gold["variables"]}
        prose = {
            "field": item.get("domain", ""),
            "statement": item["prose"],
            "context": "Variables and their ranges are listed with the observation table. Judge only what is written.",
            "premises": {lab: f"It is taken as given that {a}." for lab, a in zip(labels, gold.get("assumptions") or [])},
            "observations_table": {"columns": columns, "rows": rows, "provenance": "illustrative"},
        }
        formal = {"hypothesis": hyp, "observations": rows, "assumption_labels": labels}
        if item_id in RIVALS:
            text, claims, scope = RIVALS[item_id]
            prose["rival_statement"] = text
            formal["rival"] = {"hypothesis_id": f"{task_id}-R", "variables": gold["variables"], "scope": scope,
                               "assumptions": [], "claims": claims}
        task = {"task_id": task_id, "source_item": item_id, "proposer_orcid": "0000-0000-0000-0000",
                "licence": "CC-BY-4.0", "confidential": False, "prose": prose, "formal": formal}
        problems = validate_task(task)
        if problems:
            raise SystemExit(f"{task_id} ({item_id}) invalid: {problems}")
        (TASKS / f"{task_id}.json").write_text(json.dumps(task, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(task_id)
    return written


PACK_HEADER = """You are taking part in a blinded study of how well hypotheses are judged from their wording alone.
Below are {n} independent tasks. Treat each one separately, judge only what is written, and do not use outside
knowledge about whether a hypothesis is true.

{system}

Return ONE JSON object and nothing else. Its keys are the task ids. Each value is an object with exactly the keys
listed under "Answer these keys" for that task, each mapping to {{"value": ..., "confidence": 1-5,
"rationale": "one sentence"}}. Premise labels are strings such as "P1"; row numbers are integers starting at 1.
"""


def pack() -> Path:
    tasks = load_tasks(TASKS)
    blocks = [f"=== Task {tid} ===\n{user_prompt(task)}" for tid, task in sorted(tasks.items())]
    text = PACK_HEADER.format(n=len(tasks), system=SYSTEM_PROMPT) + "\n" + "\n\n".join(blocks) + "\n"
    out = ROUND / "claude_science_prompt.txt"
    out.write_text(text, encoding="utf-8", newline="\n")
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def seal() -> Path:
    tasks = load_tasks(TASKS)
    answers = {tid: coresearcher_answers(task) for tid, task in sorted(tasks.items())}
    out = ROUND / "coresearcher_answers.json"
    out.write_text(json.dumps({"arm": "coresearcher", "answers": answers}, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    return out


def ingest(raw: Path) -> Path:
    """Claude Science's reply (pasted text) -> validated answers per task; anything malformed is INVALID."""
    from python.discovery.formalizer import extract_json

    tasks = load_tasks(TASKS)
    text = raw.read_text(encoding="utf-8")
    data = extract_json(text) or {}
    answers = {tid: parse_answers(json.dumps(data.get(tid, {})), task) for tid, task in sorted(tasks.items())}
    out = ROUND / "claude_science_answers.json"
    out.write_text(json.dumps({"arm": "claude_science", "pack_version": PACK_VERSION, "prompt_sha256": prompt_sha256(),
                               "raw_sha256": sha256(raw), "answers": answers}, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    return out


def _kappa(pairs: list) -> float | None:
    from concordance_score import cohen_kappa

    return cohen_kappa(pairs)


def compare(arms: dict) -> dict:
    """Pairwise agreement per question between the formal arm and each judge, with every disagreement listed."""
    tasks = load_tasks(TASKS)
    base = arms["coresearcher"]
    report = {"note": "AI-expert concordance; not human validation.", "pairs": {}}
    for name, answers in arms.items():
        if name == "coresearcher":
            continue
        per_q, disagreements = {}, []
        for q in ["Q1", "Q2", "Q2_items", "Q3", "Q3_items", "Q4"]:
            pairs = [(base[t][q], answers[t].get(q, "MISSING")) for t in sorted(tasks) if q in base[t]]
            pairs = [(json.dumps(a), json.dumps(b)) for a, b in pairs]
            if not pairs:
                continue
            agree = sum(a == b for a, b in pairs)
            per_q[q] = {"n": len(pairs), "agree": agree, "kappa": None if q.endswith("_items") else _kappa(pairs)}
            disagreements += [{"task": t, "question": q, "coresearcher": base[t][q], name: answers[t].get(q)}
                              for t in sorted(tasks) if q in base[t] and base[t][q] != answers[t].get(q)]
        report["pairs"][name] = {"per_question": per_q, "disagreements": disagreements}
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    sub.add_parser("pack")
    sub.add_parser("seal")
    i = sub.add_parser("ingest")
    i.add_argument("--raw", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--llm-answers", help="Answers file from concordance_llm_arm.py run (second model family)")
    c.add_argument("--out", default=str(ROUND / "concordance_report.json"))
    args = parser.parse_args(argv)
    if args.cmd == "build":
        print("\n".join(build()))
    elif args.cmd == "pack":
        out = pack()
        print(f"{out}\nsha256 {sha256(out)}")
    elif args.cmd == "seal":
        out = seal()
        print(f"{out}\nsha256 {sha256(out)}")
    elif args.cmd == "ingest":
        out = ingest(Path(args.raw))
        print(f"{out}\nsha256 {sha256(out)}")
    elif args.cmd == "compare":
        arms = {"coresearcher": json.loads((ROUND / "coresearcher_answers.json").read_text(encoding="utf-8"))["answers"]}
        cs = ROUND / "claude_science_answers.json"
        if cs.exists():
            arms["claude_science"] = json.loads(cs.read_text(encoding="utf-8"))["answers"]
        if args.llm_answers:
            arms["local_llm"] = json.loads(Path(args.llm_answers).read_text(encoding="utf-8"))["llm_answers"]
        report = compare(arms)
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({k: v["per_question"] for k, v in report["pairs"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
