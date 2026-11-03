"""
scripts/cases/trivial_witness_probe_report.py - Trivial-witness / vacuity probe over every openai/math Comparator target.

    python scripts/cases/trivial_witness_probe_report.py static  --corpus <openai/math checkout or extract>
    python scripts/cases/trivial_witness_probe_report.py prepare --math-root <openai/math checkout with lean built>
    python scripts/cases/trivial_witness_probe_report.py run     --math-root <...> [--only ClassicalON] [--timeout 600]
    python scripts/cases/trivial_witness_probe_report.py report  --math-root <...>

`static` needs no Lean: it runs stage 1 (z3 consistency of the explicit hypotheses) and writes
examples/openai-math-coverage/vacuity_probe.json with every Lean probe marked NOT_RUN. `prepare` writes the stage 2
and 3 probe files under lean/ComparatorChallenges/Probes/ of a checkout at the pinned commit; `run` elaborates them one
at a time with `lake env lean` (resumable: finished probes are skipped); `report` folds the outcomes into the JSON.
`run` needs the openai/math Lean project built (Linux; see docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md).
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import shlex
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from python.discovery import formal_provenance, kernel_records  # noqa: E402
from python.discovery import openai_math_coverage as cov  # noqa: E402
from python.discovery import trivial_witness_probe as probe  # noqa: E402

OUT = ROOT / "examples" / "openai-math-coverage" / "vacuity_probe.json"
PROBE_DIR = "ComparatorChallenges/Probes"


def _targets(math_root: Path):
    """(challenge path, source, theorem names) for every Comparator config."""
    comparator = Path(math_root) / "lean" / "ComparatorChallenges"
    for config_path in sorted(comparator.glob("**/*.json")):
        if PROBE_DIR in config_path.as_posix():
            continue
        config = json.loads(config_path.read_text(encoding="utf-8"))
        module = config.get("challenge_module", "").removeprefix("ComparatorChallenges.").replace(".", "/") + ".lean"
        path = comparator / module
        if path.exists():
            yield module, path.read_text(encoding="utf-8"), config.get("theorem_names", [])


def _all_probes(math_root: Path):
    probes = []
    for challenge, source, names in _targets(math_root):
        probes += probe.cheap_tactic_probes(source, challenge, names)
        for case in probe.CASES:
            if case.challenge == challenge:
                probes += probe.degenerate_probe_files(case, source)
    return probes


def static(corpus: Path) -> None:
    rows = []
    for challenge, source, names in _targets(corpus):
        for name in names:
            statement = probe.expanded_statement(source, name.split(".")[-1])
            rows.append({"challenge": challenge, "theorem": name, **probe.arithmetic_check(statement)})
    probes = _all_probes(corpus)
    data = {
        "source_commit": cov.SOURCE_COMMIT,
        "tactic_menu": probe.TACTIC_MENU,
        "max_heartbeats": probe.HEARTBEATS,
        "stage1_arithmetic": {"summary": dict(Counter(r["verdict"] for r in rows)), "targets": rows},
        "lean_probes": {
            "summary": {"NOT_RUN": len(probes)},
            # Targets whose `theorem ... sorry` text was not located (attributes, indentation): no stage 2 probe.
            "targets_without_probe": sorted(
                {r["theorem"] for r in rows} - {p.theorem for p in probes if p.mode == "trivial"}
            ),
            "probes": [
                {
                    "probe_id": p.probe_id,
                    "theorem": p.theorem,
                    "mode": p.mode,
                    "module_path": p.module_path,
                    "outcome": probe.LeanOutcome.NOT_RUN.value,
                }
                for p in probes
            ],
        },
        "degenerate_cases": [
            {k: v for k, v in asdict(c).items() if k != "lemmas"} | {"lemmas": list(c.lemmas)} for c in probe.CASES
        ],
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"stage 1: {data['stage1_arithmetic']['summary']}; {len(probes)} Lean probes prepared (NOT_RUN)")


def _aborted(records: Path | None) -> set:
    """Probe ids whose record says a tactic aborted the combined menu (they get single-tactic probes)."""
    if records is None or not Path(records).is_dir():
        return set()
    ids = set()
    for path in Path(records).glob("openai-math-probe-*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["result"] == kernel_records.BLOCKED and any("menu was aborted" in r for r in record["reasons"]):
            ids.add(record["probe"]["probe_id"])
    return ids


def prepare(math_root: Path, records: Path | None = None) -> None:
    head = subprocess.run(["git", "-C", str(math_root), "rev-parse", "HEAD"], capture_output=True, text=True)
    if head.stdout.strip() != cov.SOURCE_COMMIT:
        raise SystemExit(f"{math_root} is at {head.stdout.strip() or '?'}, expected {cov.SOURCE_COMMIT}")
    lean = Path(math_root) / "lean"
    probes = _all_probes(math_root)
    aborted = _aborted(records)
    sources = {challenge: source for challenge, source, _ in _targets(math_root)}
    for p in [p for p in probes if p.probe_id in aborted]:
        probes += probe.single_tactic_probes(sources[p.challenge], p.challenge, p.theorem)
    for p in probes:
        target = lean / p.module_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(p.text, encoding="utf-8")
    manifest = [{k: v for k, v in asdict(p).items() if k != "text"} for p in probes]
    (lean / PROBE_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"wrote {len(probes)} probe files under {lean / PROBE_DIR}")


_MISSING_IMPORT = re.compile(
    r"object file \S+ of module \S+ does not exist|unknown module prefix '[^']*'|unknown package '[^']*'"
)

_ABORTED = re.compile(r"maximum recursion depth has been reached|failed with a nested error")


def _current(out: Path, entry: Dict[str, Any], lean: Path) -> bool:
    """A record exists for this probe and was made from the probe file as it is now (same SHA-256)."""
    path = out / f"{_probe_target(entry['probe_id'])}.json"
    if not path.exists():
        return False
    recorded = json.loads(path.read_text(encoding="utf-8")).get("file_sha256")
    return recorded == kernel_records.sha256_file(lean / entry["module_path"])


def _probe_target(probe_id: str) -> str:
    """A record target name: lower-case, `-` separated, prefixed like the other openai/math records."""
    return "openai-math-probe-" + re.sub(r"[^a-z0-9]+", "-", probe_id.lower()).strip("-")


def _qualified(entry: Dict[str, Any]) -> str:
    """The probe declaration's full name, as `#print axioms` prints it (the target's namespace plus the name)."""
    namespace = entry["theorem"].rsplit(".", 1)[0]
    return f"{namespace}.{entry['declaration']}"


def _check_one(entry: Dict[str, Any], lean: Path, out: Path, timeout: int, env: Dict[str, str]) -> str:
    """Elaborates one probe file and writes its kernel record and log (ADR-DISCOVERY-092 format)."""
    target = _probe_target(entry["probe_id"])
    path = lean / entry["module_path"]
    cmd = ["lake", "env", "lean", entry["module_path"]]
    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=lean, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False
        )
        output, code = proc.stdout.decode("utf-8", errors="replace"), proc.returncode
    except subprocess.TimeoutExpired as exc:
        output, code = (exc.stdout or b"").decode("utf-8", errors="replace"), None
    wall = time.monotonic() - started
    blocked = f"the kernel run did not finish within {timeout} s" if code is None else ""
    if not blocked and _MISSING_IMPORT.search(output):
        # The file imports modules that were never built here (e.g. ComparatorChallenges.* support files): the probe
        # did not reach elaboration, so it is a non-verdict, not a FAIL.
        blocked = "an imported module is not built in this environment: " + _MISSING_IMPORT.search(output).group(0)
    if not blocked and _ABORTED.search(output):
        # A tactic raised an error `first` cannot catch, so the remaining tactics of the menu never ran.
        blocked = "the tactic menu was aborted before every tactic ran: " + _ABORTED.search(output).group(0)
    declaration = _qualified(entry)
    log = (
        f"# kernel-check lean_file {target}\n# file: {entry['module_path']} (generated probe, mode {entry['mode']})\n"
        f"# file_sha256: {kernel_records.sha256_file(path)}\n# command: {shlex.join(cmd)}\n"
        f"# probe of: {entry['theorem']}; checked declaration: {declaration}\n"
        f"{output}{kernel_records.FOOTER}{-1 if code is None else code}\n"
    )
    record = kernel_records.build(
        target=target,
        kind="lean_file",
        source={
            "repository": "openai/math",
            "commit": cov.SOURCE_COMMIT,
            "path": f"lean/{entry['module_path']}",
            "generated_by": "scripts/cases/trivial_witness_probe_report.py",
        },
        file_sha256=kernel_records.sha256_file(path),
        toolchain=env["toolchain"],
        lean_version=env["lean_version"],
        mathlib_rev=env["mathlib_rev"],
        theorems=[declaration],
        log=log,
        kernel_log=f"{target}.log",
        wall_time_s=wall,
        checked_by=f"local:{platform.node()}",
        date=formal_provenance.utc_now(),
        blocked_reason=blocked,
        extra={
            "probe": {
                "probe_id": entry["probe_id"],
                "mode": entry["mode"],
                "target_theorem": entry["theorem"],
                "meaning": probe.meaning(entry["mode"]),
            }
        },
    )
    (out / f"{target}.log").write_bytes(log.encode("utf-8"))
    (out / f"{target}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"{entry['probe_id']}: {record['result']} ({record['wall_time_s']} s)"


def run(math_root: Path, out: Path, only: str, timeout: int, jobs: int) -> None:
    """Elaborates the probes `jobs` at a time; a probe that already has a record in `out` is skipped (resumable)."""
    lean = Path(math_root) / "lean"
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((lean / PROBE_DIR / "manifest.json").read_text(encoding="utf-8"))
    todo = [e for e in manifest if (not only or only in e["probe_id"]) and not _current(out, e, lean)]
    version = subprocess.run(["lake", "env", "lean", "--version"], cwd=lean, capture_output=True, text=True)
    packages = json.loads((lean / "lake-manifest.json").read_text(encoding="utf-8")).get("packages", [])
    env = {
        "toolchain": (lean / "lean-toolchain").read_text(encoding="utf-8").strip(),
        "lean_version": version.stdout.strip().splitlines()[-1] if version.returncode == 0 else "",
        "mathlib_rev": next((p.get("rev", "") for p in packages if p.get("name") == "mathlib"), ""),
    }
    print(f"{len(todo)} probes to run, {jobs} at a time; {env}", flush=True)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for line in pool.map(lambda e: _check_one(e, lean, out, timeout, env), todo):
            print(line, flush=True)


def report(records: Path) -> None:
    """Folds the kernel records of a probe run into vacuity_probe.json, each verified against its log first."""
    by_probe = {}
    for path in sorted(Path(records).glob("openai-math-probe-*.json")):
        record = kernel_records.load(path)  # Raises when a record does not match its log.
        by_probe[record["probe"]["probe_id"]] = (path.resolve(), record)
    data = json.loads(OUT.read_text(encoding="utf-8"))
    for row in data["lean_probes"]["probes"]:
        found = by_probe.get(row["probe_id"])
        if found is None:
            row["outcome"] = probe.LeanOutcome.NOT_RUN.value
            continue
        path, record = found
        row["kernel_result"] = record["result"]
        row["outcome"] = probe.outcome_from_kernel(record["result"]).value
        row["kernel_record"] = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        row["wall_time_s"] = record["wall_time_s"]
        row["reasons"] = record["reasons"]
    probes = data["lean_probes"]["probes"]
    data["lean_probes"]["summary"] = dict(Counter(r["outcome"] for r in probes))
    data["lean_probes"]["by_mode"] = {
        mode: dict(Counter(r["outcome"] for r in probes if r["mode"] == mode))
        for mode in sorted({r["mode"] for r in probes})
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(data["lean_probes"]["summary"], data["lean_probes"]["by_mode"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["static", "prepare", "run", "report"])
    parser.add_argument("--out", type=Path, help="directory for the kernel records of a probe run")
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--math-root", type=Path)
    parser.add_argument("--only", default="")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    if args.command == "static":
        static(args.corpus or args.math_root)
    elif args.command == "prepare":
        prepare(args.math_root, args.out)
    elif args.command == "run":
        run(args.math_root, args.out, args.only, args.timeout, args.jobs)
    else:
        report(args.out)


if __name__ == "__main__":
    main()
