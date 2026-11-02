"""
python/discovery/kernel_records.py - Recorded Lean kernel runs, the only way into KERNEL_CHECKED (ADR-DISCOVERY-091).

A kernel record is written by the run that checked a Lean file (`scripts/lean/kernel_check.py`, run by the
`Lean kernel checks` workflow on a Linux runner). It pins what ran and what came out:

| Field                 | Meaning                                                                               |
|-----------------------|---------------------------------------------------------------------------------------|
| `target`, `kind`      | What was checked: `lean_file` (one of our files) or `comparator` (an openai/math      |
|                       | Comparator challenge checked with comparator + landrun).                              |
| `source`              | Where the checked file comes from (repository, commit, path).                        |
| `file_sha256`         | SHA-256 of the checked Lean file (the challenge file for Comparator).                 |
| `toolchain`           | The elan toolchain, and `lean_version` the output of `lean --version`.                |
| `mathlib_rev`         | Mathlib commit from the project's lake-manifest.json.                                |
| `theorems`, `axioms_by_theorem`, `axioms` | Output of `#print axioms` for every checked theorem, and its union. |
| `wall_time_s`         | Wall time of the kernel run.                                                          |
| `result`              | PASS, FAIL or BLOCKED (`reasons` says why it is not PASS).                            |
| `kernel_log`, `kernel_log_sha256` | The full run log, stored next to the record, and its digest.             |
| `checked_by`          | The run that produced the record (a GitHub Actions run URL, or a named machine).      |

Rules:
- The result is recomputed from the log, never trusted from the record. The log ends with a footer the runner
  writes (`# kernel-check: exit_code=N`), and the axioms are re-parsed from the `#print axioms` lines in it.
- PASS needs: exit code 0, no Lean error line, at least one theorem, an axioms line for every theorem, only the
  permitted axioms (`propext`, `Quot.sound`, `Classical.choice`; never `sorryAx`), and for Comparator its success
  line. Anything else is FAIL.
- BLOCKED means the kernel did not run or did not finish (landrun unavailable, a timeout, a build that never
  reached the check). It is a non-verdict: it says nothing about the proof, and it never climbs.
- A record counts only when it is hash-verified: the stored log hashes to `kernel_log_sha256`, the recomputed
  result and axioms equal the recorded ones, and the record hashes to the digest the climb cites.
- Only a verified PASS record lets a claim climb to KERNEL_CHECKED, in the claim history (`trust_ladder`) and in the
  registry (`cited_registry`). A FAIL or BLOCKED record, or a record whose hashes do not match, never does.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from python.discovery import formal_provenance, formal_trust

SCHEMA = "coresearcher.kernel-record/v1"
PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"
RESULTS = (PASS, FAIL, BLOCKED)
KINDS = ("lean_file", "comparator")
PERMITTED_AXIOMS = formal_trust.PERMITTED_AXIOMS
COMPARATOR_OK = "Your solution is okay!"
FOOTER = "# kernel-check: exit_code="
# Evidence a KERNEL_CHECKED step carries, beyond the trust ladder's own fields.
EVIDENCE_KEYS = ("kernel_record", "kernel_record_sha256", "kernel_record_path")
# The fields of the record the trust ladder's KERNEL_CHECKED rung names (trust_ladder.REQUIRED_EVIDENCE).
LADDER_FIELDS = ("toolchain", "axioms", "kernel_log_sha256", "checked_by")

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
# Names may contain primes (`foo'`), so the name runs up to the last quote before the phrase.
_DEPENDS = re.compile(r"'([^\n]+?)' depends on axioms: \[([^\]]*)\]")
_NO_AXIOMS = re.compile(r"'([^\n]+?)' does not depend on any axioms")
_ERROR = re.compile(r"^(?:\S*:\d+:\d+: error|error:)", re.MULTILINE)
_FOOTER = re.compile(r"^" + re.escape(FOOTER) + r"(-?\d+)\s*$", re.MULTILINE)
_ROOT = Path(__file__).resolve().parents[2]
RECORDS_DIR = _ROOT / "records" / "kernel"


class KernelRecordError(ValueError):
    """A record that is malformed, does not match its log, or cannot support the step it is cited for."""


def sha256_file(path: Path) -> str:
    return formal_provenance.sha256_bytes(Path(path).read_bytes())


def record_sha256(record: Dict[str, Any]) -> str:
    """The digest a climb cites: SHA-256 of the canonical JSON of the record."""
    return formal_provenance.sha256_canonical(record)


def parse_axioms(log: str) -> Dict[str, List[str]]:
    """`#print axioms` output in the log, as theorem -> sorted axioms (empty when it depends on none)."""
    out: Dict[str, List[str]] = {}
    for name, listed in _DEPENDS.findall(log):
        out[name] = sorted(a.strip() for a in listed.replace("\n", " ").split(",") if a.strip())
    for name in _NO_AXIOMS.findall(log):
        out.setdefault(name, [])
    return out


def parse_exit_code(log: str) -> Optional[int]:
    """The exit code in the runner's footer; the last footer wins. None when there is no footer."""
    found = _FOOTER.findall(log)
    return int(found[-1]) if found else None


def evaluate(kind: str, log: str, theorems: List[str], blocked_reason: str = "") -> Tuple[str, List[str], Dict]:
    """The result a log supports: (result, reasons, axioms by theorem). The same log always gives the same result."""
    axioms = parse_axioms(log)
    if blocked_reason.strip():
        return BLOCKED, [blocked_reason.strip()], axioms
    reasons: List[str] = []
    code = parse_exit_code(log)
    if code is None:
        reasons.append("the log has no exit-code footer")
    elif code != 0:
        reasons.append(f"the kernel run exited with code {code}")
    if _ERROR.search(log):
        reasons.append("the log has a Lean error line")
    if not theorems:
        reasons.append("no theorem was checked")
    missing = [t for t in theorems if t not in axioms]
    if missing:
        reasons.append(f"no #print axioms output for {missing}")
    extra = sorted({a for t in theorems for a in axioms.get(t, [])} - set(PERMITTED_AXIOMS))
    if extra:
        reasons.append(f"depends on axioms outside {list(PERMITTED_AXIOMS)}: {extra}")
    if kind == "comparator" and COMPARATOR_OK not in log:
        reasons.append(f"Comparator did not print {COMPARATOR_OK!r}")
    return (FAIL if reasons else PASS), reasons, axioms


def build(
    *,
    target: str,
    kind: str,
    source: Dict[str, Any],
    file_sha256: str,
    toolchain: str,
    lean_version: str,
    mathlib_rev: str,
    theorems: List[str],
    log: str,
    kernel_log: str,
    wall_time_s: float,
    checked_by: str,
    date: str,
    blocked_reason: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """A record whose result, reasons and axioms are computed from the log it will be stored with."""
    if kind not in KINDS:
        raise KernelRecordError(f"Unknown kind {kind!r}; one of {list(KINDS)}.")
    result, reasons, by_theorem = evaluate(kind, log, theorems, blocked_reason)
    checked = {t: by_theorem[t] for t in theorems if t in by_theorem}
    record = {
        "schema": SCHEMA,
        "target": target,
        "kind": kind,
        "source": dict(source),
        "file_sha256": file_sha256,
        "toolchain": toolchain,
        "lean_version": lean_version,
        "mathlib_rev": mathlib_rev,
        "theorems": list(theorems),
        "axioms_by_theorem": checked,
        "axioms": sorted({a for v in checked.values() for a in v}),
        "permitted_axioms": list(PERMITTED_AXIOMS),
        "wall_time_s": round(float(wall_time_s), 1),
        "exit_code": parse_exit_code(log),
        "result": result,
        "reasons": reasons,
        "status": "KERNEL_CHECKED" if result == PASS else "NOT_KERNEL_CHECKED",
        "kernel_log": kernel_log,
        "kernel_log_sha256": formal_provenance.sha256_bytes(log.encode("utf-8")),
        "checked_by": checked_by,
        "date": date,
    }
    record.update(extra or {})
    return record


def record_reasons(record: Any) -> List[str]:
    """Why a record, read on its own, cannot support a KERNEL_CHECKED step (empty when it can)."""
    if not isinstance(record, dict):
        return ["no kernel record is on record"]
    reasons = []
    if record.get("schema") != SCHEMA:
        reasons.append(f"kernel record schema is {record.get('schema')!r}, not {SCHEMA}")
    if record.get("result") != PASS:
        reasons.append(f"kernel record result is {record.get('result')!r}, not PASS: it never climbs")
    if record.get("status") != "KERNEL_CHECKED":
        reasons.append(f"kernel record status is {record.get('status')!r}")
    for key in ("toolchain", "checked_by", "kernel_log", "target"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            reasons.append(f"kernel record {key} is missing")
    for key in ("file_sha256", "kernel_log_sha256"):
        if not isinstance(record.get(key), str) or not _HEX64.match(record[key]):
            reasons.append(f"kernel record {key} is missing or not a SHA-256")
    axioms = record.get("axioms")
    if not isinstance(axioms, list) or not record.get("theorems"):
        reasons.append("kernel record has no theorems or no axioms list")
    elif set(axioms) - set(PERMITTED_AXIOMS):
        reasons.append(f"kernel record depends on axioms outside {list(PERMITTED_AXIOMS)}")
    return reasons


def verify(record: Dict[str, Any], log_bytes: bytes) -> List[str]:
    """Why a record does not match its log (empty when it does): the hash, the result and the axioms are recomputed."""
    reasons = []
    if formal_provenance.sha256_bytes(log_bytes) != record.get("kernel_log_sha256"):
        return ["the stored log does not hash to kernel_log_sha256"]
    log = log_bytes.decode("utf-8", errors="replace")
    blocked = "; ".join(record.get("reasons", [])) if record.get("result") == BLOCKED else ""
    result, _, by_theorem = evaluate(record.get("kind", ""), log, list(record.get("theorems", [])), blocked)
    if result != record.get("result"):
        reasons.append(f"the log supports result {result}, but the record says {record.get('result')}")
    checked = {t: by_theorem[t] for t in record.get("theorems", []) if t in by_theorem}
    if checked != record.get("axioms_by_theorem"):
        reasons.append("the axioms in the log differ from the recorded axioms_by_theorem")
    if sorted({a for v in checked.values() for a in v}) != record.get("axioms"):
        reasons.append("the recorded axioms are not the union of the logged axioms")
    if parse_exit_code(log) != record.get("exit_code"):
        reasons.append("the exit code in the log differs from the recorded exit_code")
    return reasons


def resolve(path: str | Path) -> Path:
    """A record path as cited in evidence: absolute, or relative to the repository root."""
    p = Path(path)
    return p if p.is_absolute() else _ROOT / p


def in_records_dir(name: str) -> Path:
    """A record path under records/kernel/, refusing anything that resolves outside it (for API callers)."""
    path = (RECORDS_DIR / name).resolve()
    if RECORDS_DIR.resolve() not in path.parents or path.suffix != ".json":
        raise KernelRecordError(f"{name!r} is not a .json record under records/kernel/.")
    return path


def load(path: str | Path) -> Dict[str, Any]:
    """Reads a record and its log and verifies them. Raises KernelRecordError when they do not match."""
    path = resolve(path)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise KernelRecordError(f"Cannot read kernel record {path}: {exc}") from exc
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        raise KernelRecordError(f"{path} is not a {SCHEMA} record.")
    log_path = path.parent / str(record.get("kernel_log", ""))
    if not record.get("kernel_log") or not log_path.is_file():
        raise KernelRecordError(f"The log {log_path} of {path.name} is missing.")
    problems = verify(record, log_path.read_bytes())
    if problems:
        raise KernelRecordError(f"{path.name}: " + "; ".join(problems))
    return record


def load_dir(directory: str | Path) -> List[Dict[str, Any]]:
    """Every record in a directory, each verified, as {path, record} in path order."""
    directory = resolve(directory)
    return [{"path": p, "record": load(p)} for p in sorted(directory.rglob("*.json"))]


def ladder_evidence(path: str | Path) -> Dict[str, Any]:
    """The evidence of a KERNEL_CHECKED step, taken from a verified PASS record. Refuses anything else."""
    record = load(path)
    problems = record_reasons(record)
    if problems:
        raise KernelRecordError("; ".join(problems))
    evidence = {k: record[k] for k in LADDER_FIELDS}
    evidence.update(
        {"kernel_record": record, "kernel_record_sha256": record_sha256(record), "kernel_record_path": str(path)}
    )
    return evidence


def evidence_reasons(evidence: Dict[str, Any], verify_log: bool = True) -> List[str]:
    """Why a KERNEL_CHECKED step's evidence does not come from a recorded, hash-verified PASS run.

    The evidence must embed the record, cite its digest, and repeat the record's toolchain, axioms, log digest and
    checker. With `verify_log` the record is also re-read from `kernel_record_path` and checked against its log.
    """
    record = evidence.get("kernel_record")
    reasons = record_reasons(record)
    if reasons:
        return reasons
    if evidence.get("kernel_record_sha256") != record_sha256(record):
        reasons.append("kernel_record_sha256 does not match the embedded record")
    for key in LADDER_FIELDS:
        if evidence.get(key) != record.get(key):
            reasons.append(f"evidence {key} differs from the kernel record's")
    if verify_log:
        where = evidence.get("kernel_record_path")
        if not where:
            reasons.append("kernel_record_path is missing, so the run's log cannot be verified")
        else:
            try:
                stored = load(where)
            except KernelRecordError as exc:
                reasons.append(str(exc))
            else:
                if record_sha256(stored) != record_sha256(record):
                    reasons.append("the record at kernel_record_path differs from the embedded record")
    return reasons


def trust_check(record: Dict[str, Any], statement_sha256: Optional[str] = None) -> Dict[str, Any]:
    """The record in the shape `formal_trust.kernel_check_reasons` grades (ADR-080)."""
    return {
        "status": record.get("status"),
        "toolchain": record.get("toolchain"),
        "file_sha256": record.get("file_sha256"),
        "statement_sha256": statement_sha256,
        "axioms": list(record.get("axioms", [])),
        "checker": record.get("checked_by"),
        "kernel_record_sha256": record_sha256(record),
    }


def climb(claim, path: str | Path, date: str, reason: str):
    """Climbs a `trust_ladder.ClaimRecord` to KERNEL_CHECKED from the verified PASS record at `path`."""
    from python.discovery.trust_ladder import Rung

    return claim.climb(Rung.KERNEL_CHECKED, date, reason, ladder_evidence(path))


_DECL = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma)\s+([^\s(:{\[⦃]+)"
)
_NAMESPACE = re.compile(r"^\s*namespace\s+(\S+)")
_SECTION = re.compile(r"^\s*(?:noncomputable\s+)?section\b\s*(\S*)")
_END = re.compile(r"^\s*end\b\s*(\S*)")


def theorem_names(text: str) -> List[str]:
    """Fully qualified names of the theorems and lemmas a Lean file declares at the start of a line.

    Namespaces and sections are tracked so `#print axioms` can name each theorem after the file's last `end`.
    Block comments are skipped. This is a reader for our own files, not a Lean parser.
    """
    names: List[str] = []
    scopes: List[Tuple[str, str]] = []  # (kind, name) with kind "namespace" or "section"
    in_comment = 0
    for line in text.splitlines():
        if in_comment or line.lstrip().startswith("/-"):
            in_comment += line.count("/-") - line.count("-/")
            continue
        if m := _NAMESPACE.match(line):
            scopes.extend(("namespace", part) for part in m.group(1).split("."))
        elif m := _SECTION.match(line):
            scopes.append(("section", m.group(1)))
        elif m := _END.match(line):
            closing = m.group(1).split(".") if m.group(1) else [""]
            for _ in closing:
                if scopes:
                    scopes.pop()
        elif m := _DECL.match(line):
            name = m.group(1)
            if name.startswith("_root_."):
                names.append(name[len("_root_.") :])
            else:
                prefix = [n for kind, n in scopes if kind == "namespace"]
                names.append(".".join(prefix + [name]))
    return names
