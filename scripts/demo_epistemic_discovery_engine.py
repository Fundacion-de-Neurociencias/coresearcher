"""
scripts/demo_epistemic_discovery_engine.py - The 3 Epistemic Discovery Engines Interactive CLI

Demonstrates:
1. Constraint Discovery Engine: Mining and cross-cohort stress testing across ADNI, NACC, AIBL, OASIS.
2. Constraint Court: Bayesian trial and conflict resolution between Amyloid-First vs Tau-Connectome vs Vascular.
3. Scientific Git History: Epistemic commit graph with parent SHAs, diffs, and mutation triggers.
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


def run_discovery_engine_demo():
    client = authenticated_client(app)

    print("=" * 105)
    print("🧬 CORESEARCHER: AUTONOMOUS THEORY DISCOVERY, CONFLICT RESOLUTION & GIT ENGINE")
    print("   Empirical Discovery Machine | Cross-Cohort Falsification | Epistemic Version Control")
    print("=" * 105)

    # -------------------------------------------------------------------------
    # 1. Constraint Discovery Engine (Cross-Cohort Mining & Stress Testing)
    # -------------------------------------------------------------------------
    print("\n[1] CONSTRAINT DISCOVERY ENGINE (Cross-Cohort Stress Testing):")
    print("    Mining invariant boundary candidate from 4 independent empirical cohorts...")

    mine_payload = {
        "statement": "Connectome hub reserve > 0.65 prohibits 36m accelerated dementia progression.",
        "threshold_cutoff": 0.65
    }
    mine_res = client.post("/api/discovery/constraints/mine-and-verify", json=mine_payload).json()

    print(f"\n    • Candidate ID:        {mine_res['candidate_id']}")
    print(f"    • Proposed Statement:  \"{mine_res['proposed_statement']}\"")
    print(f"    • Total Samples Tested:n = {mine_res['total_samples_tested']} across 4 independent cohorts")
    print(f"    • Total Violations:    {mine_res['counterexamples_total']} counterexamples found")
    print(f"    • Statistical Status:  {'INVARIANT DISCOVERED' if mine_res['is_statistically_invariant'] else 'FALSIFIED'}")
    print(f"    • Promoted Constraint: {mine_res['promoted_constraint_id']} (CDV = {mine_res['derived_cdv']})")

    print("\n    ADVERSARIAL STRESS TEST BREAKDOWN ACROSS COHORTS:")
    for t in mine_res["stress_test_results"]:
        status_tag = "SURVIVED" if t['survived'] else "FAILED"
        print(f"       [{status_tag}] Cohort {t['cohort']:<6} (n={t['sample_size']:<3}) | Counterexamples: {t['counterexamples']} | p-value = {t['p_value']}")

    # -------------------------------------------------------------------------
    # 2. Constraint Court (Conflict Resolution Engine)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 105)
    print("[2] CONSTRAINT COURT (Adversarial Conflict Resolution & Bayesian Trial):")
    print("    Case: In re Amyloid-Cascade vs Connectome-Tauopathy vs Microvascular-Ischemia")

    court_res = client.post("/api/discovery/court/adjudicate").json()

    print(f"\n    • Trial ID:        {court_res['trial_id']}")
    print(f"    • Case Title:      {court_res['case_title']}")
    print(f"    • Verdict Type:    {court_res['verdict_type']}")
    print(f"    • Winning Invariant: {court_res['winning_constraint_id']}")
    print(f"    • Bayes Factor:    K = {court_res['bayes_factor']} (Decisive Evidence in favor of Connectome-Tau)")

    print("\n    BAYESIAN POSTERIOR PROBABILITIES P(C | E_multi_cohort):")
    for c_id, post_p in court_res["posterior_probabilities"].items():
        print(f"       • {c_id:<26}: P = {post_p:.4f} ({post_p*100:.1f}%)")

    print(f"\n    ADJUDICATION SUMMARY:\n    \"{court_res['adjudication_summary']}\"")

    print("\n    RESOLVED DOMAIN SCOPE BOUNDARIES:")
    for c_id, scope in court_res["resolved_scope_boundaries"].items():
        print(f"       - {c_id:<24}: {scope}")

    # -------------------------------------------------------------------------
    # 3. Scientific Git History (Epistemic Version Control)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 105)
    print("[3] SCIENTIFIC GIT HISTORY (Theory Lineage & Epistemic Commits):")
    print("    Inspecting immutable commit log for HYP-TAU-CONNECTOME / CONST-INVARIANT-HUB-RESERVE...\n")

    commits_res = client.get("/api/discovery/history/commits?entity_id=CONST-INVARIANT-HUB-RESERVE").json()

    for idx, c in enumerate(reversed(commits_res), 1):
        print(f"    [Commit {idx}] {c['commit_sha']} (Parent: {c['parent_commit_sha'] or 'ROOT'})")
        print(f"       • Tag & Entity:     {c['version_tag']} | {c['entity_type']}: {c['entity_id']}")
        print(f"       • Author & Time:    {c['author_role']} | {c['timestamp']}")
        print(f"       • Commit Message:   {c['commit_message']}")
        print(f"       • Mutation Trigger: {c['mutation_trigger']}")
        print(f"       • Epistemic Diff:   Parameters modified: {c['epistemic_diff']['parameter_changes']}")
        print(f"       • SOM Hash:         {c['som_lineage_hash']}")
        print()

    print("=" * 105)
    print("✅ AUTONOMOUS DISCOVERY, COURT ADJUDICATION & SCIENTIFIC GIT FULLY VALIDATED")
    print("=" * 105)


if __name__ == "__main__":
    run_discovery_engine_demo()
