"""Recomputes the Local smoothing proof-anatomy case (python/discovery/local_smoothing_anatomy.py).

python scripts/cases/local_smoothing_anatomy_report.py --out examples/local-smoothing-anatomy/anatomy_report.json

Also writes dag.mmd (Mermaid) next to the report.
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.local_smoothing_anatomy import anatomy_report, mermaid  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "examples" / "local-smoothing-anatomy" / "anatomy_report.json"
    )
    args = parser.parse_args()
    start = time.time()
    report = anatomy_report()
    report["seconds"] = round(time.time() - start, 1)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.out.parent / "dag.mmd").write_text(mermaid() + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s")
    dag = report["dag"]
    print(
        f"DAG: {dag['internal_nodes']} results, {dag['imported_leaves']} imported leaves, acyclic={dag['is_acyclic']}, "
        f"missing premises={len(dag['missing_premises'])}"
    )
    for item in report["checks"]:
        print(f"check {item['id']}: {item['status']} ({len(item['assertions'])} assertions)")
    for item in report["mutants"]:
        print(f"mutant {item['base']} / {item['label']}: {item['status']} (expected {item['expected']})")
    print(json.dumps(report["summary"]))


if __name__ == "__main__":
    main()
