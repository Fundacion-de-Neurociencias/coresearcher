"""Tests for the trivial-witness probe and the Lean exclusion lint (python/discovery/trivial_witness.py), and for
the two cases that use them (yang_mills_case, o3_continuum_case)."""

import json
from pathlib import Path

import pytest

from python.discovery import preregistration as pr
from python.discovery import o3_continuum_case as o3
from python.discovery import yang_mills_case as ymc
from python.discovery.trivial_witness import checklist_clauses, lint_exclusions, necessity, parse_declarations, probe

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def ym():
    return pr.load(ymc.CHECKLIST)


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------


def test_checklist_excludes_every_catalogued_witness(ym):
    for claim in ("YM", "QCD"):
        report = probe(ym, checklist_clauses(ym, claim))
        assert report.outcome == "EXCLUDES_ALL_CATALOGUED", claim
        assert all(w.result == "EXCLUDED" for w in report.witnesses)


def test_the_brief_catalogue_is_present(ym):
    kinds = {w.kind for w in ym.witnesses}
    assert {"trivial", "gaussian", "abelian", "lower_dimension", "finite_volume", "lattice_only"} <= kinds


def test_os_axioms_on_a_group_label_are_vacuous(ym):
    """An OS theory on R^4 with a non-abelian label: Yang-Mills at zero coupling satisfies it."""
    clauses = {
        "group": "gauge_group in ('SU2', 'SU3', 'SUN_only', 'all_compact_simple')",
        "dim": "dim == 4",
        "volume": "volume == 'infinite'",
        "rp": "os_reflection_positivity",
        "euclid": "os_euclidean_invariance",
        "cluster": "os_cluster",
    }
    report = probe(ym, clauses)
    assert report.outcome == "VACUOUS_RELATIVE_TO_INTENT"
    assert "free_nonabelian_gaussian_4d" in report.satisfied_by
    by_id = {w.witness: w for w in report.witnesses}
    assert by_id["maxwell_u1_4d"].excluded_by == ["group"]
    assert by_id["ym_torus_4d"].result == "EXCLUDED"
    assert by_id["zero_theory"].result == "UNDETERMINED"  # Its group label is free: a human must look.


def test_adding_non_triviality_closes_the_gaussian_gap(ym):
    clauses = {
        "group": "gauge_group in ('SU2', 'SU3', 'SUN_only', 'all_compact_simple')",
        "dim": "dim == 4",
        "volume": "volume == 'infinite'",
        "continuum": "spacing == 0 and continuum_limit == 'lattice_independent'",
        "nontrivial": "connected_4pt == 'nonzero'",
        "euclid": "os_euclidean_invariance",
    }
    report = probe(ym, clauses)
    assert report.satisfied_by == []
    assert "free_nonabelian_gaussian_4d" not in report.undetermined


def test_a_lattice_statement_is_satisfied_by_the_lattice_witness(ym):
    clauses = {"group": "gauge_group != 'none' and gauge_group != 'U1'", "dim": "dim == 4", "rp": "os_reflection_positivity"}
    report = probe(ym, clauses)
    assert {"lattice_ym_4d", "free_nonabelian_gaussian_4d"} <= set(report.satisfied_by)


def test_empty_statement_is_rejected(ym):
    with pytest.raises(ValueError):
        probe(ym, {})


def test_necessity_finds_the_only_barriers(ym):
    assert {k: v for k, v in necessity(ym, "YM").items() if v} == {"YM-CONTINUUM": ["subsequential_limit_4d"]}
    without_sd = ymc.scenario_clauses(ym, ymc.SCENARIOS[0])
    load_bearing = {k: v for k, v in necessity(ym, clauses=without_sd).items() if v}
    assert load_bearing["YM-NONTRIVIAL"] == ["zero_theory", "free_nonabelian_gaussian_4d"]
    assert load_bearing["YM-SPACETIME-DIM4"] == ["ym_3d"]


# ---------------------------------------------------------------------------
# Lean exclusion lint
# ---------------------------------------------------------------------------

TORUS_STATEMENT = """
import Mathlib
/-- A gauge theory on the torus. Comment text: ReflectionPositive, cluster, Wilson. -/
structure GaugeTheory (G : Type) [Group G] where
  site : Type
  schwinger : (Fin 4 → AddCircle (1 : ℝ)) → ℝ
  -- reflection positivity, Euclidean invariance and clustering are only in this comment
def YangMills (G : Type) [Group G] : Prop := ∃ T : GaugeTheory G, T.schwinger = T.schwinger
theorem ym_exists (G : Type) [Group G] [CompactSpace G] : YangMills G := by
  sorry
"""

CAREFUL_STATEMENT = """
structure EuclideanQFT where
  S : ℕ → SchwartzMap (Fin 4 → EuclideanSpace ℝ (Fin 4)) ℂ → ℂ
def ReflectionPositive (T : EuclideanQFT) : Prop := True
def EuclideanInvariant (T : EuclideanQFT) : Prop := True
def Clusters (T : EuclideanQFT) : Prop := True
def PermutationSymmetric (T : EuclideanQFT) : Prop := ∀ σ : Equiv.Perm (Fin 4), True
def TruncatedFourPointNonzero (T : EuclideanQFT) : Prop := True
def WilsonLoopsGaugeInvariant (T : EuclideanQFT) : Prop := True
def CurvatureFields (T : EuclideanQFT) : Prop := True
def AsymptoticFreedom (T : EuclideanQFT) : Prop := True
def ContinuumLimit (T : EuclideanQFT) : Prop := True
theorem ym_exists (G : Type) [Group G] [CompactSpace G] [LieGroup G] :
    ∃ T : EuclideanQFT, ReflectionPositive T ∧ EuclideanInvariant T ∧ Clusters T ∧ PermutationSymmetric T ∧
      TruncatedFourPointNonzero T ∧ WilsonLoopsGaugeInvariant T ∧ CurvatureFields T ∧ AsymptoticFreedom T ∧
      ContinuumLimit T := by
  sorry
"""


def test_structures_are_declarations_and_comments_are_ignored():
    names = [d.name for d in parse_declarations(TORUS_STATEMENT)]
    assert names == ["GaugeTheory", "YangMills", "ym_exists"]


def test_lint_flags_a_torus_statement(ym):
    report = lint_exclusions(TORUS_STATEMENT, ym, theorem="ym_exists")
    assert report.flag == "POSSIBLY_VACUOUS_RELATIVE_TO_INTENT"
    by_id = {w.witness: w for w in report.witnesses}
    torus = by_id["ym_torus_4d"]
    assert torus.status == "NO_EXCLUDING_CLAUSE_FOUND"
    assert {h.pattern for h in torus.counter_evidence} >= {"AddCircle"}
    assert by_id["zero_theory"].status == "NO_EXCLUDING_CLAUSE_FOUND"  # The OS words sit in comments only.
    # Dimension 4 is mentioned (Fin 4), which is a marker against the 2D and 3D witnesses.
    assert by_id["ym_2d"].status == "ADDRESSED_IN_TEXT"
    assert all(w.semantic_confirmation == "HUMAN_REQUIRED" for w in report.witnesses)


def test_lint_finds_markers_for_every_witness_in_a_careful_statement(ym):
    report = lint_exclusions(CAREFUL_STATEMENT, ym, theorem="ym_exists")
    assert report.flag == "EVERY_WITNESS_ADDRESSED_IN_TEXT"
    # Markers say only that the text mentions the clause; these definitions are `True`, so a human would reject
    # them. The lint never confirms semantics.
    assert all(w.semantic_confirmation == "HUMAN_REQUIRED" for w in report.witnesses)


# ---------------------------------------------------------------------------
# Cases: the stored reports are what the code computes
# ---------------------------------------------------------------------------


def test_yang_mills_case_report_is_reproduced():
    stored = json.loads((ymc.CASE_DIR / "preregistration_report.json").read_text(encoding="utf-8"))
    assert ymc.case_report() == stored
    record = json.loads((ymc.CASE_DIR / "ym_claim_record.json").read_text(encoding="utf-8"))
    assert record == stored["claim_record"]
    assert record["rung"] == "CLAIMED"


def test_o3_vendored_files_match_their_pins():
    for name in o3.VENDORED:
        o3.vendored(name)


def test_o3_coverage_map_shows_the_gap():
    rows = {r["obligation"]: r["coverage"] for r in o3.coverage_rows()}
    assert {k for k, v in rows.items() if v == "COVERED"} == {"O3-FIELD", "O3-DIM2", "LAT-DECAY"}
    assert {k for k, v in rows.items() if v == "OBJECT_DIFFERS"} == {"O3-INFINITE-VOLUME", "O3-CONTINUUM"}
    os_and_more = {
        "O3-OS-REGULARITY", "O3-OS-EUCLIDEAN", "O3-OS-RP", "O3-OS-SYMMETRY", "O3-OS-CLUSTER",
        "O3-NONTRIVIAL", "O3-UNIQUE-VACUUM", "O3-MASS-GAP", "O3-INTERNAL-SYMMETRY",
    }
    assert {k for k, v in rows.items() if v == "NOT_ADDRESSED"} == os_and_more


def test_o3_case_report_is_reproduced():
    stored = json.loads((o3.CASE_DIR / "rehearsal_report.json").read_text(encoding="utf-8"))
    report = o3.case_report()
    assert report == stored
    assert report["probes"]["paper_claim"]["outcome"] == "EXCLUDES_ALL_CATALOGUED"
    assert report["probes"]["lean_covered_part_of_claim"]["outcome"] == "VACUOUS_RELATIVE_TO_INTENT"
    assert "lattice_o3_high_temperature_finite" in report["probes"]["lean_covered_part_of_claim"]["satisfied_by"]
    assert report["exclusion_lint"]["flag"] == "POSSIBLY_VACUOUS_RELATIVE_TO_INTENT"
    statuses = {r["item"]: r["status"] for r in report["family_coverage"]}
    assert [k for k, v in statuses.items() if v == "COMPARATOR"] == ["Exponential decay in classical O(n) models (September 23, 2026)"]
