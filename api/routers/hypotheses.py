"""Formal hypothesis evaluation endpoints (ADR-DISCOVERY-059, ADR-DISCOVERY-060, ADR-DISCOVERY-064)."""

import os

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
from python.discovery.formalization_gate import (
    DEFAULT_SAMPLES,
    DEFAULT_TEMPERATURE,
    MAX_SAMPLES,
    GateResult,
    formalize_gated,
)
from python.discovery.formalizer import ChatClient

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


def _gate_samples(requested) -> int:
    if requested is not None:
        return max(1, min(MAX_SAMPLES, requested))
    try:
        return max(1, min(MAX_SAMPLES, int(os.getenv("FORMALIZER_SAMPLES", DEFAULT_SAMPLES))))
    except ValueError:
        return DEFAULT_SAMPLES


def run_formalizer(prose: str, hypothesis_id: str, schema, samples=None) -> GateResult:
    """Draws N formalizations from the configured model(s) and gates them by exact equivalence (ADR-064).

    N comes from the request, else FORMALIZER_SAMPLES, else 5. FORMALIZER_GATE_MODELS (comma-separated) spreads the
    samples over several models served at the same endpoint. HTTP 503 when no model is configured, 502 when the
    endpoint cannot be reached.
    """
    try:
        names = [m.strip() for m in os.getenv("FORMALIZER_GATE_MODELS", "").split(",") if m.strip()]
        if names:
            clients = {name: ChatClient(model=name) for name in names}
        else:
            client = ChatClient()
            clients = {getattr(client, "model", "") or "default": client}
        temperature = float(os.getenv("FORMALIZER_GATE_TEMPERATURE", DEFAULT_TEMPERATURE))
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=f"Formalizer not configured: {exc}") from exc
    try:
        return formalize_gated(prose, clients, _gate_samples(samples), hypothesis_id, schema, temperature)
    except FormalHypothesisError:
        raise
    except Exception as exc:  # Transport and HTTP errors from the model endpoint.
        raise HTTPException(status_code=502, detail=f"Formalizer endpoint failed: {type(exc).__name__}") from exc


def gated_payload(result: GateResult, rivals: list) -> dict:
    """The formalizer response. Only a formalization that passes the gate is evaluated and compared with rivals.

    `status` is PARSED when the gate passes. On FORMALIZATION_AMBIGUOUS nothing is evaluated as if it were the
    hypothesis: the rival readings are in `formalization_gate.classes`. With one sample that fails, `status` is that
    sample's parse status, as before the gate.
    """
    accepted = result.formalization
    if result.passes:
        status, error = accepted.status.value, accepted.error
    elif result.n_samples == 1:
        status, error = result.samples[0].status.value, result.sample_errors[0] or result.samples[0].error
    else:
        status, error = result.status.value, result.reason
    payload = {
        "status": status,
        "error": error,
        "formal_hypothesis": accepted.data if accepted is not None else {},
        "draft": True,
        "formalization_gate": result.to_dict(),
    }
    if result.passes:
        payload.update(formal_block(accepted.hypothesis, rivals))
    return payload


@router.post("/api/hypotheses/formalize", dependencies=[Depends(require_api_key)])
def formalize_hypothesis(req: FormalizeHypothesisRequest):
    """Prose -> N formal objects (by the configured local model) -> self-consistency gate -> exact evaluation.

    The gate (ADR-DISCOVERY-064) accepts a formalization only when a strict majority of the samples is proved
    logically equivalent; otherwise the response is FORMALIZATION_AMBIGUOUS and carries no evaluation. An accepted
    object is still a draft: the researcher must confirm it says what the prose meant.
    """
    schema = [v.model_dump() for v in req.variable_schema] if req.variable_schema is not None else None
    result = run_formalizer(req.prose, req.hypothesis_id, schema, req.samples)
    try:
        return gated_payload(result, [_to_hypothesis(r) for r in req.rivals])
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
