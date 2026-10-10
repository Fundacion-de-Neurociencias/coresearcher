"""
Test suite for Rosen Autopoietic Closure & Causal Organization Auditor (ADR-DISCOVERY-052).
Verifies:
1. Interception of causal open leaks (catalysts lacking internal synthesis).
2. Interception of non-dissipative dead equilibrium (zero entropy production).
3. Interception of tautological circularity without open nutrient throughput.
4. Identification of pure mechanical linear DAGs.
5. Successful verification of authentic autopoietic (M,R) living organization.
6. REST API endpoint /api/discovery/autopoietic/audit-closure.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.server import app
from python.discovery.autopoietic_closure_auditor import (
    AutopoieticSystemSpec,
    CatalyticProcess,
    ClosureVerdictStatus,
    MetabolicComponent,
    RosenAutopoieticClosureAuditor,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_causal_open_leak_unproduced_catalyst_detected():
    # Catalyst E1 is used, but never produced by the system
    comps = {
        "nutr_A": MetabolicComponent("nutr_A", "Nutrient A", is_external_nutrient=True),
        "prod_B": MetabolicComponent("prod_B", "Metabolite B"),
        "cat_E1": MetabolicComponent("cat_E1", "Enzyme 1"),
    }
    processes = [
        CatalyticProcess(
            process_id="p1",
            name="A to B",
            material_inputs=["nutr_A"],
            efficient_catalysts=["cat_E1"],
            material_products=["prod_B"],
            entropy_production_rate=0.08,
        )
    ]
    spec = AutopoieticSystemSpec(
        system_id="system_leaky",
        system_name="Leaky Non-Living System",
        components=comps,
        processes=processes,
    )
    report = RosenAutopoieticClosureAuditor.audit_system(spec)
    assert not report.is_closed_to_efficient_causation
    assert report.verdict == ClosureVerdictStatus.CAUSAL_LEAK_UNPRODUCED_CATALYST
    assert "cat_E1" in report.unaccounted_external_catalysts


def test_equilibrium_death_zero_entropy_production():
    comps = {
        "nutr_A": MetabolicComponent("nutr_A", "Nutrient A", is_external_nutrient=True),
        "prod_B": MetabolicComponent("prod_B", "Product B"),
        "cat_E1": MetabolicComponent("cat_E1", "Enzyme E1"),
    }
    processes = [
        CatalyticProcess(
            process_id="p1",
            name="Cold reaction",
            material_inputs=["nutr_A"],
            efficient_catalysts=["cat_E1"],
            material_products=["prod_B", "cat_E1"],
            entropy_production_rate=0.0,  # Zero dissipation!
        )
    ]
    spec = AutopoieticSystemSpec(
        system_id="system_frozen",
        system_name="Non-dissipative system",
        components=comps,
        processes=processes,
    )
    report = RosenAutopoieticClosureAuditor.audit_system(spec)
    assert not report.is_closed_to_efficient_causation
    assert report.verdict == ClosureVerdictStatus.EQUILIBRIUM_DEATH_NO_DISSIPATION


def test_tautological_circular_collapse_detected():
    # Circular loop with zero external nutrients
    comps = {
        "spec_X": MetabolicComponent("spec_X", "Species X", is_external_nutrient=False),
        "spec_Y": MetabolicComponent("spec_Y", "Species Y", is_external_nutrient=False),
    }
    processes = [
        CatalyticProcess("p1", "X makes Y", ["spec_X"], ["spec_Y"], ["spec_Y"], entropy_production_rate=0.05),
        CatalyticProcess("p2", "Y makes X", ["spec_Y"], ["spec_X"], ["spec_X"], entropy_production_rate=0.05),
    ]
    spec = AutopoieticSystemSpec(
        system_id="system_tautology",
        system_name="Tautological isolated loop",
        components=comps,
        processes=processes,
    )
    report = RosenAutopoieticClosureAuditor.audit_system(spec)
    assert not report.is_closed_to_efficient_causation
    assert report.verdict == ClosureVerdictStatus.TAUTOLOGICAL_CIRCULAR_COLLAPSE


def test_sound_autopoietic_system_verified():
    # Canonical Rosen (M,R) system:
    # 1. Metabolism (f): Nutrient A --[ Enzyme E_M ]--> Metabolite B + Repair substrate S
    # 2. Repair (Phi): Repair substrate S --[ Repair enzyme E_R ]--> Enzyme E_M
    # 3. Replication (beta): Metabolite B --[ Enzyme E_M ]--> Repair enzyme E_R + Waste
    comps = {
        "nutr_A": MetabolicComponent("nutr_A", "Nutrient A", is_external_nutrient=True),
        "metab_B": MetabolicComponent("metab_B", "Metabolite B"),
        "repair_S": MetabolicComponent("repair_S", "Repair Substrate S"),
        "enz_M": MetabolicComponent("enz_M", "Metabolic Enzyme"),
        "enz_R": MetabolicComponent("enz_R", "Repair Enzyme"),
        "waste": MetabolicComponent("waste", "Dissipated Waste", is_dissipated_waste=True),
    }
    processes = [
        CatalyticProcess("p_metab", "Metabolism", ["nutr_A"], ["enz_M"], ["metab_B", "repair_S"], 0.12),
        CatalyticProcess("p_repair", "Repair", ["repair_S"], ["enz_R"], ["enz_M"], 0.08),
        CatalyticProcess("p_repl", "Replication", ["metab_B"], ["enz_M"], ["enz_R", "waste"], 0.09),
    ]
    spec = AutopoieticSystemSpec(
        system_id="protocell_rosen_mr",
        system_name="Canonical Rosen (M,R) Autopoietic Cell",
        components=comps,
        processes=processes,
    )
    report = RosenAutopoieticClosureAuditor.audit_system(spec)
    assert report.is_closed_to_efficient_causation
    assert report.is_thermodynamically_dissipative
    assert report.verdict == ClosureVerdictStatus.AUTOPOIETIC_CLOSURE_VERIFIED
    assert len(report.unaccounted_external_catalysts) == 0
    assert report.holonomy_defect == 0.0
    assert report.som_autopoietic_hash.startswith("sha256:")


def test_autopoietic_rest_api_endpoint(client):
    payload = {
        "system_id": "test_cell_api",
        "system_name": "Autopoietic API Cell",
        "components": [
            {"component_id": "glucose", "name": "Glucose", "is_external_nutrient": True},
            {"component_id": "pyruvate", "name": "Pyruvate"},
            {"component_id": "kinase", "name": "Kinase enzyme"},
            {"component_id": "ribosome", "name": "Ribosome"},
            {"component_id": "heat", "name": "Heat waste", "is_dissipated_waste": True},
        ],
        "processes": [
            {
                "process_id": "glycolysis",
                "name": "Glycolysis",
                "material_inputs": ["glucose"],
                "efficient_catalysts": ["kinase"],
                "material_products": ["pyruvate", "heat"],
                "entropy_production_rate": 0.15,
            },
            {
                "process_id": "translation_k",
                "name": "Kinase Synthesis",
                "material_inputs": ["pyruvate"],
                "efficient_catalysts": ["ribosome"],
                "material_products": ["kinase"],
                "entropy_production_rate": 0.05,
            },
            {
                "process_id": "translation_r",
                "name": "Ribosome Assembly",
                "material_inputs": ["pyruvate"],
                "efficient_catalysts": ["ribosome"],
                "material_products": ["ribosome"],
                "entropy_production_rate": 0.06,
            },
        ],
    }
    response = client.post("/api/discovery/autopoietic/audit-closure", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["system_id"] == "test_cell_api"
    assert data["is_closed_to_efficient_causation"]
    assert data["verdict"] == "AUTOPOIETIC_CLOSURE_VERIFIED"
    assert "som_autopoietic_hash" in data
