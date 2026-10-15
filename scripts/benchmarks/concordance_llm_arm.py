"""Third arm of the concordance benchmark: a local language model (Laya or similar) judging from the prose arm.

Protocol: docs/reference/benchmarks/CONCORDANCE_BENCH_PROTOCOL.md, section 7a.

The model sees exactly what the scientists see (statement, context, premises, observation table, rival) and answers
the same questions. Its answers are sealed before unblinding, like CoResearcher's:

    python scripts/benchmarks/concordance_llm_arm.py run --tasks TASK_DIR --out LLM_ANSWERS.json

The command prints the SHA-256 of the output; record it in the ledger before any judgment is opened. The scorer
then takes `--llm-answers LLM_ANSWERS.json --llm-sha256 <hash>` and refuses a file whose hash differs.

Needs FORMALIZER_BASE_URL / FORMALIZER_MODEL (or --base-url / --model) pointing at an OpenAI-compatible endpoint.
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from concordance_score import load_tasks  # noqa: E402

from python.discovery.formalizer import ChatClient, extract_json  # noqa: E402

PROMPT_VERSION = "concordance-llm-arm-v1"
INVALID = "INVALID"  # A missing or out-of-range answer. Scored as a disagreement, never dropped.

ANSWER_SETS = {
    "Q1": ["VACUOUS", "SELF_CONTRADICTORY", "UNFALSIFIABLE", "FALSIFIABLE", "CANNOT_JUDGE"],
    "Q2": ["COMPATIBLE", "CONFLICTING", "CANNOT_JUDGE"],
    "Q3": ["REFUTED", "POSSIBLY_REFUTED", "NOT_REFUTED", "CANNOT_JUDGE"],
    "Q4": ["EQUIVALENT", "STRONGER", "WEAKER", "INCOMPARABLE", "CONTRADICTORY", "CANNOT_JUDGE"],
}

SYSTEM_PROMPT = """You are a careful scientist judging the logical form of a hypothesis. Judge only what is written. \
Do not use outside knowledge about whether the hypothesis is true.

Definitions:
- Q1: VACUOUS if no situation satisfies the hypothesis's conditions; SELF_CONTRADICTORY if every situation where it \
applies violates it; UNFALSIFIABLE if no possible observation could violate it; otherwise FALSIFIABLE.
- Q2: are the premises compatible with each other (COMPATIBLE) or can they not all hold at once (CONFLICTING)? \
Q2_items: labels of the premises in a minimal conflicting set, empty list if none.
- Q3: do the observations refute the hypothesis? REFUTED if some row is certainly incompatible with it, \
POSSIBLY_REFUTED if some row is incompatible under some value of what the row does not report, otherwise \
NOT_REFUTED. Q3_items: row numbers (from 1) that certainly refute it.
- Q4: compare the hypothesis H with the rival R by the situations each one forbids. EQUIVALENT if they forbid the \
same; STRONGER if H forbids everything R forbids and more; WEAKER if the reverse; CONTRADICTORY if no situation is \
allowed by both; otherwise INCOMPARABLE.
You may answer CANNOT_JUDGE.

Answer with one JSON object only, with the keys you are asked for, each mapping to {"value": ..., "confidence": 1-5, \
"rationale": "one sentence"}."""


def prompt_sha256() -> str:
    return hashlib.sha256((PROMPT_VERSION + SYSTEM_PROMPT).encode("utf-8")).hexdigest()


def questions_for(task: dict) -> list:
    prose = task["prose"]
    questions = ["Q1", "Q2", "Q2_items"]
    if prose.get("observations_table", {}).get("rows"):
        questions += ["Q3", "Q3_items"]
    if prose.get("rival_statement"):
        questions.append("Q4")
    return questions


def user_prompt(task: dict) -> str:
    """Only the prose arm. Nothing from the formal arm or the proposer's expected answers is included."""
    prose = task["prose"]
    parts = [f"Field: {prose['field']}", f"Hypothesis H: {prose['statement']}", f"Context: {prose['context']}"]
    if prose.get("premises"):
        parts.append("Premises:\n" + "\n".join(f"  {k}: {v}" for k, v in prose["premises"].items()))
    table = prose.get("observations_table")
    if table and table.get("rows"):
        cols = "\n".join(f"  {k}: {v}" for k, v in table["columns"].items())
        rows = "\n".join(f"  row {i}: {json.dumps(r, ensure_ascii=False)}" for i, r in enumerate(table["rows"], 1))
        parts.append(f"Observation table columns:\n{cols}\nRows:\n{rows}")
    if prose.get("rival_statement"):
        parts.append(f"Rival R: {prose['rival_statement']}")
    parts.append("Answer these keys: " + ", ".join(questions_for(task)))
    return "\n\n".join(parts)


def parse_answers(text: str, task: dict) -> dict:
    """Validated answers; anything missing or outside the answer set becomes INVALID."""
    data = extract_json(text) or {}
    answers = {}
    for q in questions_for(task):
        raw = data.get(q)
        value = raw.get("value") if isinstance(raw, dict) else raw
        if q in ANSWER_SETS:
            answers[q] = value if value in ANSWER_SETS[q] else INVALID
        elif value == "CANNOT_JUDGE":
            answers[q] = value
        elif isinstance(value, list) and all(isinstance(x, (str, int)) for x in value):
            answers[q] = (
                sorted(int(x) for x in value)
                if q == "Q3_items" and all(str(x).isdigit() for x in value)
                else sorted(str(x) for x in value)
            )
        else:
            answers[q] = INVALID
    return answers


def run(tasks: dict, client) -> dict:
    out = {
        "arm": "llm",
        "model": getattr(client, "model", "unknown"),
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": prompt_sha256(),
        "llm_answers": {},
        "raw_outputs": {},
    }
    for task_id, task in tasks.items():
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt(task)}]
        try:
            text = client.complete(messages)
        except Exception as exc:  # Recorded, not retried: a retry after seeing outputs would bias the arm.
            text = f"TRANSPORT_ERROR {type(exc).__name__}"
        out["raw_outputs"][task_id] = text
        out["llm_answers"][task_id] = parse_answers(text, task)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--tasks", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--model")
    r.add_argument("--base-url")
    args = parser.parse_args(argv)
    tasks = load_tasks(Path(args.tasks))
    result = run(tasks, ChatClient(base_url=args.base_url, model=args.model))
    result["sealed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    path = Path(args.out)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"Sealed LLM arm: {path}  SHA-256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    print("Record this hash in the ledger before opening any judgment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
