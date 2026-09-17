"""
python/discovery/biological_programs_catalog.py - Operational Biological Programs Library
Implements the primary mechanistic causal units connecting molecular findings to phenotypic trajectories.
"""

from typing import List, Dict, Any
from python.discovery.epistemic_trajectory import BiologicalProgram, ExplanationLevel


def get_canonical_biological_programs() -> List[BiologicalProgram]:
    """Returns the foundational operational biological programs across neurodegeneration."""
    return [
        # 1. Trans-Synaptic Spreading
        BiologicalProgram(
            program_id="BP-TRANS-SYNAPTIC-SPREADING",
            name="Activity-Dependent Trans-Synaptic Proteopathy Spreading",
            explanation_level=ExplanationLevel.ALGORITHMIC,
            computational_objective="Non-autonomous propagation of pathologically misfolded proteins along functional circuits",
            key_entities=["pTau217 / pTau181", "Synaptic vesicles", "Functional hubs (Default Mode Network)"],
            causal_chain=[
                {"step": 1, "description": "Neuronal hyperexcitability drives local tau hyperphosphorylation and synaptic release."},
                {"step": 2, "description": "Oligomeric tau enters synaptic cleft and binds LRP1/heparan sulfate proteoglycans on post-synaptic terminals."},
                {"step": 3, "description": "Retrograde propagation through high-degree functional hub nodes, causing connectivity decay."}
            ],
            target_diseases=["ALZHEIMER_DISEASE", "FRONTOTEMPORAL_DEMENTIA", "PARKINSON_DISEASE"],
            transferability_score=0.92,
            marr_links={"computational_parent": "BP-HOMEOSTATIC-FAILURE", "implementational_child": "BP-PHOSPHO-TAU-KINETICS"}
        ),
        # 2. Proteostatic Autophagy Collapse
        BiologicalProgram(
            program_id="BP-PROTEOSTASIS-AUTOPHAGY",
            name="Endolysosomal & Autophagic Proteostasis Failure",
            explanation_level=ExplanationLevel.IMPLEMENTATIONAL,
            computational_objective="Clearance of misfolded aggregate species under cellular metabolic stress",
            key_entities=["Lysosomal Cathepsins", "LAMP2A", "Ubiquitin-Proteasome", "Autophagosomes"],
            causal_chain=[
                {"step": 1, "description": "Age- and genetic-dependent decline in lysosomal acidification."},
                {"step": 2, "description": "Accumulation of insoluble oligomers exceeding chaperone buffering capacity."},
                {"step": 3, "description": "Failure of macroautophagy leading to proteostatic catastrophe and cell death."}
            ],
            target_diseases=["ALZHEIMER_DISEASE", "PARKINSON_DISEASE", "AMYOTROPHIC_LATERAL_SCLEROSIS", "HUNTINGTON_DISEASE"],
            transferability_score=0.95,
            marr_links={"computational_parent": "BP-CELLULAR-HOMEOSTASIS"}
        ),
        # 3. Microglial Neuroimmune Activation
        BiologicalProgram(
            program_id="BP-MICROGLIAL-NEUROIMMUNE",
            name="TREM2-Mediated Microglial Phenotypic Switching & Neuroinflammation",
            explanation_level=ExplanationLevel.IMPLEMENTATIONAL,
            computational_objective="Damage-associated molecular pattern (DAMP) containment and barrier formation",
            key_entities=["TREM2", "TYROBP", "GFAP", "Pro-inflammatory cytokines (IL-1β, TNF-α)"],
            causal_chain=[
                {"step": 1, "description": "Plaque-associated lipid recognition activates DAM (Disease-Associated Microglia) state."},
                {"step": 2, "description": "Sustained microglial priming induces secondary astrocytic reactivity (A1 toxic phenotype)."},
                {"step": 3, "description": "Synaptic stripping and neuroaxonal breakdown accelerate cognitive decline."}
            ],
            target_diseases=["ALZHEIMER_DISEASE", "FRONTOTEMPORAL_DEMENTIA", "MULTIPLE_SCLEROSIS"],
            transferability_score=0.89,
            marr_links={"computational_parent": "BP-NEUROIMMUNE-SURVEILLANCE"}
        ),
        # 4. Lipid-ApoE4 Trafficking
        BiologicalProgram(
            program_id="BP-LIPID-APOE4-TRAFFICKING",
            name="ApoE4-Mediated Lipid Dyshomeostasis & Blood-Brain Barrier Breakdown",
            explanation_level=ExplanationLevel.IMPLEMENTATIONAL,
            computational_objective="Cholesterol and phospholipid transport to synapses for membrane maintenance",
            key_entities=["ApoE4 isoform", "Pericytes", "ABCA1", "Endothelial tight junctions"],
            causal_chain=[
                {"step": 1, "description": "ApoE4 impairs lipid efflux and promotes endosomal cholesterol sequestration."},
                {"step": 2, "description": "CypA-NFκB-MMP9 pathway activation in pericytes degrades endothelial basal lamina."},
                {"step": 3, "description": "Microvascular hypoperfusion synergizes with amyloid to accelerate tau spreading."}
            ],
            target_diseases=["ALZHEIMER_DISEASE", "VASCULAR_DEMENTIA", "LEWY_BODY_DEMENTIA"],
            transferability_score=0.86,
            marr_links={"computational_parent": "BP-VASCULAR-SUPPLY"}
        )
    ]
