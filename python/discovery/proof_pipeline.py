"""
python/discovery/proof_pipeline.py - Reproducible pipeline for machine-checked obligation proofs, ADR-DISCOVERY-076.

A case (such as the Mahler scalar input) is a list of proof steps. Each step is a script that writes one JSON report,
depends on some source files, and records success under one or more dotted keys of its report. The pipeline keeps a
manifest with the SHA-256 of every source file and every report, plus the environment that produced them.

- `check` is the fast audit (seconds). Every report must exist and say verified. Its hash must match the manifest,
  and so must the hashes of the sources it depends on. A source edited after its proof makes that proof STALE: the
  ledger can no longer cite it until the step is rerun. Finally the claim status in the ledger is recomputed from
  its obligations by the weakest-link rule and compared with the stored one.
- `run` reruns steps (all, or by name) in dependency order and rewrites the manifest.

Hashes ignore line endings (the repository is checked out with CRLF on Windows) and the wall-clock "seconds"
fields of reports, so a rerun on another machine reproduces the same report hashes when the results agree.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from python.discovery.obligation_ledger import Status

ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class ProofStep:
    name: str
    script: str  # repository-relative path
    output: str  # repository-relative path of the JSON report
    verified_keys: List[str]  # dotted keys that must be true in the report
    sources: List[str]  # repository-relative paths the result depends on (the script is added automatically)
    args: List[str] = field(default_factory=list)
    minutes: float = 1.0  # rough cost with 8 workers, for planning

    def all_sources(self) -> List[str]:
        return sorted(set(self.sources) | {self.script})


def _strip_seconds(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_seconds(v) for k, v in obj.items() if k != "seconds"}
    if isinstance(obj, list):
        return [_strip_seconds(v) for v in obj]
    return obj


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def report_hash(path: Path) -> str:
    data = _strip_seconds(json.loads(path.read_text(encoding="utf-8")))
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _get(obj: Any, dotted: str) -> Any:
    for part in dotted.split("."):
        obj = obj[part] if isinstance(obj, dict) else None
    return obj


def environment() -> Dict[str, str]:
    import mpmath
    import numpy
    import sympy

    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "mpmath": mpmath.__version__,
        "sympy": sympy.__version__,
        "numpy": numpy.__version__,
    }
    try:
        env["git_commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        env["git_commit"] = "unknown"
    return env


def build_manifest(steps: Sequence[ProofStep], root: Path = ROOT) -> Dict[str, Any]:
    out: Dict[str, Any] = {"environment": environment(), "steps": {}}
    for st in steps:
        out["steps"][st.name] = {
            "script": st.script,
            "output": st.output,
            "output_sha256": report_hash(root / st.output),
            "sources": {s: source_hash(root / s) for s in st.all_sources()},
        }
    return out


def recompute_claim_status(ledger: Dict[str, Any]) -> str:
    """Weakest-link roll-up of a stored ledger (as obligation_ledger.Claim.status computes it)."""
    obs = ledger["claim"]["obligations"]
    statuses = [Status(o["status"]) for o in obs]
    if not statuses:
        return Status.OPEN.value
    if Status.REFUTED in statuses:
        return Status.REFUTED.value
    order = [
        Status.DISCHARGED_FORMAL,
        Status.DISCHARGED_SYMBOLIC,
        Status.DISCHARGED_INTERVAL,
        Status.CHECKED_NUMERIC,
        Status.CERTIFIED_BY_AUTHOR,
        Status.OPEN,
    ]
    return max(statuses, key=order.index).value


def check(
    steps: Sequence[ProofStep], manifest: Dict[str, Any], ledger_path: Optional[str] = None, root: Path = ROOT
) -> Dict[str, Any]:
    """Fast audit. Returns per-step findings and an overall `ok`."""
    report: Dict[str, Any] = {"steps": {}, "ok": True}
    for st in steps:
        f: Dict[str, Any] = {"problems": []}
        m = manifest.get("steps", {}).get(st.name)
        out = root / st.output
        if m is None:
            f["problems"].append("not in manifest")
        if not out.exists():
            f["problems"].append("report missing")
        else:
            data = json.loads(out.read_text(encoding="utf-8"))
            bad = [k for k in st.verified_keys if _get(data, k) is not True]
            if bad:
                f["problems"].append(f"not verified: {bad}")
            if m and report_hash(out) != m["output_sha256"]:
                f["problems"].append("report differs from manifest")
        if m:
            stale = [s for s in st.all_sources() if source_hash(root / s) != m["sources"].get(s)]
            if stale:
                f["problems"].append(f"STALE, sources changed since the proof ran: {stale}")
        f["status"] = "ok" if not f["problems"] else "fail"
        report["ok"] &= not f["problems"]
        report["steps"][st.name] = f
    if ledger_path:
        led = json.loads((root / ledger_path).read_text(encoding="utf-8"))
        stored, again = led["claim"]["status"], recompute_claim_status(led)
        report["ledger"] = {"stored_status": stored, "recomputed_status": again, "consistent": stored == again}
        report["ok"] &= stored == again
    return report


def run(steps: Sequence[ProofStep], names: Optional[Sequence[str]] = None, root: Path = ROOT) -> List[str]:
    """Rerun the named steps (all if None), in the given order. Returns the names that ran."""
    ran = []
    for st in steps:
        if names and st.name not in names:
            continue
        subprocess.run([sys.executable, "-W", "ignore", str(root / st.script), *st.args], cwd=root, check=True)
        ran.append(st.name)
    return ran
