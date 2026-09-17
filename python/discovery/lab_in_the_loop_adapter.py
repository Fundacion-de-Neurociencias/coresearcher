"""
python/discovery/lab_in_the_loop_adapter.py - Closed-Loop Lab-in-the-Loop Grounding Adapter (ADR-DISCOVERY-008)
Connects CoResearcher epistemic discovery to physical laboratory instruments,
sparse imaging arrays, automated reactors, and wet-lab assay protocols.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import hashlib
import json
import uuid


@dataclass
class LabProtocolRecipe:
    recipe_id: str
    target_prediction_id: str
    instrument_type: str  # "SPARSE_IMAGING" | "SEMI_AUTO_REACTOR" | "MASS_SPEC_ASSAY" | "FLOW_CYTOMETRY"
    protocol_name: str
    hardware_constraints: List[str]
    parameters: Dict[str, Any]
    readout_metric: str
    falsification_cutoff: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "target_prediction_id": self.target_prediction_id,
            "instrument_type": self.instrument_type,
            "protocol_name": self.protocol_name,
            "hardware_constraints": self.hardware_constraints,
            "parameters": self.parameters,
            "readout_metric": self.readout_metric,
            "falsification_cutoff": self.falsification_cutoff
        }


class LabInTheLoopAdapter:
    """
    Translates epistemic predictions into actionable laboratory recipes
    and ingests real-world measurement feeds with cryptographic SOM lineage.
    """

    @staticmethod
    def generate_grounded_recipe(
        prediction_id: str,
        hypothesis_statement: str,
        target_instrument: str = "SPARSE_IMAGING"
    ) -> LabProtocolRecipe:
        """
        Synthesizes a precise physical laboratory protocol tailored to experimental constraints.
        """
        if target_instrument == "SPARSE_IMAGING":
            return LabProtocolRecipe(
                recipe_id=f"RECIPE-{uuid.uuid4().hex[:8].upper()}",
                target_prediction_id=prediction_id,
                instrument_type="SPARSE_IMAGING",
                protocol_name="High-Content Trans-Synaptic Tau Microfluidic Spreading Assay",
                hardware_constraints=[
                    "Microfluidic triple-chamber device (PDMS)",
                    "Live confocal time-lapse (488nm/561nm excitation)",
                    "Sparse sampling interval: 6h for 72h total duration"
                ],
                parameters={
                    "pTau217_precursor_concentration_nM": 25.0,
                    "neuronal_culture_density_cells_cm2": 50000,
                    "fluidic_isolation_resistance_Pa": 120.0,
                    "imaging_magnification": "60x Oil Immersion",
                    "sparse_fov_sampling_points": 12
                },
                readout_metric="retrograde_transport_velocity_um_sec",
                falsification_cutoff=0.45
            )
        else:
            return LabProtocolRecipe(
                recipe_id=f"RECIPE-{uuid.uuid4().hex[:8].upper()}",
                target_prediction_id=prediction_id,
                instrument_type=target_instrument,
                protocol_name="Automated High-Throughput Biomarker Binding Titration",
                hardware_constraints=["Liquid handler (Tecan/Biomek)", "Plate reader (SpectraMax)"],
                parameters={"antibody_dilution": "1:1000", "incubation_time_min": 60},
                readout_metric="optical_density_450nm",
                falsification_cutoff=1.20
            )

    @staticmethod
    def ingest_real_world_measurements(
        recipe: LabProtocolRecipe,
        raw_measurement_feed: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processes real-world instrument outputs, computes cryptographic SOM hashes,
        and determines if the empirical observation validates or refutes the prediction.
        """
        # Cryptographic lineage hash
        payload_bytes = json.dumps(raw_measurement_feed, sort_keys=True).encode("utf-8")
        som_data_hash = f"sha256:{hashlib.sha256(payload_bytes).hexdigest()}"

        observed_value = raw_measurement_feed.get("measured_mean_value", 0.0)
        cutoff = recipe.falsification_cutoff
        
        # In our assay, higher transport velocity / slope indicates trans-synaptic activity
        survived = observed_value >= cutoff

        return {
            "ingestion_id": f"INGEST-{uuid.uuid4().hex[:8].upper()}",
            "recipe_id": recipe.recipe_id,
            "target_prediction_id": recipe.target_prediction_id,
            "instrument_source": recipe.instrument_type,
            "som_cryptographic_hash": som_data_hash,
            "raw_measurements_count": raw_measurement_feed.get("data_points_count", 100),
            "observed_value": observed_value,
            "falsification_cutoff": cutoff,
            "prediction_outcome": "SURVIVED" if survived else "REFUTED",
            "empirical_verdict": "Real-world wet-lab measurements corroborated the trans-synaptic prediction." if survived else "Real-world wet-lab measurements refuted the prediction."
        }
