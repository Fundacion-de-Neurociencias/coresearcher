"""Interval-arithmetic proof of the Mahler scalar inequalities on a bounded window (mahler_interval.py, ADR-076).

python scripts/cases/mahler_interval_report.py --w1 8 --w2 3 --workers 8

Writes examples/mahler-obligations/interval_proof.json. The first bullet is proved on [0, w1] (evenness covers
[-w1, 0]); the two inequalities (3) on [-w2, w2]^2. Runtime is tens of minutes with 8 workers.
"""

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import mahler_interval as mi  # noqa: E402


def one(chunk):
    lo, hi, n0 = chunk
    return mi.verify_1d(lo, hi, n0)


def two(chunk):
    w2, n0, i, j = chunk
    return mi.verify_2d(w2, n0, z_range=(i, j))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--w1", type=float, default=8.0)
    parser.add_argument("--w2", type=float, default=3.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "mahler-obligations" / "interval_proof.json")
    args = parser.parse_args()
    start = time.time()
    sym = mi.symbolic_checks()
    step = 0.5
    chunks1 = [(i * step, min((i + 1) * step, args.w1), 8) for i in range(int(args.w1 / step))]
    n2 = int(args.w2 * 16)
    per = max(1, n2 // args.workers)
    chunks2 = [(args.w2, n2, i, min(i + per, n2)) for i in range(0, n2, per)]
    with Pool(args.workers) as pool:
        r1 = pool.map(one, chunks1, chunksize=1)
        r2 = pool.map(two, chunks2, chunksize=1)
    first = {
        "window": [-args.w1, args.w1],
        "verified": all(r["verified"] for r in r1),
        "certified_boxes": sum(r["certified_boxes"] for r in r1),
        "min_lower_bound": {k: min(r["min_lower_bound"].get(k, 1e9) for r in r1) for k in mi.FIRST_BULLET},
        "uncertified": [u for r in r1 for u in r["uncertified"]],
    }
    second = {
        "window": [-args.w2, args.w2],
        "verified": all(r["verified"] for r in r2),
        "certified_pairs": sum(r["certified_pairs"] for r in r2),
        "min_lower_bound": [min(r["min_lower_bound"][i] for r in r2) for i in (0, 1)],
        "uncertified": [u for r in r2 for u in r["uncertified"]],
    }
    report = {
        "symbolic": [{"check": n, "holds": ok} for n, ok in sym],
        "first_bullet": first,
        "two_variable": second,
        "seconds": round(time.time() - start, 1),
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s")
    print("symbolic all true:", all(ok for _, ok in sym))
    print("first bullet verified:", first["verified"], first["certified_boxes"], "boxes")
    print("two-variable verified:", second["verified"], second["certified_pairs"], "pairs", second["min_lower_bound"])


if __name__ == "__main__":
    main()
