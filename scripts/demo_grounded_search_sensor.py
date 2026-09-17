"""
scripts/demo_grounded_search_sensor.py - Grounded Search Sensor & Cryptographic Source Lineage CLI

Demonstrates:
1. Unopinionated raw structured search retrieval (DOIs, PMIDs, cohorts, sample sizes, negative results).
2. Cryptographic SHA-256 source hashing (som_source_hash).
3. Direct bridging into Constraint Miner & Constraint Discovery Engine.
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


def run_grounded_search_demo():
    client = TestClient(app)

    print("=" * 105)
    print("📡 CORESEARCHER: GROUNDED SEARCH SENSOR & CRYPTOGRAPHIC SOURCE LINEAGE LAYER")
    print("   Unopinionated Empirical Sensor | Zero LLM Pre-Summarization | SHA-256 Pinned Lineage")
    print("=" * 105)

    topic = "pTau217 Connectome Hub Vulnerability"
    print(f"\n[1] QUERYING GROUNDED SEARCH SENSOR (Target: '{topic}'):")
    print("    Fetching raw, unopinionated structured empirical records...\n")

    payload = {
        "query_topic": topic,
        "target_disease": "ALZHEIMER_DISEASE"
    }

    res = client.post("/api/discovery/search/grounded-ingest", json=payload).json()
    sources = res["sources"]
    bridge = res["bridge_result"]

    for idx, s in enumerate(sources, 1):
        print(f"    [{idx}] DOI: {s['doi']:<28} | PMID: {s['pmid']:<8} | Cohort: {s['cohort_name']}")
        print(f"        Title: \"{s['title']}\"")
        print(f"        Empirical Stats:  Sample Size n = {s['sample_size']} | Annualized Slope β = {s['effect_size_beta']} (p = {s['p_value']})")
        print(f"        Verbatim Negative Result: \"{s['verbatim_negative_results'][0]}\"")
        if s['counterexamples_detected']:
            print(f"        Counterexample Found: \"{s['counterexamples_detected'][0]}\"")
        print(f"        Cryptographic Hash: {s['som_source_hash']}")
        print()

    print("-" * 105)
    print("[2] BRIDGING RAW SOURCES DIRECTLY INTO CONSTRAINT MINER & DISCOVERY ENGINE:")
    print(f"    • Total Ingested Sources:      {bridge['ingested_sources_count']} peer-reviewed articles / cohorts")
    print(f"    • Cumulative Empirical Sample: n = {bridge['total_empirical_sample_size']} subjects")
    print(f"    • Cryptographic Source Hashes: {len(bridge['cryptographic_source_hashes'])} SHA-256 hashes registered")
    
    cand = bridge["discovered_invariant_candidate"]
    print(f"\n    🏆 EXTRACTED INVARIANT CONSTRAINT: [{cand['promoted_constraint_id']}]")
    print(f"       Statement:  \"{cand['proposed_statement']}\"")
    print(f"       CDV Pruned: {cand['derived_cdv']*100:.1f}% of state space Ω (Mathematical CDV = {cand['derived_cdv']})")
    print(f"       Verdict:    \"{bridge['bridge_verdict']}\"")

    print("\n" + "=" * 105)
    print("🏛️ CORE PRINCIPLE VALIDATED:")
    print("   \"Search is responsible for finding raw structured facts.")
    print("    CoResearcher is responsible for reasoning, falsification, and constraint discovery.\"")
    print("=" * 105)


if __name__ == "__main__":
    run_grounded_search_demo()
