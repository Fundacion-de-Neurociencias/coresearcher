"""
python/discovery/formal_provenance.py - Provenance of formal verdicts (ADR-DISCOVERY-068).

Every EvaluationReport, ComparisonReport, ConsequenceReport and formalization-gate result carries a `provenance`
block: which engine and solver produced it, under which thresholds, from which exact input, with which output.

Digests use the EvidenceGraph convention of ADR-DISCOVERY-067, defined once here: SHA-256 of the canonical JSON
(sorted keys, no whitespace, UTF-8, non-JSON values through `str`). `input_sha256` covers the operation, the formal
object(s) and the request parameters; `output_sha256` covers the verdict body of the report (everything except the
provenance block itself). Two reports with the same input digest and threshold set must have the same output digest;
`coresearcher formal analyze` checks exactly that.

`timestamp`, `python` and `platform` are volatile: they describe the run, not the result, and are left out when two
records are compared (see VOLATILE_FIELDS).
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from python.discovery import formal_thresholds

ENGINE = "coresearcher"
VOLATILE_FIELDS = ("timestamp", "python", "platform")


def canonical(data: Any) -> bytes:
    """Canonical JSON bytes (ADR-067 convention, shared with the evidence graph)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def sha256_canonical(data: Any) -> str:
    return hashlib.sha256(canonical(data)).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@lru_cache(maxsize=1)
def engine_version() -> str:
    """The installed coresearcher package version, else the version in pyproject.toml."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            return version(ENGINE)
        except PackageNotFoundError:
            pass
    except ImportError:  # pragma: no cover
        pass
    try:
        import tomllib

        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        return str(tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"])
    except (OSError, KeyError, ValueError):
        return "unknown"


@lru_cache(maxsize=1)
def z3_version() -> Optional[str]:
    try:
        import z3

        return z3.get_version_string()
    except ImportError:
        return None


def build(
    operation: str,
    inputs: Dict[str, Any],
    output_body: Dict[str, Any],
    backend: Optional[str],
    formalizer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """The provenance block of one formal result.

    `inputs` is the full request (formal objects and parameters); `output_body` is the report without provenance.
    The solver timeout is recorded whenever z3 could have been called; it is None for pure enumeration.
    """
    thresholds = formal_thresholds.active()
    record: Dict[str, Any] = {
        "engine": ENGINE,
        "engine_version": engine_version(),
        "operation": operation,
        "backend": backend,
        "z3_version": z3_version(),
        "solver_timeout_ms": thresholds.get("solver_timeout_ms") if backend in ("smt", "mixed") else None,
        "input_sha256": sha256_canonical({"operation": operation, **inputs}),
        "output_sha256": sha256_canonical(output_body),
        **thresholds.record(),
        "timestamp": utc_now(),
        "python": sys.version.split()[0],
        "platform": platform.system(),
    }
    if formalizer is not None:
        record["formalizer"] = formalizer
    return record


def comparable(provenance: Dict[str, Any]) -> Dict[str, Any]:
    """The provenance block without volatile fields."""
    return {k: v for k, v in provenance.items() if k not in VOLATILE_FIELDS}
