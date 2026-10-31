"""Recomputes the O(3) continuum-limit rehearsal (python/discovery/o3_continuum_case.py).

python scripts/cases/o3_rehearsal_report.py --out examples/o3-continuum-rehearsal/rehearsal_report.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.o3_continuum_case import case_report  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "examples" / "o3-continuum-rehearsal" / "rehearsal_report.json"
    )
    args = parser.parse_args()
    start = time.time()
    report = case_report()
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {args.out} in {time.time() - start:.1f} s")
    for row in report["coverage"]:
        print(f"{row['obligation']}: {row['coverage']}")
    for name, result in report["probes"].items():
        print(f"probe {name}: {result['outcome']} satisfied={result['satisfied_by']}")
    print(f"exclusion lint: {report['exclusion_lint']['flag']}")


if __name__ == "__main__":
    main()
