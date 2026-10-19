"""
python/cli/formal.py - `coresearcher formal run | analyze | doctor` (ADR-DISCOVERY-068).

Two phases, after the tool design of Google's Open Agentic Science Engine (OASE, Apache 2.0):

    coresearcher formal run --hypothesis H.json [--rival R.json] [--consequence "..."] --out raw/formal
      -> raw/formal/<name>.request.json    the request, including the formalizer messages when prose is given
      -> raw/formal/<name>.response.json   the raw formalizer outputs and the reports computed at run time
      -> raw/formal/<name>.meta.json       sidecar: outputs[{path, sha256, bytes}], parameters, relays, versions
      stdout: the three paths, nothing else

    coresearcher formal analyze raw/formal/<name>.meta.json
      -> raw/formal/<name>.analysis.json   source_sha256, threshold_set, metrics, verdict, mandatory_relays
      stdout: the analysis path and one summary line

`run` performs the non-deterministic act (the formalizer call, when prose is given) and records it. `analyze` is
offline and deterministic: it checks every output checksum, re-runs the gate from the stored raw outputs and z3 or
enumeration from the stored formal object, and compares its result with the run's, report by report. Network access
is refused while it runs. It never replaces a differing `.analysis.json` (exit 9) unless `--overwrite` is given.

`coresearcher formal doctor` reports which capabilities are present: z3, a Lean toolchain, a formalizer model.

Exit codes: 0 decided; 3 artifact missing, malformed or checksum mismatch; 4 threshold unresolved; 7 formalizer
endpoint unreachable; 8 capability missing; 9 invalid input or refusal to overwrite; 10 UNDECIDED (solver);
11 formalization ambiguous or failed; 12 analysis does not reproduce the run.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from python.discovery import formal_pipeline, formal_provenance, formal_status, formal_thresholds
from python.discovery.formal_status import FormalStatus

TOOL = "coresearcher"
SIDECAR_SCHEMA = "coresearcher.formal.sidecar/v1"
ANALYSIS_SCHEMA = "coresearcher.formal.analysis/v1"
# Fields of an analysis record that describe the run of `analyze`, not its result (OASE _VOLATILE_ANALYSIS_FIELDS).
VOLATILE_ANALYSIS_FIELDS = (
    "timestamp",
    "written_by",
    "work_order_id",
    "cli_integrity",
    "env_version",
    "capability_state",
)


class CliError(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------------------
# Environment stamps and capabilities
# ---------------------------------------------------------------------------


def env_version() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "z3": formal_provenance.z3_version(),
        "platform": sys.platform,
    }


def cli_integrity() -> Optional[str]:
    """`git describe --dirty --always` of the engine checkout, when it is one. A stamp, not science."""
    try:
        out = subprocess.run(
            ["git", "describe", "--dirty", "--always"],
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def _lean_binary() -> Optional[str]:
    return shutil.which("lean") or shutil.which("lake")


def capability_state() -> Dict[str, str]:
    state = {"z3": "available" if formal_provenance.z3_version() else "unavailable"}
    state["lean"] = "available" if _lean_binary() else "unavailable"
    has_model = bool(os.getenv("FORMALIZER_MODEL") or os.getenv("FORMALIZER_GATE_MODELS"))
    state["formalizer"] = "configured" if has_model else "unconfigured"
    return state


def formalizer_clients() -> Dict[str, Any]:
    """Clients for the configured formalizer model(s); empty when none is configured (the request is then BLOCKED)."""
    from python.discovery.formalizer import ChatClient

    names = [m.strip() for m in os.getenv("FORMALIZER_GATE_MODELS", "").split(",") if m.strip()]
    if names:
        return {name: ChatClient(model=name) for name in names}
    if not os.getenv("FORMALIZER_MODEL"):
        return {}
    client = ChatClient()
    return {client.model: client}


@contextlib.contextmanager
def offline() -> Iterator[None]:
    """Refuses every network connection while phase 2 runs: analyze must reach nothing but the files it was given."""

    def refuse(*_args, **_kwargs):
        raise CliError("formal analyze is offline; a network connection was attempted.", formal_status.EXIT_REFUSAL)

    saved = (socket.socket.connect, socket.socket.connect_ex, socket.create_connection)
    socket.socket.connect, socket.socket.connect_ex, socket.create_connection = refuse, refuse, refuse
    try:
        yield
    finally:
        socket.socket.connect, socket.socket.connect_ex, socket.create_connection = saved


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8", newline="\n")


def _read_json(path: Path, what: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CliError(f"{what} not found: {path}", formal_status.EXIT_ARTIFACT) from exc
    except (OSError, ValueError) as exc:
        raise CliError(f"{what} is not readable JSON: {path} ({exc})", formal_status.EXIT_ARTIFACT) from exc


def _output_entry(path: Path) -> Dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.name, "sha256": formal_provenance.sha256_bytes(data), "bytes": len(data)}


def _thresholds_from_flags(flags: List[str]) -> formal_thresholds.ThresholdSet:
    base = formal_thresholds.active()
    overrides: Dict[str, Any] = {}
    for item in flags or []:
        key, sep, raw = item.partition("=")
        if not sep:
            raise CliError(f"--threshold expects KEY=VALUE, got {item!r}.", formal_status.EXIT_REFUSAL)
        try:
            overrides[key.strip()] = json.loads(raw)
        except ValueError:
            overrides[key.strip()] = raw
    if not overrides:
        return base
    try:
        return base.with_overrides(overrides, "flag", "command-line --threshold overrides")
    except formal_thresholds.ThresholdError as exc:
        raise CliError(str(exc), formal_status.EXIT_THRESHOLD) from exc


def _exit_for(response: Dict[str, Any]) -> int:
    status = FormalStatus(response["formal_status"])
    return formal_status.exit_code(status, response.get("_exception"))


# ---------------------------------------------------------------------------
# formal run
# ---------------------------------------------------------------------------


def _request_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    prose = args.prose
    if args.prose_file:
        prose = Path(args.prose_file).read_text(encoding="utf-8")
    hypothesis = _read_json(Path(args.hypothesis), "hypothesis") if args.hypothesis else None
    try:
        return formal_pipeline.make_request(
            hypothesis=hypothesis,
            prose=prose,
            hypothesis_id=args.hypothesis_id,
            variable_schema=_read_json(Path(args.variable_schema), "variable schema") if args.variable_schema else None,
            rivals=[_read_json(Path(p), "rival") for p in args.rival or []],
            consequences=list(args.consequence or []),
            observations=_read_json(Path(args.observations), "observations") if args.observations else [],
            max_examples=args.max_examples,
            backend=args.backend,
            samples=args.samples,
            include_lean=args.lean,
        )
    except ValueError as exc:
        raise CliError(str(exc), formal_status.EXIT_REFUSAL) from exc


def run(args: argparse.Namespace, clients: Optional[Dict[str, Any]] = None) -> int:
    """Phase 1. `clients` is injectable for tests; by default the configured formalizer model(s) are used."""
    request = _request_from_args(args)
    thresholds = _thresholds_from_flags(args.threshold)
    if request["input_kind"] == "prose":
        from python.discovery.formalizer import build_messages

        request["formalizer_messages"] = build_messages(request["prose"], request["variable_schema"])
        if clients is None:
            try:
                clients = formalizer_clients()
            except ValueError:
                clients = {}
    name = args.name or f"F-{formal_provenance.sha256_canonical(request)[:12]}"
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    paths = {kind: out / f"{name}.{kind}.json" for kind in ("request", "response", "meta")}
    if paths["meta"].exists() and not args.overwrite:
        raise CliError(
            f"{paths['meta']} already exists; choose another --name or --out, or pass --overwrite.",
            formal_status.EXIT_REFUSAL,
        )
    started = formal_provenance.utc_now()
    with formal_thresholds.using(thresholds):
        response = formal_pipeline.compute(request, clients=clients)
        threshold_record = thresholds.record()
    exception = response.pop("_exception", None)
    _write_json(paths["request"], request)
    _write_json(paths["response"], response)
    endpoint = None
    if request["input_kind"] == "prose":
        endpoint = (os.getenv("FORMALIZER_BASE_URL") or "http://localhost:11434/v1").rstrip("/")
    warnings = [response["reason"]] if response["reason"] else []
    sidecar = {
        "schema": SIDECAR_SCHEMA,
        "tool": TOOL,
        "subcommand": "formal run",
        "work_order_id": os.getenv("CORESEARCHER_WORK_ORDER") or None,
        "cli_version": formal_provenance.engine_version(),
        "cli_integrity": cli_integrity(),
        "env_version": env_version(),
        "interpreter": sys.executable,
        "endpoint": endpoint,
        "parameters": {k: v for k, v in request.items() if k not in ("hypothesis", "rivals", "formalizer_messages")},
        **threshold_record,
        "timestamp": started,
        "completed": formal_provenance.utc_now(),
        "outputs": [_output_entry(paths["request"]), _output_entry(paths["response"])],
        "formal_status": response["formal_status"],
        "warnings": warnings + [r["message"] for r in response["mandatory_relays"]],
        "mandatory_relays": response["mandatory_relays"],
        "capability_state": capability_state(),
    }
    _write_json(paths["meta"], sidecar)
    for kind in ("request", "response", "meta"):
        print(paths[kind])
    if response["formal_status"] != FormalStatus.DECIDED.value:
        print(f"{response['formal_status']}: {response['reason']}", file=sys.stderr)
    return formal_status.exit_code(FormalStatus(response["formal_status"]), exception)


# ---------------------------------------------------------------------------
# formal analyze
# ---------------------------------------------------------------------------


def _strip_volatile(data: Any) -> Any:
    """Recursively drops the volatile provenance fields, so two records compare on what they found."""
    if isinstance(data, dict):
        return {
            k: _strip_volatile(v)
            for k, v in data.items()
            if k not in VOLATILE_ANALYSIS_FIELDS and k not in formal_provenance.VOLATILE_FIELDS
        }
    if isinstance(data, list):
        return [_strip_volatile(v) for v in data]
    return data


def comparable(record: Dict[str, Any]) -> Dict[str, Any]:
    return _strip_volatile(record)


def _compare_with_run(run_response: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
    """Report-by-report comparison of the run's response and the recomputed one, on comparable fields."""
    mismatches: List[str] = []
    if run_response.get("formal_status") != response["formal_status"]:
        mismatches.append(
            f"formal_status: run {run_response.get('formal_status')} != analyze {response['formal_status']}"
        )
    try:
        before = formal_pipeline.report_digests(run_response)
    except (KeyError, TypeError) as exc:
        raise CliError(f"The run's response is not a formal response ({exc}).", formal_status.EXIT_ARTIFACT) from exc
    after = formal_pipeline.report_digests(response)
    if [d["report"] for d in before] != [d["report"] for d in after]:
        mismatches.append("The set of reports differs between run and analyze.")
    for b, a in zip(before, after):
        for key in ("input_sha256", "output_sha256", "threshold_set"):
            if b[key] != a[key]:
                mismatches.append(f"{b['report']}.{key}: run {b[key]} != analyze {a[key]}")
    same_bytes = formal_provenance.canonical(
        comparable(_without_exception(run_response))
    ) == formal_provenance.canonical(comparable(_without_exception(response)))
    if not same_bytes and not mismatches:
        mismatches.append("The responses differ outside the report digests.")
    return {
        "reproduces_run": not mismatches,
        "reports_compared": len(after),
        "mismatches": mismatches,
    }


def _without_exception(response: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in response.items() if k != "_exception"}


def _resolve_meta(target: str) -> Path:
    path = Path(target)
    if path.name.endswith(".meta.json"):
        return path
    for suffix in (".response.json", ".request.json", ".analysis.json"):
        if path.name.endswith(suffix):
            return path.with_name(path.name[: -len(suffix)] + ".meta.json")
    return path.with_name(path.name + ".meta.json")


def analyze(args: argparse.Namespace) -> int:
    """Phase 2: offline, deterministic re-analysis of a stored run."""
    meta_path = _resolve_meta(args.target)
    sidecar = _read_json(meta_path, "sidecar")
    if not isinstance(sidecar, dict) or sidecar.get("schema") != SIDECAR_SCHEMA:
        raise CliError(f"{meta_path} is not a coresearcher formal sidecar.", formal_status.EXIT_ARTIFACT)
    files: Dict[str, Path] = {}
    for entry in sidecar.get("outputs", []):
        path = meta_path.parent / entry["path"]
        if not path.is_file():
            raise CliError(f"Declared output {path} is missing.", formal_status.EXIT_ARTIFACT)
        digest = formal_provenance.sha256_bytes(path.read_bytes())
        if digest != entry["sha256"]:
            raise CliError(
                f"{path.name} does not match its recorded sha256 ({digest} != {entry['sha256']}); it changed since run.",
                formal_status.EXIT_ARTIFACT,
            )
        files[path.name.rsplit(".", 2)[-2]] = path
    if set(files) != {"request", "response"}:
        raise CliError(f"{meta_path} must declare a request and a response output.", formal_status.EXIT_ARTIFACT)
    request = _read_json(files["request"], "request")
    run_response = _read_json(files["response"], "response")
    thresholds = _thresholds_from_flags(args.threshold)
    stored = run_response.get("formalizer") or {}
    if request.get("input_kind") == "prose" and not stored.get("raw_outputs"):
        raise CliError(
            "The run stored no formalizer outputs (it did not reach the gate); there is nothing to re-analyze offline.",
            formal_status.EXIT_ARTIFACT,
        )
    with formal_thresholds.using(thresholds), offline():
        response = formal_pipeline.compute(
            request, clients=None, raw_outputs=stored.get("raw_outputs"), specs=stored.get("specs")
        )
    exception = response.pop("_exception", None)
    comparison = _compare_with_run(run_response, response)
    comparison["thresholds_match_run"] = sidecar.get("thresholds_applied") == thresholds.applied()
    record: Dict[str, Any] = {
        "record_type": "analysis",
        "schema": ANALYSIS_SCHEMA,
        "source": files["response"].name,
        "source_sha256": formal_provenance.sha256_bytes(files["response"].read_bytes()),
        "request": files["request"].name,
        "request_sha256": formal_provenance.sha256_bytes(files["request"].read_bytes()),
        "sidecar": meta_path.name,
        "cli_version": formal_provenance.engine_version(),
        "cli_integrity": cli_integrity(),
        "env_version": env_version(),
        "timestamp": formal_provenance.utc_now(),
        **thresholds.record(),
        "metrics": formal_pipeline.metrics(response),
        "formal_status": response["formal_status"],
        "verdict": formal_pipeline.verdict(response),
        "assessment": {
            "formal_status": response["formal_status"],
            "reason": response["reason"],
            **comparison,
        },
        "mandatory_relays": response["mandatory_relays"],
        "reports": response["reports"],
        "formalization_gate": response["formalization_gate"],
        "lean": response["lean"],
        "written_by": os.getenv("CORESEARCHER_AGENT") or "unattributed",
        "work_order_id": os.getenv("CORESEARCHER_WORK_ORDER") or None,
        "capability_state": capability_state(),
    }
    out = Path(args.out) if args.out else meta_path.with_name(meta_path.name[: -len(".meta.json")] + ".analysis.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not args.overwrite:
        existing = None
        with contextlib.suppress(OSError, ValueError):
            existing = json.loads(out.read_text(encoding="utf-8"))
        if isinstance(existing, dict) and comparable(existing) == comparable(
            json.loads(json.dumps(record, default=str))
        ):
            print(out)
            print(f"{out.name} already holds an identical analysis; left as it is.", file=sys.stderr)
            return _analysis_exit(response, comparison, exception)
        who = existing.get("written_by", "an earlier run") if isinstance(existing, dict) else "an unreadable file"
        raise CliError(
            f"{out} already holds a different analysis (by {who}). Write this one elsewhere with --out and compare "
            "the two, or pass --overwrite if replacing it is what you mean. Two verdicts that disagree are evidence; "
            "one silently replaced is not.",
            formal_status.EXIT_REFUSAL,
        )
    _write_json(out, record)
    print(out)
    summary = ", ".join(f"{k}={v}" for k, v in record["verdict"].items() if not isinstance(v, dict)) or "no verdict"
    print(f"{record['formal_status']} ({summary}); reproduces_run={comparison['reproduces_run']}")
    return _analysis_exit(response, comparison, exception)


def _analysis_exit(response: Dict[str, Any], comparison: Dict[str, Any], exception) -> int:
    if not comparison["reproduces_run"] and comparison["thresholds_match_run"]:
        print("The analysis does not reproduce the run under the same thresholds.", file=sys.stderr)
        return formal_status.EXIT_NOT_REPRODUCED
    return formal_status.exit_code(FormalStatus(response["formal_status"]), exception)


# ---------------------------------------------------------------------------
# formal doctor
# ---------------------------------------------------------------------------


def doctor(args: argparse.Namespace) -> int:
    """Which formal capabilities are present. Exit 0 when z3 works (offline analysis is possible), else 8."""
    report: Dict[str, Any] = {"cli_version": formal_provenance.engine_version(), "env_version": env_version()}
    z3_ok = False
    try:
        import z3

        solver = z3.Solver()
        x = z3.Real("x")
        solver.add(x > 0, x < 1)
        z3_ok = solver.check() == z3.sat
        report["z3"] = {"status": "available" if z3_ok else "broken", "version": z3.get_version_string()}
    except ImportError as exc:
        report["z3"] = {"status": "unavailable", "detail": str(exc)}
    lean = _lean_binary()
    if lean:
        try:
            out = subprocess.run([lean, "--version"], capture_output=True, text=True, timeout=30)
            version = (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else ""
        except (OSError, subprocess.SubprocessError) as exc:
            version = f"could not run: {type(exc).__name__}"
        report["lean"] = {
            "status": "available",
            "binary": lean,
            "version": version,
            "note": "Theorems are still NOT_KERNEL_CHECKED until compiled against Mathlib (formal_lean.py).",
        }
    else:
        report["lean"] = {"status": "unavailable", "note": "Lean theorems stay NOT_KERNEL_CHECKED."}
    models = [m.strip() for m in os.getenv("FORMALIZER_GATE_MODELS", "").split(",") if m.strip()]
    if os.getenv("FORMALIZER_MODEL"):
        models = models or [os.environ["FORMALIZER_MODEL"]]
    from python.discovery.formalizer import PROMPT_VERSION, prompt_sha256

    formalizer: Dict[str, Any] = {
        "status": "configured" if models else "unconfigured",
        "models": models,
        "base_url": (os.getenv("FORMALIZER_BASE_URL") or "http://localhost:11434/v1").rstrip("/"),
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": prompt_sha256(),
    }
    if not models:
        formalizer["note"] = "Prose requests are BLOCKED; formal objects are still evaluated."
    if args.probe and models:
        import httpx

        try:
            httpx.get(f"{formalizer['base_url']}/models", timeout=5).raise_for_status()
            formalizer["endpoint"] = "reachable"
        except Exception as exc:  # Any transport or HTTP failure.
            formalizer["endpoint"] = f"unreachable ({type(exc).__name__})"
    report["formalizer"] = formalizer
    try:
        thresholds = formal_thresholds.active()
        override = formal_thresholds.find_override_file()
        report["thresholds"] = {
            **thresholds.record(),
            "override_file": str(override) if override else None,
        }
    except formal_thresholds.ThresholdError as exc:
        report["thresholds"] = {"status": "blocked", "detail": str(exc)}
    report["relay_codes"] = sorted(formal_status.RELAY_CODES)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if z3_ok else formal_status.EXIT_DEPENDENCY


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------


def add_parser(subparsers) -> None:
    p_formal = subparsers.add_parser("formal", help="Formal hypotheses: two-phase run/analyze with provenance")
    sub = p_formal.add_subparsers(dest="formal_command")

    p_run = sub.add_parser("run", help="Phase 1: formalize (if prose) and evaluate; write request, response, sidecar")
    source = p_run.add_mutually_exclusive_group(required=True)
    source.add_argument("--hypothesis", help="Formal hypothesis JSON file")
    source.add_argument("--prose", help="Hypothesis in prose (calls the formalizer and the self-consistency gate)")
    source.add_argument("--prose-file", help="File with the hypothesis in prose")
    p_run.add_argument("--hypothesis-id", default="H", help="Id given to a formalized hypothesis")
    p_run.add_argument("--variable-schema", help="JSON file with the variables the formalizer must use")
    p_run.add_argument("--rival", action="append", help="Rival formal hypothesis JSON file (repeatable)")
    p_run.add_argument("--consequence", action="append", help="Predicate to check for entailment (repeatable)")
    p_run.add_argument("--observations", help="JSON file with a list of observations")
    p_run.add_argument("--max-examples", type=int, default=5)
    p_run.add_argument("--backend", default="auto", choices=("auto", "enumeration", "smt"))
    p_run.add_argument("--samples", type=int, default=None, help="Formalizer samples (default: gate_samples)")
    p_run.add_argument("--lean", action="store_true", help="Also state each consequence as a Lean 4 theorem")
    p_run.add_argument("--threshold", action="append", help="Override a threshold for this run: KEY=VALUE")
    p_run.add_argument("--out", default=os.path.join("raw", "formal"), help="Output directory")
    p_run.add_argument("--name", default=None, help="Artifact base name (default: digest of the request)")
    p_run.add_argument("--overwrite", action="store_true", help="Replace an existing run with the same name")

    p_an = sub.add_parser("analyze", help="Phase 2: offline, deterministic re-analysis of a stored run")
    p_an.add_argument("target", help="The run's .meta.json (or its base path)")
    p_an.add_argument("--threshold", action="append", help="Re-analyze under a changed threshold: KEY=VALUE")
    p_an.add_argument("--out", default=None, help="Analysis path (default: next to the sidecar)")
    p_an.add_argument("--overwrite", action="store_true", help="Replace a differing existing analysis")

    p_doc = sub.add_parser("doctor", help="Report z3, Lean and formalizer availability and the thresholds in force")
    p_doc.add_argument("--probe", action="store_true", help="Also contact the formalizer endpoint")


def main(args: argparse.Namespace) -> int:
    commands = {"run": run, "analyze": analyze, "doctor": doctor}
    if not getattr(args, "formal_command", None):
        print("usage: coresearcher formal {run,analyze,doctor} ...", file=sys.stderr)
        return 2
    try:
        return commands[args.formal_command](args)
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code
    except formal_thresholds.ThresholdError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return formal_status.EXIT_THRESHOLD
