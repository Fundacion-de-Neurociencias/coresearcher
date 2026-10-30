"""
scripts/cases/openai_math_coverage_report.py - Builds the corpus-wide claim-vs-formal coverage map of openai/math.

    python scripts/cases/openai_math_coverage_report.py --fetch <empty dir>     # sparse, blobless fetch at the pin
    python scripts/cases/openai_math_coverage_report.py --corpus <dir>          # build the map from that checkout

The fetch reads only CONTENTS.md, overview.tex, lean/docs/, lean/formalization.yaml and lean/ComparatorChallenges/
at `SOURCE_COMMIT` (a blobless clone with core.longpaths=true, so it works on Windows). The corpus is data: nothing in
it is built or executed. Families are processed in batches and each batch is written to disk before the next one;
z3 queries run one at a time with the solver timeout of `formal_thresholds`.

Input committed here: examples/openai-math-coverage/judgements.json (reading judgements, one per headline claim of
a family with a Lean scope note, each tagged [inferred]). Outputs: coverage_map.json (dataset and summary) and
lint_open.json (OPEN junk-value findings of every Comparator target).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from python.discovery import openai_math_coverage as cov  # noqa: E402

OUT = ROOT / "examples" / "openai-math-coverage"
SPARSE = ["/CONTENTS.md", "/overview.tex", "/lean/docs/", "/lean/formalization.yaml", "/lean/ComparatorChallenges/"]
BATCH = 50


def fetch(target: Path) -> None:
    target = Path(target)
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"{target} is not empty")
    git = ["git", "-c", "core.longpaths=true"]
    subprocess.run(
        git + ["clone", "--filter=blob:none", "--no-checkout", "--sparse", cov.SOURCE_REPOSITORY, str(target)],
        check=True,
    )
    subprocess.run(git + ["-C", str(target), "sparse-checkout", "set", "--no-cone", *SPARSE], check=True)
    subprocess.run(git + ["-C", str(target), "checkout", "--quiet", cov.SOURCE_COMMIT], check=True)


def corpus_commit(root: Path) -> str:
    """HEAD of the checkout, or "unknown" for a plain extract (then the file hashes are the pin)."""
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    head = result.stdout.strip()
    return head if result.returncode == 0 and Path(root, ".git").exists() else "unknown"


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def build(root: Path) -> None:
    started = time.time()
    commit = corpus_commit(root)
    if commit not in ("unknown", cov.SOURCE_COMMIT):
        raise SystemExit(f"checkout is at {commit}, expected {cov.SOURCE_COMMIT}")
    corpus = cov.load_corpus(root)
    judgements = {j["claim_id"]: j for j in json.loads((OUT / "judgements.json").read_text(encoding="utf-8"))}
    specs = cov.hand_specs()
    family_ids = sorted(corpus.families)
    partial = OUT / "partial"
    partial.mkdir(exist_ok=True)
    rows, families = [], []
    for start in range(0, len(family_ids), BATCH):
        batch_rows, batch_families = [], []
        for fid in family_ids[start : start + BATCH]:
            record = cov.family_record(corpus, fid)
            for claim in record["claims"]:
                batch_rows.append(cov.classify_claim(record, claim, judgements.get(claim["claim_id"]), specs))
            keys = ("family_id", "title", "discipline", "lean_doc", "summary_overview_similarity", "comparator_rows",
                    "yaml_main_results")
            batch_families.append({k: record[k] for k in keys})
        write(partial / f"rows_{start:03d}.json", batch_rows)
        rows += batch_rows
        families += batch_families
        print(f"families {start + 1}-{start + len(batch_families)}: {len(batch_rows)} claims", flush=True)

    file_to_families = {}
    for family in families:
        for row in family["comparator_rows"]:
            file_to_families.setdefault(row["file"], set()).add(family["family_id"])
    lint_files = []
    for name in sorted(corpus.targets):
        config = corpus.configs.get(cov.config_for(name, corpus.configs), {})
        source = (Path(root) / "lean" / "ComparatorChallenges" / name).read_text(encoding="utf-8")
        entry = cov.lint_comparator_file(source, name, config.get("theorem_names", []))
        for finding in entry["open"]:
            finding["families"] = sorted(file_to_families.get(name, []))
        lint_files.append(entry)
    open_findings = [f for entry in lint_files for f in entry["open"]]
    lint_summary = {
        "files": len(lint_files),
        "targets": sum(e["targets"] for e in lint_files),
        "findings": sum(e["findings"] for e in lint_files),
        "open": len(open_findings),
        "targets_with_open": len({(f["file"], f["theorem"]) for f in open_findings}),
        "open_by_kind": dict(sorted(Counter(f["kind"] for f in open_findings).items())),
    }
    write(OUT / "lint_open.json", {"source_commit": cov.SOURCE_COMMIT, **lint_summary, "open_findings": open_findings})

    summary = cov.summarise(rows)
    summary["lint"] = lint_summary
    dataset = {
        "source": {
            "repository": cov.SOURCE_REPOSITORY,
            "commit": cov.SOURCE_COMMIT,
            "checkout_head": commit,
            "files_read": len(corpus.hashes),
            "sha256": {k: corpus.hashes[k] for k in ("CONTENTS.md", "overview.tex", "lean/formalization.yaml")},
            "sha256_of_all_file_hashes": cov.sha256(json.dumps(corpus.hashes, sort_keys=True).encode()),
        },
        "statuses": cov.STATUS_ORDER,
        "summary": summary,
        "calibration_paper_items": cov.paper_item_calibration(),
        "families": families,
        "claims": rows,
    }
    write(OUT / "coverage_map.json", dataset)
    for f in partial.glob("rows_*.json"):
        f.unlink()
    partial.rmdir()
    print(f"{len(rows)} claims, {len(families)} families, {len(open_findings)} OPEN lint findings, "
          f"{time.time() - started:.0f} s")
    print("overall shares:", summary["overall"]["shares"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fetch", type=Path, help="empty directory for a sparse, blobless clone at the pin")
    parser.add_argument("--corpus", type=Path, help="openai/math checkout or extract to read")
    args = parser.parse_args()
    if args.fetch:
        fetch(args.fetch)
    if args.corpus or args.fetch:
        build(args.corpus or args.fetch)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
