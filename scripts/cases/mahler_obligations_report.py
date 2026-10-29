"""Recomputes the Mahler scalar-input obligation ledger (python/discovery/mahler_obligations.py, ADR-DISCOVERY-076).

python scripts/cases/mahler_obligations_report.py --out examples/mahler-obligations/ledger.json

Default resolution: pointwise inequalities on [-20, 20] every 0.02; two-variable and segment inequalities on
[-12, 12] every 0.02, segment endpoints every 0.04. About 5 minutes on a laptop.
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import mahler_obligations as mo  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "mahler-obligations" / "ledger.json")
    args = parser.parse_args()
    start = time.time()
    proof = args.out.parent / "interval_proof.json"
    interval = json.loads(proof.read_text(encoding="utf-8")) if proof.exists() else None
    claim, _ = mo.run(interval=interval)
    report = {"source": mo.SOURCE, "claim": claim.to_dict(), "seconds": round(time.time() - start, 1)}
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} in {report['seconds']} s; claim status {report['claim']['status']}")
    for ob in report["claim"]["obligations"]:
        margins = [d["margin"] for d in ob["discharges"] if d["margin"] is not None]
        print(f"  {ob['status']:20s} {ob['id']}  margin={margins[0] if margins else '-'}")


if __name__ == "__main__":
    main()
