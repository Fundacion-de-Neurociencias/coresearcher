"""
scripts/cases/trivial_witness_probe_report.py - Trivial-witness / vacuity probe over every openai/math Comparator target.

    python scripts/cases/trivial_witness_probe_report.py static  --corpus <openai/math checkout or extract>
    python scripts/cases/trivial_witness_probe_report.py prepare --math-root <openai/math checkout with lean built>
    python scripts/cases/trivial_witness_probe_report.py run     --math-root <...> [--only ClassicalON] [--timeout 600]
    python scripts/cases/trivial_witness_probe_report.py report  --math-root <...>

`static` needs no Lean: it runs stage 1 (z3 consistency of the explicit hypotheses) and writes
examples/openai-math-coverage/vacuity_probe.json with every Lean probe marked NOT_RUN. `prepare` writes the stage 2
and 3 probe files under lean/ComparatorChallenges/Probes/ of a checkout at the pinned commit; `run` elaborates them one
at a time with `lake env lean` (resumable: finished probes are skipped); `report` folds the outcomes into the JSON.
`run` needs the openai/math Lean project built (Linux; see docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from python.discovery import openai_math_coverage as cov  # noqa: E402
from python.discovery import trivial_witness_probe as probe  # noqa: E402

OUT = ROOT / "examples" / "openai-math-coverage" / "vacuity_probe.json"
PROBE_DIR = "ComparatorChallenges/Probes"


def _targets(math_root: Path):
    """(challenge path, source, theorem names) for every Comparator config."""
    comparator = Path(math_root) / "lean" / "ComparatorChallenges"
    for config_path in sorted(comparator.glob("**/*.json")):
        if PROBE_DIR in config_path.as_posix():
            continue
        config = json.loads(config_path.read_text(encoding="utf-8"))
        module = config.get("challenge_module", "").removeprefix("ComparatorChallenges.").replace(".", "/") + ".lean"
        path = comparator / module
        if path.exists():
            yield module, path.read_text(encoding="utf-8"), config.get("theorem_names", [])


def _all_probes(math_root: Path):
    probes = []
    for challenge, source, names in _targets(math_root):
        probes += probe.cheap_tactic_probes(source, challenge, names)
        for case in probe.CASES:
            if case.challenge == challenge:
                probes += probe.degenerate_probe_files(case, source)
    return probes


def static(corpus: Path) -> None:
    rows = []
    for challenge, source, names in _targets(corpus):
        for name in names:
            statement = probe.expanded_statement(source, name.split(".")[-1])
            rows.append({"challenge": challenge, "theorem": name, **probe.arithmetic_check(statement)})
    probes = _all_probes(corpus)
    data = {
        "source_commit": cov.SOURCE_COMMIT,
        "tactic_menu": probe.TACTIC_MENU,
        "max_heartbeats": probe.HEARTBEATS,
        "stage1_arithmetic": {"summary": dict(Counter(r["verdict"] for r in rows)), "targets": rows},
        "lean_probes": {
            "summary": {"NOT_RUN": len(probes)},
            # Targets whose `theorem ... sorry` text was not located (attributes, indentation): no stage 2 probe.
            "targets_without_probe": sorted(
                {r["theorem"] for r in rows} - {p.theorem for p in probes if p.mode == "trivial"}
            ),
            "probes": [
                {"probe_id": p.probe_id, "theorem": p.theorem, "mode": p.mode, "module_path": p.module_path,
                 "outcome": probe.LeanOutcome.NOT_RUN.value}
                for p in probes
            ],
        },
        "degenerate_cases": [
            {k: v for k, v in asdict(c).items() if k != "lemmas"} | {"lemmas": list(c.lemmas)} for c in probe.CASES
        ],
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"stage 1: {data['stage1_arithmetic']['summary']}; {len(probes)} Lean probes prepared (NOT_RUN)")


def prepare(math_root: Path) -> None:
    head = subprocess.run(["git", "-C", str(math_root), "rev-parse", "HEAD"], capture_output=True, text=True)
    if head.stdout.strip() != cov.SOURCE_COMMIT:
        raise SystemExit(f"{math_root} is at {head.stdout.strip() or '?'}, expected {cov.SOURCE_COMMIT}")
    lean = Path(math_root) / "lean"
    probes = _all_probes(math_root)
    for p in probes:
        target = lean / p.module_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(p.text, encoding="utf-8")
    manifest = [{k: v for k, v in asdict(p).items() if k != "text"} for p in probes]
    (lean / PROBE_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"wrote {len(probes)} probe files under {lean / PROBE_DIR}")


def run(math_root: Path, only: str, timeout: int) -> None:
    lean = Path(math_root) / "lean"
    manifest = json.loads((lean / PROBE_DIR / "manifest.json").read_text(encoding="utf-8"))
    results_path = lean / PROBE_DIR / "results.jsonl"
    done = set()
    if results_path.exists():
        done = {json.loads(line)["probe_id"] for line in results_path.read_text(encoding="utf-8").splitlines() if line}
    for entry in manifest:
        if entry["probe_id"] in done or (only and only not in entry["probe_id"]):
            continue
        started = time.time()
        try:
            proc = subprocess.run(["lake", "env", "lean", entry["module_path"]], cwd=lean, capture_output=True,
                                  text=True, timeout=timeout)
            output = proc.stdout + proc.stderr
            outcome = probe.parse_lean_output(output, entry["declaration"]).value
        except subprocess.TimeoutExpired:
            output, outcome = "", "TIMEOUT"
        record = {"probe_id": entry["probe_id"], "outcome": outcome, "seconds": round(time.time() - started, 1),
                  "output_tail": output[-2000:]}
        with results_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{entry['probe_id']}: {outcome} ({record['seconds']} s)", flush=True)


def report(math_root: Path) -> None:
    results_path = Path(math_root) / "lean" / PROBE_DIR / "results.jsonl"
    results = {}
    for line in results_path.read_text(encoding="utf-8").splitlines():
        if line:
            record = json.loads(line)
            results[record["probe_id"]] = record
    data = json.loads(OUT.read_text(encoding="utf-8"))
    for row in data["lean_probes"]["probes"]:
        if row["probe_id"] in results:
            row["outcome"] = results[row["probe_id"]]["outcome"]
            row["seconds"] = results[row["probe_id"]]["seconds"]
            row["output_tail"] = results[row["probe_id"]]["output_tail"][-600:]
    data["lean_probes"]["summary"] = dict(Counter(r["outcome"] for r in data["lean_probes"]["probes"]))
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(data["lean_probes"]["summary"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["static", "prepare", "run", "report"])
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--math-root", type=Path)
    parser.add_argument("--only", default="")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    if args.command == "static":
        static(args.corpus or args.math_root)
    elif args.command == "prepare":
        prepare(args.math_root)
    elif args.command == "run":
        run(args.math_root, args.only, args.timeout)
    else:
        report(args.math_root)


if __name__ == "__main__":
    main()
