"""Proof of the profile derivative bounds used by the Mahler segment inequality (mahler_ranges.py, ADR-076).

python scripts/cases/mahler_ranges_report.py --workers 8

Writes examples/mahler-obligations/ranges_proof.json: the window 0 <= x <= 8 split into 32 chunks for the worker pool,
plus the tail x >= 8. Takes tens of minutes with 8 workers.
"""

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import mahler_ranges as mr  # noqa: E402


def chunk(lohi):
    lo, hi = lohi
    stack = [(lo + (hi - lo) * i / 4, lo + (hi - lo) * (i + 1) / 4, 0) for i in range(4)][::-1]
    return mr._branch_and_bound(stack, mr.window_margins, lambda a, b: [a, b], 30, None)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "mahler-obligations" / "ranges_proof.json")
    args = parser.parse_args()
    start = time.time()
    chunks = [(i * 0.25, (i + 1) * 0.25) for i in range(int(mr.WINDOW / 0.25))]
    with Pool(args.workers) as pool:
        parts = pool.map(chunk, chunks, chunksize=1)
    window = {
        "range": [0.0, mr.WINDOW],
        "verified": all(p["verified"] for p in parts),
        "certified_boxes": sum(p["certified_boxes"] for p in parts),
        "min_lower_bound": {k: min(p["min_lower_bound"].get(k, 1e9) for p in parts) for k in mr.BOUNDS},
        "uncertified": [u for p in parts for u in p["uncertified"]][:20],
    }
    tail = mr.verify_tail()
    report = {"bounds": mr.BOUNDS, "window": window, "tail": tail, "seconds": round(time.time() - start, 1)}
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s; window {window['verified']}, tail {tail['verified']}")
    print(window["min_lower_bound"], tail["min_lower_bound"])


if __name__ == "__main__":
    main()
