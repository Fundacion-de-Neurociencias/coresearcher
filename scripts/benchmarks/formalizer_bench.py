"""Formalizer benchmark: how faithfully a local model turns prose hypotheses into formal objects.

Protocol: docs/reference/benchmarks/FORMALIZER_BENCH_PROTOCOL.md

Steps:

    # 0. Check the gold formalizations against their intended verdicts (no model needed).
    python scripts/benchmarks/formalizer_bench.py gold-check

    # 1. Query the model (on the Legion; needs FORMALIZER_BASE_URL and FORMALIZER_MODEL).
    python scripts/benchmarks/formalizer_bench.py run --out runs/formalizer_<model>.jsonl [--no-schema]

    # 2. Score the saved outputs (offline, deterministic).
    python scripts/benchmarks/formalizer_bench.py score --responses runs/formalizer_<model>.jsonl \
        --out docs/reference/benchmarks/FORMALIZER_BENCH_REPORT_<model>.md

`run` stores the raw output of every item, so scoring can be repeated and audited without calling the model again.
"""

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.formal_hypothesis import (  # noqa: E402
    ContentVerdict,
    FormalHypothesisError,
    HypothesisEvaluator,
    Relation,
    hypothesis_from_dict,
)
from python.discovery.formalizer import (  # noqa: E402
    PROMPT_VERSION,
    ChatClient,
    FormalizationStatus,
    build_messages,
    parse_formalization,
    prompt_sha256,
)

DATASET = ROOT / "docs" / "reference" / "benchmarks" / "formalizer_dataset.json"
DEFECTS = {ContentVerdict.VACUOUS.value, ContentVerdict.UNFALSIFIABLE.value, ContentVerdict.SELF_CONTRADICTORY.value}


def load_items(path: Path = DATASET) -> list:
    return json.loads(path.read_text(encoding="utf-8"))["items"]


def gold_hypothesis(item: dict):
    return hypothesis_from_dict({**item["gold"], "hypothesis_id": f"{item['id']}-gold"})


def gold_check(items: list) -> list:
    """Items whose gold formalization does not have the verdict the dataset says it should."""
    problems = []
    for item in items:
        verdict = HypothesisEvaluator.evaluate(gold_hypothesis(item)).content_verdict.value
        if verdict != item["intended_verdict"]:
            problems.append(f"{item['id']}: gold verdict {verdict}, intended {item['intended_verdict']}")
    return problems


def score_item(item: dict, raw_output: str, with_schema: bool) -> dict:
    schema = item["gold"]["variables"] if with_schema else None
    result = parse_formalization(raw_output, f"{item['id']}-model", schema)
    row = {"id": item["id"], "status": result.status.value, "error": result.error}
    gold = gold_hypothesis(item)
    gold_verdict = HypothesisEvaluator.evaluate(gold).content_verdict.value
    row["gold_verdict"] = gold_verdict
    if result.hypothesis is None:
        return row
    try:
        verdict = HypothesisEvaluator.evaluate(result.hypothesis).content_verdict.value
    except FormalHypothesisError as exc:
        row.update(status=FormalizationStatus.INVALID.value, error=str(exc))
        return row
    row["verdict"] = verdict
    row["verdict_matches_gold"] = verdict == gold_verdict
    row["spurious_defect"] = verdict in DEFECTS and gold_verdict not in DEFECTS
    row["missed_defect"] = gold_verdict in DEFECTS and verdict != gold_verdict
    if result.status == FormalizationStatus.PARSED:
        try:
            row["relation_to_gold"] = HypothesisEvaluator.compare(result.hypothesis, gold).relation.value
        except FormalHypothesisError as exc:
            row["relation_to_gold"] = f"NOT_COMPARABLE: {exc}"
    return row


def summarize(rows: list) -> dict:
    n = len(rows)
    status = Counter(r["status"] for r in rows)
    evaluated = [r for r in rows if "verdict" in r]
    verdicts = Counter(r["verdict"] for r in evaluated)
    comparable = [r for r in rows if r.get("relation_to_gold", "").split(":")[0] in {x.value for x in Relation}]

    def rate(k, d):
        return round(k / d, 4) if d else None

    return {
        "items": n,
        "parse_rate": rate(status[FormalizationStatus.PARSED.value], n),
        "status_counts": dict(status),
        "evaluated": len(evaluated),
        "verdict_counts": dict(verdicts),
        "vacuous_rate": rate(verdicts[ContentVerdict.VACUOUS.value], len(evaluated)),
        "unfalsifiable_rate": rate(verdicts[ContentVerdict.UNFALSIFIABLE.value], len(evaluated)),
        "self_contradictory_rate": rate(verdicts[ContentVerdict.SELF_CONTRADICTORY.value], len(evaluated)),
        "verdict_agreement_with_gold": rate(sum(r["verdict_matches_gold"] for r in evaluated), len(evaluated)),
        "spurious_defects": sum(r["spurious_defect"] for r in evaluated),
        "missed_defects": sum(r["missed_defect"] for r in evaluated),
        "equivalent_to_gold_rate": rate(sum(r["relation_to_gold"] == "EQUIVALENT" for r in comparable), n),
    }


def report_markdown(meta: dict, summary: dict, rows: list) -> str:
    lines = [
        f"# Formalizer benchmark report: {meta.get('model', 'unknown model')}",
        "",
        "Generated by `scripts/benchmarks/formalizer_bench.py score`. Protocol: "
        "[FORMALIZER_BENCH_PROTOCOL.md](FORMALIZER_BENCH_PROTOCOL.md).",
        "",
        f"- Prompt: `{meta.get('prompt_version')}`, SHA-256 `{meta.get('prompt_sha256')}`",
        f"- Variable schema given to the model: {meta.get('with_schema')}",
        f"- Dataset: `{meta.get('dataset_sha256')}`",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "| Item | Status | Verdict | Gold verdict | Relation to gold | Error |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        error = (r.get("error") or "").replace("|", "\\|")[:120]
        lines.append(
            f"| {r['id']} | {r['status']} | {r.get('verdict', '')} | {r['gold_verdict']} | "
            f"{r.get('relation_to_gold', '')} | {error} |"
        )
    return "\n".join(lines) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_run(args) -> None:
    client = ChatClient(base_url=args.base_url, model=args.model)
    items = load_items(Path(args.dataset))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "kind": "meta",
        "model": client.model,
        "base_url_host": client.base_url.split("//")[-1].split("/")[0],
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": prompt_sha256(),
        "dataset_sha256": sha256_file(Path(args.dataset)),
        "with_schema": not args.no_schema,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    with out.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(meta) + "\n")
        for item in items:
            schema = None if args.no_schema else item["gold"]["variables"]
            t0 = time.time()
            try:
                output, error = client.complete(build_messages(item["prose"], schema)), ""
            except Exception as exc:  # A transport failure is recorded as an empty output, not retried silently.
                output, error = "", f"{type(exc).__name__}: {exc}"
            fh.write(
                json.dumps(
                    {
                        "id": item["id"],
                        "output": output,
                        "transport_error": error,
                        "seconds": round(time.time() - t0, 2),
                    }
                )
                + "\n"
            )
            print(f"{item['id']}: {len(output)} chars{' ERROR ' + error if error else ''}")
    print(f"Wrote {out}")


def cmd_score(args) -> None:
    items = {i["id"]: i for i in load_items(Path(args.dataset))}
    lines = [json.loads(line) for line in Path(args.responses).read_text(encoding="utf-8").splitlines() if line]
    meta = next((x for x in lines if x.get("kind") == "meta"), {})
    responses = {x["id"]: x["output"] for x in lines if x.get("kind") != "meta"}
    with_schema = meta.get("with_schema", True)
    rows = [score_item(item, responses.get(item_id, ""), with_schema) for item_id, item in items.items()]
    summary = summarize(rows)
    print(json.dumps(summary, indent=2))
    if args.out:
        Path(args.out).write_text(report_markdown(meta, summary, rows), encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", default=str(DATASET))
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("gold-check")
    run = sub.add_parser("run")
    run.add_argument("--out", required=True)
    run.add_argument("--model")
    run.add_argument("--base-url")
    run.add_argument("--no-schema", action="store_true")
    score = sub.add_parser("score")
    score.add_argument("--responses", required=True)
    score.add_argument("--out")
    args = parser.parse_args(argv)
    if args.cmd == "gold-check":
        problems = gold_check(load_items(Path(args.dataset)))
        print("\n".join(problems) or f"All gold formalizations have their intended verdict. Prompt {prompt_sha256()}")
        return 1 if problems else 0
    {"run": cmd_run, "score": cmd_score}[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
