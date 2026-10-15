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
    hypothesis_from_dict,
)

QUESTIONS = ["Q1", "Q2", "Q3", "Q4"]
# Itemised answers: which labelled premises conflict, which table rows (numbered from 1) refute the hypothesis.
ITEM_QUESTIONS = ["Q2_items", "Q3_items"]
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
        # Q6 (open critique) is a list of critiques; every other answer carries a "value".
        answers = {q: (a if q == "Q6" else a["value"]) for q, a in j.get("answers", {}).items()}
        judgments.setdefault(j["task_id"], {})[j["judge_orcid"]] = answers
    return judgments


def to_hypothesis(spec: dict) -> Hypothesis:
    return hypothesis_from_dict(spec)


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
    labels = formal.get("assumption_labels") or [f"A{i + 1}" for i in range(len(h.assumptions))]
    label_of = dict(zip(h.assumptions, labels))
    conflicts = HypothesisEvaluator.conflicting_assumption_sets(h)
    answers["Q2_items"] = sorted(
        {"SCOPE" if e.startswith("scope: ") else label_of.get(e, e) for group in conflicts for e in group}
    )
    if observations:
        answers["Q3_items"] = sorted(r["observation_index"] + 1 for r in report.certain_counterexamples)
        if report.certain_counterexamples:
            answers["Q3"] = "REFUTED"
        elif report.possible_counterexamples:
            answers["Q3"] = "POSSIBLY_REFUTED"
        else:
            answers["Q3"] = "NOT_REFUTED"
    if formal.get("rival"):
        answers["Q4"] = HypothesisEvaluator.compare(h, to_hypothesis(formal["rival"])).relation.value
    return answers


def validate_task(task: dict) -> list:
    """Preflight checks before a task is sent to judges. Returns a list of problems (empty when valid)."""
    problems = []
    prose, formal = task.get("prose", {}), task.get("formal", {})
    try:
        h = to_hypothesis(formal["hypothesis"])
    except (KeyError, FormalHypothesisError) as exc:
        return [f"formal hypothesis does not build: {exc}"]
    if formal.get("rival"):
        try:
            rival = to_hypothesis(formal["rival"])
            if [(v.name, v.domain) for v in rival.variables] != [(v.name, v.domain) for v in h.variables]:
                problems.append("rival does not share the hypothesis's variables and domains")
        except FormalHypothesisError as exc:
            problems.append(f"formal rival does not build: {exc}")
        if not prose.get("rival_statement"):
            problems.append("formal rival given but prose.rival_statement is missing")
    labels = formal.get("assumption_labels")
    if h.assumptions:
        if labels is None or len(labels) != len(h.assumptions):
            problems.append("assumption_labels must give one label per formal assumption")
        elif set(labels) - set(prose.get("premises", {})):
            problems.append(f"labels {sorted(set(labels) - set(prose.get('premises', {})))} are not prose premises")
    observations = formal.get("observations") or []
    rows = (prose.get("observations_table") or {}).get("rows", [])
    if len(rows) != len(observations):
        problems.append(f"prose table has {len(rows)} rows but formal observations has {len(observations)}")
    else:
        for i, (row, obs) in enumerate(zip(rows, observations), start=1):
            shared = set(row) & set(obs)
            if any(row[k] != obs[k] for k in shared):
                problems.append(f"row {i} differs between the prose table and the formal observation")
    try:
        HypothesisEvaluator.confront(h, observations)
    except FormalHypothesisError as exc:
        problems.append(f"observations invalid: {exc}")
    return problems


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


def _norm(value):
    """Item answers are compared as sets; categorical answers as plain values."""
    return tuple(sorted(value)) if isinstance(value, list) else value


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def gold_labels(judgments: dict, adjudications: dict) -> tuple[dict, list]:
    """Gold per task and question: unanimous judges, else the adjudicator. Unresolved items are listed."""
    gold: dict = {}
    unresolved = []
    for task_id, by_judge in judgments.items():
        for q in QUESTIONS + ITEM_QUESTIONS:
            values = [_norm(a[q]) for a in by_judge.values() if q in a and a[q] != CANNOT_JUDGE]
            if not values:
                continue
            if len(set(values)) == 1 and len(values) >= 2:
                gold.setdefault(task_id, {})[q] = values[0]
            elif q in adjudications.get(task_id, {}):
                gold.setdefault(task_id, {})[q] = adjudications[task_id][q]
            else:
                unresolved.append({"task_id": task_id, "question": q, "answers": values})
    return gold, unresolved


def _arm_vs_gold(answers: dict, gold: dict, proposer: dict, q: str, order) -> dict:
    """Agreement of one sealed arm (CoResearcher or the LLM) with the gold label for a categorical question."""
    rows = [(tid, gold[tid][q], answers[tid][q]) for tid in gold if q in gold[tid] and q in answers.get(tid, {})]

    def kappa_of(rs):
        return cohen_kappa([(a, b) for _, a, b in rs], order)

    return {
        "n": len(rows),
        "raw_agreement": (sum(a == b for _, a, b in rows) / len(rows)) if rows else None,
        "kappa": kappa_of(rows),
        "ci95": clustered_bootstrap(rows, lambda r: proposer[r[0]], kappa_of),
        "confusion_gold_by_arm": confusion([(a, b) for _, a, b in rows]),
        "disagreements": [{"task_id": t, "gold": a, "arm": b} for t, a, b in rows if a != b],
    }


def _llm_order(order):
    # INVALID answers from the LLM arm sit outside the ordered scale; they count as maximal disagreement.
    return None if order is None else order + ["INVALID"]


def score(tasks: dict, sealed: dict, judgments: dict, adjudications: dict, llm: dict | None = None) -> dict:
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
        if llm is not None:
            per_question[q]["llm_gold"] = _arm_vs_gold(llm, gold, proposer, q, _llm_order(order))
    cannot_judge = sum(
        1 for by_judge in judgments.values() for a in by_judge.values() for v in a.values() if v == CANNOT_JUDGE
    )
    per_item_question = {}
    for q in ITEM_QUESTIONS:
        jj = []
        for task_id, by_judge in judgments.items():
            vals = [by_judge[o][q] for o in sorted(by_judge) if q in by_judge[o] and by_judge[o][q] != CANNOT_JUDGE]
            if len(vals) >= 2:
                jj.append((task_id, vals[0], vals[1]))
        cg = [(tid, gold[tid][q], answers[tid][q]) for tid in gold if q in gold[tid] and q in answers.get(tid, {})]

        def mean_jaccard(rows):
            return sum(jaccard(a, b) for _, a, b in rows) / len(rows) if rows else None

        per_item_question[q] = {
            "judge_judge": {
                "n": len(jj),
                "mean_jaccard": mean_jaccard(jj),
                "ci95": clustered_bootstrap(jj, lambda r: proposer[r[0]], mean_jaccard),
            },
            "coresearcher_gold": {
                "n": len(cg),
                "mean_jaccard": mean_jaccard(cg),
                "ci95": clustered_bootstrap(cg, lambda r: proposer[r[0]], mean_jaccard),
                "mismatches": [
                    {"task_id": t, "gold": list(a), "coresearcher": list(b)} for t, a, b in cg if set(a) != set(b)
                ],
            },
        }
        if llm is not None:
            lg = [(tid, gold[tid][q], llm[tid][q]) for tid in gold if q in gold[tid] and q in llm.get(tid, {})]
            lg = [(t, a, b if isinstance(b, (list, tuple)) else []) for t, a, b in lg]  # INVALID scores as empty.
            per_item_question[q]["llm_gold"] = {
                "n": len(lg),
                "mean_jaccard": mean_jaccard(lg),
                "ci95": clustered_bootstrap(lg, lambda r: proposer[r[0]], mean_jaccard),
            }
    open_critiques = [
        {"task_id": tid, "judge_orcid": judge, "critiques": a["Q6"]}
        for tid, by_judge in judgments.items()
        for judge, a in by_judge.items()
        if a.get("Q6")
    ]
    return {
        "per_question": per_question,
        "per_item_question": per_item_question,
        "open_critiques": open_critiques,
        "unresolved_gold": unresolved,
        "cannot_judge_answers": cannot_judge,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["validate", "seal", "score"])
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--sealed", type=Path)
    parser.add_argument("--judgments", type=Path)
    parser.add_argument("--adjudications", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--llm-answers", type=Path)
    parser.add_argument("--llm-sha256")
    args = parser.parse_args(argv)
    tasks = load_tasks(args.tasks)
    if args.step == "validate":
        failed = {tid: probs for tid, t in tasks.items() if (probs := validate_task(t))}
        for tid, probs in failed.items():
            for prob in probs:
                print(f"[FAIL] {tid}: {prob}")
        print(f"{len(tasks)} tasks checked, {len(failed)} with problems.")
        return 1 if failed else 0
    if not args.out:
        parser.error("seal and score need --out")
    if args.step == "seal":
        args.out.write_text(json.dumps(seal(tasks), indent=2, sort_keys=True), encoding="utf-8")
        print(f"Sealed {len(tasks)} tasks. SHA-256: {file_sha256(args.out)}")
        return 0
    if not args.sealed or not args.judgments:
        parser.error("score needs --sealed and --judgments")
    sealed = json.loads(args.sealed.read_text(encoding="utf-8"))
    adjudications = json.loads(args.adjudications.read_text(encoding="utf-8")) if args.adjudications else {}
    llm = None
    if args.llm_answers:
        if not args.llm_sha256 or file_sha256(args.llm_answers) != args.llm_sha256:
            raise SystemExit("LLM arm file does not match the SHA-256 recorded before unblinding.")
        llm_file = json.loads(args.llm_answers.read_text(encoding="utf-8"))
        llm = {tid: {q: _norm(v) for q, v in a.items()} for tid, a in llm_file["llm_answers"].items()}
    result = score(tasks, sealed, load_judgments(args.judgments), adjudications, llm)
    result["sealed_sha256"] = file_sha256(args.sealed)
    if llm is not None:
        result["llm_arm"] = {
            "sha256": args.llm_sha256,
            "model": llm_file.get("model"),
            "prompt_sha256": llm_file.get("prompt_sha256"),
        }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({q: v["coresearcher_gold"]["kappa"] for q, v in result["per_question"].items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
