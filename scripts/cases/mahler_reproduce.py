"""Reproduce or audit the whole Mahler scalar-input proof (proof_pipeline.py, ADR-076).

python scripts/cases/mahler_reproduce.py                  # fast audit against manifest.json (seconds)
python scripts/cases/mahler_reproduce.py --run all        # rerun every proof (about 4 hours with 8 workers)
python scripts/cases/mahler_reproduce.py --run segment_box ledger
python scripts/cases/mahler_reproduce.py --write-manifest # record the current reports and sources

The audit fails when a report is missing or unverified, differs from the manifest, or depends on a source file
edited after the proof ran (STALE), or when the ledger's claim status is not the weakest-link roll-up.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import proof_pipeline as pp  # noqa: E402
from python.discovery.proof_cases import CASES, EX  # noqa: E402

CASE = CASES["mahler-scalar-input"]
STEPS = CASE.steps
MANIFEST = ROOT / CASE.manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", nargs="+", metavar="STEP", help="steps to rerun, or 'all'")
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    if args.run:
        names = None if args.run == ["all"] else args.run
        print("ran:", pp.run(STEPS, names))
        args.write_manifest = True
    if args.write_manifest:
        MANIFEST.write_text(json.dumps(pp.build_manifest(STEPS), indent=2) + "\n", encoding="utf-8")
        print(f"wrote {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    result = pp.check(STEPS, manifest, EX + "ledger.json")
    for name, f in result["steps"].items():
        print(f"{name:12s} {f['status']:5s} {'; '.join(f['problems'])}")
    print("ledger", result.get("ledger"))
    print("AUDIT OK" if result["ok"] else "AUDIT FAILED")
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
