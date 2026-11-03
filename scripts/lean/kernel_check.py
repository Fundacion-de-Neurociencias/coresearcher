"""Runs a Lean kernel check and writes its kernel record and log (ADR-DISCOVERY-092).

Runs on the Linux runner of the `Lean kernel checks` workflow (.github/workflows/lean-kernel.yml), not on the dev
box. Each subcommand writes <out>/<target>.json and <out>/<target>.log; the record's result is computed from the log
by python/discovery/kernel_records.py. The script exits 0 whatever the result (a FAIL or BLOCKED record is an
outcome, not a crash); `verify` exits 1 when a record does not match its log.

  python scripts/lean/kernel_check.py lean-file --project lean/kernel-check --file examples/x/X.lean --target x --out out
  python scripts/lean/kernel_check.py comparator --project math/lean --config ComparatorChallenges/X.json \
      --target x --out out --repository openai/math --commit <sha>
  python scripts/lean/kernel_check.py blocked --kind comparator --target x --reason "..." --out out
  python scripts/lean/kernel_check.py verify records/kernel
"""

import argparse
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
# The record modules need only the standard library. Registering the package without running its __init__ (which
# imports the whole engine) lets this script run on a bare Linux machine with only python3.
if "python.discovery" not in sys.modules:
    import types

    _pkg = types.ModuleType("python.discovery")
    _pkg.__path__ = [str(ROOT / "python" / "discovery")]
    sys.modules["python.discovery"] = _pkg

from python.discovery import formal_provenance, kernel_records  # noqa: E402


def _checked_by() -> str:
    if os.getenv("GITHUB_ACTIONS") == "true":
        server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
        return f"{server}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
    # Outside Actions, KERNEL_CHECKED_BY names the machine (for example "lenovo (WSL2)"); the host name otherwise.
    return f"local:{os.getenv('KERNEL_CHECKED_BY') or platform.node()}"


def _run(cmd: List[str], cwd: Path, timeout: float) -> Tuple[Optional[int], str, float]:
    """(exit code or None on timeout, merged output, wall seconds)."""
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False
        )
        out, code = proc.stdout, proc.returncode
    except subprocess.TimeoutExpired as exc:
        out, code = exc.stdout or b"", None
    except FileNotFoundError as exc:
        out, code = f"{exc}\n".encode(), 127
    return code, out.decode("utf-8", errors="replace"), time.monotonic() - start


def _oom_lines() -> List[str]:
    """Kernel log lines about processes killed for lack of memory (empty when there are none or dmesg is denied)."""
    # The kernel's OOM killer logs to dmesg; systemd-oomd (which can kill a whole `systemd-run --user` unit under
    # memory pressure) logs to its journal.
    marks = ("out of memory", "oom-kill", "killed process", "killed /")
    lines: List[str] = []
    for cmd in (["sudo", "-n", "dmesg"], ["sudo", "-n", "journalctl", "-q", "--no-pager", "-u", "systemd-oomd"]):
        code, out, _ = _run(cmd, ROOT, 60)
        if code == 0:
            lines += [line for line in out.splitlines() if any(m in line.lower() for m in marks)]
    return lines[-20:]


def _toolchain(project: Path) -> str:
    path = project / "lean-toolchain"
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def _mathlib_rev(project: Path) -> str:
    path = project / "lake-manifest.json"
    if not path.is_file():
        return ""
    for package in json.loads(path.read_text(encoding="utf-8")).get("packages", []):
        if package.get("name") == "mathlib":
            return package.get("rev", "")
    return ""


def _lean_version(project: Path) -> str:
    code, out, _ = _run(["lake", "env", "lean", "--version"], project, 300)
    return out.strip().splitlines()[-1] if code == 0 and out.strip() else ""


def _write(args, record_kwargs: dict, log: str) -> dict:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    record = kernel_records.build(
        target=args.target,
        log=log,
        kernel_log=f"{args.target}.log",
        checked_by=_checked_by(),
        date=formal_provenance.utc_now(),
        **record_kwargs,
    )
    (out / f"{args.target}.log").write_bytes(log.encode("utf-8"))
    (out / f"{args.target}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{args.target}: {record['result']} {'; '.join(record['reasons'])}")
    return record


def _footer(code: Optional[int]) -> str:
    return f"{kernel_records.FOOTER}{-1 if code is None else code}\n"


def lean_file(args) -> None:
    project = Path(args.project).resolve()
    source = (ROOT / args.file).resolve() if not Path(args.file).is_absolute() else Path(args.file)
    text = source.read_text(encoding="utf-8")
    theorems = kernel_records.theorem_names(text)
    wrapper = project / f"KernelCheck_{args.target.replace('-', '_')}.lean"
    wrapper.write_text(text.rstrip("\n") + "\n\n" + "".join(f"#print axioms {t}\n" for t in theorems), encoding="utf-8")
    cmd = ["lake", "env", "lean", wrapper.name]
    code, output, wall = _run(cmd, project, args.timeout)
    blocked = ""
    if code is None:
        blocked = f"the kernel run did not finish within {args.timeout:.0f} s"
    elif code == 127 and "No such file" in output:
        blocked = "lake is not installed on this machine"
    log = (
        f"# kernel-check lean_file {args.target}\n# file: {args.file}\n"
        f"# file_sha256: {kernel_records.sha256_file(source)}\n# command: {shlex.join(cmd)}\n"
        f"# #print axioms appended for: {', '.join(theorems)}\n{output}{_footer(code)}"
    )
    _write(
        args,
        {
            "kind": "lean_file",
            "source": {"repository": os.getenv("GITHUB_REPOSITORY", "local"), "commit": _git_head(), "path": args.file},
            "file_sha256": kernel_records.sha256_file(source),
            "toolchain": _toolchain(project),
            "lean_version": _lean_version(project),
            "mathlib_rev": _mathlib_rev(project),
            "theorems": theorems,
            "wall_time_s": wall,
            "blocked_reason": blocked,
        },
        log,
    )


def _git_head() -> str:
    code, out, _ = _run(["git", "rev-parse", "HEAD"], ROOT, 60)
    return out.strip() if code == 0 else ""


def comparator(args) -> None:
    project = Path(args.project).resolve()
    config_path = project / args.config
    config = json.loads(config_path.read_text(encoding="utf-8"))
    challenge = project / (config["challenge_module"].replace(".", "/") + ".lean")
    theorems = list(config.get("theorem_names", []))
    inner = ["lake", "env", "comparator", args.config]
    if args.systemd_run:
        cmd = [
            "systemd-run", "--user", "--pipe", "--wait", "--collect", "--quiet",
            "--property=RestrictAddressFamilies=~AF_UNIX", "-E", f"PATH={os.environ.get('PATH', '')}",
            "--working-directory", str(project), "--", *inner,
        ]  # fmt: skip
    else:
        cmd = inner
    code, output, wall = _run(cmd, project, args.timeout)
    blocked = ""
    if code is None:
        blocked = f"comparator did not finish within {args.timeout:.0f} s on the runner (no verdict on the proof)"
    elif code != 0 and kernel_records.COMPARATOR_OK not in output:
        # A build killed by the kernel's OOM killer prints nothing itself; the kernel log says so. The lines go into
        # the hashed log, and only then is the run recorded as BLOCKED rather than FAIL.
        oom = _oom_lines()
        if oom:
            output += "# kernel messages (dmesg) about killed processes:\n" + "".join(f"{line}\n" for line in oom)
            blocked = "the runner's kernel killed the build for lack of memory before Comparator reached a verdict"
    log = (
        f"# kernel-check comparator {args.target}\n# repository: {args.repository} @ {args.commit}\n"
        f"# config: {args.config} (sha256 {kernel_records.sha256_file(config_path)})\n"
        f"# challenge: {challenge.relative_to(project)} (sha256 {kernel_records.sha256_file(challenge)})\n"
        f"# command: {shlex.join(cmd)}\n{output}"
    )
    if code == 0 and kernel_records.COMPARATOR_OK in output:
        # Comparator already built the solution inside its sandbox; this only reads the built environment.
        probe = project / f"KernelAxioms_{args.target.replace('-', '_')}.lean"
        probe.write_text(
            f"import {config['solution_module']}\n\n" + "".join(f"#print axioms {t}\n" for t in theorems),
            encoding="utf-8",
        )
        code2, output2, wall2 = _run(["lake", "env", "lean", probe.name], project, args.timeout)
        wall += wall2
        log += f"# command: lake env lean {probe.name}\n{output2}"
        if code2 is None:
            blocked = "#print axioms did not finish within the time limit"
        code = code2
    log += _footer(code)
    _write(
        args,
        {
            "kind": "comparator",
            "source": {
                "repository": args.repository,
                "commit": args.commit,
                "path": f"lean/{challenge.relative_to(project).as_posix()}",
                "config": f"lean/{args.config}",
                "config_sha256": kernel_records.sha256_file(config_path),
                "solution_module": config["solution_module"],
            },
            "file_sha256": kernel_records.sha256_file(challenge),
            "toolchain": _toolchain(project),
            "lean_version": _lean_version(project),
            "mathlib_rev": _mathlib_rev(project),
            "theorems": theorems,
            "wall_time_s": wall,
            "blocked_reason": blocked,
            "extra": {"sandbox": {"landrun": args.landrun, "systemd_run_guard": bool(args.systemd_run)}},
        },
        log,
    )


def blocked(args) -> None:
    detail = Path(args.log).read_text(encoding="utf-8", errors="replace") if args.log else ""
    log = f"# kernel-check {args.kind} {args.target}: BLOCKED\n# reason: {args.reason}\n{detail}"
    source = json.loads(args.source) if args.source else {}
    _write(
        args,
        {
            "kind": args.kind,
            "source": source,
            "file_sha256": args.file_sha256 or "",
            "toolchain": args.toolchain or "",
            "lean_version": "",
            "mathlib_rev": args.mathlib_rev or "",
            "theorems": [],
            "wall_time_s": 0.0,
            "blocked_reason": args.reason,
        },
        log,
    )


def verify(args) -> None:
    """Verifies every record under a directory against its log and prints a Markdown summary."""
    bad = 0
    rows = ["| Target | Kind | Result | Axioms | Wall (s) | Toolchain | Reasons |", "|---|---|---|---|---|---|---|"]
    for path in sorted(Path(args.directory).rglob("*.json")):
        try:
            record = kernel_records.load(path)
        except kernel_records.KernelRecordError as exc:
            bad += 1
            rows.append(f"| {path.name} | ? | INVALID | | | | {exc} |")
            continue
        rows.append(
            f"| {record['target']} | {record['kind']} | {record['result']} | {', '.join(record['axioms']) or '-'} "
            f"| {record['wall_time_s']} | {record['toolchain']} | {'; '.join(record['reasons']) or '-'} |"
        )
    print("\n".join(rows))
    if bad:
        print(f"\n{bad} record(s) do not match their logs.")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("lean-file", help="check one of our Lean files against the kernel-check project")
    p.add_argument("--project", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--timeout", type=float, default=3600)
    p.set_defaults(func=lean_file)

    p = sub.add_parser("comparator", help="check an openai/math Comparator challenge")
    p.add_argument("--project", required=True, help="the lean/ directory of the openai/math checkout")
    p.add_argument("--config", required=True, help="config path relative to --project")
    p.add_argument("--target", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--repository", default="openai/math")
    p.add_argument("--commit", required=True)
    p.add_argument("--landrun", default="", help="landrun version or commit, for the record")
    p.add_argument("--systemd-run", action="store_true", help="wrap the run in systemd-run as Comparator advises")
    p.add_argument("--timeout", type=float, default=4 * 3600)
    p.set_defaults(func=comparator)

    p = sub.add_parser("blocked", help="record a check that could not run")
    p.add_argument("--kind", required=True, choices=kernel_records.KINDS)
    p.add_argument("--target", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--log", default="", help="a file whose text is appended to the log (the failing step's output)")
    p.add_argument("--source", default="", help="source as a JSON object")
    p.add_argument("--file-sha256", default="")
    p.add_argument("--toolchain", default="")
    p.add_argument("--mathlib-rev", default="")
    p.set_defaults(func=blocked)

    p = sub.add_parser("verify", help="verify every record under a directory against its log")
    p.add_argument("directory")
    p.set_defaults(func=verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
