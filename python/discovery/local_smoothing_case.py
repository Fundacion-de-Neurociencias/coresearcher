"""
python/discovery/local_smoothing_case.py - Statement fidelity of OpenAI's "Local smoothing for the Euclidean wave
equation" (October 25, 2026) against its Lean Comparator reference statements (ADR-DISCOVERY-070).

Three parts, all about formal statement fidelity (not the paper's credit, novelty or announcements):

1. range equivalence: the hypothesis range of each Comparator theorem, as stated in the paper and as written in
   Lean, decided by z3 (`statement_fidelity`), with mutated ranges as negative controls;
2. junk-value lint of the Lean statement file (`lean_junk_lint`), with a review note on every OPEN finding;
3. coverage map: every theorem and corollary of the paper with its formal status.

Sources are pinned to one commit of github.com/openai/math and treated as data. The Comparator statement file is
vendored (Apache-2.0) in examples/local-smoothing-fidelity/; its SHA-256 is checked before use.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List

from python.discovery.lean_junk_lint import lint
from python.discovery.statement_fidelity import Parameter, Quantity, RangeSpec, compare_ranges, cross_check

ROOT = Path(__file__).resolve().parent.parent.parent
CASE_DIR = ROOT / "examples" / "local-smoothing-fidelity"

SOURCE = {
    "repository": "https://github.com/openai/math",
    "commit": "7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a",
    "paper": "preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026/paper.pdf",
    "paper_sha256": "9ca156c552f2d940528f7131716326ef0d67a5829e723e1d294d74560c8636ff",
    "lean_statements": "lean/ComparatorChallenges/LocalSmoothing.lean",
    "lean_statements_sha256": "58dd1d878cd08f8d32850b1142e451a5efd4b0cdcf538ba80efbd01ea83cd9fd",
    "comparator_config": "lean/ComparatorChallenges/LocalSmoothing.json",
    "comparator_config_sha256": "73392b548f23dd8b1b0b459fae548212b58aab280fdcd0120d06f856c18daa91",
    "scope_note": "lean/docs/079.md",
    "scope_note_sha256": "3c550c200f483746fb2cd47fff2f2ba0194a4ae9c11562e41c463814137a72a9",
    "lean_toolchain": "leanprover/lean4:v4.34.1",
    "mathlib_rev": "d13f23b723b8a846827a245b89c10fc7d3f11612",
    "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"],
}

N = Parameter("n", integer=True, lower=2)

# ---------------------------------------------------------------------------
# Part 1: hypothesis ranges
# ---------------------------------------------------------------------------

RANGE_SPECS: List[RangeSpec] = [
    RangeSpec(
        theorem="euclidean_local_smoothing",
        parameters=[N, Parameter("p"), Parameter("eps")],
        paper="2 <= p and (eps > 0 or (p == 2 and eps == 0))",
        lean="2 <= p and (0 < eps or (p == 2 and eps == 0))",
        paper_source="Theorem 1.1: n >= 2, 2 <= p < inf, eps > 0; at p = 2 one can take eps = 0. Order s+(p) + eps.",
        lean_source="∀ n, 2 ≤ n → ∀ p ε : ℝ, 2 ≤ p → (0 < ε ∨ (p = 2 ∧ ε = 0)) → ... besselPotential "
        "(max 0 (((n : ℝ) - 1) / 2 - n / p) + ε)",
        encoding=["p : ℝ is finite, so p < ∞ holds on both sides.", "n : ℕ with 2 ≤ n is an Int symbol n >= 2."],
        quantities=[
            Quantity("sobolev_order", paper="max(0, (n - 1)/2 - n/p) + eps", lean="max(0, (n - 1)/2 - n/p) + eps")
        ],
    ),
    RangeSpec(
        theorem="bochner_riesz",
        parameters=[N, Parameter("q", lower=0, upper=1), Parameter("delta")],
        paper="delta > max(0, n*abs(q - 1/2) - 1/2)",
        lean="max(n*abs(q - 1/2) - 1/2, 0) < delta",
        paper_source="Theorem 10.1 (10.1): n >= 2, 1 <= p <= inf, alpha > delta(p) = max{0, n|1/p - 1/2| - 1/2}.",
        lean_source="∀ p : ℝ≥0∞, 1 ≤ p → ∀ δ : ℝ, max ((n : ℝ) * |(p⁻¹).toReal - 1 / 2| - 1 / 2) 0 < δ → "
        "∃ C, ∀ R > 0, ...",
        encoding=[
            "p ∈ [1, ∞] (ℝ≥0∞) is encoded by q = (p⁻¹).toReal ∈ [0, 1], a bijection; p = ∞ is q = 0.",
            "The toReal is not a junk value here: 1 ≤ p gives p⁻¹ ≤ 1 < ∞ (lint finding TO_REAL, discharged).",
            "The paper's order α is the Lean δ; the uniform-in-R form matches sup over r > 0 in (10.1).",
        ],
    ),
    RangeSpec(
        theorem="spherical_restriction",
        parameters=[N, Parameter("q", lower=0), Parameter("b")],
        domain="q < 1",
        paper="b > 2*n/(n - 1) and b > (n + 1)/(n - 1) / (1 - q)",
        lean="2*n/(n - 1) < b and ((q == 0 and (n + 1)/(n - 1) * 1 < b) or "
        "(q > 0 and (n + 1)/(n - 1) * ((1/q) / ((1/q) - 1)) < b))",
        paper_source="Corollary 9.3 (9.3): 1 < a <= inf, b < inf, b > pc = 2n/(n-1), b > (n+1)/(n-1) a'.",
        lean_source="∀ a : ℝ≥0∞, 1 < a → ∀ b : ℝ, 2 * (n : ℝ) / (n - 1) < b → ((n : ℝ) + 1) / ((n : ℝ) - 1) * "
        "conjugateExponent a < b; conjugateExponent a = if a = ∞ then 1 else a.toReal / (a.toReal - 1)",
        encoding=[
            "a ∈ (1, ∞] is encoded by q = 1/a ∈ [0, 1); a' = 1/(1 - q) in the paper.",
            "The Lean `if a = ∞` branch is q = 0; the else branch uses a.toReal = 1/q, finite for q > 0.",
            "b : ℝ is finite, so the paper's b < ∞ holds on both sides.",
        ],
    ),
    RangeSpec(
        theorem="kakeya_maximal",
        parameters=[N, Parameter("delta")],
        paper="0 < delta and delta <= 1",
        lean="0 < delta and delta <= 1",
        paper_source="Corollary 9.1: n >= 2, 0 < delta <= 1, ‖K_delta f‖_{L^n(S^{n-1})} <= C_n [log(2/delta)]^{4/pc} ‖f‖_n.",
        lean_source="∀ ε > 0, ∃ C > 0, ∀ δ, 0 < δ → δ ≤ 1 → ∀ f, MemLp f n → ... ≤ ofReal (C * δ ^ (-ε)) * eLpNorm f n",
        encoding=[
            "Only the scale range is compared. The bound itself (log^{4/pc} against δ^{-ε}) is outside the decidable "
            "fragment; see the coverage map: the Lean bound is weaker.",
        ],
    ),
    RangeSpec(
        theorem="kakeya",
        parameters=[N],
        paper="True",
        lean="True",
        paper_source="Corollary 9.1: every subset of R^n containing a unit line segment in each direction has "
        "Hausdorff dimension n.",
        lean_source="∀ n, 2 ≤ n → ∀ F, IsKakeyaSet F → dimH F = n (no measurability assumed)",
        encoding=["The only parameter is n >= 2 on both sides; the set F is universally quantified in both."],
    ),
    RangeSpec(
        theorem="stein_square",
        parameters=[N, Parameter("p"), Parameter("alpha")],
        paper="2 <= p and alpha > max(1/2, n*(1/2 - 1/p))",
        lean="2 <= p and max(1/2, n*(1/2 - 1/p)) < alpha",
        paper_source="Theorem 11.1: n >= 2, 2 <= p < inf, alpha > max{1/2, n(1/2 - 1/p)}.",
        lean_source="∀ p α : ℝ, 2 ≤ p → max (1 / 2) ((n : ℝ) * (1 / 2 - 1 / p)) < α → ...",
        encoding=["p : ℝ is finite."],
    ),
    RangeSpec(
        theorem="stein_square (paper §1.1 form)",
        parameters=[N, Parameter("p"), Parameter("alpha")],
        paper="2 <= p and alpha > 1/2 + max(0, (n - 1)/2 - n/p)",
        lean="2 <= p and max(1/2, n*(1/2 - 1/p)) < alpha",
        paper_source="Section 1.1: conjectured bounds for 2 <= p < inf and alpha > 1/2 + s+(p).",
        lean_source="stein_square as above",
        encoding=["Same statement, paper range written through s+(p) as in the introduction."],
    ),
]

# Exponent ranges of statements that live in the openai/math Lean development but are not Comparator targets.
DEVELOPMENT_SPECS: List[RangeSpec] = [
    RangeSpec(
        theorem="logarithmic_refinement (Theorem 1.2)",
        parameters=[N, Parameter("A")],
        paper="A >= (n - 1)/n",
        lean="A >= 2*n + 5",
        paper_source="Theorem 1.2: p = pc, ‖U(T) P_N f‖ <= C [log(2 + N)]^{2/p} ‖f‖_p; 2/pc = (n-1)/n.",
        lean_source="OAI/Analysis/Fourier/LocalSmoothing/Definitions.lean, LogarithmicRefinement: "
        "ofReal (C * (1 + Real.log (1 / h)) ^ (2 * n + 5)), h = 1/N ≤ 1",
        encoding=[
            "A is the logarithmic power; an estimate with power A implies every larger power, so each side asserts "
            "the upward-closed set of powers above its own.",
            "1 + log(1/h) and log(2 + N) with N = 1/h >= 1 are comparable, so the powers are directly comparable.",
        ],
    ),
    RangeSpec(
        theorem="logarithmic_sobolev (Corollary 7.1, C = 0 slice)",
        parameters=[N, Parameter("p"), Parameter("B")],
        domain="p > 2",
        paper="B > min((n - 1)*(1 - 2/p), 2/p) + 1/2 - 1/p",
        lean="B > 2*n + 6",
        paper_source="Corollary 7.1: B > B*(p) = beta(p) + delta_p, beta(p) = min{d(1 - 2/p), 2/p}, "
        "delta_p = 1/2 - 1/p (any C), or B = B*(p) with C > delta_p.",
        lean_source="Definitions.lean, LogarithmicSobolev: ∀ p B, 2 < p → 2 * n + 6 < B → ... logBesselPotential "
        "(smoothingOrder n p) B f",
        encoding=[
            "The Lean statement has no log-log factor, so it is compared with the paper's C = 0 slice, where the "
            "paper needs B > B*(p) (the endpoint B = B*(p) needs C > delta_p > 0).",
        ],
    ),
]

# Negative controls: plausible formalization slips. Each must be detected (not EQUIVALENT) unless noted.
MUTANTS: List[Dict[str, Any]] = [
    {
        "base": "stein_square",
        "label": "non-strict alpha",
        "lean": "2 <= p and max(1/2, n*(1/2 - 1/p)) <= alpha",
        "expected": "STRONGER",
    },
    {
        "base": "stein_square",
        "label": "dropped 1/2 floor",
        "lean": "2 <= p and n*(1/2 - 1/p) < alpha",
        "expected": "STRONGER",
    },
    {
        "base": "stein_square",
        "label": "(n-1) for n",
        "lean": "2 <= p and max(1/2, (n - 1)*(1/2 - 1/p)) < alpha",
        "expected": "STRONGER",
    },
    {
        "base": "euclidean_local_smoothing",
        "label": "no p = 2 endpoint",
        "lean": "2 <= p and 0 < eps",
        "expected": "WEAKER",
    },
    {
        "base": "bochner_riesz",
        "label": "missing abs",
        "lean": "max(n*(q - 1/2) - 1/2, 0) < delta",
        "expected": "STRONGER",
    },
    {
        "base": "bochner_riesz",
        "label": "non-strict delta (admits delta = 0, where 0^0 = 1 makes the symbol 1)",
        "lean": "max(n*abs(q - 1/2) - 1/2, 0) <= delta",
        "expected": "STRONGER",
    },
    {
        "base": "spherical_restriction",
        "label": "Tomas-Stein exponent 2(n+1)/(n-1) for pc",
        "lean": "2*(n + 1)/(n - 1) < b and ((q == 0 and (n + 1)/(n - 1) * 1 < b) or "
        "(q > 0 and (n + 1)/(n - 1) * ((1/q) / ((1/q) - 1)) < b))",
        "expected": "WEAKER",
    },
    {
        "base": "spherical_restriction",
        "label": "dropped mixed condition",
        "lean": "2*n/(n - 1) < b",
        "expected": "STRONGER",
    },
    {
        "base": "spherical_restriction",
        "label": "unguarded toReal (a = ∞ gives conjugate 0/(0-1) = 0)",
        "lean": "2*n/(n - 1) < b and ((q == 0 and (n + 1)/(n - 1) * 0 < b) or "
        "(q > 0 and (n + 1)/(n - 1) * ((1/q) / ((1/q) - 1)) < b))",
        "expected": "EQUIVALENT",
        "note": "The junk value is masked: b > 2n/(n-1) > (n+1)/(n-1) already, so the guard does not change the range.",
    },
]

CROSS_CHECK_N = tuple(range(2, 7))


def _spec(name: str) -> RangeSpec:
    return next(s for s in RANGE_SPECS if s.theorem == name)


def mutant_spec(mutant: Dict[str, Any]) -> RangeSpec:
    base = _spec(mutant["base"])
    return RangeSpec(
        theorem=f"{base.theorem} [mutant: {mutant['label']}]",
        parameters=base.parameters,
        paper=base.paper,
        lean=mutant["lean"],
        domain=base.domain,
    )


# ---------------------------------------------------------------------------
# Part 2: junk-value lint, with review notes on findings no syntactic rule discharges
# ---------------------------------------------------------------------------

REVIEWER = "CoResearcher agent analysis (not machine-checked); a human should confirm"
REVIEWS = {
    ("stein_square", "DIVISION", 49): (
        "Not a fidelity gap. bochnerRieszSymbol is used with R := s, the variable of the deriv lambda evaluated at "
        "r ∈ Ioi 0, so ‖ξ‖ / s is only needed for s near r > 0. " + REVIEWER
    ),
    ("stein_square", "RPOW", 49): (
        "Not a fidelity gap. The exponent is the order α, and the premise gives α > max(1/2, ...) ≥ 1/2 > 0, so "
        "0 ^ α = 0 and the symbol vanishes outside the ball. " + REVIEWER
    ),
    ("stein_square", "DERIV", 76): (
        "Open question for a human, believed harmless. deriv returns 0 where r ↦ B_r^α f(x) is not differentiable, "
        "which would shrink the square function and weaken the statement. For Schwartz f, polar coordinates and "
        "ρ = r t give B_r^α f(x) = c r^n ∫_0^1 (1 - t²)^α t^(n-1) F_x(r t) dt with F_x smooth, which is smooth in "
        "r > 0 for every α > -1; so for α > 1/2 the junk branch never fires. The statement does not say so "
        "(no differentiability conjunct), and nothing here checks the argument. " + REVIEWER
    ),
}


def lint_report() -> Dict[str, Any]:
    path = CASE_DIR / "LocalSmoothing.lean"
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SOURCE["lean_statements_sha256"]:
        raise ValueError(f"{path} has SHA-256 {digest}, expected {SOURCE['lean_statements_sha256']}.")
    report = lint(data.decode("utf-8"), file=SOURCE["lean_statements"], reviews=REVIEWS).to_dict()
    report["sha256"] = digest
    return report


# ---------------------------------------------------------------------------
# Part 3: coverage map
# ---------------------------------------------------------------------------

COMPARATOR = "Comparator target"  # One of the six reference statements; kernel check claimed upstream, not re-run.
DEVELOPMENT = "Lean statement outside Comparator"  # In the openai/math development; read, not kernel-checked here.
PROSE = "prose only"  # No Lean statement located in the files read.
UNCHECKED = "not checked"  # Not searched for in the Lean development.

COVERAGE: List[Dict[str, str]] = [
    {
        "item": "Theorem 1.1 (1.1)",
        "claim": "local smoothing, n >= 2, 2 <= p < inf, order s+(p) + eps; eps = 0 at p = 2",
        "status": COMPARATOR,
        "lean": "euclidean_local_smoothing",
        "fidelity": "range and Sobolev order EQUIVALENT (z3)",
    },
    {
        "item": "Theorem 1.2 (1.2)",
        "claim": "critical annular estimate with [log(2 + N)]^{2/pc}",
        "status": DEVELOPMENT,
        "lean": "LocalSmoothing.Main.logarithmic_refinement (LogarithmicRefinement)",
        "fidelity": "WEAKER: Lean log power 2n + 5 against 2/pc = (n-1)/n (z3); the sharp power is not formalized",
    },
    {
        "item": "Corollary 7.1 (7.4)",
        "claim": "log-Sobolev estimate for B > B*(p), or B = B*(p) with C > delta_p",
        "status": DEVELOPMENT,
        "lean": "LocalSmoothing.Main.logarithmic_sobolev (LogarithmicSobolev)",
        "fidelity": "WEAKER: Lean needs B > 2n + 6 and has no log-log factor (z3 on the C = 0 slice)",
    },
    {
        "item": "Proposition 8.1 (8.1)",
        "claim": "radial focusing: s+(p) and the 1/pc log power are necessary",
        "status": DEVELOPMENT,
        "lean": "LocalSmoothing/Sharpness (sobolev_estimate_sharp_order, " "logarithmic_estimate_exponent_necessary)",
        "fidelity": "not audited",
    },
    {
        "item": "Proposition 8.2 (8.4)",
        "claim": "weak spacetime obstruction for 2 < p <= pc",
        "status": UNCHECKED,
        "lean": "-",
        "fidelity": "Sharpness/ has packet and modulation files that were not read",
    },
    {
        "item": "Corollary 9.1, first estimate",
        "claim": "local spherical extension on B(z, R) with [log(2 + R)]^{2/pc}",
        "status": PROSE,
        "lean": "-",
        "fidelity": "Restriction/Local*.lean exist but were not read; no statement " "with the 2/pc power located",
    },
    {
        "item": "Corollary 9.1, Kakeya maximal",
        "claim": "‖K_delta f‖_{L^n(S^{n-1})} <= C [log(2/delta)]^{4/pc} ‖f‖_n",
        "status": COMPARATOR,
        "lean": "kakeya_maximal",
        "fidelity": "range EQUIVALENT (z3); bound WEAKER: δ^{-ε} for every ε > 0 instead of log^{4/pc} "
        "(log^c(2/δ) <= C_ε δ^{-ε}, not conversely; outside the SMT fragment)",
    },
    {
        "item": "Corollary 9.1, Hausdorff dimension",
        "claim": "Kakeya sets in R^n have Hausdorff dimension n",
        "status": COMPARATOR,
        "lean": "kakeya",
        "fidelity": "EQUIVALENT; no measurability assumed on either side",
    },
    {
        "item": "Corollary 9.1, Minkowski (bounded sets)",
        "claim": "full Minkowski dimension of bounded Kakeya sets",
        "status": DEVELOPMENT,
        "lean": "LocalSmoothing.FurtherResults.kakeya_minkowski",
        "fidelity": "not audited",
    },
    {
        "item": "Corollary 9.3 (9.3)",
        "claim": "global sphere extension L^a -> L^b, b > pc, b > (n+1)a'/(n-1)",
        "status": COMPARATOR,
        "lean": "spherical_restriction",
        "fidelity": "range EQUIVALENT (z3)",
    },
    {
        "item": "Corollary 9.3, b = inf",
        "claim": "both estimates at b = inf for every 1 <= a <= inf",
        "status": PROSE,
        "lean": "-",
        "fidelity": "b : ℝ in the Comparator statement excludes b = ∞ (trivial L1 bound)",
    },
    {
        "item": "Corollary 9.3 (9.4)",
        "claim": "truncated cone extension in the same range",
        "status": DEVELOPMENT,
        "lean": "Cone.Main.cone_extension (ConeExtensionEstimates)",
        "fidelity": "not audited",
    },
    {
        "item": "(9.7) Nikodym maximal",
        "claim": "‖N_delta f‖_n <= C L(1/delta)^{2A} ‖f‖_n",
        "status": DEVELOPMENT,
        "lean": "LocalSmoothing.FurtherResults.nikodym_maximal (NikodymMaximalConjecture)",
        "fidelity": "WEAKER by its docstring: every positive ε loss instead of the log power; definition not read",
    },
    {
        "item": "Section 9.4, Nikodym dimension",
        "claim": "positive-measure Nikodym sets have full dimension",
        "status": DEVELOPMENT,
        "lean": "LocalSmoothing.FurtherResults.nikodym_dimension",
        "fidelity": "not audited",
    },
    {
        "item": "Section 9.4, quadratic curves",
        "claim": "minimum dimension n - rank B + rank B^2, attained",
        "status": DEVELOPMENT,
        "lean": "FurtherResults.quadratic_curve_dimension_infimum_attained, "
        "matrix_quadratic_curve_dimension_infimum_attained",
        "fidelity": "not audited",
    },
    {
        "item": "Theorem 10.1 (10.1)",
        "claim": "uniform Bochner-Riesz bounds, 1 <= p <= inf, alpha > delta(p)",
        "status": COMPARATOR,
        "lean": "bochner_riesz",
        "fidelity": "range EQUIVALENT (z3); Schwartz data in Lean",
    },
    {
        "item": "Theorem 10.1 (10.2)",
        "claim": "maximal Bochner-Riesz, 2 <= p < inf, alpha > s+(p)",
        "status": DEVELOPMENT,
        "lean": "BochnerRiesz.MainTheorem.bochnerRieszMaximalLp_of_localSmoothing, "
        "MaximalLp.localSmoothing_bochnerRiesz_Lp_full_maximal",
        "fidelity": "not audited",
    },
    {
        "item": "Theorem 10.1, convergence",
        "claim": "L^p convergence (p < inf) and a.e. convergence",
        "status": DEVELOPMENT,
        "lean": "BochnerRiesz.AEConvergence.localSmoothing_bochnerRiesz_Lp_ae_convergence",
        "fidelity": "not audited",
    },
    {
        "item": "Theorem 11.1",
        "claim": "Stein square function, 2 <= p < inf, alpha > max{1/2, n(1/2 - 1/p)}",
        "status": COMPARATOR,
        "lean": "stein_square",
        "fidelity": "range EQUIVALENT (z3, both paper forms); deriv junk branch open for human review",
    },
    {
        "item": "Corollary 12.1 (12.1)",
        "claim": "compact paraboloid extension",
        "status": PROSE,
        "lean": "-",
        "fidelity": "no statement located (no paraboloid or Schrödinger module in OAI/Analysis/Fourier)",
    },
    {
        "item": "Corollary 12.1 (12.2)",
        "claim": "critical Schrödinger estimate with [log(2 + N)]^{2/pc}",
        "status": PROSE,
        "lean": "-",
        "fidelity": "no statement located",
    },
    {
        "item": "Corollary 12.1 (12.3)",
        "claim": "mixed-norm Schrödinger local smoothing, s = d(1 - 2/p) - 2/r",
        "status": PROSE,
        "lean": "-",
        "fidelity": "no statement located",
    },
    {
        "item": "Theorem A.1",
        "claim": "periodic Dirichlet problem (proof input)",
        "status": UNCHECKED,
        "lean": "-",
        "fidelity": "proof-internal; not searched",
    },
    {
        "item": "Theorem B.1",
        "claim": "angular endpoint: log power 1/pc with angular regularity B > 1/2 + 1/p",
        "status": PROSE,
        "lean": "-",
        "fidelity": "no statement located",
    },
    {
        "item": "Theorem E.1",
        "claim": "curved characteristic sheets of symmetric systems",
        "status": UNCHECKED,
        "lean": "-",
        "fidelity": "not searched",
    },
]

COVERAGE_FILES_READ = [
    "lean/ComparatorChallenges/LocalSmoothing.lean",
    "lean/docs/079.md",
    "lean/OAI/Analysis/Fourier/LocalSmoothing/{Definitions,Main,FurtherResults,Implications,ResultsFromPackets,"
    "FromLogarithmic,Comparator}.lean",
    "lean/OAI/Analysis/Fourier/LocalSmoothing/Sharpness/{LogNecessity,PowerNecessity,Logarithmic}.lean",
    "lean/OAI/Analysis/Fourier/BochnerRiesz/{MainTheorem,MaximalLp,AEConvergence}.lean",
    "lean/OAI/Analysis/Fourier/{Cone/Main,Restriction/Main,Dispersion/Statements}.lean",
    "the full file list of the commit (for module names)",
]


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def case_report() -> Dict[str, Any]:
    ranges = []
    for spec in RANGE_SPECS + DEVELOPMENT_SPECS:
        result = compare_ranges(spec).to_dict()
        result["cross_check"] = cross_check(spec, {"n": CROSS_CHECK_N})
        result["scope"] = "comparator" if spec in RANGE_SPECS else "development"
        ranges.append(result)
    mutants = []
    for mutant in MUTANTS:
        result = compare_ranges(mutant_spec(mutant))
        mutants.append(
            {
                "base": mutant["base"],
                "label": mutant["label"],
                "lean": mutant["lean"],
                "expected": mutant["expected"],
                "relation": result.relation.value,
                "lean_only_witness": result.lean_only_witness,
                "paper_only_witness": result.paper_only_witness,
                "note": mutant.get("note", ""),
            }
        )
    return {
        "source": SOURCE,
        "ranges": ranges,
        "mutants": mutants,
        "lint": lint_report(),
        "coverage": COVERAGE,
        "coverage_files_read": COVERAGE_FILES_READ,
        "kernel_check": {
            "status": "NOT RUN",
            "reason": "Comparator needs landrun (Linux Landlock), which macOS lacks; a substitute build of the "
            "solution module on the Mac Studio was not started because the session's permission policy blocked "
            "running the downloaded project's build. No kernel check is reported.",
        },
    }
