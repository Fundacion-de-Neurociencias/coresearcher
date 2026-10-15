"""Recomputes the Sakana Error Diffusion showcase (python/discovery/ed_polarity_case.py) and writes its report.

python scripts/cases/ed_polarity_report.py --out examples/sakana-ed-polarity/z3_report.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.ed_polarity_case import case_report  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "sakana-ed-polarity" / "z3_report.json")
    args = parser.parse_args()
    start = time.time()
    report = case_report()
    report["seconds"] = round(time.time() - start, 1)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s")
    for key, value in report["main_claim"].items():
        print(f"main {key}: {value['status']}")
    for key, value in report["variants"].items():
        print(f"variant {key}: {value['status']}")
    for key, table in report["assumption_necessity"].items():
        print(f"necessity {key}: {table}")


if __name__ == "__main__":
    main()
