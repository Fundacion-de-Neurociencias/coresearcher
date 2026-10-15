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

    # 3. Self-consistency gate ablation (ADR-DISCOVERY-063): draw N samples per item, then gate them offline.
    python scripts/benchmarks/formalizer_bench.py run --samples 5 --out runs/formalizer_<model>_n5.jsonl
    python scripts/benchmarks/formalizer_bench.py gate --responses runs/a_n5.jsonl runs/b_n5.jsonl --n 1 3 5 \
        --out docs/reference/benchmarks/FORMALIZER_GATE_REPORT.md --json runs/gate_ablation.json

`run` stores the raw output of every item, so scoring can be repeated and audited without calling the model again.
Sample 0 of every item uses the frozen decoding (temperature 0, seed 0); samples 1.. use `--temperature` and seeds
1, 2, ... `score` reads sample 0 only, so it scores exactly the ungated formalizer.
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
from python.discovery.formalization_gate import SampleSpec, gate, sampling_schedule  # noqa: E402
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
    client = ChatClient(base_url=args.base_url, model=args.model, timeout=args.timeout)
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
    meta.update(samples=args.samples, temperature=args.temperature)
    kept = {}
    if args.resume and out.exists():
        # Only samples lost to the connection (endpoint unreachable) are drawn again; a model timeout or any other
        # failure stays recorded as the model's output, as in an uninterrupted run.
        previous = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
        meta = {**next(x for x in previous if x.get("kind") == "meta"), "resumed": time.strftime("%Y-%m-%dT%H:%M:%S")}
        kept = {
            (x["id"], x.get("sample", 0)): x
            for x in previous
            if x.get("kind") != "meta" and not x.get("transport_error", "").startswith("ConnectError")
        }
    with out.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(meta) + "\n")
        for item in items:
            schema = None if args.no_schema else item["gold"]["variables"]
            messages = build_messages(item["prose"], schema)
            for k in range(args.samples):
                if (item["id"], k) in kept:
                    fh.write(json.dumps(kept[(item["id"], k)]) + "\n")
                    continue
                temperature = 0.0 if k == 0 else args.temperature
                t0 = time.time()
                try:
                    output, error = client.complete(messages, temperature=temperature, seed=k), ""
                except Exception as exc:  # A transport failure is recorded as an empty output, not retried silently.
                    output, error = "", f"{type(exc).__name__}: {exc}"
                fh.write(
                    json.dumps(
                        {
                            "id": item["id"],
                            "sample": k,
                            "temperature": temperature,
                            "seed": k,
                            "output": output,
                            "transport_error": error,
                            "seconds": round(time.time() - t0, 2),
                        }
                    )
                    + "\n"
                )
                fh.flush()
                print(f"{item['id']}#{k}: {len(output)} chars{' ERROR ' + error if error else ''}", flush=True)
    print(f"Wrote {out}")


def cmd_score(args) -> None:
    items = {i["id"]: i for i in load_items(Path(args.dataset))}
    lines = [json.loads(line) for line in Path(args.responses).read_text(encoding="utf-8").splitlines() if line]
    meta = next((x for x in lines if x.get("kind") == "meta"), {})
    responses = {x["id"]: x["output"] for x in lines if x.get("kind") != "meta" and x.get("sample", 0) == 0}
    with_schema = meta.get("with_schema", True)
    rows = [score_item(item, responses.get(item_id, ""), with_schema) for item_id, item in items.items()]
    summary = summarize(rows)
    print(json.dumps(summary, indent=2))
    if args.out:
        Path(args.out).write_text(report_markdown(meta, summary, rows), encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


def load_samples(path: Path):
    """Meta and {item id: {sample index: raw output}} from a run file."""
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    meta = next((x for x in lines if x.get("kind") == "meta"), {})
    samples: dict = {}
    for x in lines:
        if x.get("kind") != "meta":
            samples.setdefault(x["id"], {})[x.get("sample", 0)] = x["output"]
    return meta, samples


def gate_item(item: dict, outputs: list, specs: list, with_schema: bool) -> dict:
    """Gates the raw outputs drawn for one item and scores the accepted one against the gold."""
    schema = item["gold"]["variables"] if with_schema else None
    parsed = [parse_formalization(text, f"{item['id']}-s{i}", schema) for i, text in enumerate(outputs)]
    result = gate(parsed, specs)
    row = {
        "id": item["id"],
        "gate_status": result.status.value,
        "passes": result.passes,
        "agreement": result.agreement,
        "classes": [len(c) for c in result.classes],
        "baseline_equivalent": score_item(item, outputs[0], with_schema).get("relation_to_gold") == "EQUIVALENT",
    }
    if result.passes:
        scored = score_item(item, outputs[result.accepted], with_schema)
        row.update(
            accepted_sample=result.accepted,
            equivalent=scored.get("relation_to_gold") == "EQUIVALENT",
            relation_to_gold=scored.get("relation_to_gold"),
            verdict_matches_gold=scored.get("verdict_matches_gold"),
            spurious_defect=scored.get("spurious_defect"),
        )
    return row


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from the discordant pair counts."""
    from math import comb

    n = b + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, k) for k in range(0, min(b, c) + 1)) / 2**n
    return round(min(1.0, 2 * tail), 4)


def gate_summary(rows: list) -> dict:
    n = len(rows)
    accepted = [r for r in rows if r["passes"]]
    status = Counter(r["gate_status"] for r in rows)
    wrong_baseline = [r for r in rows if not r["baseline_equivalent"]]
    right_baseline = [r for r in rows if r["baseline_equivalent"]]

    def rate(k, d):
        return round(k / d, 4) if d else None

    return {
        "items": n,
        "accepted": len(accepted),
        "coverage": rate(len(accepted), n),
        "ambiguous_rate": rate(status["FORMALIZATION_AMBIGUOUS"], n),
        "failed_rate": rate(status["FORMALIZATION_FAILED"], n),
        "status_counts": dict(status),
        "equivalent_among_accepted": rate(sum(r["equivalent"] for r in accepted), len(accepted)),
        "equivalent_over_all_items": rate(sum(r["equivalent"] for r in accepted), n),
        "false_acceptances": sum(not r["equivalent"] for r in accepted),
        "verdict_agreement_among_accepted": rate(sum(bool(r["verdict_matches_gold"]) for r in accepted), len(accepted)),
        "spurious_defects_among_accepted": sum(bool(r["spurious_defect"]) for r in accepted),
        "baseline_errors_blocked": rate(sum(not r["passes"] for r in wrong_baseline), len(wrong_baseline)),
        "baseline_correct_blocked": rate(sum(not r["passes"] for r in right_baseline), len(right_baseline)),
        "mean_agreement": rate(sum(r["agreement"] for r in rows), n),
    }


def gate_conditions(runs: list, ns: list) -> list:
    """(label, [(run name, sample index), ...]) for each model alone and, with two or more runs, mixed."""
    conditions = []
    for n in ns:
        for name in runs:
            conditions.append((f"{name} N={n}", [(name, k) for k in range(n)]))
        if len(runs) > 1 and n > 1:
            conditions.append((f"mixed N={n}", [(spec.model, spec.seed) for spec in sampling_schedule(runs, n)]))
    return conditions


def _false_acceptance(row: dict) -> bool:
    return row["passes"] and not row["equivalent"]


def cmd_gate(args) -> None:
    items = load_items(Path(args.dataset))
    runs, metas = {}, {}
    for path in args.responses:
        meta, samples = load_samples(Path(path))
        name = meta.get("model", Path(path).stem)
        runs[name], metas[name] = samples, meta
    results = []
    for label, picks in gate_conditions(list(runs), args.n):
        specs = [SampleSpec(name, 0.0 if k == 0 else metas[name].get("temperature", 0.7), k) for name, k in picks]
        with_schema = all(metas[name].get("with_schema", True) for name, _ in picks)
        rows = []
        for item in items:
            outputs = [runs[name].get(item["id"], {}).get(k) for name, k in picks]
            if any(o is None for o in outputs):
                raise SystemExit(f"{label}: the run file lacks a sample for {item['id']}; draw more samples.")
            rows.append(gate_item(item, outputs, specs, with_schema))
        results.append({"condition": label, "summary": gate_summary(rows), "rows": rows})
        print(f"{label}: {json.dumps(results[-1]['summary'])}")
    baselines = {r["condition"].rsplit(" N=", 1)[0]: r for r in results if r["condition"].endswith(" N=1")}
    if runs and list(runs)[0] in baselines:  # Mixed sample 0 is the first model's frozen sample.
        baselines["mixed"] = baselines[list(runs)[0]]
    for r in results:
        base = baselines.get(r["condition"].rsplit(" N=", 1)[0])
        if base is None or base is r:
            continue
        # Paired on items: which false acceptances of the ungated formalizer the gate removes, and which it adds.
        pairs = list(zip(base["rows"], r["rows"]))
        fixed = sum(_false_acceptance(x) and not _false_acceptance(y) for x, y in pairs)
        introduced = sum(not _false_acceptance(x) and _false_acceptance(y) for x, y in pairs)
        r["summary"]["false_acceptance_mcnemar_vs_n1"] = {
            "fixed": fixed,
            "introduced": introduced,
            "p": mcnemar_exact(fixed, introduced),
        }
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps({"metas": metas, "results": results}, indent=2), encoding="utf-8")
    if args.out:
        Path(args.out).write_text(gate_report_markdown(metas, results), encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


GATE_KEYS = [
    "coverage",
    "ambiguous_rate",
    "failed_rate",
    "equivalent_among_accepted",
    "equivalent_over_all_items",
    "false_acceptances",
    "spurious_defects_among_accepted",
    "baseline_errors_blocked",
    "baseline_correct_blocked",
    "mean_agreement",
]


def gate_report_markdown(metas: dict, results: list) -> str:
    lines = [
        "# Formalizer self-consistency gate: ablation",
        "",
        "Generated by `scripts/benchmarks/formalizer_bench.py gate` (ADR-DISCOVERY-063).",
        "",
    ]
    for name, meta in metas.items():
        lines.append(
            f"- `{name}`: prompt `{meta.get('prompt_version')}` (`{meta.get('prompt_sha256', '')[:12]}`), "
            f"dataset `{meta.get('dataset_sha256', '')[:12]}`, {meta.get('samples', 1)} samples per item, "
            f"temperature {meta.get('temperature')} after sample 0, schema given: {meta.get('with_schema')}"
        )
    lines += ["", "| Condition | " + " | ".join(GATE_KEYS) + " | False acceptances vs N=1 (fixed/introduced, p) |"]
    lines.append("| --- " * (len(GATE_KEYS) + 2) + "|")
    for r in results:
        s = r["summary"]
        m = s.get("false_acceptance_mcnemar_vs_n1")
        mc = f"{m['fixed']}/{m['introduced']}, p={m['p']}" if m else ""
        lines.append(f"| {r['condition']} | " + " | ".join(str(s[k]) for k in GATE_KEYS) + f" | {mc} |")
    lines += ["", "## Per item", ""]
    for r in results:
        lines += [f"### {r['condition']}", "", "| Item | Gate | Class sizes | Accepted sample | Relation to gold |"]
        lines.append("| --- " * 5 + "|")
        for x in r["rows"]:
            lines.append(
                f"| {x['id']} | {x['gate_status']} | {x['classes']} | {x.get('accepted_sample', '')} | "
                f"{x.get('relation_to_gold', '')} |"
            )
        lines.append("")
    return "\n".join(lines)


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
    run.add_argument("--samples", type=int, default=1, help="Samples per item (ADR-063 gate); sample 0 is frozen.")
    run.add_argument("--temperature", type=float, default=0.7, help="Decoding temperature for samples 1, 2, ...")
    run.add_argument("--timeout", type=float, default=300.0)
    run.add_argument("--resume", action="store_true", help="Redraw only samples lost to connection errors.")
    score = sub.add_parser("score")
    score.add_argument("--responses", required=True)
    score.add_argument("--out")
    gate_cmd = sub.add_parser("gate")
    gate_cmd.add_argument("--responses", nargs="+", required=True)
    gate_cmd.add_argument("--n", nargs="+", type=int, default=[1, 3, 5])
    gate_cmd.add_argument("--out")
    gate_cmd.add_argument("--json")
    args = parser.parse_args(argv)
    if args.cmd == "gold-check":
        problems = gold_check(load_items(Path(args.dataset)))
        print("\n".join(problems) or f"All gold formalizations have their intended verdict. Prompt {prompt_sha256()}")
        return 1 if problems else 0
    {"run": cmd_run, "score": cmd_score, "gate": cmd_gate}[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
