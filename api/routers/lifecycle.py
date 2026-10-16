"""Research lifecycle endpoints: stage gates, versions, releases and the OnTrack export (ADR-DISCOVERY-063)."""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import (
    CreateLifecycleProjectRequest,
    LifecycleActorRequest,
    LifecycleReleaseRequest,
    LifecycleResultRequest,
    LifecycleReworkRequest,
)
from api.security import require_api_key
from python.discovery.research_lifecycle import (
    ActorRole,
    LifecycleError,
    LifecycleService,
    LifecycleWatcher,
    ontrack_status,
    project_to_dict,
    template_to_dict,
)

router = APIRouter()

ROOT = Path(__file__).resolve().parent.parent.parent
# With CORESEARCHER_LIFECYCLE_LOG set, every change is appended to that JSON Lines file and replayed at start-up.
service = LifecycleService(os.environ.get("CORESEARCHER_LIFECYCLE_LOG") or None)


def _project(project_id: str):
    try:
        return service.get(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown project {project_id!r}.") from exc


def _conflict(exc: LifecycleError) -> HTTPException:
    return HTTPException(status_code=409, detail=str(exc))


@router.get("/api/lifecycle/template")
def lifecycle_template(name: str = "default"):
    """The checklist of every stage: each check's kind (VERIFIER, HUMAN, ARTIFACT, RUBRIC) and threshold."""
    try:
        return template_to_dict(name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown template {name!r}.") from exc


@router.post("/api/lifecycle/projects", dependencies=[Depends(require_api_key)])
def create_lifecycle_project(req: CreateLifecycleProjectRequest):
    try:
        project = service.create_project(req.project_id, req.title, req.template)
    except LifecycleError as exc:
        raise _conflict(exc) from exc
    return project_to_dict(project, service)


@router.get("/api/lifecycle/projects")
def list_lifecycle_projects():
    return {"projects": [project_to_dict(p, service) for p in service.projects.values()]}


@router.get("/api/lifecycle/projects/{project_id}")
def get_lifecycle_project(project_id: str):
    return project_to_dict(_project(project_id), service)


@router.post("/api/lifecycle/projects/{project_id}/results", dependencies=[Depends(require_api_key)])
def submit_lifecycle_result(project_id: str, req: LifecycleResultRequest):
    """Record a check result. A self-check (role AGENT) is kept but never satisfies a VERIFIER or HUMAN check."""
    _project(project_id)
    try:
        role = ActorRole(req.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="role must be AGENT, VERIFIER_TOOL or HUMAN.") from exc
    try:
        result = service.submit_result(
            project_id,
            req.check_id,
            req.ok,
            req.actor,
            role,
            req.note,
            req.value,
            req.artifact_path,
            req.sha256,
            req.criteria,
        )
    except LifecycleError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.to_dict()


@router.get("/api/lifecycle/projects/{project_id}/gate")
def evaluate_lifecycle_gate(project_id: str):
    """Decision for the gate of the current stage, with the status of each check and why."""
    _project(project_id)
    return service.evaluate_gate(project_id).to_dict()


@router.post("/api/lifecycle/projects/{project_id}/gate/pass", dependencies=[Depends(require_api_key)])
def pass_lifecycle_gate(project_id: str, req: LifecycleActorRequest):
    """Record the current gate as passed (refused unless every required check is satisfied) and advance."""
    _project(project_id)
    try:
        return service.pass_gate(project_id, req.actor).to_dict()
    except LifecycleError as exc:
        raise _conflict(exc) from exc


@router.post("/api/lifecycle/projects/{project_id}/rework", dependencies=[Depends(require_api_key)])
def rework_lifecycle_stage(project_id: str, req: LifecycleReworkRequest):
    _project(project_id)
    try:
        project = service.rework(project_id, req.stage, req.actor, req.reason)
    except LifecycleError as exc:
        raise _conflict(exc) from exc
    return project_to_dict(project, service)


@router.post("/api/lifecycle/projects/{project_id}/release", dependencies=[Depends(require_api_key)])
def release_lifecycle_project(project_id: str, req: LifecycleReleaseRequest):
    """Release the current version. The kind (EXPLORATORY or PREREGISTERED) is decided by policy, not the caller."""
    _project(project_id)
    try:
        return service.release(project_id, req.actor, req.summary).to_dict()
    except LifecycleError as exc:
        raise _conflict(exc) from exc


@router.get("/api/lifecycle/watch")
def watch_lifecycle():
    """Stalled stages, pending sign-offs, unreleased reports, and artifacts that changed after they were recorded."""
    return {"findings": [f.to_dict() for f in LifecycleWatcher(service, root=ROOT).scan()]}


@router.get("/api/lifecycle/ontrack")
def lifecycle_ontrack_status():
    """Every project in the `coresearcher.lifecycle/v1` shape that OnTrack ingests."""
    return ontrack_status(service, LifecycleWatcher(service, root=ROOT).scan())
