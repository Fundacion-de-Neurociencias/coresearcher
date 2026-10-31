"""Cited-results registry endpoints: register, cite-check, dependencies, retraction (ADR-DISCOVERY-083)."""

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import (
    CiteCheckRequest,
    RegistryDependencyRequest,
    RegistryEntryRequest,
    RegistryReevaluatedRequest,
    RegistryRetractRequest,
)
from api.security import require_api_key
from python.discovery import cited_registry
from python.discovery.formal_hypothesis import FormalHypothesisError

router = APIRouter()
_registry = cited_registry.load()


def registry() -> cited_registry.Registry:
    """The process-wide registry: persisted at CORESEARCHER_REGISTRY_PATH when set, in memory otherwise."""
    return _registry


def _fail(exc: Exception):
    status = 404 if "No registry entry" in str(exc) else 422
    raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.post("/api/registry/entries", dependencies=[Depends(require_api_key)])
def register_entry(req: RegistryEntryRequest):
    """Adds a cited result or premise, or a new version of one. The source is provenance, never evidence."""
    try:
        entry = registry().register(req.model_dump())
    except (cited_registry.RegistryError, FormalHypothesisError, TypeError) as exc:
        _fail(exc)
    return {"entry": asdict(entry)}


@router.get("/api/registry/entries/{entry_id}")
def get_entry(entry_id: str, version: Optional[int] = None):
    """One entry (the latest version unless `version` is given), with its re-evaluation flag if any."""
    try:
        entry = registry().get(entry_id, version)
    except cited_registry.RegistryError as exc:
        _fail(exc)
    return {"entry": asdict(entry), "flag": registry().flags.get(entry_id)}


@router.post("/api/registry/cite-check", dependencies=[Depends(require_api_key)])
def cite_check(req: CiteCheckRequest):
    """Checks one use of a registered result: conventions match and hypotheses are entailed by the citing context.

    `outcome` is CLEAR (all discharged and matched, entry active), FINDINGS (a mismatch, an undischarged hypothesis
    with counterexamples, or a retracted entry) or INCOMPLETE (nothing contradicts, but something is UNDECIDED or
    UNSPECIFIED). Only a formal entailment discharges a hypothesis; a phrase in the text is STATED_IN_TEXT.
    """
    try:
        entry = registry().get(req.entry_id, req.version)
        return cited_registry.cite_check(entry, req.context.model_dump())
    except (cited_registry.RegistryError, FormalHypothesisError) as exc:
        _fail(exc)


@router.post("/api/registry/dependencies", dependencies=[Depends(require_api_key)])
def add_dependency(req: RegistryDependencyRequest):
    """Records that a claim or entry uses another. Edges that would close a cycle are refused."""
    try:
        return registry().depend(req.node, req.depends_on)
    except cited_registry.RegistryError as exc:
        _fail(exc)


@router.post("/api/registry/entries/{entry_id}/retract", dependencies=[Depends(require_api_key)])
def retract_entry(entry_id: str, req: RegistryRetractRequest):
    """Retracts an entry (or downgrades it to a lower rung) and flags every transitive dependent.

    A flagged dependent's rung is capped at CLAIMED until it is re-evaluated.
    """
    try:
        return registry().retract(entry_id, req.reason, req.downgrade_to, req.date)
    except cited_registry.RegistryError as exc:
        _fail(exc)


@router.get("/api/registry/impact/{node}")
def impact(node: str):
    """Every claim or entry that transitively depends on `node`, with any re-evaluation flags."""
    return registry().impact(node)


@router.post("/api/registry/flags/{node}/reevaluated", dependencies=[Depends(require_api_key)])
def clear_flag(node: str, req: RegistryReevaluatedRequest):
    """Clears a dependent's re-evaluation flag; the note records how it was re-checked."""
    try:
        return registry().reevaluated(node, req.note)
    except cited_registry.RegistryError as exc:
        _fail(exc)
