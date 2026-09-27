"""
tests/test_epistemic_stigmergy.py - Tests for ADR-DISCOVERY-027 Epistemic Stigmergy & Reality Contact.
"""

import pytest

from python.discovery.epistemic_stigmergy import (
    EpistemicPheromoneField,
    RealityContactFirewall,
)
from python.discovery.scientific_git_history import EpistemicGitRepo


@pytest.mark.epistemic
@pytest.mark.fast
def test_pheromone_field_landscape():
    """Verifies that the pheromone field scans the epistemic git repo and produces a valid landscape."""
    repo = EpistemicGitRepo.create_canonical_tau_lineage()
    report = EpistemicPheromoneField.scan_git_repository(repo, uncertainty_threshold=0.60)
    assert report is not None
    assert hasattr(report, "total_active_pheromones")
    assert isinstance(report.total_active_pheromones, int)
    assert report.total_active_pheromones > 0
    assert report.som_landscape_hash.startswith("sha256:")
    assert report.recommended_swarm_role in [
        "POPPER_ADVERSARIAL_AUDITOR",
        "HYPOTHESIS_EXPLORER",
        "INVARIANT_FORMALIZER",
        "VALIDATION_AUDITOR",
        "AUTONOMOUS_SCOUT",
    ]


@pytest.mark.epistemic
@pytest.mark.fast
def test_reality_contact_firewall_enforcement():
    """Verifies that ungrounded theories (RCS < 2.0) are blocked from being promoted to invariants."""
    # Low RCS (in silico hallucination without external anchor)
    report_low = RealityContactFirewall.audit_promotion_request(
        hypothesis_id="THEORY-SYNTH-01",
        claimed_regularity="Hypothetical fifth force coupling constant alpha_5 = 1.37e-4",
        rcs_level=1,
        empirical_anchors=[],
    )
    assert not report_low.is_firewall_passed
    assert "BLOCKED" in report_low.rejection_reason

    # High RCS with external physical anchor
    report_high = RealityContactFirewall.audit_promotion_request(
        hypothesis_id="THEORY-COSMO-02",
        claimed_regularity="Hubble parameter measurement H0 = 67.4 +/- 0.5 km/s/Mpc",
        rcs_level=2,
        empirical_anchors=["Planck 2018 Legacy Data Release", "CODATA 2022 recommended values"],
    )
    assert report_high.is_firewall_passed
    assert report_high.rejection_reason is None
