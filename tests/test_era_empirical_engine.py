"""
tests/test_era_empirical_engine.py - Test suite for Google ERA Empirical Research Engine (ADR-DISCOVERY-057).
"""

from __future__ import annotations

import numpy as np
import pytest

from api.server import app
from api.testing import authenticated_client
from python.discovery.era_empirical_engine import (
    ClinicalLeadTimeEvaluator,
    CodeVariant,
    ERAClosedLoopTreeSearch,
    ERAMethodologicalMutationGenerator,
    ERASearchCampaignReport,
    MutationStrategy,
)


@pytest.fixture
def client():
    return authenticated_client(app)


def test_era_methodological_mutation_generation():
    """Verifies that code mutations produce valid offspring with shifted parameters and code snippets."""
    parent = CodeVariant(
        variant_id="base-root",
        parent_id=None,
        generation_depth=0,
        mutation_strategy=MutationStrategy.EXPONENTIAL_DECAY_LAG,
        parameter_spec={"decay_alpha": 0.50},
        code_snippet="y_pred[t] = 0.5 * y[t-1] + 0.5 * y_pred[t-1]",
    )

    child = ERAMethodologicalMutationGenerator.mutate_candidate(
        parent=parent,
        new_variant_id="child-1",
        target_strategy=MutationStrategy.KALMAN_DYNAMIC_FILTER,
    )

    assert child.variant_id == "child-1"
    assert child.parent_id == "base-root"
    assert child.generation_depth == 1
    assert child.mutation_strategy == MutationStrategy.KALMAN_DYNAMIC_FILTER
    assert "measurement_noise" in child.parameter_spec
    assert "kalman_gain" in child.code_snippet


def test_clinical_lead_time_evaluator():
    """Verifies that early prediction crossing critical threshold correctly awards lead-time anticipation days."""
    # True surge occurs at index 8 (day 56)
    true_series = np.array([10, 12, 14, 15, 18, 22, 25, 30, 65, 80, 100], dtype=np.float64)
    # Predictive model anticipates surge crossing >= 60 at index 6 (day 42) -> 2 steps earlier = 14 days lead time
    pred_series = np.array([10, 13, 16, 22, 35, 50, 62, 75, 85, 95, 110], dtype=np.float64)

    lead_days = ClinicalLeadTimeEvaluator.evaluate_lead_time(
        true_series=true_series,
        pred_series=pred_series,
        critical_surge_threshold=60.0,
        time_step_days=7.0,
    )

    assert lead_days == 14.0


def test_era_closed_loop_tree_search_campaign():
    """Executes an empirical tree search over synthetic hospital admissions / biomarker trajectory."""
    # Synthetic epidemiological trajectory with seasonality and surge
    t = np.linspace(0, 4 * np.pi, 25)
    synthetic_admissions = (50 + 25 * np.sin(t) + 30 * np.exp(t / 10)).tolist()

    searcher = ERAClosedLoopTreeSearch()
    report = searcher.run_campaign(
        campaign_id="era-cdc-flu-test",
        dataset_name="Synthetic-Hospital-Surge-2026",
        ground_truth_time_series=synthetic_admissions,
        time_step_days=7.0,
        surge_threshold_quantile=0.80,
        max_iterations=40,
        beam_width=3,
    )

    assert isinstance(report, ERASearchCampaignReport)
    assert report.total_iterations_explored > 10
    assert report.best_variant.is_valid is True
    assert report.best_rmse <= report.baseline_rmse + 1e-4
    assert report.best_variant.r_squared > -10.0
    assert report.era_calibration_hash.startswith("sha256:")
    assert report.tree_depth_reached >= 1


def test_era_api_endpoints(client):
    """Tests the REST API endpoints for code mutation and search campaigns."""
    # 1. Test mutate endpoint
    mutate_resp = client.post(
        "/api/discovery/era/mutate-code",
        json={
            "parent_variant_id": "api-parent",
            "generation_depth": 0,
            "mutation_strategy": "SPLINE_WEIGHTING",
            "parameter_spec": {"spline_knot_weight": 1.0},
            "code_snippet": "spline basis",
            "new_variant_id": "api-mutant-1",
        },
    )
    assert mutate_resp.status_code == 200
    mutant_data = mutate_resp.json()
    assert mutant_data["variant_id"] == "api-mutant-1"
    assert mutant_data["mutation_strategy"] == "SPLINE_WEIGHTING"

    # 2. Test search campaign endpoint
    series = [20.0, 22.0, 25.0, 28.0, 35.0, 50.0, 75.0, 90.0, 60.0, 30.0]
    campaign_resp = client.post(
        "/api/discovery/era/run-search-campaign",
        json={
            "campaign_id": "api-campaign-1",
            "dataset_name": "RSV-Trajectory-Weekly",
            "ground_truth_time_series": series,
            "time_step_days": 7.0,
            "surge_threshold_quantile": 0.75,
            "max_iterations": 20,
            "beam_width": 2,
        },
    )
    assert campaign_resp.status_code == 200
    campaign_data = campaign_resp.json()
    assert campaign_data["campaign_id"] == "api-campaign-1"
    assert "best_variant" in campaign_data
    assert campaign_data["best_rmse"] > 0.0
    assert campaign_data["era_calibration_hash"].startswith("sha256:")
