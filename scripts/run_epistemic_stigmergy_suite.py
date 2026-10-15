"""
scripts/run_epistemic_stigmergy_suite.py - Verification Suite for Epistemic Stigmergy & Meta-Recursive Instrument Engine (ADR-DISCOVERY-027)
Tests:
1. Pheromone field scanning over canonical EpistemicGitRepo (attractors, repulsors, role recommendation, SOM hash).
2. MetaRecursiveInstrumentCompiler: hypothesis-to-world compilation with constraint rule inference.
3. RealityContactFirewall: promotion gating for swarm-derived theories (pass and block scenarios).
4. FastAPI REST API endpoints via TestClient for all three stigmergy routes.
"""

import sys
import os
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from python.discovery.epistemic_stigmergy import (
    PheromoneType,
    EpistemicPheromone,
    PheromoneLandscapeReport,
    EpistemicPheromoneField,
    MetaRecursiveInstrument,
    MetaRecursiveInstrumentCompiler,
    RealityContactFirewallReport,
    RealityContactFirewall,
)
from python.discovery.scientific_git_history import EpistemicGitRepo
from fastapi.testclient import TestClient
from api.server import app
from api.testing import authenticated_client


def test_pheromone_field_scanning():
    print("\n--- 1. Testing Epistemic Pheromone Field Scanning ---")

    # Use canonical tau lineage repo (has verified claims, active branches, commits)
    repo = EpistemicGitRepo.create_canonical_tau_lineage()
    report = EpistemicPheromoneField.scan_git_repository(repo, uncertainty_threshold=0.60)

    assert isinstance(report, PheromoneLandscapeReport)
    assert report.total_active_pheromones > 0
    assert report.som_landscape_hash.startswith("sha256:")
    assert isinstance(report.attractors, list)
    assert isinstance(report.repulsors, list)
    assert report.recommended_swarm_role in [
        "POPPER_ADVERSARIAL_AUDITOR",
        "HYPOTHESIS_EXPLORER",
        "INVARIANT_FORMALIZER",
        "VALIDATION_AUDITOR",
        "AUTONOMOUS_SCOUT",
    ]
    print(f"  [PASS] Pheromone field scanned: {report.total_active_pheromones} active pheromones")
    print(f"  [PASS] Recommended swarm role: {report.recommended_swarm_role}")
    print(f"  [PASS] Attractors: {len(report.attractors)}, Repulsors: {len(report.repulsors)}")
    print(f"  [PASS] SOM landscape hash: {report.som_landscape_hash[:24]}...")

    # Verify to_dict roundtrip
    d = report.to_dict()
    assert "total_active_pheromones" in d
    assert "recommended_swarm_role" in d
    assert "som_landscape_hash" in d
    print("  [PASS] to_dict() roundtrip verified")

    # Verify pheromone types are proper enum values
    if report.strongest_attractor:
        att_dict = report.strongest_attractor.to_dict()
        assert att_dict["pheromone_type"] in [pt.value for pt in PheromoneType]
        print(f"  [PASS] Strongest attractor: {att_dict['pheromone_type']} (intensity={att_dict['intensity']})")


def test_meta_recursive_instrument_compiler():
    print("\n--- 2. Testing Meta-Recursive Instrument Compiler ---")

    # Scenario A: Necessary condition hypothesis
    inst_a = MetaRecursiveInstrumentCompiler.compile_hypothesis_into_world(
        representation_id="REP-TAU-PHOSPHO-001",
        hypothesis_statement="Tau hyperphosphorylation requires both GSK3-beta activation and PP2A inhibition",
        key_variables=["GSK3_BETA_ACTIVITY", "PP2A_ACTIVITY"]
    )
    assert isinstance(inst_a, MetaRecursiveInstrument)
    assert inst_a.is_compiled is True
    assert inst_a.instrument_id.startswith("INST-")
    assert inst_a.simulated_world_id.startswith("WORLD-SIM-")
    assert inst_a.target_representation_id == "REP-TAU-PHOSPHO-001"
    assert len(inst_a.executable_rules) > 0
    assert inst_a.executable_rules[0]["rule_type"] == "NECESSARY_CONDITION"
    assert inst_a.som_instrument_hash.startswith("sha256:")
    print(f"  [PASS] Instrument A compiled: {inst_a.instrument_id} -> {inst_a.simulated_world_id}")
    print(f"  [PASS] Rule type: {inst_a.executable_rules[0]['rule_type']}")

    # Scenario B: Inhibition hypothesis
    inst_b = MetaRecursiveInstrumentCompiler.compile_hypothesis_into_world(
        representation_id="REP-ABETA-CLEAR-002",
        hypothesis_statement="Microglial TREM2 deficiency blocks amyloid-beta clearance",
        key_variables=["TREM2_EXPRESSION"]
    )
    assert inst_b.executable_rules[0]["rule_type"] == "SUFFICIENT_TRIGGER"
    print(f"  [PASS] Instrument B: inhibition -> SUFFICIENT_TRIGGER (world={inst_b.simulated_world_id})")

    # Scenario C: Default boundary threshold
    inst_c = MetaRecursiveInstrumentCompiler.compile_hypothesis_into_world(
        representation_id="REP-FDG-PET-003",
        hypothesis_statement="FDG-PET metabolic decline predicts cognitive transition within 24 months",
        key_variables=["FDG_SUVr"]
    )
    assert inst_c.executable_rules[0]["rule_type"] == "BOUNDARY_THRESHOLD"
    print(f"  [PASS] Instrument C: default -> BOUNDARY_THRESHOLD")

    # Verify to_dict
    d = inst_a.to_dict()
    assert "instrument_id" in d
    assert "simulated_world_id" in d
    assert "executable_rules" in d
    assert "som_instrument_hash" in d
    print("  [PASS] to_dict() roundtrip verified")


def test_reality_contact_firewall():
    print("\n--- 3. Testing Reality Contact Firewall ---")

    # Scenario A: Insufficient RCS (Level 1) -> BLOCKED
    report_a = RealityContactFirewall.audit_promotion_request(
        hypothesis_id="HYPO-SWARM-TAU-001",
        claimed_regularity="Tau seeding follows exponential kinetics in silico with k=0.032",
        rcs_level=1,
        empirical_anchors=["SIMULATED_AGENT_TRAJECTORY_42"]
    )
    assert isinstance(report_a, RealityContactFirewallReport)
    assert report_a.is_firewall_passed is False
    assert "BLOCKED" in report_a.rejection_reason
    assert report_a.epistemic_directive == "REJECT_PROMOTION_AND_DEMAND_PHYSICAL_BENCHMARK"
    assert report_a.som_firewall_hash.startswith("sha256:")
    print(f"  [PASS] Firewall correctly BLOCKED RCS Level 1 theory")
    print(f"  [PASS] Rejection: {report_a.rejection_reason[:60]}...")

    # Scenario B: Sufficient RCS (Level 3) with empirical anchors -> PASSED
    report_b = RealityContactFirewall.audit_promotion_request(
        hypothesis_id="HYPO-VALIDATED-ABETA-002",
        claimed_regularity="Abeta42 oligomer-induced membrane thinning follows Helfrich elasticity model",
        rcs_level=3,
        empirical_anchors=["ADNI_COHORT_CSF_ABETA42", "HUCA_PROSPECTIVE_PET"]
    )
    assert report_b.is_firewall_passed is True
    assert report_b.rejection_reason is None
    assert report_b.epistemic_directive == "PROMOTE_TO_INVARIANT_CONSTRAINT"
    print(f"  [PASS] Firewall correctly PASSED RCS Level 3 theory with physical anchors")

    # Scenario C: Sufficient RCS but NO empirical anchors -> BLOCKED
    report_c = RealityContactFirewall.audit_promotion_request(
        hypothesis_id="HYPO-EMPTY-003",
        claimed_regularity="Pure simulation emergent pattern without grounding",
        rcs_level=3,
        empirical_anchors=[]
    )
    assert report_c.is_firewall_passed is False
    print(f"  [PASS] Firewall correctly BLOCKED: high RCS but empty anchors")

    # Verify to_dict
    d = report_a.to_dict()
    assert "hypothesis_id" in d
    assert "is_firewall_passed" in d
    assert "som_firewall_hash" in d
    print("  [PASS] to_dict() roundtrip verified")


def test_rest_api_endpoints():
    print("\n--- 4. Testing REST API Endpoints (TestClient) ---")

    client = authenticated_client(app)

    # 4a. Query Pheromone Field
    resp = client.post("/api/discovery/stigmergy/query-pheromone-field", json={
        "uncertainty_threshold": 0.60
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "total_active_pheromones" in data
    assert "recommended_swarm_role" in data
    assert "som_landscape_hash" in data
    assert data["total_active_pheromones"] > 0
    print(f"  [PASS] POST /api/discovery/stigmergy/query-pheromone-field -> {data['total_active_pheromones']} pheromones, role={data['recommended_swarm_role']}")

    # 4b. Compile Instrument
    resp = client.post("/api/discovery/stigmergy/compile-instrument", json={
        "representation_id": "REP-API-TEST-001",
        "hypothesis_statement": "Neuroinflammation requires both TREM2 upregulation and complement C3 activation",
        "key_variables": ["TREM2_LEVEL", "C3_ACTIVATION"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_compiled"] is True
    assert data["instrument_id"].startswith("INST-")
    assert data["simulated_world_id"].startswith("WORLD-SIM-")
    assert len(data["executable_rules"]) > 0
    print(f"  [PASS] POST /api/discovery/stigmergy/compile-instrument -> {data['instrument_id']} (world={data['simulated_world_id']})")

    # 4c. Audit Reality Firewall - BLOCK scenario
    resp = client.post("/api/discovery/stigmergy/audit-reality-firewall", json={
        "hypothesis_id": "HYPO-API-BLOCK-001",
        "claimed_regularity": "Swarm emergent tau aggregation rate law",
        "rcs_level": 0,
        "empirical_anchors": []
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_firewall_passed"] is False
    assert data["epistemic_directive"] == "REJECT_PROMOTION_AND_DEMAND_PHYSICAL_BENCHMARK"
    print(f"  [PASS] POST /api/discovery/stigmergy/audit-reality-firewall -> BLOCKED (RCS=0, no anchors)")

    # 4d. Audit Reality Firewall - PASS scenario
    resp = client.post("/api/discovery/stigmergy/audit-reality-firewall", json={
        "hypothesis_id": "HYPO-API-PASS-002",
        "claimed_regularity": "Validated abeta clearance pathway",
        "rcs_level": 2,
        "empirical_anchors": ["ADNI_HOLDOUT_SET_42"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_firewall_passed"] is True
    assert data["epistemic_directive"] == "PROMOTE_TO_INVARIANT_CONSTRAINT"
    print(f"  [PASS] POST /api/discovery/stigmergy/audit-reality-firewall -> PROMOTED (RCS=2, anchored)")


def main():
    print("=" * 80)
    print("ADR-DISCOVERY-027: Epistemic Stigmergy & Meta-Recursive Instrument Engine")
    print("Verification Suite")
    print("=" * 80)

    passed = 0
    failed = 0

    for test_fn in [
        test_pheromone_field_scanning,
        test_meta_recursive_instrument_compiler,
        test_reality_contact_firewall,
        test_rest_api_endpoints,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n  [FAIL] {test_fn.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} test groups")
    print("=" * 80)

    if failed > 0:
        sys.exit(1)
    else:
        print("[ALL GATES PASSED] ADR-DISCOVERY-027 verification complete.")


if __name__ == "__main__":
    main()
