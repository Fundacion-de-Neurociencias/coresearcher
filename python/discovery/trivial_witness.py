"""
python/discovery/trivial_witness.py - Trivial-witness probe for existence statements (ADR-DISCOVERY-077).

An existence statement "there is a T with P(T)" can be kernel-checked and still say much less than its title: if a
cheap model satisfies P, the statement is true for a reason unrelated to the result it names. For quantum field
theory the cheap models are well known: the zero theory, the free (Gaussian) field, abelian Maxwell theory,
lower-dimensional versions, a theory on a finite torus, and a lattice theory that never takes the continuum limit.

Two tools, both driven by a frozen checklist (`preregistration`):

1. `probe` (semantic). P is a list of named clauses over the checklist vocabulary, transcribed from the statement.
   Each catalogued witness is a list of facts over the same vocabulary; features it leaves out are free. For every
   witness and clause, `preregistration.decide` asks whether the facts force the clause (SATISFIES), force its
   negation (EXCLUDES), or neither (UNDETERMINED); enumeration or z3 decides. The statement is
   VACUOUS_RELATIVE_TO_INTENT when some witness satisfies every clause, POSSIBLY_VACUOUS when no witness does but
   some is undetermined, and EXCLUDES_ALL_CATALOGUED otherwise. The last outcome is not fidelity: it says only that
   no catalogued cheap model passes.

2. `lint_exclusions` (syntactic). For a Lean file, the main theorem and every definition it uses (by name,
   transitively, as in `lean_junk_lint`) are searched for the markers each obligation pre-registers. A witness is
   ADDRESSED_IN_TEXT when some obligation that excludes it (decided as in 1) has a marker in that text, and
   NO_EXCLUDING_CLAUSE_FOUND otherwise. Counter-markers (a `Finset` of sites, `ℤ × ℤ`, `AddCircle`) are reported as
   text suggesting the statement's object has the witness's feature. The lint is a reading list for a human: a
   marker shows that the text mentions something, not that the clause means it. Semantic confirmation is always
   left to a human.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

from python.discovery.lean_junk_lint import _BOUNDARY, Declaration, _uses, strip_comments
from python.discovery.preregistration import Checklist, Obligation, Witness, decide


class WitnessResult(str, Enum):
    SATISFIES = "SATISFIES"  # The witness's facts force every clause of the statement.
    EXCLUDED = "EXCLUDED"  # Some clause is false for the witness.
    UNDETERMINED = "UNDETERMINED"  # No clause excludes it, but some clause depends on a feature the witness leaves free.


class ProbeOutcome(str, Enum):
    VACUOUS_RELATIVE_TO_INTENT = "VACUOUS_RELATIVE_TO_INTENT"
    POSSIBLY_VACUOUS = "POSSIBLY_VACUOUS"
    EXCLUDES_ALL_CATALOGUED = "EXCLUDES_ALL_CATALOGUED"


@dataclass
class WitnessReport:
    witness: str
    title: str
    kind: str
    result: str
    excluded_by: List[str]  # Clause names whose negation the witness's facts force.
    open_clauses: List[str]  # Clause names the witness's facts leave undecided.


@dataclass
class ProbeReport:
    statement: str
    checklist: str
    checklist_sha256: str
    clauses: Dict[str, str]
    outcome: str
    satisfied_by: List[str]
    undetermined: List[str]
    witnesses: List[WitnessReport] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


def probe(
    checklist: Checklist,
    clauses: Dict[str, str],
    statement: str = "statement",
    witnesses: Optional[Sequence[Witness]] = None,
) -> ProbeReport:
    """Tries every catalogued witness against the conjunction of `clauses` (name -> predicate)."""
    if not clauses:
        raise ValueError("A statement needs at least one clause; an empty predicate is satisfied by everything.")
    reports = []
    for w in witnesses if witnesses is not None else checklist.witnesses:
        decisions = {name: decide(checklist, w.facts, clause) for name, clause in clauses.items()}
        excluded_by = [n for n, d in decisions.items() if d == "REFUTED"]
        open_clauses = [n for n, d in decisions.items() if d == "OPEN"]
        if excluded_by:
            result = WitnessResult.EXCLUDED
        elif open_clauses:
            result = WitnessResult.UNDETERMINED
        else:
            result = WitnessResult.SATISFIES
        reports.append(WitnessReport(w.id, w.title, w.kind, result.value, excluded_by, open_clauses))
    satisfied = [r.witness for r in reports if r.result == WitnessResult.SATISFIES.value]
    undetermined = [r.witness for r in reports if r.result == WitnessResult.UNDETERMINED.value]
    if satisfied:
        outcome = ProbeOutcome.VACUOUS_RELATIVE_TO_INTENT
    elif undetermined:
        outcome = ProbeOutcome.POSSIBLY_VACUOUS
    else:
        outcome = ProbeOutcome.EXCLUDES_ALL_CATALOGUED
    return ProbeReport(
        statement=statement,
        checklist=f"{checklist.id} v{checklist.version}",
        checklist_sha256=checklist.sha256,
        clauses=dict(clauses),
        outcome=outcome.value,
        satisfied_by=satisfied,
        undetermined=undetermined,
        witnesses=reports,
    )


def checklist_clauses(checklist: Checklist, claim: Optional[str] = None) -> Dict[str, str]:
    """The checklist's own in-claim obligations as a statement, for probing the checklist itself."""
    return {o.id: o.formal_clause for o in checklist.in_claim(claim)}


def necessity(
    checklist: Checklist, claim: Optional[str] = None, clauses: Optional[Dict[str, str]] = None
) -> Dict[str, List[str]]:
    """For each clause (default: the in-claim obligations), the witnesses no longer excluded once it alone is
    dropped (they satisfy the rest, or the rest leaves them undetermined).

    A clause with an empty list is not the only barrier against any catalogued witness; one with entries is
    load-bearing: without it, the statement would no longer rule those witnesses out.
    """
    clauses = clauses if clauses is not None else checklist_clauses(checklist, claim)
    out = {}
    for name in clauses:
        rest = {k: v for k, v in clauses.items() if k != name}
        report = probe(checklist, rest, statement=f"without {name}")
        out[name] = report.satisfied_by + report.undetermined
    return out


# ---------------------------------------------------------------------------
# Lean exclusion lint (syntactic)
# ---------------------------------------------------------------------------


class LintStatus(str, Enum):
    ADDRESSED_IN_TEXT = "ADDRESSED_IN_TEXT"  # A marker of an excluding obligation occurs; a human must confirm it.
    NO_EXCLUDING_CLAUSE_FOUND = "NO_EXCLUDING_CLAUSE_FOUND"


@dataclass
class MarkerHit:
    obligation: str
    pattern: str
    declaration: str
    line: int
    snippet: str


@dataclass
class WitnessLint:
    witness: str
    title: str
    status: str
    excluding_obligations: List[str]  # Obligations whose clause the witness violates (semantic, from the catalogue).
    evidence: List[MarkerHit]  # Marker hits for those obligations in the theorem's text.
    counter_evidence: List[MarkerHit]  # Text suggesting the statement's object has the witness's feature.
    semantic_confirmation: str = "HUMAN_REQUIRED"


@dataclass
class ExclusionLintReport:
    file: str
    theorem: str
    checklist: str
    checklist_sha256: str
    closure: List[str]
    obligations: Dict[str, Dict[str, List[Dict]]]  # id -> {"markers": [...], "counter_markers": [...]}
    witnesses: List[WitnessLint]
    flag: str  # POSSIBLY_VACUOUS_RELATIVE_TO_INTENT when some witness has no excluding clause in the text.

    def to_dict(self) -> Dict:
        return asdict(self)


# lean_junk_lint's parser, extended to `structure`, `class` and `inductive`: a statement's object (a lattice graph,
# a field theory record) is often a structure, and its fields carry the clauses that matter here.
_DECL = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|nonrec)\s+)*"
    r"(def|abbrev|theorem|lemma|instance|structure|class|inductive)\s+([^\s:({\[]+)"
)


def parse_declarations(source: str) -> List[Declaration]:
    lines = strip_comments(source).split("\n")
    starts: List[Tuple[int, str, str]] = []
    boundaries = set()
    for index, line in enumerate(lines):
        match = _DECL.match(line)
        if match:
            starts.append((index, match.group(1), match.group(2)))
        elif _BOUNDARY.match(line):
            boundaries.add(index)
    declarations = []
    for k, (index, kind, name) in enumerate(starts):
        stop = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        stop = min([b for b in boundaries if index < b < stop] + [stop])
        text = "\n".join(lines[index:stop]).rstrip()
        declarations.append(Declaration(kind, name, index + 1, index + text.count("\n") + 1, text))
    return declarations


def _closure(theorem: Declaration, declarations: Sequence[Declaration]) -> List[Declaration]:
    closure = [theorem]
    frontier = [theorem]
    while frontier:
        current = frontier.pop()
        for used in _uses(current, declarations):
            if used not in closure:
                closure.append(used)
                frontier.append(used)
    return sorted(closure, key=lambda d: d.start)


def _hits(obligation: Obligation, patterns: Sequence[str], closure: Sequence[Declaration]) -> List[MarkerHit]:
    hits = []
    for pattern in patterns:
        regex = re.compile(pattern)
        for d in closure:
            for offset, line in enumerate(d.text.split("\n")):
                if regex.search(line):
                    hits.append(MarkerHit(obligation.id, pattern, d.name, d.start + offset, line.strip()[:160]))
    return hits


def lint_exclusions(
    source: str,
    checklist: Checklist,
    theorem: Optional[str] = None,
    file: str = "<string>",
    claim: Optional[str] = None,
) -> ExclusionLintReport:
    """Checks whether the text of `theorem` (default: the last theorem in the file) addresses every witness."""
    declarations = parse_declarations(source)
    theorems = [d for d in declarations if d.kind in ("theorem", "lemma")]
    if not theorems:
        raise ValueError("No theorem in the file.")
    target = next((d for d in theorems if d.name == theorem or d.short == theorem), None) if theorem else theorems[-1]
    if target is None:
        raise ValueError(f"No theorem named {theorem!r}.")
    closure = _closure(target, declarations)
    obligations = checklist.in_claim(claim)
    found: Dict[str, Tuple[List[MarkerHit], List[MarkerHit]]] = {
        o.id: (_hits(o, o.lean_markers, closure), _hits(o, o.lean_counter_markers, closure)) for o in obligations
    }
    witnesses = []
    for w in checklist.witnesses:
        excluders = [o.id for o in obligations if decide(checklist, w.facts, o.formal_clause) == "REFUTED"]
        evidence = [h for oid in excluders for h in found[oid][0]]
        counter = [h for oid in excluders for h in found[oid][1]]
        status = LintStatus.ADDRESSED_IN_TEXT if evidence else LintStatus.NO_EXCLUDING_CLAUSE_FOUND
        witnesses.append(WitnessLint(w.id, w.title, status.value, excluders, evidence, counter))
    unaddressed = any(w.status == LintStatus.NO_EXCLUDING_CLAUSE_FOUND.value for w in witnesses)
    return ExclusionLintReport(
        file=file,
        theorem=target.name,
        checklist=f"{checklist.id} v{checklist.version}",
        checklist_sha256=checklist.sha256,
        closure=[f"{d.kind} {d.name} (lines {d.start}-{d.end})" for d in closure],
        obligations={
            oid: {"markers": [asdict(h) for h in m], "counter_markers": [asdict(h) for h in c]}
            for oid, (m, c) in found.items()
        },
        witnesses=witnesses,
        flag="POSSIBLY_VACUOUS_RELATIVE_TO_INTENT" if unaddressed else "EVERY_WITNESS_ADDRESSED_IN_TEXT",
    )
