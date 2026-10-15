"""Lean/Comparator label oracle for the openai/math statement-fidelity pilot.

Protocol and runbook: docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md

For every pilot pair it writes a copy of the original Comparator challenge and one challenge per
mutant, each with its own config, then runs Comparator against the paper's existing proof.
Expected outcome: the original copy is accepted and every mutant is rejected. A mutant that is
accepted did not change what the proof establishes, so its "mismatch" label is noise.

Usage (on a Linux machine with Lean, landrun and lean4export installed):
    python scripts/benchmarks/openai_math_lean_oracle.py preflight --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_oracle.py prepare --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_oracle.py run     --math-root /path/to/openai-math
    python scripts/benchmarks/openai_math_lean_oracle.py report  --math-root /path/to/openai-math

`prepare` and `report` need no Lean toolchain; `run` does. `run` is resumable: finished entries are
skipped, so it can be interrupted and restarted. `preflight` checks the machine before `run` and exits 1 if
anything required is missing; `scripts/benchmarks/legion_lean_oracle_setup.sh` installs what it checks.
"""

import argparse
import ctypes
import json
import math
import os
import platform
import shlex
import shutil
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


# ---------------------------------------------------------------- preflight

# landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION) returns the kernel's Landlock ABI version.
_LANDLOCK_SYSCALL = {"x86_64": 444, "aarch64": 444}
# Landlock ABI from which landrun can also restrict UNIX sockets. Below it, Comparator (which calls landrun with
# --best-effort) silently falls back to a sandbox without that restriction, and the systemd-run guard is what blocks
# AF_UNIX. The guard is therefore required, not optional, on such kernels.
_LANDRUN_FULL_ABI = 9


def landlock_abi() -> int:
    number = _LANDLOCK_SYSCALL.get(platform.machine())
    if number is None:
        return -1
    libc = ctypes.CDLL(None, use_errno=True)
    return libc.syscall(number, None, ctypes.c_size_t(0), ctypes.c_uint32(1))


def _probe(cmd: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    lines = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode == 0, lines[-1] if lines else ""


def _tool(name: str, env_var: str | None = None) -> str:
    return (os.environ.get(env_var) if env_var else None) or shutil.which(name) or ""


def olean_path(math_root: Path, module: str) -> Path:
    return lean_dir(math_root) / ".lake" / "build" / "lib" / "lean" / (module.replace(".", "/") + ".olean")


def preflight(math_root: Path) -> int:
    """Check everything `run` needs, without running Comparator. Exit 1 if a required check fails."""
    checks: list[tuple[str, bool, str, bool]] = []  # (name, ok, detail, required)

    def check(name: str, ok: bool, detail: str, required: bool = True) -> None:
        checks.append((name, ok, detail, required))

    check("Linux", sys.platform.startswith("linux"), sys.platform)
    euid = os.geteuid() if hasattr(os, "geteuid") else -1
    check("non-root user", euid not in (0, -1), f"euid {euid}")

    abi = landlock_abi() if sys.platform.startswith("linux") else -1
    check("Landlock enabled", abi >= 1, f"ABI v{abi}" if abi >= 1 else "not available")
    check(
        f"Landlock ABI >= v{_LANDRUN_FULL_ABI} (full landrun sandbox)",
        abi >= _LANDRUN_FULL_ABI,
        "below it, landrun falls back (--best-effort) and the systemd-run guard below is required",
        required=False,
    )
    if os.environ.get("COMPARATOR_CMD"):
        check("systemd-run guard", False, "COMPARATOR_CMD is set: runs bypass the systemd-run guard; unset it")
    else:
        ok, tail = _probe(
            [
                "systemd-run",
                "--property=RestrictAddressFamilies=~AF_UNIX",
                "--user",
                "--pipe",
                "--wait",
                "--quiet",
                "--",
                "true",
            ]
        )
        check("systemd-run --user (AF_UNIX guard)", ok, "ok" if ok else f"{tail} (needs a systemd user session)")

    lake = _tool("lake")
    check("lake on PATH", bool(lake), lake or "install elan")
    landrun = _tool("landrun", "COMPARATOR_LANDRUN")
    check("landrun", bool(landrun), landrun or "not on PATH and COMPARATOR_LANDRUN unset")
    if landrun:
        ok, tail = _probe(
            [landrun, "--best-effort", "--ro", "/", "--ldd", "--add-exec", "--", shutil.which("true") or "/bin/true"]
        )
        check("landrun sandbox starts", ok, "ok" if ok else tail)
    lean4export = _tool("lean4export", "COMPARATOR_LEAN4EXPORT")
    check("lean4export", bool(lean4export), lean4export or "not on PATH and COMPARATOR_LEAN4EXPORT unset")
    comparator = _tool("comparator")
    check("comparator on PATH", bool(comparator), comparator or "run uses `lake env comparator`")

    head = check_commit(math_root) if (math_root / ".git").exists() else "missing"
    check("openai/math at pinned commit", head == EXPECTED_COMMIT, head)
    toolchain_file = lean_dir(math_root) / "lean-toolchain"
    toolchain = toolchain_file.read_text(encoding="utf-8").strip() if toolchain_file.exists() else ""
    if lake and toolchain:
        ok, tail = _probe([lake, "--version"], cwd=lean_dir(math_root))
        version = toolchain.rsplit(":v", 1)[-1]
        check("project toolchain installed", ok and version in tail, f"{toolchain}: {tail}")
    mathlib_build = lean_dir(math_root) / ".lake" / "packages" / "mathlib" / ".lake" / "build" / "lib"
    check("Mathlib cache", mathlib_build.is_dir(), "ok" if mathlib_build.is_dir() else "run `lake exe cache get`")

    if manifest_path(math_root).exists():
        manifest = json.loads(manifest_path(math_root).read_text(encoding="utf-8"))
        n, problems = len(manifest["entries"]), len(manifest["problems"])
        check("challenges prepared", n == 71 and problems == 0, f"{n} challenges, {problems} problems")
        modules = manifest["solution_modules"]
        missing = [m for m in modules if not olean_path(math_root, m).exists()]
        check(
            "solution modules built",
            not missing,
            f"{len(modules) - len(missing)}/{len(modules)} built"
            + (f"; next: lake build {missing[0]}" if missing else ""),
        )
    else:
        check("challenges prepared", False, "run `prepare` first")

    failed = 0
    for name, ok, detail, required in checks:
        mark = "ok  " if ok else ("FAIL" if required else "warn")
        failed += (not ok) and required
        print(f"[{mark}] {name}: {detail}")
    print("preflight passed" if not failed else f"preflight failed: {failed} required check(s)")
    return 1 if failed else 0


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
    parser.add_argument("step", choices=["preflight", "prepare", "run", "report"])
    parser.add_argument("--math-root", required=True, type=Path, help="Path to an openai/math checkout")
    parser.add_argument("--timeout", type=int, default=3600, help="Seconds per Comparator run (run step)")
    args = parser.parse_args()
    math_root = args.math_root.resolve()
    if args.step == "preflight":
        return preflight(math_root)
    if args.step == "prepare":
        return prepare(math_root)
    if args.step == "run":
        return run(math_root, args.timeout)
    return report(math_root)


if __name__ == "__main__":
    raise SystemExit(main())
