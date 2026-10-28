"""Recomputes the Collatz checkability case (python/discovery/collatz_case.py).

python scripts/cases/collatz_report.py --out examples/collatz-checkable/collatz_report.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.collatz_case import case_report  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "collatz-checkable" / "collatz_report.json")
    args = parser.parse_args()
    start = time.time()
    report = case_report()
    report["seconds"] = round(time.time() - start, 1)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s")
    dag = report["dag"]
    print(f"DAG acyclic={dag['is_acyclic']}, missing premises={len(dag['missing_premises'])}, open={dag['open_nodes']}")
    for item in report["checks"]:
        print(f"check {item['id']}: {item['status']} {item['values'] or ''}")
    for item in report["negative_controls"]:
        print(f"control: {item['label']}: detected={item['detected']}")
    print(json.dumps(report["summary"]))


if __name__ == "__main__":
    main()
