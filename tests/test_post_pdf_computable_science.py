"""
tests/test_post_pdf_computable_science.py - Tests for ADR-EPISTEMIC-033 Post-PDF Computable Science & Anti-Slop Invariant.
Verifies that:
1. Synthetic ungrounded placeholder code is intercepted as SYNTHETIC_SLOP_UNGROUNDED.
2. Clean code passes the anti-slop verification gate.
3. RealityContactScore enforces empirical grounding (RCS >= 2.0).
"""

import pytest

from python.discovery.epistemic_pr_auditor import (
    FileDiffChunk,
    PullRequestDiffSnapshot,
    ReviewSeverity,
    ScientificEpistemicPRAuditor,
    ScientificViolationCategory,
)
from python.discovery.reality_contact_score import (
    RealityContactEvaluator,
    RealityContactEvidence,
    RealityContactLevel,
)


@pytest.mark.epistemic
@pytest.mark.fast
def test_anti_slop_interception_of_mock_simulation():
    """Verifies that commits containing mock empirical simulations are critically rejected under ADR-EPISTEMIC-033."""
    auditor = ScientificEpistemicPRAuditor()
    mock_file = FileDiffChunk(
        file_path="src/models/synthetic_experiment.py",
        content=(
            "import numpy as np\n"
            "simulated_empirical_results = True\n"
            "# Breakthrough p-value achieved on synthetic cohort\n"
            "p_val = 0.001\n"
        ),
    )
    pr = PullRequestDiffSnapshot(
        repo_name="Fundacion-de-Neurociencias/test-pipeline",
        pull_request_number=42,
        base_branch="main",
        head_branch="feature/mock-data",
        commit_sha="abcd1234efgh5678",
        pr_title="feat: breakthrough synthetic discovery",
        pr_description="Adds synthetic simulation run",
        files=[mock_file],
    )

    report = auditor.audit_pull_request(pr)
    assert report is not None
    assert len(report.inline_findings) >= 1

    slop_findings = [
        f for f in report.inline_findings if f.category == ScientificViolationCategory.SYNTHETIC_SLOP_UNGROUNDED
    ]
    assert len(slop_findings) == 1
    assert slop_findings[0].severity == ReviewSeverity.CRITICAL_REJECTION
    assert "Ungrounded Academic Slop" in slop_findings[0].title


@pytest.mark.epistemic
@pytest.mark.fast
def test_clean_empirical_code_passes_anti_slop_gate():
    """Verifies that clean code without mock data passes the audit."""
    auditor = ScientificEpistemicPRAuditor()
    clean_file = FileDiffChunk(
        file_path="src/analysis/real_pipeline.py",
        content=(
            "import pandas as pd\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "df = pd.read_csv('data/metaboad_atn_processed.csv')\n"
            "X = df[['plasma_ptau217', 'gfap']]\n"
            "y = df['cdr_progression']\n"
            "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n"
            "scaler = StandardScaler()\n"
            "X_train_scaled = scaler.fit_transform(X_train)\n"
        ),
    )
    pr = PullRequestDiffSnapshot(
        repo_name="Fundacion-de-Neurociencias/test-pipeline",
        pull_request_number=43,
        base_branch="main",
        head_branch="feature/clean-analysis",
        commit_sha="1122334455667788",
        pr_title="feat: empirical cohort evaluation",
        pr_description="Evaluates real cohort data",
        files=[clean_file],
    )

    report = auditor.audit_pull_request(pr)
    slop_findings = [
        f for f in report.inline_findings if f.category == ScientificViolationCategory.SYNTHETIC_SLOP_UNGROUNDED
    ]
    assert len(slop_findings) == 0


@pytest.mark.epistemic
@pytest.mark.fast
def test_reality_contact_score_requires_data_contact():
    """Verifies that RCS Level 0 (pure literature) cannot be promoted as an active invariant."""
    evidence = RealityContactEvidence(
        literature_citations_count=50, retrospective_cohorts_validated=[], prospective_holdout_datasets=[]
    )
    report = RealityContactEvaluator.evaluate_rcs("THEORY-TEXT-ONLY", evidence)
    assert report.rcs_score == RealityContactLevel.LEVEL_0_LITERATURE_ONLY
    assert not report.is_promotable_as_invariant
