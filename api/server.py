"""FastAPI application for CoResearcher.

Routes live in ``api/routers/``, grouped by domain. This module only assembles
the application: CORS, rate limiting, routers and the health probe.

Configuration comes from environment variables (see ``.env.example``):

- ``CORESEARCHER_API_KEY``: required in ``X-API-Key`` for every POST, PUT and DELETE.
- ``CORESEARCHER_GITHUB_WEBHOOK_SECRET``: HMAC secret for the GitHub PR webhook.
- ``CORESEARCHER_CORS_ORIGINS``: comma-separated list of allowed browser origins.
- ``CORESEARCHER_RATE_LIMIT_PER_MINUTE``: requests allowed per client IP per minute.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import discovery, evidence, formal_audits, hypotheses, lifecycle, ontology, provenance, webhooks
from api.security import RateLimitMiddleware
from api.state import (
    biological_programs_list,
    epistemic_git_repo,
    hypothesis_graveyard,
    representation_ledger,
    state_space_omega,
    workbenches_registry,
)

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="CoResearcher Epistemic Discovery & Auditor API", version="4.1.0")

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.environ.get("CORESEARCHER_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(
            ","
        )
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key"],
)

for _module in (discovery, evidence, formal_audits, hypotheses, lifecycle, provenance, ontology, webhooks):
    app.include_router(_module.router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CoResearcher Epistemic Discovery & Auditor API (TRACES Epistemic Adapter & Test-Time Science Active)",
        "architecture_status": "FROZEN (ADR-009)",
        "state_space_omega_volume": state_space_omega.total_volume,
        "representation_space_count": len(representation_ledger.candidate_representations),
        "biological_programs_count": len(biological_programs_list),
        "defeated_hypotheses_in_graveyard": len(hypothesis_graveyard.records),
        "active_workbenches_count": len(workbenches_registry),
        "scientific_commits_count": len(epistemic_git_repo.commits),
        "universality_domains": ["NEUROSCIENCE", "ASTRONOMY", "MACROECONOMICS", "MARINE_ECOLOGY"],
        "discovery_benchmark": "TRACES Epistemic Meta-Audit (DV, RCS, FRI, SG, CSR) & ConstraintBox",
        "reality_distance_hierarchy": "Dry (Synthetic) -> Damp (Surrogate) -> Wet (Empirical)",
        "failure_engine_status": "DUHEM-QUINE ROOT CAUSE AUTOPSY ACTIVE",
        "long_horizon_engine_status": "MULTI-CYCLE TEST-TIME SCIENCE + BAYESIAN SURPRISE + ECONOMIC BUDGET ACTIVE",
        "core_maxim": "CoResearcher is NOT an answer system. It IS a system for the progressive reduction of the possible scientific state space via audit-grade constraints, predictions, and falsifications.",
    }
