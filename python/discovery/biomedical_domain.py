"""
python/discovery/biomedical_domain.py - Biomedical checks of a formal hypothesis (ADR-DISCOVERY-086).

Block E of docs/architecture/VERIFICATION_METHODOLOGY.md ran the verification chain (ADR-085) on biomedical
hypotheses. The gaps it found are closed here, as checks the chain, the API and the CLI run when a request carries a
`biomedical` block:

    {
      "units": {"ptau": "pg/mL", "egfr": "mL/min/1.73m^2", "age": "years"},
      "conventions": {"validated_assay": "...", "matrix": "plasma", "units": "pg/mL", ...},
      "probes": {
        "null_biomarker": ["ptau"],
        "untreated_arm": {"untreated": "treated == 0", "outcome": "decline == 1"},
        "population": {"validated": "age >= 50", "label": "validated in people aged 50 or more"}
      }
    }

Obligations (ADR-076 statuses), each decided exactly (enumeration or z3) or left OPEN with the reason:

- `units` (M6): every predicate is dimensionally and unit-homogeneous (`biomedical_units`). A dimension or scale
  mismatch is REFUTED: the formal object compares quantities that cannot be compared. An undeclared unit is OPEN.
- `probe:null_biomarker[b]` (M4): replacing the biomarker by a constant changes nothing. It is REFUTED when no two
  applicable states that differ only in `b` are treated differently (one allowed, the other forbidden): the biomarker
  does no work in the claims. When some stated prediction follows from the claims that do not mention `b`, the
  prediction does not test the biomarker, and the obligation stays OPEN with that finding.
- `probe:untreated_arm` (M4): the predicted outcome must not be met by the untreated arm. REFUTED when the hypothesis
  restricted to the untreated arm entails the outcome; OPEN when it merely allows it (observing the outcome would
  not discriminate the hypothesis from no treatment); DISCHARGED_SYMBOLIC when it forbids it.
- `probe:population` (M6): the hypothesis applies only inside the validated population. When some applicable state
  lies outside it, the obligation is OPEN with a witness: a transfer defect, like a convention mismatch (ADR-083), not
  a refutation of the claims.

The hypothesis's `conventions` are also the default conventions of each cited result's use, so a citation that names
a `variable` gets that variable's unit, and the registry compares them with the convention vocabulary
(`biomedical_conventions`). Scope: formal soundness only. Whether a cutoff, a unit or a population is clinically
right is never judged, and provenance never decides validity.
"""

from __future__ import annotations

import ast
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from python.discovery import biomedical_units, formal_status
from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, hypothesis_from_dict
from python.discovery.obligation_ledger import Discharge, Obligation, Status

SCHEMA = "coresearcher.biomedical_domain/v1"
BY = "CoResearcher"
_KEYS = {"units", "conventions", "probes"}
_PROBES = {"null_biomarker", "untreated_arm", "population"}


def obligation_dict(ob: Obligation) -> Dict[str, Any]:
    """One obligation in the serialized form of an ADR-076 ledger (`Claim.to_dict`)."""
    return {
        **{k: v for k, v in asdict(ob).items() if k != "discharges"},
        "status": ob.status.value,
        "independent": ob.independent,
        "discharges": [{**asdict(d), "status": d.status.value} for d in ob.discharges],
    }


class DomainSpecError(ValueError):
    """A malformed biomedical block (HTTP 422, CLI exit 9)."""


def validate(spec: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    spec = spec or {}
    if not isinstance(spec, dict):
        raise DomainSpecError("'biomedical' must be an object")
    unknown = set(spec) - _KEYS
    if unknown:
        raise DomainSpecError(f"unknown biomedical keys {sorted(unknown)}; use {sorted(_KEYS)}")
    probes = spec.get("probes") or {}
    if set(probes) - _PROBES:
        raise DomainSpecError(f"unknown probes {sorted(set(probes) - _PROBES)}; use {sorted(_PROBES)}")
    if "untreated_arm" in probes and not {"untreated", "outcome"} <= set(probes["untreated_arm"] or {}):
        raise DomainSpecError("untreated_arm needs 'untreated' and 'outcome' predicates")
    if "population" in probes and not (probes["population"] or {}).get("validated"):
        raise DomainSpecError("population needs a 'validated' predicate")
    return spec


# ---------------------------------------------------------------------------
# Exact helpers
# ---------------------------------------------------------------------------


class _Rename(ast.NodeTransformer):
    def __init__(self, old: str, new: str):
        self.old, self.new = old, new

    def visit_Name(self, node: ast.Name) -> ast.AST:
        return ast.copy_location(ast.Name(self.new, node.ctx), node) if node.id == self.old else node


def _rename(expression: str, old: str, new: str) -> str:
    return ast.unparse(_Rename(old, new).visit(ast.parse(expression.strip(), mode="eval")))


def _names(expression: str) -> set:
    return {n.id for n in ast.walk(ast.parse(expression.strip(), mode="eval")) if isinstance(n, ast.Name)}


def _applies(hypothesis: Dict[str, Any]) -> List[str]:
    return ([hypothesis["scope"]] if hypothesis.get("scope") else []) + list(hypothesis.get("assumptions") or [])


def _conj(predicates: List[str]) -> str:
    return " and ".join(f"({p})" for p in predicates) if predicates else ""


def _satisfiable(variables: List[Dict[str, Any]], predicates: List[str], backend: str
                 ) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Is the conjunction satisfiable over the declared domains or ranges? Exact; returns a witness when it is."""
    first = variables[0]["name"]
    h = hypothesis_from_dict({"hypothesis_id": "probe", "variables": variables,
                              "scope": _conj(predicates) or None, "claims": [f"{first} != {first}"]})
    report = HypothesisEvaluator.evaluate(h, max_examples=1, backend=backend)
    if report.content_verdict.value == "VACUOUS":
        return False, None
    return True, (report.falsifier_examples or [None])[0]


def _scope(hypothesis: Dict[str, Any]) -> str:
    continuous = any(v.get("continuous") for v in hypothesis.get("variables") or [])
    return "the declared ranges, decided by z3" if continuous else "the declared finite domains, by enumeration"


def _discharge(status: Status, method: str, scope: str, **detail) -> Discharge:
    return Discharge(status=status, method=method, scope=scope, by=BY, detail=detail)


def _open_on_error(ob: Obligation, exc: Exception) -> Dict[str, Any]:
    status = formal_status.classify(exc)  # Re-raises anything that is not a known non-verdict.
    ob.discharges.append(_discharge(Status.OPEN, "exact evaluation", "", reason=f"{status.value}: {exc}"))
    return {"outcome": status.value, "reason": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------


def null_biomarker(hypothesis: Dict[str, Any], biomarker: str, consequences: List[str], backend: str = "auto"
                   ) -> Tuple[Obligation, Dict[str, Any]]:
    variables = hypothesis.get("variables") or []
    var = next((v for v in variables if v["name"] == biomarker), None)
    if var is None:
        raise DomainSpecError(f"null_biomarker: {biomarker!r} is not a variable of the hypothesis")
    ob = Obligation(f"probe:null_biomarker[{biomarker}]", f"Replacing {biomarker} by a constant changes what the "
                    "hypothesis allows (the biomarker does work in the claims)", "biomedical.probes.null_biomarker",
                    "domain vacuity probe")
    alt = f"{biomarker}__alt"
    if any(v["name"] == alt for v in variables):
        raise DomainSpecError(f"null_biomarker: the name {alt!r} is taken")
    applies = _applies(hypothesis)
    claims = list(hypothesis.get("claims") or [])
    twin = [_rename(p, biomarker, alt) for p in applies]
    constraints = applies + twin + claims + [f"not ({_conj([_rename(c, biomarker, alt) for c in claims])})"]
    report: Dict[str, Any] = {"biomarker": biomarker}
    try:
        works, witness = _satisfiable(variables + [dict(var, name=alt)], constraints, backend)
        independent = []
        if works and consequences:
            kept = [c for c in claims if biomarker not in _names(c)]
            first = variables[0]["name"]
            reduced = hypothesis_from_dict(dict(hypothesis, claims=kept or [f"{first} == {first}"], non_witnesses=[]))
            for i, consequence in enumerate(consequences):
                rep = HypothesisEvaluator.entails(reduced, consequence, max_examples=1, backend=backend)
                if rep.entailed and not rep.vacuous:
                    independent.append({"index": i, "consequence": consequence})
    except FormalHypothesisError as exc:
        report.update(_open_on_error(ob, exc))
        return ob, report
    method = "exact two-copy search: two applicable states differing only in the biomarker, one allowed and one " \
             "forbidden"
    if not works:
        ob.discharges.append(_discharge(Status.REFUTED, method, _scope(hypothesis), reason=(
            f"no two applicable states that differ only in {biomarker} are treated differently: the claims hold or "
            f"fail regardless of {biomarker}, so a constant would do as well")))
        report["outcome"] = "BIOMARKER_IDLE"
    elif independent:
        ob.discharges.append(_discharge(Status.OPEN, method, _scope(hypothesis), reason=(
            f"the biomarker does work, but some stated predictions follow from the claims that do not mention "
            f"{biomarker}, so they do not test it"), predictions_without_biomarker=independent, witness=witness))
        report.update(outcome="PREDICTIONS_WITHOUT_BIOMARKER", predictions_without_biomarker=independent,
                      witness=witness)
    else:
        ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, method, _scope(hypothesis), witness=witness))
        report.update(outcome="BIOMARKER_DOES_WORK", witness=witness)
    return ob, report


def untreated_arm(hypothesis: Dict[str, Any], untreated: str, outcome: str, backend: str = "auto", label: str = ""
                  ) -> Tuple[Obligation, Dict[str, Any]]:
    ob = Obligation("probe:untreated_arm", "The predicted outcome is not met by the untreated arm",
                    "biomedical.probes.untreated_arm", "domain vacuity probe")
    variables = hypothesis.get("variables") or []
    base = _applies(hypothesis) + list(hypothesis.get("claims") or [])
    report: Dict[str, Any] = {"untreated": untreated, "outcome": outcome, "label": label}
    method = "exact satisfiability and entailment within the untreated arm"
    try:
        arm, _ = _satisfiable(variables, base + [untreated], backend)
        shows, witness = _satisfiable(variables, base + [untreated, outcome], backend) if arm else (False, None)
        must, _ = _satisfiable(variables, base + [untreated, f"not ({outcome})"], backend) if shows else (True, None)
    except FormalHypothesisError as exc:
        report.update(_open_on_error(ob, exc))
        return ob, report
    if not arm:
        ob.discharges.append(_discharge(Status.OPEN, method, _scope(hypothesis), reason=(
            "the hypothesis allows no state of the untreated arm, so the probe says nothing")))
        report["outcome_status"] = "ARM_NOT_ALLOWED"
    elif shows and not must:
        ob.discharges.append(_discharge(Status.REFUTED, method, _scope(hypothesis), reason=(
            "in the untreated arm the hypothesis entails the predicted outcome: the prediction is met without the "
            "treatment"), witness=witness))
        report.update(outcome_status="MET_BY_UNTREATED_ARM", witness=witness)
    elif shows:
        ob.discharges.append(_discharge(Status.OPEN, method, _scope(hypothesis), reason=(
            "the untreated arm may also show the predicted outcome, so observing it does not discriminate the "
            "hypothesis from no treatment"), witness=witness))
        report.update(outcome_status="ALLOWED_IN_UNTREATED_ARM", witness=witness)
    else:
        ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, method, _scope(hypothesis)))
        report["outcome_status"] = "FORBIDDEN_IN_UNTREATED_ARM"
    return ob, report


def population(hypothesis: Dict[str, Any], validated: str, backend: str = "auto", label: str = ""
               ) -> Tuple[Obligation, Dict[str, Any]]:
    ob = Obligation("probe:population", f"The hypothesis applies only inside the validated population "
                    f"({label or validated})", "biomedical.probes.population", "domain transfer probe")
    variables = hypothesis.get("variables") or []
    report: Dict[str, Any] = {"validated": validated, "label": label}
    try:
        outside, witness = _satisfiable(variables, _applies(hypothesis) + [f"not ({validated})"], backend)
    except FormalHypothesisError as exc:
        report.update(_open_on_error(ob, exc))
        return ob, report
    method = "exact satisfiability of the scope and assumptions outside the validated population"
    if outside:
        ob.discharges.append(_discharge(Status.OPEN, method, _scope(hypothesis), reason=(
            "the hypothesis applies to states outside the validated population; its claims are asserted where the "
            "imported result was not validated"), witness=witness))
        report.update(outcome="APPLIES_OUTSIDE_VALIDATED_POPULATION", witness=witness)
    else:
        ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, method, _scope(hypothesis)))
        report["outcome"] = "INSIDE_VALIDATED_POPULATION"
    return ob, report


def units_obligation(hypothesis: Dict[str, Any], units: Dict[str, str], consequences: List[str]
                     ) -> Tuple[Obligation, Dict[str, Any]]:
    ob = Obligation("units", "Every predicate compares and adds quantities of the same unit", "biomedical.units",
                    "dimensional homogeneity")
    report = biomedical_units.check(hypothesis, units, consequences)
    method = report["method"]
    if report["outcome"] == "FINDINGS":
        bad = [p for p in report["predicates"] if p["outcome"] in (biomedical_units.DIMENSION_MISMATCH,
                                                                    biomedical_units.SCALE_MISMATCH)]
        ob.discharges.append(_discharge(Status.REFUTED, method, "every predicate", findings=bad))
    elif report["outcome"] == "INCOMPLETE":
        bad = [p for p in report["predicates"] if p["outcome"] == biomedical_units.UNDECLARED_UNIT]
        ob.discharges.append(_discharge(Status.OPEN, method, "every predicate", reason="undeclared or unreadable "
                                        "units where a unit matters", findings=bad))
    else:
        ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, method, "every predicate"))
    return ob, report


# ---------------------------------------------------------------------------
# Citations and the whole check
# ---------------------------------------------------------------------------


def fill_citations(citations: List[Dict[str, Any]], spec: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Each use of a cited result inherits the hypothesis's conventions, and the unit of the `variable` it names.
    Conventions written on the use itself win. A use with an explicit `context` is left as it is."""
    spec = spec or {}
    base = dict(spec.get("conventions") or {})
    units = spec.get("units") or {}
    out = []
    for item in citations or []:
        item = dict(item)
        if not isinstance(item.get("context"), dict) and (base or item.get("variable")):
            filled = dict(base)
            if item.get("variable") in units:
                filled["units"] = units[item["variable"]]
            filled.update(item.get("conventions") or {})
            item["conventions"] = filled
        out.append(item)
    return out


def check(hypothesis: Dict[str, Any], spec: Optional[Dict[str, Any]], consequences: Optional[List[str]] = None,
          backend: str = "auto", mechanism: Optional[Dict[str, Any]] = None) -> Tuple[List[Obligation], Dict[str, Any]]:
    """The biomedical obligations of one hypothesis and their report. `mechanism` is a compiled mechanistic chain
    (`mechanistic_chain.compile_mechanism`): its link obligations, its node units and its untreated arm are added."""
    spec = validate(spec)
    consequences = list(consequences or [])
    obligations: List[Obligation] = []
    report: Dict[str, Any] = {"schema": SCHEMA}
    hypothesis_from_dict(hypothesis)  # validates the object before any probe
    units = dict(spec.get("units") or {})
    if mechanism is not None:
        from python.discovery import mechanistic_chain

        units = {**mechanism.get("units", {}), **units}
        links, link_report = mechanistic_chain.obligations(mechanism, backend)
        obligations += links
        report["mechanism"] = link_report
    if units:
        ob, rep = units_obligation(hypothesis, units, consequences)
        obligations.append(ob)
        report["units"] = rep
    probes = dict(spec.get("probes") or {})
    if mechanism is not None and mechanism.get("outcome") and "untreated_arm" not in probes:
        probes["untreated_arm"] = {"untreated": mechanism["untreated"], "outcome": mechanism["outcome"],
                                   "label": "no root node moves (the untreated arm of the mechanism)"}
    for biomarker in probes.get("null_biomarker") or []:
        ob, rep = null_biomarker(hypothesis, biomarker, consequences, backend)
        obligations.append(ob)
        report.setdefault("null_biomarker", []).append(rep)
    if probes.get("untreated_arm"):
        arm = probes["untreated_arm"]
        ob, rep = untreated_arm(hypothesis, arm["untreated"], arm["outcome"], backend, arm.get("label", ""))
        obligations.append(ob)
        report["untreated_arm"] = rep
    if probes.get("population"):
        pop = probes["population"]
        ob, rep = population(hypothesis, pop["validated"], backend, pop.get("label", ""))
        obligations.append(ob)
        report["population"] = rep
    if spec.get("conventions"):
        report["conventions"] = dict(spec["conventions"])
    report["obligations"] = {o.id: o.status.value for o in obligations}
    report["scope_note"] = ("Formal soundness only: units, probes and conventions of the formal object. Whether a "
                            "cutoff, a unit or a population is clinically right is not judged.")
    return obligations, report


__all__ = ["check", "validate", "obligation_dict", "fill_citations", "null_biomarker", "untreated_arm", "population",
           "units_obligation", "DomainSpecError", "SCHEMA"]
