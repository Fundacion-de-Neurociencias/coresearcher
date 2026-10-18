"""EvidenceRequest -> EvidenceGraph for EdiTXT, and the capability catalogue of the whole API (ADR-DISCOVERY-067)."""

import json
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Request

from api.routers.lifecycle import service as lifecycle_service
from api.security import require_api_key
from python.discovery import evidence_service

router = APIRouter()

ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = ROOT / "schemas" / "evidence" / "v1"
MATURITY = ROOT / "schemas" / "module_maturity.json"

# Graphs are content-addressed, so a bounded in-memory store is enough: a client that misses one asks again.
MAX_STORED_GRAPHS = 512
_graphs: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
_lock = threading.Lock()


@router.post("/api/evidence/requests", dependencies=[Depends(require_api_key)])
def resolve_evidence_request(request: Dict[str, Any] = Body(...)):
    """Answer an EvidenceRequest with an EvidenceGraph (schema `coresearcher.evidence/v1`).

    Nothing in CoResearcher's evidence changes: the graph is computed from lifecycle projects, published research
    packages, the claims register, formal hypotheses and formal cases. Requires the API key because formal checks
    can be expensive.
    """
    try:
        graph = evidence_service.resolve(request, lifecycle_service=lifecycle_service, root=ROOT)
    except evidence_service.EvidenceRequestError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    with _lock:
        _graphs[graph["graph_id"]] = graph
        _graphs.move_to_end(graph["graph_id"])
        while len(_graphs) > MAX_STORED_GRAPHS:
            _graphs.popitem(last=False)
    return graph


@router.get("/api/evidence/graphs/{graph_id}")
def get_evidence_graph(graph_id: str):
    """A graph this server produced recently. Graphs are content-addressed; a missing one is recomputed by asking."""
    with _lock:
        graph = _graphs.get(graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Graph {graph_id!r} is not stored; send the request again.")
    return graph


@router.get("/api/evidence/schema")
def evidence_schema():
    """The JSON Schemas of the EvidenceRequest and EvidenceGraph contract (coresearcher.evidence/v1)."""
    return {
        "schema": evidence_service.SCHEMA,
        "evidence_request": json.loads((SCHEMA_DIR / "evidence_request.schema.json").read_text(encoding="utf-8")),
        "evidence_graph": json.loads((SCHEMA_DIR / "evidence_graph.schema.json").read_text(encoding="utf-8")),
    }


@router.get("/api/evidence/targets")
def evidence_targets():
    """Everything an EvidenceRequest can point at: lifecycle projects, packages, register rows and formal cases."""
    return evidence_service.list_targets(lifecycle_service)


# --------------------------------------------------------------------------- capability catalogue

# Pure computations: same input, same output, nothing stored. Everything else is NON_DETERMINISTIC by default.
DETERMINISTIC = {
    ("POST", "/api/hypotheses/evaluate"),
    ("POST", "/api/hypotheses/compare"),
    ("POST", "/api/hypotheses/entails"),
    ("POST", "/api/lifecycle/packages/inspect"),
    ("GET", "/api/hypotheses/scenarios/alzheimer"),
    ("GET", "/api/lifecycle/template"),
    ("GET", "/api/evidence/schema"),
}
# POST endpoints that compute and return without changing any state the server keeps (beyond caches).
READ_ONLY_POSTS = {
    "/api/evidence/requests",
    "/api/hypotheses/evaluate",
    "/api/hypotheses/compare",
    "/api/hypotheses/entails",
    "/api/hypotheses/formalize",
    "/api/lifecycle/packages/inspect",
}


def _maturity() -> Dict[str, str]:
    try:
        data = json.loads(MATURITY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {m["module"]: m["level"] for m in data.get("modules", [])}


def _modules_of(endpoint) -> list:
    """Discovery modules an endpoint's code refers to, found from the names it uses."""
    code = getattr(endpoint, "__code__", None)
    if code is None:
        return []
    found = set()
    for name in code.co_names:
        obj = endpoint.__globals__.get(name)
        module = getattr(obj, "__module__", None) or getattr(obj, "__name__", "")
        if isinstance(module, str) and module.startswith("python.discovery."):
            found.add(module.split(".")[2])
    return sorted(found)


def _routes(routes):
    """Leaf routes, also through the included-router wrappers that newer FastAPI versions add."""
    for route in routes:
        nested = getattr(route, "original_router", None)
        if nested is not None:
            yield from _routes(nested.routes)
        elif getattr(route, "endpoint", None) is not None and hasattr(route, "path"):
            yield route


@router.get("/api/capabilities")
def capabilities(request: Request):
    """Every endpoint as an OnTrack CapabilityContract: input and output schemas, determinism, operation class,
    whether it needs the API key, and the maturity of the modules behind it (docs/reference/MODULE_MATURITY.md).
    """
    spec = request.app.openapi()
    endpoints = {
        (method, route.path): route.endpoint for route in _routes(request.app.routes) for method in route.methods or ()
    }
    maturity = _maturity()
    items = []
    for path, operations in sorted(spec.get("paths", {}).items()):
        for method, op in sorted(operations.items()):
            verb = method.upper()
            body = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            output = op.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema")
            parts = path.split("/")
            modules = _modules_of(endpoints.get((verb, path)))
            items.append(
                {
                    "name": op.get("operationId", f"{verb} {path}"),
                    "description": (op.get("description") or op.get("summary") or "").strip(),
                    "method": verb,
                    "path": path,
                    "group": "/".join(parts[2:4]) if len(parts) > 3 and parts[2] == "discovery" else parts[2],
                    "inputSchema": {
                        "body": body,
                        "parameters": [
                            {"name": p["name"], "in": p["in"], "required": p.get("required", False)}
                            for p in op.get("parameters", [])
                        ],
                    },
                    "outputSchema": output or {},
                    "determinism": "DETERMINISTIC" if (verb, path) in DETERMINISTIC else "NON_DETERMINISTIC",
                    "operationClass": ("READ_ONLY" if verb == "GET" or path in READ_ONLY_POSTS else "STATE_MODIFYING"),
                    "requiresApiKey": bool(op.get("security")),
                    "modules": [{"module": m, "maturity": maturity.get(m, "unknown")} for m in modules],
                }
            )
    return {
        "schema": "coresearcher.capabilities/v1",
        "service": spec.get("info", {}).get("title"),
        "version": spec.get("info", {}).get("version"),
        "components": spec.get("components", {}).get("schemas", {}),
        "capabilities": items,
    }
