"""Formal hypothesis evaluation endpoints (ADR-DISCOVERY-059, ADR-DISCOVERY-060)."""

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import (
    CompareFormalHypothesesRequest,
    EvaluateFormalHypothesisRequest,
    FormalConsequenceRequest,
    FormalHypothesisModel,
    FormalizeHypothesisRequest,
)
from api.security import require_api_key
from python.discovery import alzheimer_formal_scenario
from python.discovery.formal_hypothesis import (
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    hypothesis_from_dict,
)
from python.discovery.formal_lean import consequence_theorem
from python.discovery.formalizer import ChatClient, FormalizationStatus, formalize

router = APIRouter()


def _to_hypothesis(model: FormalHypothesisModel) -> Hypothesis:
    return hypothesis_from_dict(model.model_dump())


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


@router.get("/api/hypotheses/scenarios/alzheimer")
def alzheimer_formal_scenario_report():
    """The demo Alzheimer rivals as formal hypotheses (draft, pending scientist review), evaluated and compared."""
    return alzheimer_formal_scenario.scenario_report()


def formal_block(hypothesis: Hypothesis, rivals: list) -> dict:
    """Evaluation of a formal hypothesis and its comparison with every rival over the same state space."""
    comparisons = []
    for rival in rivals:
        try:
            comparisons.append(HypothesisEvaluator.compare(hypothesis, rival, max_examples=3).to_dict())
        except FormalHypothesisError as exc:
            comparisons.append(
                {
                    "hypothesis_a": hypothesis.hypothesis_id,
                    "hypothesis_b": rival.hypothesis_id,
                    "relation": None,
                    "error": str(exc),
                }
            )
    return {"evaluation": HypothesisEvaluator.evaluate(hypothesis).to_dict(), "comparisons": comparisons}


def run_formalizer(prose: str, hypothesis_id: str, schema):
    """Calls the configured formalizer model; HTTP 503 when none is configured, 502 when it cannot be reached."""
    try:
        client = ChatClient()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=f"Formalizer not configured: {exc}") from exc
    try:
        return formalize(prose, client, hypothesis_id, schema)
    except Exception as exc:  # Transport and HTTP errors from the model endpoint.
        raise HTTPException(status_code=502, detail=f"Formalizer endpoint failed: {type(exc).__name__}") from exc


@router.post("/api/hypotheses/formalize", dependencies=[Depends(require_api_key)])
def formalize_hypothesis(req: FormalizeHypothesisRequest):
    """Prose -> formal object (by the configured local model) -> exact evaluation and comparison with rivals.

    The formal object is a draft: the researcher must confirm it says what the prose meant before relying on the
    verdicts, which only cover the object.
    """
    schema = [v.model_dump() for v in req.variable_schema] if req.variable_schema is not None else None
    result = run_formalizer(req.prose, req.hypothesis_id, schema)
    payload = {"status": result.status.value, "error": result.error, "formal_hypothesis": result.data, "draft": True}
    if result.status == FormalizationStatus.PARSED:
        try:
            payload.update(formal_block(result.hypothesis, [_to_hypothesis(r) for r in req.rivals]))
        except FormalHypothesisError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    return payload
