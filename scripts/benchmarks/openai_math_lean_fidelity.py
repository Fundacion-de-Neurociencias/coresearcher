"""Lean-based statement-fidelity auditor for openai/math (design: LEAN_FIDELITY_AUDITOR_PLAN.md).

Plan: docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md

Only phase 0 is implemented so far:

    python scripts/benchmarks/openai_math_lean_fidelity.py env-check --math-root /path/to/openai-math

For each of the 19 pilot pairs it checks that the statement extraction is sound on the real challenge file
(balanced, found exactly once, same theorem name) and that the challenge elaborates with `lake env lean`. It
needs Lean and the Mathlib cache (`lake exe cache get` in openai-math/lean), but not Comparator, so it also runs
on Windows. It writes docs/reference/benchmarks/lean_fidelity_env_check.json.
"""

import argparse
import importlib.util
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATASET = ROOT / "docs" / "reference" / "benchmarks" / "openai_math_pilot_dataset.json"
ENV_CHECK_OUT = ROOT / "docs" / "reference" / "benchmarks" / "lean_fidelity_env_check.json"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pilot = _load("openai_math_pilot")
oracle = _load("openai_math_lean_oracle")


def extraction_check(pair: dict, lean: str) -> dict:
    """Checks the statement extraction of one pilot pair against its real challenge file."""
    parsed = pilot.theorem_statement(lean)
    if not parsed:
        return {"ok": False, "reason": "no theorem found"}
    name, stmt, _, _ = parsed
    checks = {
        "same_theorem": name == pair["theorem"],
        "balanced": pilot._balanced(stmt),
        "found_once": lean.count(stmt) == 1,
    }
    return {"ok": all(checks.values()), **checks, "matches_frozen_statement": stmt == pair["statement"]}


def _run(cmd: list[str], cwd: Path, timeout: int) -> tuple[int | None, str, float]:
    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "", time.monotonic() - start
    except OSError as exc:
        return -1, str(exc), time.monotonic() - start
    return proc.returncode, proc.stdout + proc.stderr, time.monotonic() - start


def elaboration_errors(output: str) -> list[str]:
    """Lean error lines; `sorry` warnings are expected in a challenge file and are not errors."""
    return [line for line in output.splitlines() if ": error" in line]


def lean_version_line(output: str) -> str:
    """The `Lean (version ...)` line; Lake may print dependency warnings around it."""
    return next((line.strip() for line in output.splitlines() if line.startswith("Lean (version")), output.strip())


def env_check(math_root: Path, timeout: int) -> int:
    commit = oracle.check_commit(math_root)
    lean_root = oracle.lean_dir(math_root)
    pairs = json.loads(DATASET.read_text(encoding="utf-8"))["pairs"]
    _, version_output, _ = _run(["lake", "env", "lean", "--version"], lean_root, 600)
    lean_version = lean_version_line(version_output)

    rows = []
    for pair in pairs:
        path = math_root / pair["challenge"]
        row = {"family": pair["family"], "challenge": pair["challenge"]}
        if not path.exists():
            rows.append({**row, "extraction": {"ok": False, "reason": "challenge file not found"}})
            continue
        row["extraction"] = extraction_check(pair, path.read_text(encoding="utf-8"))
        rel = path.relative_to(lean_root).as_posix()
        code, output, seconds = _run(["lake", "env", "lean", rel], lean_root, timeout)
        errors = elaboration_errors(output)
        row["elaboration"] = {
            "ok": code == 0 and not errors,
            "exit_code": code,
            "timed_out": code is None,
            "seconds": round(seconds, 1),
            "errors": errors[:5],
        }
        rows.append(row)
        status = "ok" if row["elaboration"]["ok"] and row["extraction"]["ok"] else "PROBLEM"
        print(f"{pair['family']} {status} ({seconds:.0f} s)", flush=True)

    elaborated = sum(r.get("elaboration", {}).get("ok", False) for r in rows)
    extracted = sum(r["extraction"]["ok"] for r in rows)
    result = {
        "plan": "docs/reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md (phase 0)",
        "openai_math_commit": commit,
        "lean_version": lean_version,
        "os": platform.platform(),
        "timeout_seconds": timeout,
        "summary": {"pairs": len(rows), "extraction_ok": extracted, "elaboration_ok": elaborated},
        "rows": rows,
    }
    ENV_CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"extraction ok {extracted}/{len(rows)}, elaboration ok {elaborated}/{len(rows)} -> {ENV_CHECK_OUT}")
    return 0 if extracted == elaborated == len(rows) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["env-check"])
    parser.add_argument("--math-root", required=True, type=Path, help="Path to an openai/math checkout")
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds per elaboration")
    args = parser.parse_args()
    return env_check(args.math_root.resolve(), args.timeout)


if __name__ == "__main__":
    sys.exit(main())
