"""Recomputes the Local smoothing statement-fidelity case (python/discovery/local_smoothing_case.py).

python scripts/cases/local_smoothing_fidelity_report.py --out examples/local-smoothing-fidelity/fidelity_report.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.local_smoothing_case import case_report  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "examples" / "local-smoothing-fidelity" / "fidelity_report.json"
    )
    args = parser.parse_args()
    start = time.time()
    report = case_report()
    report["seconds"] = round(time.time() - start, 1)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s")
    for item in report["ranges"]:
        checks = ", ".join(f"{k}={v['agreement']}" for k, v in item["quantities"].items())
        print(
            f"range {item['theorem']}: {item['relation']} {item['method']} cross-check "
            f"{item['cross_check']['relation']} {checks}"
        )
    for item in report["mutants"]:
        print(f"mutant {item['base']} / {item['label']}: {item['relation']} (expected {item['expected']})")
    print(f"lint: {len(report['lint']['findings'])} findings, {report['lint']['open']} open")


if __name__ == "__main__":
    main()
