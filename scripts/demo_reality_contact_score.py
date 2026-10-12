"""
scripts/demo_reality_contact_score.py - Reality Contact Score (RCS) Demonstration CLI

"Every hypothesis must earn reality."
Demonstrates how a hypothesis ascends the 5-step Reality Earning Ladder:
Level 0 (Literature) -> Level 1 (Retrospective) -> Level 2 (Prospective) -> Level 3 (Physical Lab) -> Level 4 (Ledgered Invariant).
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


def run_rcs_demo():
    client = authenticated_client(app)

    print("=" * 105)
    print("🌍 CORESEARCHER: THE REALITY CONTACT SCORE (RCS) ENGINE — 'EVERY HYPOTHESIS MUST EARN REALITY'")
    print("   Constitutional Invariant (Decision 0.1): Reality Earning Ladder (Levels 0 to 4)")
    print("=" * 105)

    stages = [
        {
            "step": "STAGE 0: Pure Literature In-Silico Formulation",
            "payload": {
                "hypothesis_id": "HYP-TAU-CONNECTOME",
                "literature_citations_count": 48
            }
        },
        {
            "step": "STAGE 1: External Retrospective Cohort Replication",
            "payload": {
                "hypothesis_id": "HYP-TAU-CONNECTOME",
                "literature_citations_count": 48,
                "retrospective_cohorts": ["ADNI", "NACC", "AIBL", "OASIS"]
            }
        },
        {
            "step": "STAGE 2: Prospective Blinded Holdout Confirmation",
            "payload": {
                "hypothesis_id": "HYP-TAU-CONNECTOME",
                "literature_citations_count": 48,
                "retrospective_cohorts": ["ADNI", "NACC", "AIBL", "OASIS"],
                "prospective_holdouts": ["UK_BIOBANK_2026_HOLDOUT", "GERMAN_DELCODE_PROSPECTIVE"]
            }
        },
        {
            "step": "STAGE 3: Physical Laboratory Experiment Steering",
            "payload": {
                "hypothesis_id": "HYP-TAU-CONNECTOME",
                "literature_citations_count": 48,
                "retrospective_cohorts": ["ADNI", "NACC", "AIBL", "OASIS"],
                "prospective_holdouts": ["UK_BIOBANK_2026_HOLDOUT", "GERMAN_DELCODE_PROSPECTIVE"],
                "physical_experiment_runs": [
                    {"run_id": "CHIP-884", "device": "SPARSE_IMAGING_MICROFLUIDIC_PDMS"},
                    {"run_id": "TITRATION-102", "device": "MASS_SPEC_ASSAY"}
                ]
            }
        },
        {
            "step": "STAGE 4: Ledgered Invariant Constraint Discovery (Maximum Reality Contact)",
            "payload": {
                "hypothesis_id": "HYP-TAU-CONNECTOME",
                "literature_citations_count": 48,
                "retrospective_cohorts": ["ADNI", "NACC", "AIBL", "OASIS"],
                "prospective_holdouts": ["UK_BIOBANK_2026_HOLDOUT", "GERMAN_DELCODE_PROSPECTIVE"],
                "physical_experiment_runs": [
                    {"run_id": "CHIP-884", "device": "SPARSE_IMAGING_MICROFLUIDIC_PDMS"},
                    {"run_id": "TITRATION-102", "device": "MASS_SPEC_ASSAY"}
                ],
                "promoted_invariant_constraint_id": "CONST-INVARIANT-HUB-RESERVE",
                "state_space_omega_pruned_fraction": 0.1667
            }
        }
    ]

    for s in stages:
        print(f"\n▶ {s['step']}:")
        res = client.post("/api/discovery/reality-contact/evaluate", json=s['payload']).json()

        print(f"   • Reality Contact Score: RCS = {res['reality_contact_score']} ({res['level_name']})")
        print(f"   • Promotable Status:     {'CERTIFIED PROMOTABLE AS INVARIANT' if res['is_promotable_as_invariant'] else 'NOT PROMOTABLE (Requires RCS >= 3)'}")
        print("   • Structured Reality Trail:")
        for t in res["reality_trail"]:
            print(f"      - {t}")
        print(f"   • Epistemic Justification:\n     \"{res['epistemic_justification']}\"")
        print("-" * 105)

    print("\n" + "=" * 105)
    print("🏛️ SUMMARY CONSTITUTIONAL PRINCIPLE:")
    print("   \"La diferencia entre un sistema que analiza ciencia y un sistema que hace ciencia")
    print("    es la cantidad de realidad que toca.\" — CoResearcher Constitution (Decision 0.1)")
    print("=" * 105)


if __name__ == "__main__":
    run_rcs_demo()
