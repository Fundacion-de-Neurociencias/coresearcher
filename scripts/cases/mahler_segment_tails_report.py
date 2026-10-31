"""Proof of the Mahler segment inequality (4) on the short widths and the tails (mahler_segment_tails.py, ADR-076).

python scripts/cases/mahler_segment_tails_report.py --workers 8

Writes examples/mahler-obligations/segment_tails_proof.json and the zone ranges it used,
examples/mahler-obligations/segment_tails_zones.json. With --zones the stored zone ranges are reused and only the
branch and bound runs (minutes); without it the zones are recomputed first (about 15 minutes).
"""

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import mahler_segment_tails as st  # noqa: E402

EX = ROOT / "examples" / "mahler-obligations"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--zones", action="store_true", help="reuse segment_tails_zones.json")
    parser.add_argument("--out", type=Path, default=EX / "segment_tails_proof.json")
    args = parser.parse_args()
    start = time.time()
    zpath = EX / "segment_tails_zones.json"
    if args.zones:
        cells = [{k: tuple(v) for k, v in c.items()} for c in json.loads(zpath.read_text(encoding="utf-8"))["cells"]]
    else:
        with Pool(args.workers) as pool:
            cells = pool.map(st.zone_job, range(len(st.zone_breakpoints())), chunksize=4)
        zpath.write_text(
            json.dumps({"breakpoints": st.zone_breakpoints(), "far_zone_from_t": st.T_FAR, "cells": cells}) + "\n",
            encoding="utf-8",
        )
    report = st.verify_with_cells(cells, lambda n, **kw: Pool(n, **kw), args.workers)
    report = {
        "region": "m >= 0, h > 0, outside {|l| <= 1.4, y <= 3.6, h >= .16} (t = asinh(x/s), l = m - h, y = m + h)",
        **report,
        "seconds": round(time.time() - start, 1),
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s; verified {report['verified']}")
    print({k: v for k, v in report.items() if k not in ("failed", "lemmas")})


if __name__ == "__main__":
    main()
