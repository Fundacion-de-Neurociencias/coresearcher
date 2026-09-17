"""
scripts/demo_discovery_campaign.py - Constraint-Led Multi-Agent Discovery Campaign CLI (ADR-DISCOVERY-007)
Demonstrates the 9 canonical epistemic agents executing an autonomous discovery campaign
with persistent immutable memory ledger and state-space Ω reduction.
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


def run_campaign_demo():
    client = TestClient(app)

    print("=" * 90)
    print("🤖 CORESEARCHER: CONSTRAINT-LED MULTI-AGENT DISCOVERY CAMPAIGN (ADR-DISCOVERY-007)")
    print("=" * 90)

    # 1. Start Campaign
    question = "Does plasma pTau217 elevation drive longitudinal cognitive decline via connectome-mediated hub propagation, or via independent vascular/cell-intrinsic collapse?"
    print(f"\n[INITIATING CAMPAIGN] Target Question:")
    print(f"\"{question}\"")
    print(f"Executing 9 canonical epistemic agents across 10 discovery iterations...\n")

    res = client.post("/api/discovery/campaign/run", json={"question": question, "iterations": 10})
    campaign = res.json()

    print("-" * 90)
    print(f"📊 CAMPAIGN SUMMARY ({campaign['campaign_id']}):")
    print(f"   • Target Domain:              {campaign['target_domain']}")
    print(f"   • Total State Space |Ω|:      {campaign['total_state_space_volume']} combinatorial states")
    print(f"   • Iterations Completed:       {campaign['iterations_completed']}")
    print(f"   • Convergence Achieved:       {campaign['converged']}")
    print(f"   • Constraints Mined:          {campaign['constraints_mined_count']}")
    print(f"   • Biological Programs Mapped: {campaign['biological_programs_mapped_count']}")
    print(f"   • Hypotheses Generated:       {campaign['hypotheses_generated_count']}")
    print(f"   • Rival Alternatives Audited: {campaign['rival_alternatives_count']} (Mandatory >= 4)")
    print(f"   • Falsifications Executed:    {campaign['falsifications_executed_count']}")
    print(f"   • Discovery Value Achieved:   DV = {campaign['discovery_value']}")

    print("\n" + "-" * 90)
    print("📜 IMMUTABLE CAMPAIGN LEDGER ENTRIES (Zero Epistemic Amnesia):")
    print(f"   Total Entries Recorded: {campaign['ledger_entries_count']}\n")

    for idx, entry in enumerate(campaign['ledger_summary'], 1):
        tag = f"[{entry['type']}]"
        print(f"   {idx:02d}. {tag:<25} Agent: {entry['agent_role']:<28} | {entry['summary']}")

    print("\n" + "=" * 90)
    print("🏛️ CORE CONSTITUTIONAL PRINCIPLE:")
    print("   \"CoResearcher is NOT an answer system.")
    print("    CoResearcher is NOT a literature search engine.")
    print("    CoResearcher is NOT a hypothesis generator.")
    print("    CoResearcher IS a system for the progressive reduction of the possible scientific")
    print("    state space (Ω) via audit-grade constraints, predictions, and falsifications.\"")
    print("=" * 90)


if __name__ == "__main__":
    run_campaign_demo()
