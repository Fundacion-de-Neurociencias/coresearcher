"""Proof of the two-variable Mahler inequalities (3) outside [-3, 3]^2 (python/discovery/mahler_twovar.py, ADR-076).

python scripts/cases/mahler_twovar_report.py --workers 8

Writes examples/mahler-obligations/twovar_proof.json. About ten minutes with 8 workers.
"""

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import mahler_twovar as tv  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "mahler-obligations" / "twovar_proof.json")
    args = parser.parse_args()
    start = time.time()
    reduction = tv.check_reduction()
    with Pool(args.workers) as pool:
        boxes = tv.one_dim_boxes(pool=pool)
    result = tv.verify_outside(boxes)
    report = {
        "reduction": [{"identity": k, "holds": v} for k, v in reduction.items()],
        "tail_config": dict(zip(("x0", "mills_terms", "phi_power", "truncation"), tv.TAIL)),
        "band": [list(b) for b in tv.BAND],
        "result": result,
        "seconds": round(time.time() - start, 1),
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s; verified={result['verified']}")
    print({k: v for k, v in result.items() if k != "uncertified"}, result["uncertified"][:5])


if __name__ == "__main__":
    main()
