"""
Tests for Limitation Resolution & Empirical Refinement Engine (ADR-DISCOVERY-042).
"""

from python.discovery.limitation_resolution_engine import (
    BaselineLimitation,
    LimitationCategory,
    LimitationResolutionEngine,
    ScreeningVerdict,
    SupplementaryRebuttalExecution,
    TargetedSeedIdea,
)


def test_extract_actionable_limitations():
    engine = LimitationResolutionEngine()
    theory_text = (
        "The standard fluid model diverges near the boundary singularity, "
        "and relies on linear approximations that fail in coupled turbulent flow."
    )

    limitations = engine.extract_actionable_limitations("NavierStokesBaseline", theory_text)

    assert len(limitations) >= 2
    cats = [lim.category for lim in limitations]
    assert LimitationCategory.THEORETICAL_ASYMMETRY in cats
    assert LimitationCategory.ASSUMPTION_OVEREXTENSION in cats
    assert all(lim.is_actionable for lim in limitations)


def test_generate_targeted_seed_ideas():
    engine = LimitationResolutionEngine()
    lims = [
        BaselineLimitation(
            limitation_id="LIM-1",
            category=LimitationCategory.THEORETICAL_ASYMMETRY,
            description="Divergence in asymptotic limit",
            impact_severity=0.9,
            is_actionable=True,
        )
    ]

    ideas = engine.generate_targeted_seed_ideas(lims)

    assert len(ideas) == 1
    assert ideas[0].idea_id == "IDEA-LIM-1"
    assert ideas[0].novelty_score >= 0.6
    assert "topological correction" in ideas[0].proposed_mechanism


def test_subset_screening_triage():
    engine = LimitationResolutionEngine()
    idea_good = TargetedSeedIdea("ID-1", ["LIM-1"], "Good mechanism", 0.8)
    idea_bad = TargetedSeedIdea("ID-2", ["LIM-1"], "Bad mechanism", 0.5)

    # Candidate 1 yields +15% improvement
    rep_good = engine.screen_on_subset(idea_good, baseline_metric=100.0, evaluate_subset_fn=lambda _: 115.0)
    assert rep_good.verdict == ScreeningVerdict.GOOD
    assert rep_good.promoted_to_full_benchmark is True
    assert rep_good.relative_gain == 0.15

    # Candidate 2 yields -10% regression
    rep_bad = engine.screen_on_subset(idea_bad, baseline_metric=100.0, evaluate_subset_fn=lambda _: 90.0)
    assert rep_bad.verdict == ScreeningVerdict.BAD
    assert rep_bad.promoted_to_full_benchmark is False
    assert rep_bad.relative_gain == -0.10


def test_execute_active_rebuttal_task():
    engine = LimitationResolutionEngine()

    def supplementary_experiment():
        return True, "Supplementary test confirmed OOD generalization on Re=100,000 flow."

    rebuttal = engine.execute_active_rebuttal_task(
        task_id="TASK-REB-01",
        reviewer_critique="Reviewer 2 questions whether the method holds at Reynolds number > 50,000.",
        supplementary_experiment_fn=supplementary_experiment,
    )

    assert isinstance(rebuttal, SupplementaryRebuttalExecution)
    assert rebuttal.is_critique_resolved is True
    assert rebuttal.rebuttal_score_boost == 1.5
    assert "confirmed OOD generalization" in rebuttal.empirical_result_summary
