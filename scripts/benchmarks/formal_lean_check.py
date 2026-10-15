"""Cross-check of z3 entailment verdicts with the Lean 4 kernel (ADR-DISCOVERY-060).

For each check, z3 decides whether a consequence follows from a hypothesis, and `formal_lean` states the same
consequence as a Lean theorem. On a machine with a Mathlib project (the Lenovo Legion), Lean then tries to prove it:

    python scripts/benchmarks/formal_lean_check.py export --out-dir runs/lean_checks
    python scripts/benchmarks/formal_lean_check.py run --out-dir runs/lean_checks --project ~/mathlib-project \
        --out runs/lean_checks/results.json

Reading the results:
- z3 ENTAILED and Lean PROVED: agreement, now kernel-checked.
- z3 ENTAILED and Lean NOT_PROVED: the default tactic was too weak. Not a contradiction.
- z3 NOT_ENTAILED and Lean PROVED: a soundness discrepancy. One of the two translations is wrong; investigate before
  trusting either back end.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.formal_hypothesis import HypothesisEvaluator, hypothesis_from_dict  # noqa: E402
from python.discovery.formal_lean import consequence_theorem  # noqa: E402

R = {"name": "r", "continuous": True, "lower": 0, "upper": 10}
S = {"name": "s", "continuous": True}

CHECKS = [
    ("C01", {"variables": [R], "claims": ["r*r >= 2"]}, "r > 1.4"),
    ("C02", {"variables": [R], "claims": ["r*r >= 2"]}, "r > 1.5"),
    ("C03", {"variables": [R, S], "claims": ["s == 2*r + 1"]}, "s >= 1"),
    ("C04", {"variables": [R, S], "claims": ["s == 2*r + 1"]}, "s >= 2"),
    ("C05", {"variables": [S], "claims": ["s**2 <= 4"]}, "s >= -2 and s <= 2"),
    ("C06", {"variables": [R, S], "assumptions": ["s > 0"], "claims": ["r * s >= 1"]}, "r > 0"),
    ("C07", {"variables": [R, {"name": "k", "domain": [1, 2]}], "claims": ["r >= 3 * k"]}, "r >= 3"),
    ("C08", {"variables": [R, {"name": "k", "domain": [1, 2]}], "claims": ["r >= 3 * k"]}, "r >= 6"),
    (
        "C09",
        {
            "variables": [
                {"name": "dose", "continuous": True, "lower": 0, "upper": 100},
                {"name": "conc", "continuous": True, "lower": 0},
            ],
            "claims": ["dose <= 10 or conc > 2"],
        },
        "dose <= 10 or conc > 1",
    ),
    ("C10", {"variables": [S], "claims": ["s*s - 3*s + 2 == 0"]}, "s == 1 or s == 2"),
    # Added after round 0 to cover more goal shapes of the shape-directed default tactic.
    ("C11", {"variables": [R, {"name": "k", "domain": [1, 2, 3]}], "claims": ["r >= k"]}, "r >= 1"),
    ("C12", {"variables": [S], "claims": ["s*s*s - 6*s*s + 11*s - 6 == 0"]}, "s in (1, 2, 3)"),
    ("C13", {"variables": [R], "claims": ["r > 2"]}, "r != 1"),
    ("C14", {"variables": [R], "claims": ["r in (1, 2)"]}, "r not in (3, 4)"),
    ("C15", {"variables": [R], "claims": ["r > 2"]}, "1 < r <= 10"),
    ("C16", {"variables": [R], "claims": ["r >= 1"]}, "r != 2"),
]


def export(out_dir: Path) -> list:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for check_id, spec, consequence in CHECKS:
        h = hypothesis_from_dict({**spec, "hypothesis_id": check_id})
        verdict = HypothesisEvaluator.entails(h, consequence)
        path = out_dir / f"{check_id}.lean"
        path.write_text(consequence_theorem(h, consequence), encoding="utf-8", newline="\n")
        manifest.append(
            {"id": check_id, "consequence": consequence, "z3_entailed": verdict.entailed, "file": path.name}
        )
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def run(out_dir: Path, project: Path, timeout: int) -> dict:
    lake = shutil.which("lake")
    if lake is None:
        raise SystemExit("lake not found: run this on a machine with Lean 4 and a Mathlib project (see runbook).")
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    results = []
    for item in manifest:
        t0 = time.time()
        try:
            proc = subprocess.run(
                [lake, "env", "lean", str((out_dir / item["file"]).resolve())],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            status = "PROVED" if proc.returncode == 0 and "sorry" not in proc.stdout else "NOT_PROVED"
            log = (proc.stdout + proc.stderr)[-2000:]
        except subprocess.TimeoutExpired:
            status, log = "TIMEOUT", ""
        discrepancy = status == "PROVED" and not item["z3_entailed"]
        results.append(
            {
                **item,
                "lean_status": status,
                "soundness_discrepancy": discrepancy,
                "seconds": round(time.time() - t0, 1),
                "log_tail": log,
            }
        )
        print(f"{item['id']}: z3 entailed={item['z3_entailed']} lean={status}{'  DISCREPANCY' if discrepancy else ''}")
    return {
        "results": results,
        "kernel_confirmed": sum(r["lean_status"] == "PROVED" and r["z3_entailed"] for r in results),
        "z3_entailed": sum(r["z3_entailed"] for r in results),
        "soundness_discrepancies": sum(r["soundness_discrepancy"] for r in results),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--out-dir", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out-dir", required=True)
    r.add_argument("--project", required=True, help="Directory of a Lake project that depends on Mathlib.")
    r.add_argument("--out", required=True)
    r.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args(argv)
    if args.cmd == "export":
        for m in export(Path(args.out_dir)):
            print(f"{m['id']}: z3 entailed={m['z3_entailed']}  {m['file']}")
        return 0
    summary = run(Path(args.out_dir), Path(args.project).expanduser(), args.timeout)
    Path(args.out).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}))
    return 1 if summary["soundness_discrepancies"] else 0


if __name__ == "__main__":
    sys.exit(main())
