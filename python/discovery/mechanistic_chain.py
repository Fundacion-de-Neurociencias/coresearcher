"""
python/discovery/mechanistic_chain.py - Mechanistic chain hypotheses as obligation templates (ADR-DISCOVERY-086).

Method M5 of docs/architecture/VERIFICATION_METHODOLOGY.md: "A raises B, which drives C, which predicts D" is an
obligation chain. Each link can be checked on its own, the sign of each effect can be checked against the scales of
the quantities, and the links must be compatible with each other and with the end-to-end prediction.

A mechanism is a set of nodes (quantities, each with ordered levels or a continuous range, and optionally a unit and
a scale direction) and signed links between them. It compiles to an ADR-059 hypothesis by a two-world encoding: every
node X becomes X_0 (baseline) and X_1 (after an intervention), and every node with parents gets the qualitative
(sign) semantics of a signed influence graph:

- all parents unchanged -> the node is unchanged (no other cause is modelled: ceteris paribus);
- every parent moves in a direction that pushes the node up (or is unchanged), and one does -> the node goes up;
- symmetrically for down;
- parents pushing in opposite directions -> the node is unconstrained (the net effect is not determined by signs).

A link's sign is "+" (the target moves with the source) or "-". It is given directly or derived from the link's
`effect`: "raises" and "lowers" fix the sign; "worsens" and "improves" fix it only together with the target's scale
direction (worsening a higher_is_better score lowers it). The prediction is end to end: from a source node to a target
node, with a sign or an effect, under an intervention that moves only the source among the root nodes.

Obligations (ADR-076 statuses):

- `link[i]`: the link alone is consistent and admits a change of its source: some intervention on the source is
  allowed, so the link is not vacuous (a target with a single level cannot move, and the link then forbids every
  change of its source: REFUTED);
- `link_sign[i]`: the declared sign agrees with the effect and the target's scale direction (REFUTED when they
  disagree, OPEN when an effect is relative to a scale whose direction is not declared);
- `mechanism:compatibility`: the links together admit the intervention of the prediction and entail the predicted
  change. Opposite signs along a path, or paths of opposite signs, leave it REFUTED with a counterexample.

`parse_prose` reads a restricted controlled language ("A raises B, which drives C, which predicts D.") into links. It is
a deterministic grammar, not a model: a sentence outside it, or a noun phrase that names no declared node, is
FORMALIZATION_FAILED, never a guess. Scope: formal soundness of the stated mechanism; whether the mechanism is true is
not judged.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from python.discovery import formal_status
from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, hypothesis_from_dict
from python.discovery.formal_status import FormalStatus
from python.discovery.obligation_ledger import Discharge, Obligation, Status

SCHEMA = "coresearcher.mechanistic_chain/v1"
BY = "CoResearcher"

# Verbs of the controlled language. A verb fixes either a sign ("+"/"-") or an effect relative to the target's scale.
VERBS: Dict[str, Tuple[str, str]] = {
    "raises": ("sign", "+"), "increases": ("sign", "+"), "elevates": ("sign", "+"), "drives": ("sign", "+"),
    "promotes": ("sign", "+"), "causes": ("sign", "+"), "induces": ("sign", "+"), "predicts": ("sign", "+"),
    "accelerates": ("sign", "+"), "enhances": ("sign", "+"),
    "lowers": ("sign", "-"), "reduces": ("sign", "-"), "decreases": ("sign", "-"), "inhibits": ("sign", "-"),
    "suppresses": ("sign", "-"), "slows": ("sign", "-"), "protects against": ("sign", "-"),
    "worsens": ("effect", "worsens"), "impairs": ("effect", "worsens"), "predicts worse": ("effect", "worsens"),
    "improves": ("effect", "improves"), "preserves": ("effect", "improves"), "predicts better": ("effect", "improves"),
}
_EFFECT_SIGN = {"raises": "+", "lowers": "-"}
_DIRECTIONS = ("higher_is_worse", "higher_is_better")


class MechanismError(ValueError):
    """A malformed mechanism: unknown node, cycle, bad sign (HTTP 422, CLI exit 9)."""


class ProseNotInGrammar(FormalHypothesisError):
    """The prose is outside the controlled language; the chain reports FORMALIZATION_FAILED."""


# ---------------------------------------------------------------------------
# Controlled prose
# ---------------------------------------------------------------------------


def _node_for(phrase: str, nodes: List[Dict[str, Any]]) -> str:
    phrase = re.sub(r"\s+", " ", phrase.strip().lower()).strip(" .")
    phrase = re.sub(r"^(the|a|an)\s+", "", phrase)
    hits = []
    for node in nodes:
        names = [node["name"].lower(), node["name"].lower().replace("_", " ")]
        names += [a.lower() for a in node.get("aliases") or []]
        if phrase in names:
            hits.append(node["name"])
    if len(set(hits)) != 1:
        why = "no declared node" if not hits else f"several nodes {sorted(set(hits))}"
        raise ProseNotInGrammar(f"the phrase {phrase!r} names {why}; declare it as a node name or alias")
    return hits[0]


def _clause(text: str) -> Tuple[str, str]:
    """Splits 'VERB OBJECT' with the longest verb that matches."""
    text = text.strip()
    for verb in sorted(VERBS, key=len, reverse=True):
        if text.lower().startswith(verb + " "):
            return verb, text[len(verb):].strip()
    raise ProseNotInGrammar(f"no known verb at the start of {text!r}; known verbs: {sorted(VERBS)}")


def parse_prose(prose: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reads 'A raises B, which drives C, which predicts D.' (one or more sentences) into links.

    The last link of the last sentence is also the default end-to-end prediction (from the first subject to the last
    object, with the product of the signs), unless the mechanism states a prediction itself.
    """
    links: List[Dict[str, Any]] = []
    sentences = [s for s in re.split(r"(?<=[.;])\s+", prose.strip()) if s.strip(" .;")]
    if not sentences:
        raise ProseNotInGrammar("empty prose")
    for sentence in sentences:
        sentence = sentence.strip().rstrip(".;")
        parts = re.split(r",?\s+which\s+", sentence)
        head = parts[0]
        verb_at = None
        for verb in sorted(VERBS, key=len, reverse=True):
            m = re.search(rf"\s{re.escape(verb)}\s", f" {head} ", flags=re.IGNORECASE)
            if m and (verb_at is None or m.start() < verb_at[0]):
                verb_at = (m.start(), verb)
        if verb_at is None:
            raise ProseNotInGrammar(f"no known verb in {head!r}; known verbs: {sorted(VERBS)}")
        start, verb = verb_at
        subject = head[: max(start - 1, 0)] if start else ""
        rest = head[start + len(verb):].strip()
        if not subject.strip():
            raise ProseNotInGrammar(f"no subject before {verb!r} in {head!r}")
        clauses = [(verb, rest)] + [_clause(p) for p in parts[1:]]
        source = _node_for(subject, nodes)
        for verb, obj in clauses:
            target = _node_for(obj, nodes)
            kind, value = VERBS[verb]
            link = {"from": source, "to": target, "verb": verb}
            link["sign" if kind == "sign" else "effect"] = value
            links.append(link)
            source = target
    return {"links": links, "reader": "controlled-language grammar (deterministic, one reading)",
            "sentences": sentences}


# ---------------------------------------------------------------------------
# Validation and compilation
# ---------------------------------------------------------------------------


def _sign_of(link: Dict[str, Any], nodes: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], str, str]:
    """(sign or None, obligation status, reason) for one link."""
    declared = link.get("sign")
    effect = link.get("effect")
    if declared not in (None, "+", "-"):
        raise MechanismError(f"link {link['from']}->{link['to']}: sign must be '+' or '-'")
    if effect is None:
        if declared is None:
            raise MechanismError(f"link {link['from']}->{link['to']} needs a sign or an effect")
        return declared, "DISCHARGED_SYMBOLIC", "the sign is stated by the link itself"
    if effect in _EFFECT_SIGN:
        derived = _EFFECT_SIGN[effect]
        why = f"'{effect}' means sign {derived}"
    elif effect in ("worsens", "improves"):
        direction = nodes[link["to"]].get("scale_direction")
        if direction not in _DIRECTIONS:
            return declared, "OPEN", (f"'{effect}' fixes a sign only with the scale direction of {link['to']}, "
                                      "which is not declared")
        derived = "+" if (effect == "worsens") == (direction == "higher_is_worse") else "-"
        why = f"'{effect}' on {link['to']} ({direction}) means sign {derived}"
    else:
        raise MechanismError(f"link {link['from']}->{link['to']}: unknown effect {effect!r}")
    if declared is not None and declared != derived:
        # The formal object keeps the sign as written, so the seam shows in the end-to-end prediction too.
        return declared, "REFUTED", f"declared sign {declared}, but {why}"
    return derived, "DISCHARGED_SYMBOLIC", why


def _validate(mechanism: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    if not isinstance(mechanism, dict):
        raise MechanismError("a mechanism must be an object")
    nodes = mechanism.get("nodes") or []
    if not nodes:
        raise MechanismError("a mechanism needs nodes")
    by_name: Dict[str, Dict[str, Any]] = {}
    for node in nodes:
        name = node.get("name") if isinstance(node, dict) else None
        if not isinstance(name, str) or not name.isidentifier() or name.endswith(("_0", "_1")):
            raise MechanismError(f"node name {name!r} must be an identifier not ending in _0 or _1")
        if name in by_name:
            raise MechanismError(f"node {name!r} is declared twice")
        direction = node.get("scale_direction")
        if direction is not None:
            from python.discovery import biomedical_conventions

            canonical, _ = biomedical_conventions.canonical_value("scale_direction", direction)
            if canonical not in _DIRECTIONS:
                raise MechanismError(f"node {name!r}: scale_direction must be one of {_DIRECTIONS}")
            node = dict(node, scale_direction=canonical)
        by_name[name] = node
    links = mechanism.get("links")
    parse = None
    if not links and mechanism.get("prose"):
        parse = parse_prose(mechanism["prose"], list(by_name.values()))
        links = parse["links"]
    if not links:
        raise MechanismError("a mechanism needs links, or prose in the controlled language")
    for link in links:
        if not isinstance(link, dict) or link.get("from") not in by_name or link.get("to") not in by_name:
            raise MechanismError(f"link {link!r} must join two declared nodes")
        if link["from"] == link["to"]:
            raise MechanismError(f"link {link['from']}->{link['to']} is a self-loop")
    # Cycles: the two-world encoding is for acyclic mechanisms.
    order: List[str] = []
    indegree = {n: 0 for n in by_name}
    for link in links:
        indegree[link["to"]] += 1
    ready = sorted(n for n, d in indegree.items() if d == 0)
    while ready:
        n = ready.pop(0)
        order.append(n)
        for link in links:
            if link["from"] == n:
                indegree[link["to"]] -= 1
                if indegree[link["to"]] == 0:
                    ready.append(link["to"])
    if len(order) != len(by_name):
        raise MechanismError("the links form a cycle; a feedback loop is outside the two-world encoding")
    return list(by_name.values()), links, {"order": order, "parse": parse}


def _variables(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for node in nodes:
        for world in ("0", "1"):
            var = {"name": f"{node['name']}_{world}"}
            if node.get("levels") is not None:
                var["domain"] = list(node["levels"])
            else:
                var.update(continuous=True, lower=node.get("lower"), upper=node.get("upper"))
            out.append(var)
    return out


def _push(parent: str, sign: str, direction: str) -> str:
    """The predicate 'parent pushes the child up' (direction 'up') or down, for a link of the given sign."""
    up = (sign == "+") == (direction == "up")
    return f"{parent}_1 > {parent}_0" if up else f"{parent}_1 < {parent}_0"


def _node_claims(child: str, parents: List[Tuple[str, str]]) -> List[str]:
    still = " and ".join(f"{p}_1 == {p}_0" for p, _ in parents)
    no_down = " and ".join(f"not ({_push(p, s, 'down')})" for p, s in parents)
    some_up = " or ".join(f"({_push(p, s, 'up')})" for p, s in parents)
    no_up = " and ".join(f"not ({_push(p, s, 'up')})" for p, s in parents)
    some_down = " or ".join(f"({_push(p, s, 'down')})" for p, s in parents)
    return [
        f"not ({still}) or {child}_1 == {child}_0",
        f"not ({no_down} and ({some_up})) or {child}_1 > {child}_0",
        f"not ({no_up} and ({some_down})) or {child}_1 < {child}_0",
    ]


def _prediction(mechanism: Dict[str, Any], links: List[Dict[str, Any]], signs: List[Optional[str]],
                nodes: Dict[str, Dict[str, Any]], roots: List[str]) -> Dict[str, Any]:
    pred = mechanism.get("prediction")
    if pred is None:
        if mechanism.get("links"):
            raise MechanismError("state the end-to-end prediction {from, to, sign or effect}")
        # From controlled prose: the first subject to the last object, with the product of the stated signs.
        product = "+"
        for s in signs:
            if s is None:
                product = None
                break
            product = "+" if product == s else "-"
        pred = {"from": links[0]["from"], "to": links[-1]["to"], "sign": product,
                "note": "default prediction from the prose: the product of the link signs"}
    if pred.get("from") not in nodes or pred.get("to") not in nodes:
        raise MechanismError("the prediction must join two declared nodes")
    if pred["from"] not in roots:
        raise MechanismError(f"the prediction's source {pred['from']!r} must be a root node (no incoming link)")
    pseudo = {"from": pred["from"], "to": pred["to"], "sign": pred.get("sign"), "effect": pred.get("effect")}
    if pseudo["sign"] is None and pseudo["effect"] is None:
        if "note" in pred:  # The default prediction of the prose, with a link whose sign is not determined.
            return {**pred, "sign_status": "OPEN", "sign_reason": "a link's sign is not determined"}
        raise MechanismError("the prediction needs a sign or an effect")
    sign, status, why = _sign_of(pseudo, nodes)
    return {**pred, "sign": sign, "sign_status": status, "sign_reason": why}


def compile_mechanism(mechanism: Dict[str, Any]) -> Dict[str, Any]:
    """The mechanism as an ADR-059 hypothesis (two-world encoding), its prediction as a consequence, the untreated
    arm and outcome predicates for the domain probe, and the per-link data the obligations need."""
    nodes, links, meta = _validate(mechanism)
    by_name = {n["name"]: n for n in nodes}
    signs, sign_checks = [], []
    for link in links:
        sign, status, why = _sign_of(link, by_name)
        signs.append(sign)
        sign_checks.append({"status": status, "reason": why, "sign": sign})
    roots = [n for n in meta["order"] if not any(link["to"] == n for link in links)]
    prediction = _prediction(mechanism, links, signs, by_name, roots)
    claims: List[str] = []
    undetermined = [f"{links[i]['from']}->{links[i]['to']}" for i, s in enumerate(signs) if s is None]
    for child in meta["order"]:
        parents = [(link["from"], signs[i]) for i, link in enumerate(links) if link["to"] == child]
        if parents and not any(s is None for _, s in parents):
            claims += _node_claims(child, parents)
    if not claims:
        raise MechanismError("no link has a determined sign, so the mechanism constrains nothing")
    others = [r for r in roots if r != prediction["from"]]
    premise = " and ".join([f"{prediction['from']}_1 > {prediction['from']}_0"] +
                           [f"{r}_1 == {r}_0" for r in others])
    target = prediction["to"]
    outcome = None
    if prediction["sign"] is not None:
        outcome = f"{target}_1 > {target}_0" if prediction["sign"] == "+" else f"{target}_1 < {target}_0"
    hypothesis = {
        "hypothesis_id": mechanism.get("hypothesis_id") or "MECHANISM",
        "statement": mechanism.get("statement") or mechanism.get("prose") or "",
        "variables": _variables(nodes),
        "claims": claims,
    }
    untreated = " and ".join(f"{r}_1 == {r}_0" for r in roots)
    return {
        "schema": SCHEMA,
        "hypothesis": hypothesis,
        "consequences": [f"not ({premise}) or ({outcome})"] if outcome else [],
        "prediction": prediction,
        "premise": premise,
        "outcome": outcome,
        "untreated": untreated,
        "links": links,
        "link_signs": sign_checks,
        "undetermined_links": undetermined,
        "roots": roots,
        "nodes": by_name,
        "order": meta["order"],
        "parse": meta["parse"],
        "units": {f"{n['name']}_{w}": n["unit"] for n in nodes if n.get("unit") for w in ("0", "1")},
        "encoding": "two worlds per node (X_0 baseline, X_1 after the intervention); signed-influence semantics",
    }


# ---------------------------------------------------------------------------
# Obligations
# ---------------------------------------------------------------------------


def _scope(h) -> str:
    return "the declared levels, by exhaustive enumeration" if not h.is_continuous else "the declared ranges, by z3"


def _allows(hypothesis: Dict[str, Any], condition: str, backend: str) -> bool:
    """Does some state meet `condition` and every claim? Exact (enumeration or z3)."""
    h = hypothesis_from_dict(dict(hypothesis, scope=condition, assumptions=[], non_witnesses=[]))
    verdict = HypothesisEvaluator.evaluate(h, max_examples=1, backend=backend).content_verdict.value
    return verdict not in ("VACUOUS", "SELF_CONTRADICTORY")


def _discharge(status: Status, method: str, scope: str, **detail) -> Discharge:
    return Discharge(status=status, method=method, scope=scope, by=BY, detail=detail)


def obligations(compiled: Dict[str, Any], backend: str = "auto") -> Tuple[List[Obligation], Dict[str, Any]]:
    """`link[i]`, `link_sign[i]` and `mechanism:compatibility`, each decided exactly or left OPEN with the reason."""
    hyp = compiled["hypothesis"]
    links = compiled["links"]
    out: List[Obligation] = []
    report: Dict[str, Any] = {"links": [], "compatibility": None}
    nodes = compiled["nodes"]
    signs = [c["sign"] for c in compiled["link_signs"]]
    for i, link in enumerate(links):
        name = f"{link['from']} -> {link['to']}"
        ob = Obligation(f"link[{i}]", f"The link {name} is consistent and admits a change of {link['from']}",
                        f"mechanism.links[{i}]", "mechanism link")
        sign_ob = Obligation(f"link_sign[{i}]", f"The sign of {name} agrees with its effect and the scale of "
                             f"{link['to']}", f"mechanism.links[{i}]", "sign of effect")
        check = compiled["link_signs"][i]
        sign_ob.discharges.append(_discharge(Status(check["status"]), "sign rules of the mechanism template",
                                             "the link's sign, effect and the target's declared scale direction",
                                             reason=check["reason"], sign=check["sign"]))
        row = {"link": name, "sign": signs[i], "sign_status": check["status"], "sign_reason": check["reason"]}
        if signs[i] is None:
            ob.discharges.append(_discharge(Status.OPEN, "none", "", reason="the link's sign is not determined"))
            row["status"] = "OPEN"
        else:
            single = {
                "hypothesis_id": f"link-{i}",
                "variables": [v for v in hyp["variables"] if v["name"].rsplit("_", 1)[0] in (link["from"], link["to"])],
                "claims": _node_claims(link["to"], [(link["from"], signs[i])]),
            }
            try:
                h = hypothesis_from_dict(single)
                up = _allows(single, f"{link['from']}_1 > {link['from']}_0", backend)
                down = _allows(single, f"{link['from']}_1 < {link['from']}_0", backend)
            except FormalHypothesisError as exc:
                status = formal_status.classify(exc)
                ob.discharges.append(_discharge(Status.OPEN, "exact evaluation", "", reason=f"{status.value}: {exc}"))
                row["status"] = "OPEN"
            else:
                if up or down:
                    ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, "exact evaluation", _scope(h),
                                                    admits_increase=up, admits_decrease=down))
                    row["status"] = "DISCHARGED_SYMBOLIC"
                else:
                    stuck = [n for n in (link["from"], link["to"]) if len(nodes[n].get("levels") or [0, 1]) < 2]
                    ob.discharges.append(_discharge(Status.REFUTED, "exact evaluation", _scope(h), reason=(
                        f"no change of {link['from']} is allowed by the link: "
                        + (f"{', '.join(stuck)} has a single level" if stuck else
                           f"{link['to']} has no room to move in the stated direction"))))
                    row["status"] = "REFUTED"
                row.update(admits_increase=up, admits_decrease=down)
        out += [ob, sign_ob]
        report["links"].append(row)
    comp = Obligation("mechanism:compatibility", "The links together admit the predicted intervention and entail the "
                      "predicted change", "mechanism.prediction", "mechanism compatibility")
    pred = compiled["prediction"]
    row: Dict[str, Any] = {"prediction": f"{pred['from']} -> {pred['to']} ({pred.get('sign')})",
                           "premise": compiled["premise"], "outcome": compiled["outcome"]}
    if compiled["outcome"] is None or compiled["undetermined_links"]:
        why = ("the prediction's sign is not determined" if compiled["outcome"] is None else
               f"links without a determined sign: {compiled['undetermined_links']}")
        comp.discharges.append(_discharge(Status.OPEN, "none", "", reason=why))
        row["status"] = "OPEN"
    else:
        try:
            h = hypothesis_from_dict(hyp)
            admits = _allows(hyp, compiled["premise"], backend)
            entail = HypothesisEvaluator.entails(h, compiled["consequences"][0], max_examples=3, backend=backend)
        except FormalHypothesisError as exc:
            status = formal_status.classify(exc)
            comp.discharges.append(_discharge(Status.OPEN, "exact evaluation", "", reason=f"{status.value}: {exc}"))
            row["status"] = "OPEN"
        else:
            row.update(admits_intervention=admits, entailed=entail.entailed)
            if not admits:
                comp.discharges.append(_discharge(Status.REFUTED, "exact evaluation", _scope(h), reason=(
                    "the links together forbid the intervention: some node on the path cannot move")))
                row["status"] = "REFUTED"
            elif entail.entailed:
                comp.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, "exact entailment", _scope(h)))
                row["status"] = "DISCHARGED_SYMBOLIC"
            else:
                comp.discharges.append(_discharge(Status.REFUTED, "exact entailment", _scope(h), reason=(
                    "the links do not entail the predicted change: the signs along the paths do not compose to "
                    "the predicted sign"), counterexamples=entail.counterexamples[:3]))
                row["status"] = "REFUTED"
                row["counterexamples"] = entail.counterexamples[:3]
    out.append(comp)
    report["compatibility"] = row
    return out, report


def check(mechanism: Dict[str, Any], backend: str = "auto") -> Dict[str, Any]:
    """Compiles a mechanism and decides its obligations. Prose outside the grammar is FORMALIZATION_FAILED."""
    try:
        compiled = compile_mechanism(mechanism)
    except ProseNotInGrammar as exc:
        return {"schema": SCHEMA, "formal_status": FormalStatus.FORMALIZATION_FAILED.value, "reason": str(exc),
                "compiled": None, "obligations": [], "report": None}
    obs, report = obligations(compiled, backend)
    return {"schema": SCHEMA, "formal_status": FormalStatus.DECIDED.value, "reason": "", "compiled": compiled,
            "obligations": [o.to_dict() for o in obs], "report": report,
            "scope_note": "Formal soundness of the stated mechanism; whether the mechanism holds is not judged."}


__all__ = ["compile_mechanism", "obligations", "check", "parse_prose", "MechanismError", "ProseNotInGrammar",
           "VERBS", "SCHEMA"]
