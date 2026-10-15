"""Lean/Comparator label oracle for the openai/math statement-fidelity pilot.

Protocol and runbook: docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md

For every pilot pair it writes a copy of the original Comparator challenge and one challenge per
mutant, each with its own config, then runs Comparator against the paper's existing proof.
Expected outcome: the original copy is accepted and every mutant is rejected. A mutant that is
accepted did not change what the proof establishes, so its "mismatch" label is noise.

Usage (on a Linux machine with Lean, landrun and lean4export installed):
    python scripts/benchmarks/openai_math_lean_oracle.py prepare --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_oracle.py run     --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_oracle.py report  --math-root /path/to/openai-math

`prepare` and `report` need no Lean toolchain; `run` does. `run` is resumable: finished entries are
skipped, so it can be interrupted and restarted.
"""

import argparse
import json
import math
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATASET = ROOT / "docs" / "reference" / "benchmarks" / "openai_math_pilot_dataset.json"
REPORT_OUT = ROOT / "docs" / "reference" / "benchmarks" / "openai_math_lean_oracle_results.json"
EXPECTED_COMMIT = "1581d4cbdd69a0faf34b2089614fe2a814316a6a"
MUTANT_DIR = "ComparatorChallenges/OracleMutants"
Z95 = 1.959963984540054


def lean_dir(math_root: Path) -> Path:
    return math_root / "lean"


def manifest_path(math_root: Path) -> Path:
    return lean_dir(math_root) / MUTANT_DIR / "manifest.json"


def results_path(math_root: Path) -> Path:
    return lean_dir(math_root) / MUTANT_DIR / "results.jsonl"


def check_commit(math_root: Path) -> str:
    def git(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=math_root, capture_output=True, text=True).stdout.strip()
        except OSError:
            return ""

    # Only trust the commit when math_root is itself the top of a git checkout, not a folder inside another repo.
    toplevel = git("rev-parse", "--show-toplevel")
    is_own_repo = bool(toplevel) and Path(toplevel).resolve() == math_root.resolve()
    head = git("rev-parse", "HEAD") if is_own_repo else ""
    if head and head != EXPECTED_COMMIT:
        sys.exit(f"openai/math is at {head[:12]}, expected {EXPECTED_COMMIT[:12]}. Check out the pinned commit first.")
    return head or "unknown (not a git checkout)"


# ---------------------------------------------------------------- prepare


def prepare(math_root: Path) -> int:
    commit = check_commit(math_root)
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    out_dir = lean_dir(math_root) / MUTANT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    entries, problems = [], []
    for pair in dataset["pairs"]:
        challenge_rel = pair["challenge"]  # e.g. lean/ComparatorChallenges/Catalan.lean
        challenge_file = math_root / challenge_rel
        config_file = challenge_file.with_suffix(".json")
        if not challenge_file.exists() or not config_file.exists():
            problems.append({"family": pair["family"], "reason": f"missing {challenge_file.name} or its .json config"})
            continue
        source = challenge_file.read_text(encoding="utf-8")
        statement = pair["statement"]
        if source.count(statement) != 1:
            problems.append({"family": pair["family"], "reason": "statement not found exactly once in challenge file"})
            continue
        config = json.loads(config_file.read_text(encoding="utf-8"))

        variants = [("ORIGINAL", statement, 0)] + [(c, s, 1) for c, s in sorted(pair["mutants"].items())]
        for code, stmt, label in variants:
            stem = f"F{pair['family']}_{code}"
            (out_dir / f"{stem}.lean").write_text(source.replace(statement, stmt), encoding="utf-8")
            variant_config = dict(config)
            variant_config["challenge_module"] = f"{MUTANT_DIR.replace('/', '.')}.{stem}"
            (out_dir / f"{stem}.json").write_text(json.dumps(variant_config, indent=2), encoding="utf-8")
            entries.append(
                {
                    "id": stem,
                    "family": pair["family"],
                    "mutation": code,
                    "label": label,
                    "config": f"{MUTANT_DIR}/{stem}.json",
                    "solution_module": config["solution_module"],
                }
            )

    manifest = {
        "source_commit": commit,
        "entries": entries,
        "problems": problems,
        "solution_modules": sorted({e["solution_module"] for e in entries}),
    }
    manifest_path(math_root).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        f"prepared {len(entries)} challenges from {len(dataset['pairs']) - len(problems)} pairs; problems: {len(problems)}"
    )
    for p in problems:
        print(f"  - family {p['family']}: {p['reason']}")
    print(f"solution modules to build first ({len(manifest['solution_modules'])}):")
    for m in manifest["solution_modules"]:
        print(f"  lake build {m}")
    return 0


# ---------------------------------------------------------------- run


def comparator_command(config_rel: str, workdir: Path) -> list[str]:
    """Follows the Comparator README: run under systemd-run without AF_UNIX, as an unprivileged user.

    Set COMPARATOR_CMD to override, e.g. COMPARATOR_CMD='lake env comparator {config}' for a quick local test.
    """
    override = os.environ.get("COMPARATOR_CMD")
    if override:
        return shlex.split(override.format(config=config_rel))
    return [
        "systemd-run",
        "--property=RestrictAddressFamilies=~AF_UNIX",
        "--user",
        "--pipe",
        "--wait",
        "--quiet",
        "-E",
        f"PATH={os.environ.get('PATH', '')}",
        "--working-directory",
        str(workdir),
        "--",
        "bash",
        "-c",
        f"lake env comparator {shlex.quote(config_rel)}",
    ]


def run(math_root: Path, timeout: int) -> int:
    check_commit(math_root)
    if os.name == "nt":
        sys.exit("Comparator requires Linux (landrun sandbox). Run this step on the Linux machine.")
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        sys.exit("Comparator must not run as root (see its README).")
    manifest = json.loads(manifest_path(math_root).read_text(encoding="utf-8"))
    done = set()
    if results_path(math_root).exists():
        done = {
            json.loads(line)["id"] for line in results_path(math_root).read_text(encoding="utf-8").splitlines() if line
        }
    workdir = lean_dir(math_root)
    pending = [e for e in manifest["entries"] if e["id"] not in done]
    print(f"{len(done)} done, {len(pending)} pending")
    with results_path(math_root).open("a", encoding="utf-8") as out:
        for i, entry in enumerate(pending, 1):
            start = time.monotonic()
            try:
                proc = subprocess.run(
                    comparator_command(entry["config"], workdir),
                    cwd=workdir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                exit_code, tail = proc.returncode, (proc.stdout + proc.stderr)[-2000:]
            except subprocess.TimeoutExpired:
                exit_code, tail = None, f"timeout after {timeout}s"
            record = {
                **entry,
                "exit_code": exit_code,
                "accepted": exit_code == 0,
                "seconds": round(time.monotonic() - start, 1),
                "output_tail": tail,
            }
            out.write(json.dumps(record) + "\n")
            out.flush()
            status = "accepted" if exit_code == 0 else ("TIMEOUT" if exit_code is None else f"rejected ({exit_code})")
            print(f"[{i}/{len(pending)}] {entry['id']}: {status} in {record['seconds']}s")
    return 0


# ---------------------------------------------------------------- report


def wilson(k: int, n: int) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    p, z2 = k / n, Z95**2
    c = (p + z2 / (2 * n)) / (1 + z2 / n)
    h = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return [c - h, c + h]


def report(math_root: Path) -> int:
    records = [json.loads(line) for line in results_path(math_root).read_text(encoding="utf-8").splitlines() if line]
    completed = [r for r in records if r["exit_code"] is not None]
    timeouts = [r["id"] for r in records if r["exit_code"] is None]
    originals = [r for r in completed if r["label"] == 0]
    mutants = [r for r in completed if r["label"] == 1]
    orig_ok = sum(r["accepted"] for r in originals)
    mut_rejected = sum(not r["accepted"] for r in mutants)
    by_type = {}
    for code in sorted({r["mutation"] for r in mutants}):
        sub = [r for r in mutants if r["mutation"] == code]
        k = sum(not r["accepted"] for r in sub)
        by_type[code] = {"rejected": k, "n": len(sub), "wilson_95": wilson(k, len(sub))}
    summary = {
        "source_commit": EXPECTED_COMMIT,
        "originals_accepted": {"k": orig_ok, "n": len(originals), "wilson_95": wilson(orig_ok, len(originals))},
        "mutants_rejected": {"k": mut_rejected, "n": len(mutants), "wilson_95": wilson(mut_rejected, len(mutants))},
        "mutants_rejected_by_type": by_type,
        "label_noise_mutants_accepted": [r["id"] for r in mutants if r["accepted"]],
        "originals_not_accepted": [r["id"] for r in originals if not r["accepted"]],
        "timeouts": timeouts,
        "criteria": {
            "pipeline_sound_all_completed_originals_accepted": bool(originals) and orig_ok == len(originals),
            "labels_valid_rejection_lower_bound_at_least_0_9": bool(mutants)
            and wilson(mut_rejected, len(mutants))[0] >= 0.9,
        },
    }
    REPORT_OUT.write_text(json.dumps({"summary": summary, "records": records}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["prepare", "run", "report"])
    parser.add_argument("--math-root", required=True, type=Path, help="Path to an openai/math checkout")
    parser.add_argument("--timeout", type=int, default=3600, help="Seconds per Comparator run (run step)")
    args = parser.parse_args()
    math_root = args.math_root.resolve()
    if args.step == "prepare":
        return prepare(math_root)
    if args.step == "run":
        return run(math_root, args.timeout)
    return report(math_root)


if __name__ == "__main__":
    raise SystemExit(main())
