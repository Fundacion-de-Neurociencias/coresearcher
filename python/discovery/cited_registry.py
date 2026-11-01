"""
python/discovery/cited_registry.py - Registry of cited results and premises, with dependency propagation
(ADR-DISCOVERY-083).

Two methods of docs/architecture/VERIFICATION_METHODOLOGY.md meet here:

- M6, errors live at the seams. In the openai/math revision benchmark the corrected defects were imported
  conventions (a sign taken from a cited lemma under another normalization) and hypotheses of cited theorems that
  were not met where the theorem was applied. A registry entry therefore stores a cited result's hypotheses (as
  formal predicates where possible) and its conventions (as typed tags), so every use can be checked.
- M11, when a premise falls, everything built on it must be re-examined. Dependency edges run from claims to the
  results and premises they use. Retracting or downgrading a premise flags every transitive dependent for
  re-evaluation and caps its trust-ladder rung (ADR-080) until it is re-checked.

Rules:
- The source reference is provenance. It never decides validity (ADR-066).
- A citation check never passes by default. A hypothesis counts as discharged only when the citing context's
  assumptions formally entail it (exact enumeration or z3). A lexical match is recorded as STATED_IN_TEXT, which is
  not a discharge. A convention present in the entry but absent from the citing context is UNSPECIFIED, not a match.
- Every operation that decides something carries an ADR-068 status and provenance. Undecidable, missing or failing
  checks are non-verdicts (UNDECIDED), never passes.
- The store is append-only in spirit. Re-registering an entry creates a new version, and every mutation is an
  event in a hash-chained log.
"""

from __future__ import annotations

import json
import os
import re
import threading
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import date as _date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from python.discovery import formal_provenance, formal_status, hash_chain, obligation_ledger
from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, hypothesis_from_dict

STORE_ENV = "CORESEARCHER_REGISTRY_PATH"
SCHEMA = "coresearcher.cited-registry/v1"

# Convention kinds with a fixed meaning. Other tags are allowed and compared the same way.
CONVENTION_KINDS = {
    "sign": "Sign or orientation convention (e.g. 'D = d + d^*' vs 'D = d - d^*', outward vs inward normal)",
    "normalization": "Normalization of a transform, measure or constant (e.g. Fourier 'e^{-2 pi i x xi}')",
    "units": "Units of a quantity (e.g. 'pg/mL')",
    "scale_direction": "Direction of a scale (e.g. 'higher is worse')",
    "validated_assay": "Assay or instrument under which a threshold or result was validated",
    "validated_population": "Population under which a threshold or result was validated",
    "computation_model": "Model of computation for a complexity statement (e.g. 'deterministic multitape TM')",
}

# Entry status. Only ACTIVE entries can support a CLEAR citation check.
ACTIVE = "ACTIVE"
DOWNGRADED = "DOWNGRADED"
RETRACTED = "RETRACTED"

# Per-hypothesis outcomes.
DISCHARGED = "DISCHARGED"  # the citing context's assumptions formally entail it
NOT_DISCHARGED = "NOT_DISCHARGED"  # a counterexample satisfies the context but violates the hypothesis
STATED_IN_TEXT = "STATED_IN_TEXT"  # only a lexical match; not a discharge
H_UNDECIDED = "UNDECIDED"  # no formal predicate, no context variables, contradictory context or solver failure

# Per-convention outcomes.
MATCH = "MATCH"
MISMATCH = "MISMATCH"
UNSPECIFIED = "UNSPECIFIED"

# Citation-check outcomes.
CLEAR = "CLEAR"  # entry active, every hypothesis discharged, every convention matched
FINDINGS = "FINDINGS"  # at least one convention mismatch, undischarged hypothesis, or a fallen premise
INCOMPLETE = "INCOMPLETE"  # nothing contradicts, but something is undecided or unspecified

RUNG_ORDER = ["CLAIMED", "STATEMENT_PUBLIC", "STATEMENT_AUDITED", "KERNEL_CHECKED", "INDEPENDENTLY_REPRODUCED"]


class RegistryError(ValueError):
    """An unknown id, a malformed entry, or an operation the registry refuses."""


@dataclass
class CitedHypothesis:
    text: str
    formal: str = ""  # predicate in the ADR-059 language over the citing context's variables
    phrases: List[str] = field(default_factory=list)  # literal phrases, as the manuscript audit expects (ADR-082)


@dataclass
class RegistryEntry:
    id: str
    source: str  # provenance only, e.g. "Smith 2019, Lemma 3.2" or a DOI
    statement: str
    key: str = ""  # bibliography key, for manuscript audits
    locator: str = ""  # e.g. "Lemma 3.2"
    kind: str = "result"  # result | premise | threshold | definition
    formal_statement: Optional[Dict[str, Any]] = None  # an ADR-059 hypothesis object, if available
    hypotheses: List[CitedHypothesis] = field(default_factory=list)
    conventions: Dict[str, str] = field(default_factory=dict)
    rung: str = "CLAIMED"
    status: str = ACTIVE
    version: int = 1
    status_reason: str = ""

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.:\-]{1,120}", self.id or ""):
            raise RegistryError(f"Entry id {self.id!r} must be 1-120 characters of [A-Za-z0-9_.:-].")
        if self.rung not in RUNG_ORDER:
            raise RegistryError(f"Unknown trust-ladder rung {self.rung!r}; one of {RUNG_ORDER}.")
        if self.status not in (ACTIVE, DOWNGRADED, RETRACTED):
            raise RegistryError(f"Unknown status {self.status!r}.")
        self.hypotheses = [h if isinstance(h, CitedHypothesis) else CitedHypothesis(**h) for h in self.hypotheses]
        self.conventions = {str(k): str(v) for k, v in self.conventions.items()}


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def check_conventions(entry: RegistryEntry, context: Dict[str, str]) -> List[Dict[str, str]]:
    """Compares each convention of the entry with the citing context. Absent in the context is UNSPECIFIED."""
    out = []
    for tag, value in sorted(entry.conventions.items()):
        if tag not in context:
            out.append({"tag": tag, "cited": value, "citing": "", "outcome": UNSPECIFIED})
        else:
            outcome = MATCH if _norm(value) == _norm(context[tag]) else MISMATCH
            out.append({"tag": tag, "cited": value, "citing": str(context[tag]), "outcome": outcome})
    return out


def check_hypothesis(hyp: CitedHypothesis, context: Dict[str, Any]) -> Dict[str, Any]:
    """Is the cited hypothesis implied by the citing context? Only a formal entailment counts."""
    result: Dict[str, Any] = {"text": hyp.text, "formal": hyp.formal, "outcome": H_UNDECIDED, "detail": ""}
    variables = context.get("variables") or []
    if hyp.formal and variables:
        assumptions = list(context.get("assumptions") or [])
        hypothesis = hypothesis_from_dict({
            "hypothesis_id": "citing-context",
            "variables": variables,
            "claims": assumptions or ["true"],
            "assumptions": [],
            "statement": "Assumptions of the citing context",
        })
        try:
            report = HypothesisEvaluator.entails(hypothesis, hyp.formal)
        except (FormalHypothesisError, ValueError) as exc:
            result["detail"] = f"not decided: {exc}"
            return result
        if report.vacuous:
            result["detail"] = "the citing context's assumptions are contradictory; nothing follows from them"
        elif report.entailed:
            result["outcome"] = DISCHARGED
            result["detail"] = "entailed by the citing context's assumptions"
        else:
            result["outcome"] = NOT_DISCHARGED
            result["counterexamples"] = report.to_dict().get("counterexamples", [])
            result["detail"] = "a state satisfies the citing assumptions but violates the hypothesis"
        return result
    text = context.get("text") or ""
    # Literal phrases only, never regular expressions: registry entries can come from API callers.
    lexical = any(p.lower() in text.lower() for p in hyp.phrases if p.strip())
    if text and lexical:
        result["outcome"] = STATED_IN_TEXT
        result["detail"] = "found lexically in the citing text; a statement is not a discharge"
    elif not hyp.formal:
        result["detail"] = "no formal predicate registered for this hypothesis"
    else:
        result["detail"] = "the citing context declares no variables, so the predicate cannot be evaluated"
    return result


def cite_check(entry: RegistryEntry, context: Dict[str, Any]) -> Dict[str, Any]:
    """Checks one use of a registered result. The outcome is CLEAR, FINDINGS or INCOMPLETE, with provenance."""
    conventions = check_conventions(entry, context.get("conventions") or {})
    hypotheses = [check_hypothesis(h, context) for h in entry.hypotheses]
    findings: List[str] = []
    if entry.status != ACTIVE:
        findings.append(f"cited entry is {entry.status}: {entry.status_reason or 'no reason recorded'}")
    findings += [f"convention '{c['tag']}' differs: cited {c['cited']!r}, citing {c['citing']!r}"
                 for c in conventions if c["outcome"] == MISMATCH]
    findings += [f"hypothesis not discharged: {h['text']}" for h in hypotheses if h["outcome"] == NOT_DISCHARGED]
    open_items = [c["tag"] for c in conventions if c["outcome"] == UNSPECIFIED]
    open_items += [h["text"] for h in hypotheses if h["outcome"] in (H_UNDECIDED, STATED_IN_TEXT)]
    if findings:
        outcome = FINDINGS
    elif open_items:
        outcome = INCOMPLETE
    else:
        outcome = CLEAR
    status = formal_status.FormalStatus.DECIDED if outcome != INCOMPLETE else formal_status.FormalStatus.UNDECIDED
    body = {
        "entry_id": entry.id,
        "entry_version": entry.version,
        "entry_status": entry.status,
        "entry_rung": entry.rung,
        "outcome": outcome,
        "findings": findings,
        "open": open_items,
        "conventions": conventions,
        "hypotheses": hypotheses,
        "formal_status": status.value,
        "scope_note": "Formal soundness of one use of a cited result; the source is provenance, never evidence.",
    }
    body["provenance"] = formal_provenance.build(
        "cite_check", {"entry": asdict(entry), "context": context}, dict(body), backend="auto")
    return body


def to_obligation(check: Dict[str, Any], obligation_id: str, source: str) -> obligation_ledger.Obligation:
    """The citation check as an ADR-076 obligation of kind 'import'.

    Only a CLEAR check whose hypotheses were all formally discharged becomes DISCHARGED_SYMBOLIC. Findings and open
    items keep the obligation OPEN with the details attached. A convention mismatch is a defect in the transfer, not
    a refutation of the citing claim, so it is never recorded as REFUTED.
    """
    obligation = obligation_ledger.Obligation(
        id=obligation_id,
        statement=f"Use of {check['entry_id']} v{check['entry_version']} is valid in the citing context",
        source=source,
        kind="import",
    )
    if check["outcome"] == CLEAR and all(h["outcome"] == DISCHARGED for h in check["hypotheses"]):
        obligation.discharges.append(obligation_ledger.Discharge(
            status=obligation_ledger.Status.DISCHARGED_SYMBOLIC,
            method="formal entailment of every cited hypothesis; every convention matched",
            scope="the citing context's declared variables and assumptions",
            by="CoResearcher",
            detail={"cite_check_output_sha256": check["provenance"]["output_sha256"]},
        ))
    return obligation


class Registry:
    """A persistent, versioned registry with dependency edges and a hash-chained event log."""

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        self.entries: Dict[str, List[Dict[str, Any]]] = {}  # id -> versions (dicts), newest last
        self.depends_on: Dict[str, List[str]] = {}  # claim or entry id -> ids it uses
        self.flags: Dict[str, Dict[str, Any]] = {}  # id -> re-evaluation flag
        self.events: List[Dict[str, Any]] = []
        if self.path and self.path.is_file():
            self._load()

    # --- persistence -----------------------------------------------------------------------------------------
    def _load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("schema") != SCHEMA:
            raise RegistryError(f"{self.path} is not a {SCHEMA} store.")
        self.entries = data.get("entries", {})
        self.depends_on = data.get("depends_on", {})
        self.flags = data.get("flags", {})
        self.events = data.get("events", [])
        self.verify_log()

    def _save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)

    def _event(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return hash_chain.append(self.events, kind, payload)

    def verify_log(self) -> None:
        """Refuses a store whose event chain was edited."""
        hash_chain.verify(self.events, RegistryError, "store")

    def to_dict(self) -> Dict[str, Any]:
        return {"schema": SCHEMA, "entries": self.entries, "depends_on": self.depends_on, "flags": self.flags,
                "events": self.events}

    # --- entries ---------------------------------------------------------------------------------------------
    def get(self, entry_id: str, version: Optional[int] = None) -> RegistryEntry:
        versions = self.entries.get(entry_id)
        if not versions:
            raise RegistryError(f"No registry entry {entry_id!r}.")
        data = versions[-1] if version is None else next((v for v in versions if v["version"] == version), None)
        if data is None:
            raise RegistryError(f"Entry {entry_id!r} has no version {version}.")
        return RegistryEntry(**data)

    def register(self, data: Dict[str, Any]) -> RegistryEntry:
        """Adds an entry, or a new version of an existing one. Status and rung history carry over."""
        with self._lock:
            data = dict(data)
            existing = self.entries.get(data.get("id", ""), [])
            data["version"] = existing[-1]["version"] + 1 if existing else 1
            if existing and "status" not in data:
                data["status"] = existing[-1]["status"]
                data["status_reason"] = existing[-1].get("status_reason", "")
            entry = RegistryEntry(**data)
            if entry.formal_statement is not None:
                hypothesis_from_dict(entry.formal_statement)  # validates the formal object early
            self.entries.setdefault(entry.id, []).append(asdict(entry))
            self._event("register", {"id": entry.id, "version": entry.version,
                                     "sha256": formal_provenance.sha256_canonical(asdict(entry))})
            self._save()
            return entry

    # --- dependencies ----------------------------------------------------------------------------------------
    def depend(self, node: str, on: str) -> Dict[str, Any]:
        """Records that `node` (a claim or entry id) uses `on` (an entry or another claim). Cycles are refused."""
        with self._lock:
            if node == on or self._reaches(on, node):
                raise RegistryError(f"Edge {node} -> {on} would create a dependency cycle.")
            uses = self.depends_on.setdefault(node, [])
            if on not in uses:
                uses.append(on)
                self._event("depend", {"node": node, "on": on})
                self._save()
            return {"node": node, "depends_on": list(uses)}

    def _reaches(self, start: str, target: str) -> bool:
        seen, queue = set(), deque([start])
        while queue:
            current = queue.popleft()
            if current == target:
                return True
            for nxt in self.depends_on.get(current, []):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return False

    def _dependents_of(self, node: str, include_self: bool = False) -> set:
        reverse: Dict[str, List[str]] = {}
        for src, targets in self.depends_on.items():
            for t in targets:
                reverse.setdefault(t, []).append(src)
        seen = {node} if include_self else set()
        queue = deque([node])
        while queue:
            current = queue.popleft()
            for parent in reverse.get(current, []):
                if parent not in seen:
                    seen.add(parent)
                    queue.append(parent)
        return seen

    def impact(self, node: str) -> Dict[str, Any]:
        """Every claim or entry that transitively depends on `node`."""
        dependents = sorted(self._dependents_of(node))
        return {"node": node, "dependents": dependents, "count": len(dependents),
                "flags": {d: self.flags[d] for d in dependents if d in self.flags}}

    # --- retraction and re-evaluation ------------------------------------------------------------------------
    def retract(self, entry_id: str, reason: str, downgrade_to: Optional[str] = None,
                when: Optional[str] = None) -> Dict[str, Any]:
        """Retracts an entry, or downgrades it to a lower rung, and flags every transitive dependent.

        A dependent's rung is capped at CLAIMED until `reevaluated()` clears its flag: whatever it had established
        rested on the fallen premise.
        """
        if not reason.strip():
            raise RegistryError("A retraction or downgrade needs a reason.")
        with self._lock:
            current = self.get(entry_id)
            data = asdict(current)
            if downgrade_to is None:
                data["status"] = RETRACTED
            else:
                if downgrade_to not in RUNG_ORDER or RUNG_ORDER.index(downgrade_to) >= RUNG_ORDER.index(current.rung):
                    raise RegistryError(f"Downgrade must go below {current.rung}; got {downgrade_to!r}.")
                data["status"] = DOWNGRADED
                data["rung"] = downgrade_to
            data["status_reason"] = reason
            data["version"] = current.version + 1
            self.entries[entry_id].append(asdict(RegistryEntry(**data)))
            day = when or _date.today().isoformat()
            dependents = sorted(self._dependents_of(entry_id))
            for d in dependents:
                self.flags[d] = {"requires_reevaluation": True, "cause": entry_id, "cause_status": data["status"],
                                 "reason": reason, "since": day, "rung_cap": "CLAIMED"}
            self._event("retract" if downgrade_to is None else "downgrade",
                        {"id": entry_id, "version": data["version"], "reason": reason, "dependents": dependents})
            self._save()
            return {"entry": data, "flagged": dependents, "count": len(dependents)}

    def reevaluated(self, node: str, note: str) -> Dict[str, Any]:
        """Clears a re-evaluation flag after the dependent was re-checked. The note says how."""
        if not note.strip():
            raise RegistryError("Clearing a flag needs a note saying how the dependent was re-checked.")
        with self._lock:
            flag = self.flags.pop(node, None)
            if flag is None:
                raise RegistryError(f"{node!r} has no re-evaluation flag.")
            self._event("reevaluated", {"node": node, "note": note, "cleared": flag})
            self._save()
            return {"node": node, "cleared": flag}

    def effective_rung(self, node: str, rung: str) -> str:
        """The rung a dependent may claim now: its own rung, capped while a re-evaluation flag is set."""
        flag = self.flags.get(node)
        if not flag:
            return rung
        cap = flag.get("rung_cap", "CLAIMED")
        return rung if RUNG_ORDER.index(rung) <= RUNG_ORDER.index(cap) else cap

    # --- manuscript audits -----------------------------------------------------------------------------------
    def as_import_list(self) -> List[Dict[str, Any]]:
        """Entries with a bibliography key and locator, in the list shape `manuscript_audit.audit` consumes.

        Only hypotheses with literal phrases travel: the manuscript audit matches text, and an outcome there is
        never more than MATCHED, which is not a discharge.
        """
        out: List[Dict[str, Any]] = []
        for versions in self.entries.values():
            entry = RegistryEntry(**versions[-1])
            if not entry.key or not entry.locator:
                continue
            out.append({
                "key": entry.key,
                "locator": entry.locator,
                "statement": entry.statement,
                "hypotheses": [{"text": h.text, "phrases": list(h.phrases)} for h in entry.hypotheses if h.phrases],
                "conventions": dict(entry.conventions),
            })
        return out


def default_store() -> Optional[Path]:
    value = os.getenv(STORE_ENV)
    return Path(value) if value else None


def load(path: Optional[Path] = None) -> Registry:
    return Registry(path if path is not None else default_store())


def entries_from(items: Iterable[Dict[str, Any]]) -> List[RegistryEntry]:
    return [RegistryEntry(**i) for i in items]


__all__: Sequence[str] = [
    "CONVENTION_KINDS", "Registry", "RegistryEntry", "CitedHypothesis", "RegistryError", "cite_check",
    "check_conventions", "check_hypothesis", "to_obligation", "load",
]
