"""
python/discovery/preregistration.py - Frozen acceptance checklists for claimed existence results (ADR-DISCOVERY-081).

A checklist fixes, before the claimant's formal statement is public, what that statement must say. It holds:

- a vocabulary: the features of a theory the obligations talk about (finite domains, or continuous reals);
- obligations: named requirements, each with a formal clause over the vocabulary, a category and its sources;
- a catalogue of trivial witnesses: cheap models that a careless statement could be satisfied by
  (see `trivial_witness`).

The checklist is frozen by the SHA-256 of its canonical JSON, recorded with a date in a lock file next to it. A
loaded checklist whose hash differs from its lock is refused, so a later audit cannot be re-anchored on the
claimant's own definitions. A change makes a new version with a new lock.

`coverage` decides, for a formal statement transcribed into the vocabulary, the status of every obligation:
COVERED (the statement entails the clause), OBJECT_DIFFERS (the statement entails its negation: it is about a
different object, such as a lattice or a torus) or NOT_ADDRESSED (neither). The questions go through
`HypothesisEvaluator.entails` (ADR-059), so enumeration or z3 decides them exactly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from python.discovery.formal_hypothesis import (
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    Predicate,
    Variable,
)

CANONICALIZATION = "json.dumps(sort_keys=True, separators=(',', ':'), ensure_ascii=False), UTF-8"
CATEGORIES = ("core", "scope", "qcd", "out_of_claim", "companion")


class FrozenSpecMismatch(ValueError):
    """The checklist on disk is not the one its lock file froze."""


class Coverage(str, Enum):
    COVERED = "COVERED"  # The transcribed statement entails the obligation's clause.
    OBJECT_DIFFERS = "OBJECT_DIFFERS"  # It entails the negation: the statement is about another kind of object.
    NOT_ADDRESSED = "NOT_ADDRESSED"  # Neither: the statement leaves the feature free.


def canonical_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def spec_sha256(data: Any) -> str:
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


@dataclass(frozen=True)
class Obligation:
    id: str
    title: str
    category: str
    applies_to: List[str]
    requirement: str
    formal_clause: str
    sources: List[Dict[str, str]]
    lean_markers: List[str] = field(default_factory=list)
    lean_counter_markers: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Witness:
    id: str
    title: str
    kind: str
    facts: List[str]
    note: str = ""
    references: List[str] = field(default_factory=list)


@dataclass
class Checklist:
    data: Dict[str, Any]
    sha256: str
    lock: Optional[Dict[str, Any]] = None

    @property
    def id(self) -> str:
        return self.data["id"]

    @property
    def version(self) -> str:
        return self.data["version"]

    @property
    def variables(self) -> Dict[str, Variable]:
        out = {}
        for name, spec in self.data["vocabulary"].items():
            if spec.get("continuous"):
                out[name] = Variable(name, continuous=True, lower=spec.get("lower"), upper=spec.get("upper"))
            else:
                out[name] = Variable(name, tuple(spec["domain"]))
        return out

    @property
    def obligations(self) -> List[Obligation]:
        fields = Obligation.__dataclass_fields__
        return [Obligation(**{k: v for k, v in o.items() if k in fields}) for o in self.data["obligations"]]

    @property
    def witnesses(self) -> List[Witness]:
        fields = Witness.__dataclass_fields__
        return [Witness(**{k: v for k, v in w.items() if k in fields}) for w in self.data.get("witnesses", [])]

    def obligation(self, obligation_id: str) -> Obligation:
        for o in self.obligations:
            if o.id == obligation_id:
                return o
        raise KeyError(obligation_id)

    def in_claim(self, claim: Optional[str] = None) -> List[Obligation]:
        """Obligations a claim must meet: everything except out-of-claim ones, filtered by `applies_to`."""
        return [
            o
            for o in self.obligations
            if o.category != "out_of_claim" and (claim is None or claim in o.applies_to)
        ]


def validate(data: Dict[str, Any]) -> None:
    """Structural checks; every formal clause and witness fact must parse over the vocabulary."""
    for key in ("id", "version", "frozen_on", "vocabulary", "obligations"):
        if key not in data:
            raise FormalHypothesisError(f"Checklist lacks {key!r}.")
    names = list(data["vocabulary"])
    refs = set(data.get("references", {}))
    seen = set()
    for o in data["obligations"]:
        if o["id"] in seen:
            raise FormalHypothesisError(f"Duplicate obligation {o['id']!r}.")
        seen.add(o["id"])
        if o["category"] not in CATEGORIES:
            raise FormalHypothesisError(f"Obligation {o['id']!r} has unknown category {o['category']!r}.")
        if not o.get("sources"):
            raise FormalHypothesisError(f"Obligation {o['id']!r} cites no source.")
        for source in o["sources"]:
            if source["ref"] not in refs:
                raise FormalHypothesisError(f"Obligation {o['id']!r} cites unknown reference {source['ref']!r}.")
        Predicate(o["formal_clause"], names)
    for w in data.get("witnesses", []):
        for fact in w["facts"]:
            Predicate(fact, names)


def load(path: Path, lock_path: Optional[Path] = None) -> Checklist:
    """Loads a checklist and, when a lock is given (or found next to it), refuses a hash mismatch."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(data)
    digest = spec_sha256(data)
    if lock_path is None:
        candidate = Path(path).with_suffix(".lock.json")
        lock_path = candidate if candidate.exists() else None
    lock = None
    if lock_path is not None:
        lock = json.loads(Path(lock_path).read_text(encoding="utf-8"))
        if lock["sha256"] != digest:
            raise FrozenSpecMismatch(
                f"{Path(path).name} hashes to {digest}, but its lock froze {lock['sha256']} on {lock['frozen_on']}. "
                "A frozen checklist is never edited; make a new version."
            )
        if lock["version"] != data["version"] or lock["frozen_on"] != data["frozen_on"]:
            raise FrozenSpecMismatch("The lock's version or date differs from the checklist's.")
    return Checklist(data=data, sha256=digest, lock=lock)


def make_lock(data: Dict[str, Any], spec_file: str) -> Dict[str, Any]:
    return {
        "spec": spec_file,
        "id": data["id"],
        "version": data["version"],
        "frozen_on": data["frozen_on"],
        "sha256": spec_sha256(data),
        "canonicalization": CANONICALIZATION,
    }


# ---------------------------------------------------------------------------
# Deciding predicates over the vocabulary
# ---------------------------------------------------------------------------


def _used(expressions: Sequence[str], names: Sequence[str]) -> List[str]:
    used = set()
    for e in expressions:
        used |= Predicate(e, names).variables_used
    return [n for n in names if n in used]


def decide(checklist: Checklist, facts: Sequence[str], clause: str) -> str:
    """Whether `facts` force `clause`: 'ENTAILED', 'REFUTED' (they force its negation) or 'OPEN'.

    Only the variables the facts and the clause mention enter the question, so enumeration stays small; any
    continuous variable sends it to z3. Contradictory facts are rejected rather than read as entailing everything.
    """
    key = (checklist.sha256, tuple(facts), clause)
    if key not in _DECISIONS:
        _DECISIONS[key] = _decide(checklist, facts, clause)
    return _DECISIONS[key]


_DECISIONS: Dict[Any, str] = {}  # Decisions are pure functions of the frozen vocabulary, the facts and the clause.


def _relevant(facts: Sequence[str], clause: str, names: Sequence[str]) -> List[str]:
    """The facts connected to the clause through shared variables. Given consistent facts, the others cannot
    change the answer, and leaving them out keeps each question to a few variables."""
    reach = Predicate(clause, names).variables_used
    pending = [(f, Predicate(f, names).variables_used) for f in facts]
    chosen: List[str] = []
    grew = True
    while grew:
        grew = False
        for f, used in list(pending):
            if used & reach:
                reach = reach | used
                chosen.append(f)
                pending.remove((f, used))
                grew = True
    return [f for f in facts if f in chosen]


def _consistent(checklist: Checklist, facts: Sequence[str]) -> None:
    key = (checklist.sha256, tuple(facts), None)
    if key in _DECISIONS:
        return
    names = list(checklist.variables)
    used = _used(facts, names) or [names[0]]
    hypothesis = Hypothesis("facts", [checklist.variables[n] for n in used], claims=["True"], assumptions=list(facts))
    if HypothesisEvaluator.entails(hypothesis, "True").vacuous:
        raise FormalHypothesisError(f"The facts {list(facts)} are contradictory.")
    _DECISIONS[key] = "CONSISTENT"


def _decide(checklist: Checklist, facts: Sequence[str], clause: str) -> str:
    _consistent(checklist, facts)
    names = list(checklist.variables)
    facts = _relevant(facts, clause, names)
    used = _used(list(facts) + [clause], names) or [names[0]]
    variables = [checklist.variables[n] for n in used]
    hypothesis = Hypothesis("decide", variables, claims=["True"], assumptions=list(facts))
    positive = HypothesisEvaluator.entails(hypothesis, clause)
    if positive.entailed:
        return "ENTAILED"
    if HypothesisEvaluator.entails(hypothesis, f"not ({clause})").entailed:
        return "REFUTED"
    return "OPEN"


@dataclass
class CoverageRow:
    obligation: str
    title: str
    category: str
    clause: str
    coverage: str
    formal_text: str = ""  # The claimant's text the decision rests on.
    note: str = ""


def coverage(
    checklist: Checklist,
    transcription: Dict[str, Any],
    claim: Optional[str] = None,
    include_out_of_claim: bool = True,
) -> List[CoverageRow]:
    """Decides every obligation against a transcribed formal statement.

    `transcription` has `facts` (predicates over the vocabulary, each read from the formal statement) and optional
    `quotes` and `notes` keyed by obligation id. The facts are hand transcriptions: the solver decides the
    transcription, so each fact should quote its source text (ADR-070 practice).
    """
    facts = transcription["facts"]
    rows = []
    for o in checklist.obligations:
        if o.category == "out_of_claim" and not include_out_of_claim:
            continue
        if claim is not None and o.category != "out_of_claim" and claim not in o.applies_to:
            continue
        result = decide(checklist, facts, o.formal_clause)
        status = {"ENTAILED": Coverage.COVERED, "REFUTED": Coverage.OBJECT_DIFFERS, "OPEN": Coverage.NOT_ADDRESSED}
        rows.append(
            CoverageRow(
                obligation=o.id,
                title=o.title,
                category=o.category,
                clause=o.formal_clause,
                coverage=status[result].value,
                formal_text=transcription.get("quotes", {}).get(o.id, ""),
                note=transcription.get("notes", {}).get(o.id, ""),
            )
        )
    return rows
