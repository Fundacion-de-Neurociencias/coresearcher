"""Proof of the Mahler segment inequality (4) on the bounded region of the middle and large width regimes
(mahler_segment_box.py, ADR-076).

python scripts/cases/mahler_segment_box_report.py --workers 8

Writes examples/mahler-obligations/segment_box_proof.json. Takes about a quarter of an hour with 8 workers.
"""

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import mahler_segment_box as sb  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "mahler-obligations" / "segment_box_proof.json")
    args = parser.parse_args()
    start = time.time()
    with Pool(args.workers) as pool:
        report = sb.verify_bounded(pool)
    report = {
        "region": "|l| <= 1.4, y <= 3.6, h >= .16, m >= 0 (t = asinh(x/s), l = m - h, y = m + h)",
        **report,
        "seconds": round(time.time() - start, 1),
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s; verified {report['verified']}")
    print(json.dumps(report["levels"], indent=1))


if __name__ == "__main__":
    main()
