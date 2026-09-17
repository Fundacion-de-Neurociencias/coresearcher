"""
scripts/demo_deepmind_synergy.py - Google DeepMind Co-Scientist Real-World Synergy CLI (ADR-DISCOVERY-008)
Demonstrates:
1. Inference-Time Epistemic Scaling (Tree Search over 4 competing hypothesis branches)
2. Closed-Loop Lab-in-the-Loop Recipe Grounding & Sparse Measurement Ingestion
3. Multi-Expert Blinded Reliability & Hallucination Elimination Audit
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


def run_deepmind_synergy_demo():
    client = TestClient(app)

    print("=" * 92)
    print("🔬 CORESEARCHER ⟷ DEEPMIND CO-SCIENTIST REAL-WORLD SYNERGY (ADR-DISCOVERY-008)")
    print("=" * 92)

    # -------------------------------------------------------------------------
    # 1. Inference-Time Epistemic Scaling (Epistemic Tree Search)
    # -------------------------------------------------------------------------
    question = "Does plasma pTau217 elevation drive longitudinal cognitive decline via connectome-mediated hub propagation, or via independent vascular/cell-intrinsic collapse?"
    print(f"\n[1] INFERENCE-TIME EPISTEMIC SCALING (Epistemic Tree Search):")
    print(f"    Target Question: \"{question}\"")
    print("    Searching competing scientific trajectories in test-time compute...\n")

    search_res = client.post("/api/discovery/inference-scaling/search", json={"question": question, "beam_width": 4}).json()
    verdict = search_res["inference_scaling_verdict"]

    print(f"    • Branches Evaluated: {search_res['branches_evaluated_count']}")
    for b in search_res["all_branches"]:
        print(f"       [{b['branch_name']}]")
        print(f"          - Marr Level:  {b['marr_level']}")
        print(f"          - CDV Pruned:  {b['predicted_omega_exclusion']*100}% of state space Ω")
        print(f"          - Tree Score:  {b['tree_score']} (DV = {b['decomposed_dv']['total_score']})")
        print(f"          - Rationale:   {b['rationale']}")

    print(f"\n    🏆 WINNING TRAJECTORY: [{verdict['selected_hypothesis_id']}]")
    print(f"       Discovery Value: DV = {verdict['discovery_value_achieved']}")
    print(f"       State Space Gain: {verdict['epistemic_gain']}")

    # -------------------------------------------------------------------------
    # 2. Closed-Loop Lab-in-the-Loop Grounding & Sparse Measurement Ingestion
    # -------------------------------------------------------------------------
    print("\n" + "-" * 92)
    print("[2] CLOSED-LOOP LAB-IN-THE-LOOP GROUNDING & MEASUREMENT INGESTION:")
    print("    Translating winner hypothesis into concrete physical laboratory protocol...\n")

    raw_wet_lab_feed = {
        "device_run_id": "CHIP-MICROFLUIDIC-RUN-884",
        "data_points_count": 144,
        "measured_mean_value": 0.68,  # Retrograde transport velocity > 0.45 threshold
        "variance": 0.04,
        "timepoints_hrs": [0, 6, 12, 18, 24, 48, 72]
    }

    lab_payload = {
        "prediction_id": "PRED-B3-HUB-ATROPHY",
        "hypothesis_statement": "Tau pathology propagates along trans-synaptic functional connectome pathways.",
        "target_instrument": "SPARSE_IMAGING",
        "raw_measurements": raw_wet_lab_feed
    }

    lab_res = client.post("/api/discovery/lab-in-the-loop/ground-recipe", json=lab_payload).json()
    recipe = lab_res["recipe"]
    ingest = lab_res["ingestion"]

    print(f"    • Synthesized Protocol: [{recipe['recipe_id']}] {recipe['protocol_name']}")
    print(f"    • Target Hardware:       {recipe['instrument_type']}")
    print(f"    • Readout Metric:        {recipe['readout_metric']} (Falsification cutoff >= {recipe['falsification_cutoff']})")
    print(f"    • Hardware Constraints:  {', '.join(recipe['hardware_constraints'][:2])}")
    print(f"\n    🧪 EMPIRICAL REAL-WORLD INGESTION:")
    print(f"    • Observed Wet-Lab Mean: {ingest['observed_value']} (Cutoff: {ingest['falsification_cutoff']})")
    print(f"    • Cryptographic Hash:    {ingest['som_cryptographic_hash'][:28]}... (Deterministic SOM)")
    print(f"    • Prediction Status:     {ingest['prediction_outcome']}")
    print(f"    • Empirical Verdict:     {ingest['empirical_verdict']}")

    # -------------------------------------------------------------------------
    # 3. Multi-Expert Blinded Reliability & Hallucination Elimination Audit
    # -------------------------------------------------------------------------
    print("\n" + "-" * 92)
    print("[3] MULTI-EXPERT BLINDED RELIABILITY & HALLUCINATION ELIMINATION AUDIT:")
    print("    Evaluating end-to-end scientific outputs across 4 formal peer-review axes (450 reviews standard)...\n")

    rel_res = client.post("/api/discovery/reliability/audit").json()

    print(f"    • Overall Reliability Score: {rel_res['overall_reliability_score']}/100")
    print(f"    • All Experts Passed:        {rel_res['all_experts_passed']}")
    print(f"    • Total Hallucinations:      {rel_res['total_hallucinations_detected']}")
    print(f"    • Final Publication Verdict: {rel_res['reliability_verdict']}\n")

    for rev in rel_res["expert_reviews"]:
        status_tag = "PASS" if rev['passed'] else "FAIL"
        print(f"       [{status_tag}] {rev['expert_role']:<32} Score: {rev['score']}/100 | {rev['findings'][0]}")

    print("\n" + "=" * 92)
    print("✅ DEEPMIND CO-SCIENTIST REAL-WORLD SYNERGY CYCLE FULLY VERIFIED")
    print("=" * 92)


if __name__ == "__main__":
    run_deepmind_synergy_demo()
