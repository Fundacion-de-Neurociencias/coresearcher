"""Biomedical checks of formal hypotheses and mechanistic chains (ADR-DISCOVERY-086)."""

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import BiomedicalCheckRequest, MechanismCheckRequest
from api.security import require_api_key
from python.discovery import biomedical_conventions, biomedical_domain, formal_status, mechanistic_chain
from python.discovery.formal_hypothesis import FormalHypothesisError

router = APIRouter()


@router.get("/api/biomedical/vocabulary")
def vocabulary():
    """The convention kinds of the cited-results registry (assay, platform, matrix, units, population, reference
    standard, scale direction, cutoff derivation), their aliases and their canonical values."""
    return biomedical_conventions.vocabulary()


@router.post("/api/biomedical/check", dependencies=[Depends(require_api_key)])
def check(req: BiomedicalCheckRequest):
    """Units, null-biomarker, untreated-arm and population probes of one formal hypothesis, as ADR-076 obligations.

    Every obligation is decided exactly (enumeration or z3) or left OPEN with its reason. Scope: formal soundness;
    whether a unit, a cutoff or a population is clinically right is not judged.
    """
    spec = req.biomedical.model_dump(exclude_none=True)
    try:
        obligations, report = biomedical_domain.check(req.hypothesis.model_dump(), spec, req.consequences, req.backend)
    except (biomedical_domain.DomainSpecError, FormalHypothesisError) as exc:
        try:
            status = formal_status.classify(exc)
        except Exception:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if status is formal_status.FormalStatus.INVALID_INPUT:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        raise HTTPException(status_code=409, detail={"formal_status": status.value, "reason": str(exc)}) from exc
    return {
        "formal_status": formal_status.FormalStatus.DECIDED.value,
        "obligations": [biomedical_domain.obligation_dict(o) for o in obligations],
        "report": report,
    }


@router.post("/api/biomedical/mechanism", dependencies=[Depends(require_api_key)])
def mechanism(req: MechanismCheckRequest):
    """Compiles a mechanistic chain (nodes and signed links, or controlled prose) to a two-world hypothesis and decides
    each link, each link's sign and the compatibility of the links with the end-to-end prediction.

    Prose outside the controlled language returns `formal_status` FORMALIZATION_FAILED, never a guess.
    """
    try:
        return mechanistic_chain.check(req.mechanism.model_dump(by_alias=True, exclude_none=True), req.backend)
    except (mechanistic_chain.MechanismError, FormalHypothesisError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
