"""Scorer for the Hypothesis Verification Concordance Benchmark.

Protocol: docs/reference/benchmarks/CONCORDANCE_BENCH_PROTOCOL.md

Two steps, in this order:

    # 1. Before any judgment is opened: run CoResearcher on the tasks and seal its answers.
    python scripts/benchmarks/concordance_score.py seal --tasks TASK_DIR --out SEALED.json

    # 2. After all judgments are submitted: score agreement.
    python scripts/benchmarks/concordance_score.py score --tasks TASK_DIR --sealed SEALED.json \
        --judgments JUDGMENT_DIR [--adjudications ADJ.json] --out RESULTS.json

`seal` prints the SHA-256 of the sealed file; record it in the ledger before unblinding. `score` refuses to run if
the sealed file no longer matches the answers CoResearcher gives today, so the CoResearcher arm cannot be changed
after the judgments are seen.
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.formal_hypothesis import (  # noqa: E402
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    Variable,
)

QUESTIONS = ["Q1", "Q2", "Q3", "Q4"]
Q3_ORDER = ["NOT_REFUTED", "POSSIBLY_REFUTED", "REFUTED"]  # ordered: Q3 uses linear weighted kappa
CANNOT_JUDGE = "CANNOT_JUDGE"
NON_INFERIORITY_MARGIN = 0.10
BOOT_RESAMPLES = 2000
BOOT_SEED = 20261015


# ---------------------------------------------------------------- loading


def load_tasks(task_dir: Path) -> dict:
    tasks = {}
    for path in sorted(task_dir.glob("*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        for key in ("task_id", "proposer_orcid", "prose", "formal"):
            if key not in task:
                raise ValueError(f"{path.name}: missing '{key}'")
        if task["task_id"] in tasks:
            raise ValueError(f"Duplicate task_id {task['task_id']}")
        tasks[task["task_id"]] = task
    return tasks


def load_judgments(judgment_dir: Path) -> dict:
    """Returns {task_id: {judge_orcid: {question: value}}}."""
    judgments: dict = {}
    for path in sorted(judgment_dir.glob("*.json")):
        j = json.loads(path.read_text(encoding="utf-8"))
        answers = {q: a["value"] for q, a in j.get("answers", {}).items()}
        judgments.setdefault(j["task_id"], {})[j["judge_orcid"]] = answers
    return judgments


def to_hypothesis(spec: dict) -> Hypothesis:
    return Hypothesis(
        hypothesis_id=spec["hypothesis_id"],
        variables=[Variable(v["name"], tuple(v["domain"])) for v in spec["variables"]],
        claims=spec["claims"],
        assumptions=spec.get("assumptions", []),
        scope=spec.get("scope"),
        statement=spec.get("statement", ""),
    )


# ---------------------------------------------------------------- CoResearcher arm


def coresearcher_answers(task: dict) -> dict:
    formal = task["formal"]
    h = to_hypothesis(formal["hypothesis"])
    observations = formal.get("observations") or []
    report = HypothesisEvaluator.evaluate(h, observations)
    answers = {
        "Q1": report.content_verdict.value,
        "Q2": "CONFLICTING" if HypothesisEvaluator.conflicting_assumption_sets(h) else "COMPATIBLE",
    }
    if observations:
        if report.certain_counterexamples:
            answers["Q3"] = "REFUTED"
        elif report.possible_counterexamples:
            answers["Q3"] = "POSSIBLY_REFUTED"
        else:
            answers["Q3"] = "NOT_REFUTED"
    if formal.get("rival"):
        answers["Q4"] = HypothesisEvaluator.compare(h, to_hypothesis(formal["rival"])).relation.value
    return answers


def seal(tasks: dict) -> dict:
    answers = {}
    for task_id, task in tasks.items():
        try:
            answers[task_id] = coresearcher_answers(task)
        except FormalHypothesisError as exc:
            answers[task_id] = {"error": str(exc)}
    return {"coresearcher_answers": answers}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- statistics


def cohen_kappa(pairs: list, weighted_order: list | None = None) -> float | None:
    """Cohen's kappa for (rater_a, rater_b) label pairs; linear weights when an order is given.

    Returns None when the expected agreement is 1 (both raters always use the same single label).
    """
    if not pairs:
        return None
    labels = sorted({x for p in pairs for x in p}) if weighted_order is None else weighted_order
    index = {label: i for i, label in enumerate(labels)}
    k, n = len(labels), len(pairs)

    def weight(i: int, j: int) -> float:
        if weighted_order is None:
            return 1.0 if i == j else 0.0
        return 1.0 - abs(i - j) / (k - 1) if k > 1 else 1.0

    observed = sum(weight(index[a], index[b]) for a, b in pairs) / n
    pa = [sum(1 for a, _ in pairs if index[a] == i) / n for i in range(k)]
    pb = [sum(1 for _, b in pairs if index[b] == j) / n for j in range(k)]
    expected = sum(weight(i, j) * pa[i] * pb[j] for i in range(k) for j in range(k))
    if abs(1.0 - expected) < 1e-12:
        return None
    return (observed - expected) / (1.0 - expected)


def clustered_bootstrap(items: list, cluster_of, statistic, seed: int = BOOT_SEED) -> list | None:
    """95% percentile interval, resampling clusters (proposers) with replacement."""
    clusters: dict = {}
    for item in items:
        clusters.setdefault(cluster_of(item), []).append(item)
    keys = sorted(clusters)
    if not keys:
        return None
    rng = random.Random(seed)
    values = []
    for _ in range(BOOT_RESAMPLES):
        sample = [item for key in rng.choices(keys, k=len(keys)) for item in clusters[key]]
        value = statistic(sample)
        if value is not None:
            values.append(value)
    if not values:
        return None
    values.sort()
    return [values[int(0.025 * (len(values) - 1))], values[int(0.975 * (len(values) - 1))]]


def confusion(pairs: list) -> dict:
    table: dict = {}
    for gold, predicted in pairs:
        table.setdefault(gold, {}).setdefault(predicted, 0)
        table[gold][predicted] += 1
    return table


# ---------------------------------------------------------------- scoring


def gold_labels(judgments: dict, adjudications: dict) -> tuple[dict, list]:
    """Gold per task and question: unanimous judges, else the adjudicator. Unresolved items are listed."""
    gold: dict = {}
    unresolved = []
    for task_id, by_judge in judgments.items():
        for q in QUESTIONS:
            values = [a[q] for a in by_judge.values() if q in a and a[q] != CANNOT_JUDGE]
            if not values:
                continue
            if len(set(values)) == 1 and len(values) >= 2:
                gold.setdefault(task_id, {})[q] = values[0]
            elif q in adjudications.get(task_id, {}):
                gold.setdefault(task_id, {})[q] = adjudications[task_id][q]
            else:
                unresolved.append({"task_id": task_id, "question": q, "answers": values})
    return gold, unresolved


def score(tasks: dict, sealed: dict, judgments: dict, adjudications: dict) -> dict:
    current = seal(tasks)["coresearcher_answers"]
    if current != sealed["coresearcher_answers"]:
        raise SystemExit("Sealed CoResearcher answers differ from a fresh run; the CoResearcher arm changed.")
    answers = sealed["coresearcher_answers"]
    gold, unresolved = gold_labels(judgments, adjudications)
    proposer = {tid: t["proposer_orcid"] for tid, t in tasks.items()}

    per_question = {}
    for q in QUESTIONS:
        order = Q3_ORDER if q == "Q3" else None
        # Judge-judge: the first two judges (sorted by ORCID) who both answered.
        jj = []
        for task_id, by_judge in judgments.items():
            vals = [by_judge[o][q] for o in sorted(by_judge) if q in by_judge[o] and by_judge[o][q] != CANNOT_JUDGE]
            if len(vals) >= 2:
                jj.append((task_id, vals[0], vals[1]))
        # CoResearcher vs gold.
        cg = [(tid, gold[tid][q], answers[tid][q]) for tid in gold if q in gold[tid] and q in answers.get(tid, {})]

        def kappa_of(rows):
            return cohen_kappa([(a, b) for _, a, b in rows], order)

        jj_kappa = kappa_of(jj)
        cg_kappa = kappa_of(cg)
        cg_ci = clustered_bootstrap(cg, lambda r: proposer[r[0]], kappa_of)
        per_question[q] = {
            "judge_judge": {
                "n": len(jj),
                "kappa": jj_kappa,
                "ci95": clustered_bootstrap(jj, lambda r: proposer[r[0]], kappa_of),
            },
            "coresearcher_gold": {
                "n": len(cg),
                "raw_agreement": (sum(a == b for _, a, b in cg) / len(cg)) if cg else None,
                "kappa": cg_kappa,
                "ci95": cg_ci,
                "confusion_gold_by_coresearcher": confusion([(a, b) for _, a, b in cg]),
                "disagreements": [{"task_id": t, "gold": a, "coresearcher": b} for t, a, b in cg if a != b],
            },
            "non_inferior": (
                None if jj_kappa is None or cg_ci is None else cg_ci[0] >= jj_kappa - NON_INFERIORITY_MARGIN
            ),
        }
    cannot_judge = sum(
        1 for by_judge in judgments.values() for a in by_judge.values() for v in a.values() if v == CANNOT_JUDGE
    )
    return {"per_question": per_question, "unresolved_gold": unresolved, "cannot_judge_answers": cannot_judge}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["seal", "score"])
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--sealed", type=Path)
    parser.add_argument("--judgments", type=Path)
    parser.add_argument("--adjudications", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    tasks = load_tasks(args.tasks)
    if args.step == "seal":
        args.out.write_text(json.dumps(seal(tasks), indent=2, sort_keys=True), encoding="utf-8")
        print(f"Sealed {len(tasks)} tasks. SHA-256: {file_sha256(args.out)}")
        return 0
    if not args.sealed or not args.judgments:
        parser.error("score needs --sealed and --judgments")
    sealed = json.loads(args.sealed.read_text(encoding="utf-8"))
    adjudications = json.loads(args.adjudications.read_text(encoding="utf-8")) if args.adjudications else {}
    result = score(tasks, sealed, load_judgments(args.judgments), adjudications)
    result["sealed_sha256"] = file_sha256(args.sealed)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({q: v["coresearcher_gold"]["kappa"] for q, v in result["per_question"].items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
