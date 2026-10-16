"""Sensitivity analysis for the openai/math pilot after the Lean/Comparator label oracle.

Protocol: docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md, section 3. Every mutant that Comparator accepted is
label noise; this script recomputes the pilot's S1/B0/B1 figures without those mutants and prints them next to the
originals. It reuses the pilot's own statistics (same bootstrap and null-control seeds, same call order), so the
"original" column must reproduce the published pilot results exactly; the script exits 1 if it does not.

Usage:
    python scripts/benchmarks/openai_math_oracle_sensitivity.py [--out PATH]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from openai_math_pilot import BOOT_SEED, summarize  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
BENCH = ROOT / "docs" / "reference" / "benchmarks"
PILOT = BENCH / "openai_math_pilot_results.json"
ORACLE = BENCH / "openai_math_lean_oracle_results.json"
SYSTEMS = [("S1_coresearcher", "s1"), ("B0_always_match", "b0"), ("B1_numeric", "b1")]


def systems_for(rows: list[dict]) -> dict:
    rng = np.random.default_rng(BOOT_SEED)
    return {name: summarize(rows, f"{key}_flag", f"{key}_score", rng) for name, key in SYSTEMS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=BENCH / "openai_math_oracle_sensitivity.json")
    parser.add_argument(
        "--also-exclude",
        nargs="*",
        default=[],
        metavar="ID",
        help="Extra mutant ids to drop, as a supplementary (not pre-registered) analysis, e.g. ill-formed mutants",
    )
    args = parser.parse_args()

    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    noisy = set(oracle["summary"]["label_noise_mutants_accepted"])
    extra = set(args.also_exclude) - noisy
    rows = pilot["rows"]
    row_ids = {f"F{r['family']}_{r['mutation']}" for r in rows if r["label"] == 1}
    unknown = (noisy | extra) - row_ids
    if unknown:
        sys.exit(f"mutant ids not found in the pilot rows: {sorted(unknown)}")

    original = systems_for(rows)
    for name, _ in SYSTEMS:
        if original[name] != pilot["systems"][name]:
            sys.exit(f"{name}: recomputed figures differ from the published pilot results; not comparable")
    kept = [r for r in rows if f"F{r['family']}_{r['mutation']}" not in noisy]
    cleaned = systems_for(kept)

    out = {
        "protocol": "docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md",
        "removed_label_noise": sorted(noisy),
        "rows": {"original": len(rows), "without_noise": len(kept)},
        "original": original,
        "without_noise": cleaned,
    }
    if extra:
        kept_extra = [r for r in kept if f"F{r['family']}_{r['mutation']}" not in extra]
        out["supplementary"] = {
            "also_excluded": sorted(extra),
            "rows": len(kept_extra),
            "systems": systems_for(kept_extra),
        }
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"removed {len(noisy)} noisy mutant(s): {', '.join(sorted(noisy)) or 'none'}")
    if extra:
        print(f"supplementary: also excluded {', '.join(sorted(extra))}")
        for name, _ in SYSTEMS:
            s = out["supplementary"]["systems"][name]
            print(
                f"  {name:<18} sens {s['sensitivity']['flagged']}/{s['sensitivity']['n']}"
                f"  spec {s['specificity']['passed']}/{s['specificity']['n']}  AUROC {s['auroc']:.3f}"
            )
    print(f"{'system':<18} {'sens orig':>12} {'sens clean':>12} {'spec':>8} {'AUROC orig':>11} {'AUROC clean':>12}")
    for name, _ in SYSTEMS:
        o, c = original[name], cleaned[name]
        print(
            f"{name:<18} {o['sensitivity']['flagged']:>5}/{o['sensitivity']['n']:<6}"
            f" {c['sensitivity']['flagged']:>5}/{c['sensitivity']['n']:<6}"
            f" {c['specificity']['passed']:>3}/{c['specificity']['n']:<4}"
            f" {o['auroc']:>11.3f} {c['auroc']:>12.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
