"""Recomputes the Yang-Mills pre-registration case (python/discovery/yang_mills_case.py).

python scripts/cases/ym_preregistration_report.py --out examples/yang-mills-preregistration/preregistration_report.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.yang_mills_case import case_report  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "examples" / "yang-mills-preregistration" / "preregistration_report.json"
    )
    args = parser.parse_args()
    start = time.time()
    report = case_report()
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    record = args.out.parent / "ym_claim_record.json"
    record.write_text(
        json.dumps(report["claim_record"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Wrote {args.out} and {record.name} in {time.time() - start:.1f} s")
    print(f"checklist {report['checklist']['id']} v{report['checklist']['version']} sha256 {report['checklist']['sha256']}")
    print(f"claim {report['claim_record']['id']}: {report['claim_record']['rung']}")
    for claim, result in report["self_probe"].items():
        print(f"self-probe {claim}: {result['outcome']}")
    for s in report["scenarios"]:
        print(f"scenario {s['id']}: {s['outcome']} satisfied={s['satisfied_by']} undetermined={s['undetermined']}")


if __name__ == "__main__":
    main()
