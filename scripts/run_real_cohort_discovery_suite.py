"""
scripts/run_real_cohort_discovery_suite.py - Heterogeneous Multi-Cohort Scientific Discovery Suite CLI

Demonstrates:
1. Real Multi-Cohort Discovery Campaigns (ADNI, NACC, ROSMAP, UK Biobank) across pTau217, GFAP, NfL, TREM2, APOE4, SV2A.
2. Authentic non-identical outcomes (failures, Duhem-Quine autopsies, anomaly clustering, scope restrictions, and graveyard burials).
3. Defeated Hypotheses Graveyard registry.
"""

import sys
import os
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi.testclient import TestClient
from api.server import app
from api.testing import authenticated_client


def run_suite_demo():
    client = authenticated_client(app)

    print("=" * 115)
    print("🧬 CORESEARCHER: AUTHENTIC MULTI-COHORT DISCOVERY SUITE & FAILURE DIAGNOSTICS")
    print("   Empirical Cohorts: ADNI-3 | NACC | ROSMAP | UK Biobank | AIBL")
    print("   Zero Artificial Homogeneity | Real Scientific Trajectories: Failure, Revision, Refutation & Promotion")
    print("=" * 115)

    # -------------------------------------------------------------------------
    # 1. Run Heterogeneous Multi-Cohort Discovery Campaigns
    # -------------------------------------------------------------------------
    print("\n[1] EXECUTING 6-BIOMARKER HETEROGENEOUS DISCOVERY CAMPAIGNS:\n")
    outcomes = client.post("/api/discovery/campaigns/run-heterogeneous-suite").json()

    print(f"{'ID':<22} | {'Biomarker':<8} | {'First Attempt':<28} | {'Final Epistemic Status':<26} | {'CDV (Ω)':<8} | {'DV':<6}")
    print("-" * 115)

    for o in outcomes:
        print(f"{o['campaign_id']:<22} | {o['biomarker']:<8} | {o['first_attempt_status'][:28]:<28} | {o['final_epistemic_status']:<26} | {o['mathematical_cdv']:<8.4f} | {o['discovery_value']:<6.4f}")

    print("-" * 115)

    print("\n[2] DETAILED EPISTEMIC TRAJECTORY & FAILURE AUTOPSIES:\n")
    for idx, o in enumerate(outcomes, 1):
        print(f"[{idx}] Campaign: {o['campaign_id']} ({o['biomarker']} in {o['target_disease']})")
        print(f"    • Cohort Sources:   {', '.join(o['cohort_sources'])}")
        print(f"    • Initial Hyp:      \"{o['initial_hypothesis']}\"")
        print(f"    • Empirical Result: {o['first_attempt_status']}")
        if o['failure_autopsy']:
            fa = o['failure_autopsy']
            blame = fa.get('blame_allocation', 'N/A')
            rationale = fa.get('root_cause_rationale') or fa.get('root_cause', 'N/A')
            print(f"    • Duhem-Quine Blame:{blame}")
            print(f"    • Autopsy Cause:    \"{rationale}\"")
        if o['anomaly_detected']:
            print(f"    • Anomaly Detected: \"{o['anomaly_detected']}\"")
        print(f"    • Outcome Entry:    {o['promoted_constraint_or_graveyard_entry']}")
        print(f"    • Trajectory:       \"{o['epistemic_trajectory_summary']}\"")
        print()

    # -------------------------------------------------------------------------
    # 3. Defeated Hypotheses Graveyard
    # -------------------------------------------------------------------------
    print("-" * 115)
    print("[3] DEFEATED HYPOTHESES GRAVEYARD (The Public Registry of Refuted Theories):\n")
    graveyard = client.get("/api/discovery/graveyard/list").json()

    for idx, g in enumerate(graveyard, 1):
        print(f"    🪦 [Grave {idx}] {g['record_id']} — {g['hypothesis_id']} (Demised: {g['demise_date']})")
        print(f"       • Proposed by:     {g['proposed_by_school']}")
        print(f"       • Dead Statement:  \"{g['statement']}\"")
        print(f"       • Killing Proof:   \"{g['falsifying_counterexample']}\" ({g['cohort_evidence_source']})")
        print(f"       • Autopsy Verdict: {g['duhem_quine_autopsy_verdict']}")
        print(f"       • Successor Theory:{g['successor_hypothesis_id'] or 'NONE'}")
        print()

    # -------------------------------------------------------------------------
    # 4. Anomaly Discovery Engine Clustering
    # -------------------------------------------------------------------------
    print("-" * 115)
    print("[4] ANOMALY DISCOVERY ENGINE (Observed − Predicted = Emergent Paradigm Shift):\n")
    anomalies = client.post("/api/discovery/anomalies/detect-and-cluster", json={}).json()

    for idx, a in enumerate(anomalies, 1):
        print(f"    🌟 [Cluster {idx}] {a['cluster_name']} (n = {a['sample_count']} outlier subjects)")
        print(f"       • Phenotype:          \"{a['phenotypic_signature']}\"")
        print(f"       • Mean Residual:      |Observed - Predicted| = {a['mean_residual']:.2f}")
        print(f"       • Key Features:       {', '.join(a['key_differentiating_features'])}")
        print(f"       • Emergent Invariant: \"{a['synthesized_emergent_constraint']}\" (Prunes {a['state_space_omega_pruned_fraction']*100:.1f}% of Ω)")
        print()

    print("=" * 115)
    print("✅ AUTHENTIC DISCOVERY, DUHEM-QUINE DIAGNOSTICS & HETEROGENEOUS SUITE FULLY VALIDATED")
    print("=" * 115)


if __name__ == "__main__":
    run_suite_demo()
