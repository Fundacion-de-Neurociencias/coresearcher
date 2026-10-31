"""Citation-resolution gate for LaTeX manuscript sources (ADR-DISCOVERY-077).

Usage:
    python scripts/checks/citation_gate.py SOURCE_DIR [SOURCE_DIR ...] [--collection DIR]

Fails (exit code 1) when a \\cite key has no bibliography entry, or, with --collection, when a link to a manuscript
of a collection (preprints/<dir> or OAI:<dir>) names a directory that does not exist there. Sources without any
bibliography are reported and pass: the gate cannot judge them.

This is the one check that detected a real corrected defect in the openai/math revision benchmark, with no false
alarm over 47 manuscripts (docs/reference/benchmarks/OPENAI_MATH_REVISION_RESULTS.md).
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import manuscript_checks  # noqa: E402


def gate(source_dirs, collection=None) -> int:
    snapshot = {p.name for p in Path(collection).iterdir() if p.is_dir()} if collection else None
    failed = 0
    for d in source_dirs:
        files = manuscript_checks.read_sources(Path(d))
        coverage = manuscript_checks.Coverage()
        flags = manuscript_checks.check_citations(files, snapshot, coverage)
        if not coverage.bibliography_entries:
            print(f"{d}: no bibliography found; {coverage.citations} citations not checked")
            continue
        for f in flags:
            print(f"{d}/{f.file}:{f.line}: {f.detail}")
        print(f"{d}: {coverage.citations} citations, {coverage.bibliography_entries} entries, "
              f"{coverage.internal_links} collection links, {len(flags)} unresolved")
        failed += bool(flags)
    return 1 if failed else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--collection", help="directory whose subdirectories are the collection's manuscripts")
    args = ap.parse_args()
    sys.exit(gate(args.sources, args.collection))


if __name__ == "__main__":
    main()
