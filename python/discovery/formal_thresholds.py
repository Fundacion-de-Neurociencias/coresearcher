"""
python/discovery/formal_thresholds.py - Named, versioned cutoffs of the formal layer (ADR-DISCOVERY-068).

Every number that decides something in the formal pipeline (how large a state space may be enumerated, how long z3
may think, how many formalizer samples the gate draws and what counts as a majority) lives in one threshold set:

1. defaults declared here, under a version tag and with the provenance of each value;
2. a project override file, `.coresearcher/formal_thresholds.json`, found by walking up from the working directory
   (or named by the CORESEARCHER_FORMAL_THRESHOLDS environment variable);
3. per-invocation overrides (a CLI flag, a request field), recorded as such.

Every report records the set it used (`threshold_set`, `thresholds_applied`, `threshold_sources`), so a verdict cites
its criterion and not just a value. A threshold declared UNRESOLVED, or unset to null by an override file, raises
ThresholdError when it is read: the pipeline blocks rather than substitute a plausible number.

Override file shape:

    {"set": "formal", "provenance": "why these values", "overrides": {"solver_timeout_ms": 30000}}

The design mirrors `tools/oase/core/thresholds.py` of Google's Open Agentic Science Engine (Apache 2.0), so an OASE
adapter can quote these records unchanged.
"""

from __future__ import annotations

import contextlib
import contextvars
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

OVERRIDE_DIR = ".coresearcher"
OVERRIDE_FILE = "formal_thresholds.json"
OVERRIDE_ENV = "CORESEARCHER_FORMAL_THRESHOLDS"


class _Unresolved:
    def __repr__(self) -> str:
        return "UNRESOLVED"


UNRESOLVED: Any = _Unresolved()  # A threshold with no defensible value; reading it raises.


class ThresholdError(RuntimeError):
    """A threshold is unknown, unresolved or malformed. The formal pipeline reports BLOCKED, never a verdict."""


@dataclass
class ThresholdSet:
    """A named, versioned bundle of decision thresholds."""

    name: str
    version: str
    values: Dict[str, Any]
    provenance: str
    overrides: Dict[str, Any] = field(default_factory=dict)
    override_sources: Dict[str, str] = field(default_factory=dict)  # key -> "project" | "flag"
    override_provenance: List[str] = field(default_factory=list)

    @property
    def tag(self) -> str:
        return f"{self.name}@{self.version}"

    def get(self, key: str) -> Any:
        if key not in self.values:
            raise ThresholdError(f"Unknown threshold {key!r} in set {self.tag}; declared: {sorted(self.values)}.")
        value = self.overrides.get(key, self.values[key])
        if value is UNRESOLVED or value is None:
            raise ThresholdError(
                f"Threshold {key!r} in set {self.tag} is unset. The formal layer will not substitute a value: set it "
                f"in {OVERRIDE_DIR}/{OVERRIDE_FILE} under 'overrides' with a justification in 'provenance'."
            )
        return value

    def applied(self) -> Dict[str, Any]:
        """The thresholds that resolve to a value, for the report."""
        out = {}
        for key in sorted(self.values):
            value = self.overrides.get(key, self.values[key])
            if value is not UNRESOLVED and value is not None:
                out[key] = value
        return out

    def unresolved(self) -> List[str]:
        return [k for k in sorted(self.values) if k not in self.applied()]

    def sources(self) -> Dict[str, str]:
        """Where each applied threshold came from: default | project | flag."""
        return {k: self.override_sources.get(k, "default") for k in self.applied()}

    def with_overrides(self, overrides: Dict[str, Any], source: str = "flag", provenance: str = "") -> "ThresholdSet":
        """A copy with more overrides on top. Unknown keys raise."""
        unknown = sorted(set(overrides) - set(self.values))
        if unknown:
            raise ThresholdError(f"Unknown threshold(s) {unknown} for set {self.tag}; declared: {sorted(self.values)}.")
        return ThresholdSet(
            self.name,
            self.version,
            dict(self.values),
            self.provenance,
            {**self.overrides, **overrides},
            {**self.override_sources, **{k: source for k in overrides}},
            self.override_provenance + ([provenance] if provenance else []),
        )

    def record(self) -> Dict[str, Any]:
        """The threshold block every formal report carries (field names follow OASE's `.analysis.json`)."""
        out: Dict[str, Any] = {
            "threshold_set": self.tag,
            "thresholds_applied": self.applied(),
            "threshold_sources": self.sources(),
            "threshold_provenance": "; ".join([self.provenance, *self.override_provenance]),
        }
        if self.unresolved():
            out["thresholds_unresolved"] = self.unresolved()
        return out


# Values and their sources. Changing a value means bumping the version, so old reports keep citing what they used.
FORMAL_DEFAULTS = ThresholdSet(
    name="formal",
    version="2026.10.1",
    provenance=(
        "max_states, max_assumptions_for_conflict_search: engineering caps of ADR-059 (exhaustive enumeration and "
        "subset search stay under a minute). solver_timeout_ms: ADR-060, per z3 call; a timeout is UNDECIDED. "
        "gate_samples, gate_max_samples, gate_temperature, gate_majority_fraction: ADR-064 and the N=3/5/7 "
        "ablation in FORMALIZER_GATE_RESULTS.md. formalizer_temperature, formalizer_seed: frozen decoding of the "
        "ADR-061 formalizer benchmark."
    ),
    values={
        "max_states": 2_000_000,
        "max_assumptions_for_conflict_search": 12,
        "solver_timeout_ms": 10_000,
        "gate_samples": 5,
        "gate_max_samples": 7,
        "gate_temperature": 0.7,
        "gate_majority_fraction": 0.5,  # A class wins only when its size is strictly above this fraction of N.
        "formalizer_temperature": 0.0,
        "formalizer_seed": 0,
    },
)


def find_override_file(start: Optional[Path] = None) -> Optional[Path]:
    """The project override file: CORESEARCHER_FORMAL_THRESHOLDS, else the nearest `.coresearcher/` walking up."""
    env = os.getenv(OVERRIDE_ENV)
    if env:
        path = Path(env)
        if not path.is_file():
            raise ThresholdError(f"{OVERRIDE_ENV} names {path}, which is not a file.")
        return path
    here = (start or Path.cwd()).resolve()
    for directory in (here, *here.parents):
        candidate = directory / OVERRIDE_DIR / OVERRIDE_FILE
        if candidate.is_file():
            return candidate
    return None


def load_thresholds(path: Optional[Path] = None, base: ThresholdSet = FORMAL_DEFAULTS) -> ThresholdSet:
    """Defaults plus the project override file, if there is one. A malformed file raises; it is never skipped."""
    path = path if path is not None else find_override_file()
    if path is None:
        return base
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ThresholdError(f"Cannot read threshold overrides {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("set", base.name) != base.name:
        raise ThresholdError(f'{path} must be an object with "set": "{base.name}".')
    overrides = data.get("overrides", {})
    if not isinstance(overrides, dict):
        raise ThresholdError(f"'overrides' in {path} must be an object.")
    provenance = str(data.get("provenance") or "")
    if overrides and not provenance:
        raise ThresholdError(f"{path} overrides thresholds without saying why: add a 'provenance' string.")
    return base.with_overrides(overrides, "project", f"project overrides ({Path(path).name}): {provenance}")


_ACTIVE: contextvars.ContextVar[Optional[ThresholdSet]] = contextvars.ContextVar("formal_thresholds", default=None)
_LOADED: Dict[tuple, ThresholdSet] = {}  # (override path, mtime) -> set; thresholds are read on every solver call.


def active() -> ThresholdSet:
    """The threshold set in force: the one installed by `using`, else defaults plus the project override file."""
    current = _ACTIVE.get()
    if current is not None:
        return current
    path = find_override_file()
    if path is None:
        return FORMAL_DEFAULTS
    key = (str(path.resolve()), path.stat().st_mtime_ns)
    if key not in _LOADED:
        _LOADED[key] = load_thresholds(path)
    return _LOADED[key]


def get(key: str) -> Any:
    return active().get(key)


@contextlib.contextmanager
def using(thresholds: ThresholdSet) -> Iterator[ThresholdSet]:
    """Runs a block under a given threshold set (the CLI and tests use it)."""
    token = _ACTIVE.set(thresholds)
    try:
        yield thresholds
    finally:
        _ACTIVE.reset(token)
