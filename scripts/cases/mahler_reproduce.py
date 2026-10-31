"""Reproduce or audit the whole Mahler scalar-input proof (proof_pipeline.py, ADR-076).

python scripts/cases/mahler_reproduce.py                  # fast audit against manifest.json (seconds)
python scripts/cases/mahler_reproduce.py --run all        # rerun every proof (about 3.5 hours with 8 workers)
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

EX = "examples/mahler-obligations/"
D = "python/discovery/"
BASE = [D + "mahler_interval.py", D + "mahler_obligations.py"]
TAIL = BASE + [D + "mahler_tail.py"]
STEPS = [
    pp.ProofStep(
        "interval",
        "scripts/cases/mahler_interval_report.py",
        EX + "interval_proof.json",
        ["first_bullet.verified", "two_variable.verified"],
        BASE,
        minutes=20,
    ),
    pp.ProofStep("tail", "scripts/cases/mahler_tail_report.py", EX + "tail_proof.json", ["result.verified"], TAIL),
    pp.ProofStep(
        "twovar",
        "scripts/cases/mahler_twovar_report.py",
        EX + "twovar_proof.json",
        ["result.verified"],
        TAIL + [D + "mahler_twovar.py"],
        minutes=12,
    ),
    pp.ProofStep(
        "ranges",
        "scripts/cases/mahler_ranges_report.py",
        EX + "ranges_proof.json",
        ["window.verified", "tail.verified"],
        TAIL + [D + "mahler_ranges.py"],
        minutes=135,
    ),
    pp.ProofStep(
        "segment_box",
        "scripts/cases/mahler_segment_box_report.py",
        EX + "segment_box_proof.json",
        ["verified"],
        TAIL + [D + "mahler_ranges.py", D + "mahler_segment_box.py"],
        minutes=12,
    ),
    pp.ProofStep(
        "segment_tails",
        "scripts/cases/mahler_segment_tails_report.py",
        EX + "segment_tails_proof.json",
        ["verified"],
        TAIL
        + [
            D + "mahler_ranges.py",
            D + "mahler_segment_box.py",
            D + "mahler_segment_tails.py",
            D + "interval_engine.py",
        ],
        minutes=40,
    ),
    pp.ProofStep(
        "ledger",
        "scripts/cases/mahler_obligations_report.py",
        EX + "ledger.json",
        [],
        BASE
        + [D + "obligation_ledger.py", D + "mahler_segment.py"]
        + [EX + f for f in ("interval_proof.json", "tail_proof.json", "twovar_proof.json", "ranges_proof.json")]
        + [EX + "segment_box_proof.json", EX + "segment_tails_proof.json"],
        minutes=14,
    ),
]
MANIFEST = ROOT / EX / "manifest.json"


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
