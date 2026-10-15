"""Formal hypothesis evaluation endpoints (ADR-DISCOVERY-059, ADR-DISCOVERY-060)."""

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import (
    CompareFormalHypothesesRequest,
    EvaluateFormalHypothesisRequest,
    FormalConsequenceRequest,
    FormalHypothesisModel,
)
from api.security import require_api_key
from python.discovery.formal_hypothesis import (
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    Variable,
)
from python.discovery.formal_lean import consequence_theorem

router = APIRouter()

_SCALARS = (str, int, float, bool)


def _to_hypothesis(model: FormalHypothesisModel) -> Hypothesis:
    variables = []
    for v in model.variables:
        if not all(isinstance(value, _SCALARS) for value in v.domain):
            raise FormalHypothesisError(f"Domain of {v.name!r} must contain only strings, numbers or booleans.")
        variables.append(Variable(v.name, tuple(v.domain), v.continuous, v.lower, v.upper))
    return Hypothesis(
        hypothesis_id=model.hypothesis_id,
        variables=variables,
        claims=model.claims,
        assumptions=model.assumptions,
        scope=model.scope,
        statement=model.statement,
        alternatives=model.alternatives,
    )


def _bounded(n: int) -> int:
    return max(1, min(50, n))


@router.post("/api/hypotheses/evaluate", dependencies=[Depends(require_api_key)])
def evaluate_formal_hypothesis(req: EvaluateFormalHypothesisRequest):
    """Exact evaluation (enumeration, or SMT when a variable is continuous): content, conflicts, counterexamples."""
    try:
        hypothesis = _to_hypothesis(req.hypothesis)
        report = HypothesisEvaluator.evaluate(hypothesis, req.observations, max_examples=_bounded(req.max_examples))
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return report.to_dict()


@router.post("/api/hypotheses/compare", dependencies=[Depends(require_api_key)])
def compare_formal_hypotheses(req: CompareFormalHypothesesRequest):
    """Logical relation between two hypotheses over the same state space, with discriminating states."""
    try:
        report = HypothesisEvaluator.compare(
            _to_hypothesis(req.a), _to_hypothesis(req.b), max_examples=_bounded(req.max_examples)
        )
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return report.to_dict()


@router.post("/api/hypotheses/entails", dependencies=[Depends(require_api_key)])
def check_formal_consequence(req: FormalConsequenceRequest):
    """Whether a consequence holds wherever the hypothesis applies and its claims hold, with counterexamples.

    With `include_lean`, the response also carries the consequence stated as a Lean 4 theorem. It is not
    kernel-checked by this server.
    """
    try:
        hypothesis = _to_hypothesis(req.hypothesis)
        result = HypothesisEvaluator.entails(hypothesis, req.consequence, max_examples=_bounded(req.max_examples))
        payload = result.to_dict()
        if req.include_lean:
            payload["lean_theorem"] = consequence_theorem(hypothesis, req.consequence)
            payload["lean_status"] = "NOT_KERNEL_CHECKED"
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return payload
