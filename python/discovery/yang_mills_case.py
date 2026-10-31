"""
python/discovery/yang_mills_case.py - Pre-registered audit of the announced existence proof of four-dimensional
quantum Yang-Mills theory (ADR-DISCOVERY-081).

On October 26, 2026 OpenAI announced an existence proof of quantum Yang-Mills theory including fermions. A
committee (Douglas, Gross (chair), Jaffe, Klebanov, Nekrasov) holds the manuscript and a Lean formalization and will
first check that the definitions and problem statement match the standard ones. Neither is public. This module
holds what can be done now:

- the claim record, at CLAIMED on the trust ladder, with its reason;
- the frozen checklist (examples/yang-mills-preregistration/ym4_existence_checklist.v1.json and its lock);
- a self-probe: the checklist's own in-claim obligations must exclude every catalogued trivial witness, and the
  report lists, for every witness, which obligations exclude it (so the audit knows which clauses must survive
  into the Lean statement for each cheap model to stay out);
- scenario probes: the checklist with obligations removed that a formalization might plausibly leave out.

Nothing here assesses the proof, its credit or the announcement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from python.discovery import preregistration
from python.discovery.trivial_witness import checklist_clauses, necessity, probe
from python.discovery.trust_ladder import ClaimRecord

ROOT = Path(__file__).resolve().parent.parent.parent
CASE_DIR = ROOT / "examples" / "yang-mills-preregistration"
CHECKLIST = CASE_DIR / "ym4_existence_checklist.v1.json"

COMMITTEE_STATEMENT = {
    "url": "https://www.kitp.ucsb.edu/sites/default/files/YM_working_group.pdf",
    "sha256": "dbab31f0f954ac8265a3fc1c1a29664c7fa0b7f16c616d58012e65896557bd12",
    "retrieved": "2026-10-30",
    "pages": 2,
}


def checklist() -> preregistration.Checklist:
    return preregistration.load(CHECKLIST)


def claim_record() -> ClaimRecord:
    record = ClaimRecord(
        id="openai-ym4-existence-2026",
        claim="Existence of quantum Yang-Mills theory, including coupling to fermions (committee statement, "
        "October 2026). The statement does not name the dimension or the gauge groups covered; it names SU(3) "
        "with quarks (QCD) as context and says the mass gap and confinement remain open.",
        claimant="OpenAI",
    )
    record.start(
        date="2026-10-30",
        reason="Statement not public: neither the 1147-page manuscript nor the Lean formalization has been "
        "released. The committee will release the Lean proof after checking that the definitions and problem "
        "statement match the standard ones.",
        evidence={
            "announcement": COMMITTEE_STATEMENT["url"],
            "announcement_sha256": COMMITTEE_STATEMENT["sha256"],
            "retrieved": COMMITTEE_STATEMENT["retrieved"],
            "checklist_frozen_before_statement": "ym4-existence v1.0.0",
        },
    )
    return record


# Obligations a formalization might plausibly leave out, and what then gets through.
SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "no_short_distance",
        "drop": ["YM-SHORT-DISTANCE"],
        "why": "Asymptotic freedom and the OPE are the hardest clauses to state in Lean; a formalization may omit them.",
    },
    {
        "id": "no_short_distance_no_local_fields",
        "drop": ["YM-SHORT-DISTANCE", "YM-OBS-LOCAL-CURVATURE"],
        "why": "A Wilson-loop-only construction without short-distance clauses.",
    },
    {
        "id": "os_and_group_only",
        "keep": [
            "YM-GROUP-NONABELIAN",
            "YM-SPACETIME-DIM4",
            "YM-SPACETIME-INFINITE",
            "YM-OS-REGULARITY",
            "YM-OS-EUCLIDEAN",
            "YM-OS-RP",
            "YM-OS-SYMMETRY",
            "YM-OS-CLUSTER",
        ],
        "why": "'An OS theory on R^4 labelled by a compact simple group': the shape most likely to be called "
        "'Yang-Mills' without saying what makes it Yang-Mills.",
    },
    {
        "id": "no_nontriviality",
        "drop": ["YM-SHORT-DISTANCE", "YM-NONTRIVIAL"],
        "why": "Non-triviality stated only in prose.",
    },
]


def scenario_clauses(c: preregistration.Checklist, scenario: Dict[str, Any], claim: str = "YM") -> Dict[str, str]:
    clauses = checklist_clauses(c, claim)
    if "keep" in scenario:
        return {k: v for k, v in clauses.items() if k in scenario["keep"]}
    return {k: v for k, v in clauses.items() if k not in scenario["drop"]}


def case_report() -> Dict[str, Any]:
    c = checklist()
    self_probes = {claim: probe(c, checklist_clauses(c, claim), statement=f"checklist, claim {claim}").to_dict() for claim in ("YM", "QCD")}
    barriers = {
        w["witness"]: w["excluded_by"] for w in self_probes["YM"]["witnesses"]
    }
    scenarios = []
    for s in SCENARIOS:
        result = probe(c, scenario_clauses(c, s), statement=s["id"]).to_dict()
        scenarios.append(
            {
                "id": s["id"],
                "why": s["why"],
                "dropped": s.get("drop", []),
                "kept": s.get("keep", []),
                "outcome": result["outcome"],
                "satisfied_by": result["satisfied_by"],
                "undetermined": result["undetermined"],
            }
        )
    return {
        "checklist": {"id": c.id, "version": c.version, "frozen_on": c.data["frozen_on"], "sha256": c.sha256, "lock": c.lock},
        "claim_record": claim_record().to_dict(),
        "obligations": [
            {"id": o.id, "category": o.category, "applies_to": o.applies_to, "clause": o.formal_clause}
            for o in c.obligations
        ],
        "self_probe": self_probes,
        "barriers_per_witness": barriers,
        "single_barrier_obligations": necessity(c, "YM"),
        "single_barrier_obligations_without_short_distance": necessity(
            c, clauses=scenario_clauses(c, SCENARIOS[0])
        ),
        "scenarios": scenarios,
    }
