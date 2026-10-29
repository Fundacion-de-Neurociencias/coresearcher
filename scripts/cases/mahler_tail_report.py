"""Proof of the Mahler first-bullet scalar inequalities on the tail x >= 8 (python/discovery/mahler_tail.py, ADR-076).

python scripts/cases/mahler_tail_report.py

Writes examples/mahler-obligations/tail_proof.json. Takes under a minute.
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import mahler_tail as mt  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "mahler-obligations" / "tail_proof.json")
    args = parser.parse_args()
    start = time.time()
    models = mt.base_models()
    report = {
        "x_from": mt.X0,
        "mills_terms": mt.NMILLS,
        "phi_power": mt.KPHI,
        "model_min_exponents": {n: [a.min_exponent(), b.min_exponent()] for n, (a, b) in models.items()},
        "result": mt.verify_tail(16),
    }
    report["seconds"] = round(time.time() - start, 1)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s; verified={report['result']['verified']}")


if __name__ == "__main__":
    main()
