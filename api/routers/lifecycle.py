"""Research lifecycle endpoints: stage gates, versions, releases and the OnTrack export (ADR-DISCOVERY-063)."""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from api.schemas import (
    CreateLifecycleProjectRequest,
    LifecycleActorRequest,
    LifecycleReleaseRequest,
    LifecycleResultRequest,
    LifecycleReworkRequest,
)
from api.security import require_api_key
from python.discovery.evidence_service import PACKAGES_DIR, list_packages
from python.discovery.research_lifecycle import (
    ActorRole,
    LifecycleError,
    LifecycleService,
    LifecycleWatcher,
    ontrack_status,
    project_to_dict,
    template_to_dict,
)
from python.discovery.research_package import (
    EXTENSION,
    PackageError,
    SensitiveContentError,
    export_package,
    import_package,
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


MAX_UPLOAD_BYTES = 256 * 1024**2


@router.get("/api/lifecycle/projects/{project_id}/package", dependencies=[Depends(require_api_key)])
def export_lifecycle_package(project_id: str, allow_sensitive: bool = False):
    """The project as a research package (ADR-DISCOVERY-065): log, artifacts, README and RO-Crate metadata.

    Artifacts that changed or vanished since a check recorded them are listed as omissions. Possible credentials
    stop the export unless `allow_sensitive` is set. Requires the API key because the package carries file contents.
    """
    _project(project_id)
    try:
        data, _ = export_package(service, project_id, ROOT, allow_sensitive=allow_sensitive)
    except SensitiveContentError as exc:
        raise HTTPException(status_code=422, detail={"error": str(exc), "findings": exc.findings}) from exc
    except PackageError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(
        content=data,
        media_type="application/gzip",
        headers={"Content-Disposition": f'attachment; filename="{project_id}{EXTENSION}"'},
    )


@router.post("/api/lifecycle/packages/inspect", dependencies=[Depends(require_api_key)])
async def inspect_lifecycle_package(request: Request):
    """Verify a research package sent as the raw request body, without importing it. Nothing is stored."""
    data = await request.body()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Package too large for inspection over the API.")
    try:
        return import_package(data).summary()
    except PackageError as exc:
        return {"valid": False, "error": str(exc)}


@router.get("/api/lifecycle/packages")
def list_published_packages():
    """Research packages published in docs/reference/packages, with the digests listed in the package index."""
    return {"packages": list_packages()}


@router.get("/api/lifecycle/packages/{name}")
def download_published_package(name: str):
    """A published research package, byte for byte. Published packages are public, so no key is needed."""
    published = {p["name"]: p for p in list_packages()}
    if name not in published:
        raise HTTPException(status_code=404, detail=f"No published package {name!r}.")
    return Response(
        content=(PACKAGES_DIR / name).read_bytes(),
        media_type="application/gzip",
        headers={
            "Content-Disposition": f'attachment; filename="{name}"',
            "X-Package-SHA256": published[name]["sha256"],
        },
    )
