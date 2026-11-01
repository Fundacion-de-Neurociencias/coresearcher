"""Freeze service and the composed verification chain (ADR-DISCOVERY-085)."""

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import (
    FreezeDocumentRequest,
    FreezeHypothesisRequest,
    FreezeVerifyRequest,
    VerificationChainRequest,
)
from api.security import require_api_key
from python.discovery import formal_status, freeze_service, verification_chain
from python.discovery.formal_hypothesis import FormalHypothesisError

router = APIRouter()
_store = freeze_service.load()


def store() -> freeze_service.FreezeStore:
    """The process-wide freeze store: persisted at CORESEARCHER_FREEZE_PATH when set, in memory otherwise."""
    return _store


def _lifecycle(anchor):
    if anchor is None:
        return None, None
    from api.routers.lifecycle import service

    return anchor.model_dump(), freeze_service.lifecycle_lookup(service)


def _non_verdict(exc: Exception):
    """A malformed object is 422; a solver non-verdict while computing criteria is 409: nothing is frozen."""
    try:
        status = formal_status.classify(exc)
    except Exception:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if status is formal_status.FormalStatus.INVALID_INPUT:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise HTTPException(
        status_code=409,
        detail={"formal_status": status.value, "reason": f"{type(exc).__name__}: {exc}", "frozen": False},
    ) from exc


@router.post("/api/freezes/hypothesis", dependencies=[Depends(require_api_key)])
def freeze_hypothesis(req: FreezeHypothesisRequest):
    """Freezes what would count as support or refutation of a hypothesis against its rivals, before any evaluation.

    The criteria are the discriminating states, computed from the formal objects alone (no observations). The freeze
    has a SHA-256, a time and an author, recorded in a hash-chained log. Freezing the same content again returns the
    earliest freeze (`already_frozen`).
    """
    anchor, lookup = _lifecycle(req.lifecycle)
    try:
        return store().freeze_hypothesis(
            req.hypothesis.model_dump(),
            [r.model_dump() for r in req.rivals],
            req.author,
            req.label,
            req.stated_criteria or None,
            req.max_examples,
            "auto",
            anchor,
            lookup,
        )
    except freeze_service.FreezeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (FormalHypothesisError, ImportError, formal_status.CapabilityUnavailable) as exc:
        _non_verdict(exc)


@router.post("/api/freezes/document", dependencies=[Depends(require_api_key)])
def freeze_document(req: FreezeDocumentRequest):
    """Freezes a protocol or checklist by the SHA-256 of its UTF-8 bytes, the digest a lifecycle ARTIFACT records."""
    anchor, lookup = _lifecycle(req.lifecycle)
    try:
        return store().freeze_document(req.text.encode("utf-8"), req.author, req.label, req.name, anchor, lookup)
    except freeze_service.FreezeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/api/freezes/{freeze_id}")
def get_freeze(freeze_id: str):
    """One freeze record: kind, SHA-256, author, time, the frozen content and any lifecycle anchor."""
    try:
        return store().get(freeze_id)
    except freeze_service.FreezeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/freezes/{freeze_id}/verify", dependencies=[Depends(require_api_key)])
def verify_freeze(freeze_id: str, req: FreezeVerifyRequest):
    """VERIFIED (DECIDED) or CHANGED/UNKNOWN (BLOCKED): does the freeze still hold for what is about to be used?"""
    try:
        return store().verify_reference(
            freeze_id,
            req.expected_sha256,
            req.hypothesis.model_dump() if req.hypothesis is not None else None,
            [r.model_dump() for r in req.rivals],
            req.text.encode("utf-8") if req.text is not None else None,
        )
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/chain/run", dependencies=[Depends(require_api_key)])
def run_verification_chain(req: VerificationChainRequest):
    """The composed chain of the verification methodology, end to end, with every step's state.

    freeze (M3) -> formalize (M2) -> fidelity (M1) -> vacuity (M4) -> obligations (M5) -> seams (M6) -> discharge
    (M8) -> trust ladder (M7). A non-verdict stops the chain: later steps are NOT_RUN and `formal_status` is that
    non-verdict; nothing undecided is reported as decided. Prose needs the configured formalizer model. A
    `mechanism` is compiled without a model, and a `biomedical` block adds units, conventions and domain probes
    (ADR-086).
    """
    from api.routers.registry import registry

    spec = req.model_dump(exclude_none=True)
    spec["citations"] = [c.model_dump(exclude_none=True) for c in req.citations]
    if req.mechanism is not None:  # Links use the key "from" (ADR-086).
        spec["mechanism"] = req.mechanism.model_dump(by_alias=True, exclude_none=True)
    spec["claim_evidence"] = {k: v.model_dump(exclude_none=True) for k, v in req.claim_evidence.items()}
    clients = None
    if req.prose is not None:
        from python.cli.formal import formalizer_clients

        try:
            clients = formalizer_clients()
        except ValueError:
            clients = {}
    try:
        return verification_chain.run(spec, store(), registry(), clients)
    except (verification_chain.ChainInputError, FormalHypothesisError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
