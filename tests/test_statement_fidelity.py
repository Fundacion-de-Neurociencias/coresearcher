"""Tests for statement fidelity (python/discovery/statement_fidelity.py) and the Lean junk-value lint."""

import random
from fractions import Fraction

import pytest
import z3

from python.discovery import statement_fidelity as sf
from python.discovery.formal_hypothesis import Predicate, SolverUndecided
from python.discovery.lean_junk_lint import lint, parse_declarations, strip_comments
from python.discovery.statement_fidelity import Fidelity, Parameter, RangeSpec, compare_ranges, desugar

N = Parameter("n", integer=True, lower=2)
STEIN_PAPER = "alpha > 1/2 + max(0, (n - 1)/2 - n/p)"
STEIN_LEAN = "alpha > max(1/2, n*(1/2 - 1/p))"


def _stein(lean: str) -> RangeSpec:
    return RangeSpec("stein", [N, Parameter("p", lower=2), Parameter("alpha")], paper=STEIN_PAPER, lean=lean)


def _holds(expression: str, names, state) -> bool:
    """Exact truth at a state. Predicate evaluation divides integer literals in floats, so a witness exactly on a
    boundary (alpha == max(...)) could be misjudged; z3 substitution keeps every value rational."""
    encoder = sf._Encoder([Parameter(name) for name in names])
    formula = encoder.formula(expression)
    values = [(encoder.table.symbols[k], z3.RealVal(str(Fraction(v)))) for k, v in state.items()]
    return z3.is_true(z3.simplify(z3.substitute(formula, *values)))


# ---------------------------------------------------------------------------
# Range equivalence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expression",
    ["x > max(0, y - 1)", "min(x, y, 2) <= 1", "abs(x - y) < 1 + max(x, 0)", "not (max(x, y) == min(x, y))"],
)
def test_desugar_is_exact(expression):
    rng = random.Random(7)
    for _ in range(200):
        state = {"x": Fraction(rng.randint(-8, 8), 2), "y": Fraction(rng.randint(-8, 8), 2)}
        expected = eval(expression, {"max": max, "min": min, "abs": abs}, dict(state))  # Test-owned literal strings.
        assert Predicate(desugar(expression), ["x", "y"]).evaluate(state) == expected, (expression, state)


def test_desugar_rejects_other_calls():
    with pytest.raises(ValueError):
        desugar("x > log(y)")


def test_brief_example_is_equivalent_for_every_dimension():
    result = compare_ranges(_stein(STEIN_LEAN))
    assert result.relation == Fidelity.EQUIVALENT
    assert result.method == {"lean_minus_paper": "exact", "paper_minus_lean": "exact"}
    assert result.paper_nonempty and result.lean_nonempty
    assert result.division_hazards == []


def test_non_strict_inequality_is_stronger_with_a_checkable_witness():
    lean = "alpha >= max(1/2, n*(1/2 - 1/p))"
    result = compare_ranges(_stein(lean))
    assert result.relation == Fidelity.STRONGER
    witness = result.lean_only_witness
    names = ["n", "p", "alpha"]
    assert isinstance(witness["n"], int) and witness["n"] >= 2
    assert _holds(lean, names, witness) and not _holds(STEIN_PAPER, names, witness)


def test_weaker_and_incomparable():
    params = [Parameter("x")]
    assert compare_ranges(RangeSpec("t", params, paper="x > 0", lean="x > 1")).relation == Fidelity.WEAKER
    assert compare_ranges(RangeSpec("t", params, paper="x > 0", lean="x < 1")).relation == Fidelity.INCOMPARABLE


def test_integer_parameters_are_integers():
    # 2n != 5 fails only at n = 5/2, which is not an integer.
    spec = RangeSpec("t", [N], paper="True", lean="2*n != 5")
    assert compare_ranges(spec).relation == Fidelity.EQUIVALENT
    real = RangeSpec("t", [Parameter("n", lower=2)], paper="True", lean="2*n != 5")
    assert compare_ranges(real).relation == Fidelity.WEAKER


def test_reachable_division_by_zero_is_undecided():
    params = [Parameter("p", lower=2)]
    risky = compare_ranges(RangeSpec("t", params, paper="p > 2", lean="1/(p - 2) > 0"))
    assert risky.relation == Fidelity.UNDECIDED
    assert risky.division_hazards == ["lean: p - 2"]
    guarded = compare_ranges(RangeSpec("t", params, paper="p > 2", lean="p > 2 and 1/(p - 2) > 0"))
    assert guarded.division_hazards == []
    assert guarded.relation == Fidelity.EQUIVALENT


def test_solver_give_up_is_reported_undecided(monkeypatch):
    def give_up(*formulas):
        raise SolverUndecided("timeout")

    monkeypatch.setattr(sf.formal_smt, "satisfiable", give_up)
    result = compare_ranges(_stein(STEIN_LEAN))
    assert result.relation == Fidelity.UNDECIDED
    assert result.method == {"lean_minus_paper": "undecided", "paper_minus_lean": "undecided"}
    assert result.undecided_reasons


def test_real_relaxation_settles_what_the_integer_query_cannot(monkeypatch):
    original = sf.formal_smt.satisfiable

    def no_integers(*formulas):
        if any("ToReal(n)" in str(f) or "Int" in str(f.sort()) for f in formulas):
            raise SolverUndecided("mixed integer arithmetic")
        return original(*formulas)

    monkeypatch.setattr(sf.formal_smt, "satisfiable", no_integers)
    result = compare_ranges(_stein(STEIN_LEAN))
    assert result.relation == Fidelity.EQUIVALENT
    assert result.method == {"lean_minus_paper": "real relaxation", "paper_minus_lean": "real relaxation"}
    # A real witness with fractional n proves nothing about integers: undecided, never a false STRONGER.
    spec = RangeSpec("t", [N], paper="True", lean="2*n != 5")
    assert compare_ranges(spec).relation == Fidelity.UNDECIDED


def test_cross_check_through_hypothesis_evaluator_compare():
    assert sf.cross_check(_stein(STEIN_LEAN), {"n": range(2, 6)})["relation"] == "EQUIVALENT"
    assert sf.cross_check(_stein("alpha >= max(1/2, n*(1/2 - 1/p))"), {"n": range(2, 6)})["relation"] == "STRONGER"


def test_quantity_disagreement_is_found():
    spec = RangeSpec(
        "t",
        [N, Parameter("p", lower=2)],
        paper="True",
        lean="True",
        quantities=[sf.Quantity("order", paper="max(0, (n - 1)/2 - n/p)", lean="(n - 1)/2 - n/p")],
    )
    check = compare_ranges(spec).quantities["order"]
    assert check["agreement"] == "DIFFERS"
    assert check["witness"]["n"] >= 2


# ---------------------------------------------------------------------------
# Junk-value lint
# ---------------------------------------------------------------------------

HEADER = "import Mathlib\nopen MeasureTheory\nopen scoped ENNReal\nnoncomputable section\n"


def _findings(body: str):
    return lint(HEADER + body).findings


def _one(findings, kind):
    matches = [f for f in findings if f.kind == kind]
    assert len(matches) == 1, [(f.kind, f.operand) for f in findings]
    return matches[0]


def test_comments_are_blanked_and_lines_kept():
    source = "/- ∫ deriv\n nested /- ⨆ -/ -/\ndef f := 1 -- / 0\n"
    stripped = strip_comments(source)
    assert stripped.count("\n") == source.count("\n")
    assert "deriv" not in stripped and "⨆" not in stripped and "/ 0" not in stripped
    assert [d.name for d in parse_declarations(source)] == ["f"]


def test_deriv_needs_a_differentiability_premise():
    open_ = _one(_findings("theorem t : ∀ g : ℝ → ℝ, deriv g 0 = 0 := by\n  sorry\n"), "DERIV")
    assert open_.status == "OPEN"
    closed = _one(_findings("theorem t : ∀ g : ℝ → ℝ, Differentiable ℝ g → deriv g 0 = 0 := by\n  sorry\n"), "DERIV")
    assert closed.status == "DISCHARGED"


def test_division_needs_the_divisor_bounded_away_from_zero():
    open_ = _one(_findings("theorem t : ∀ p : ℝ, 1 / p ≤ 1 := by\n  sorry\n"), "DIVISION")
    assert (open_.status, open_.operand) == ("OPEN", "p")
    closed = _one(_findings("theorem t : ∀ p : ℝ, 2 ≤ p → 1 / p ≤ 1 := by\n  sorry\n"), "DIVISION")
    assert (closed.status, closed.discharged_by) == ("DISCHARGED", "premise 2 ≤ p")


def test_to_real_needs_a_guard_and_supremum_needs_a_complete_lattice():
    body = (
        "def c (a : ℝ≥0∞) : ℝ := a.toReal\n"
        "def d (a : ℝ≥0∞) : ℝ := if a = ∞ then 1 else a.toReal\n"
        "def s (f : ℕ → ℝ) : ℝ := ⨆ k, f k\n"
        "def e (f : ℕ → ℝ≥0∞) : ℝ≥0∞ := ⨆ k, f k\n"
        "theorem t : ∀ a : ℝ≥0∞, ∀ f g, c a + d a + s f ≤ (e g).toReal := by\n  sorry\n"
    )
    findings = {(f.declaration, f.kind): f for f in _findings(body)}
    assert findings[("c", "TO_REAL")].status == "OPEN"
    assert findings[("d", "TO_REAL")].status == "DISCHARGED"
    assert findings[("s", "SUPREMUM")].status == "OPEN"
    assert findings[("e", "SUPREMUM")].status == "DISCHARGED"


def test_bound_by_an_infinite_norm_needs_memlp():
    open_ = _one(
        _findings("theorem t : ∀ f g : ℝ → ℝ, eLpNorm g 2 volume ≤ 3 * eLpNorm f 2 volume := by\n  sorry\n"),
        "INFINITE_RHS",
    )
    assert (open_.status, open_.operand) == ("OPEN", "f")
    closed = _one(
        _findings(
            "theorem t : ∀ f g : ℝ → ℝ, MemLp f 2 → eLpNorm g 2 volume ≤ 3 * eLpNorm f 2 volume := by\n  sorry\n"
        ),
        "INFINITE_RHS",
    )
    assert closed.status == "DISCHARGED"


def test_natural_powers_are_not_rpow():
    findings = _findings(
        "def k {n : ℕ} (x : ℝ) : ℝ := x ^ n + x ^ 2\ntheorem t : ∀ x : ℝ, k (n := 3) x = x := by\n  sorry\n"
    )
    assert not [f for f in findings if f.kind == "RPOW"]
    real = _findings("theorem t : ∀ x s : ℝ, x ^ s = 1 := by\n  sorry\n")
    assert _one(real, "RPOW").status == "OPEN"


def test_definitions_are_followed_transitively():
    body = (
        "def inner (f : ℝ → ℝ) : ℝ := ∫ x, f x\n"
        "def outer (f : ℝ → ℝ) : ℝ := inner f + 1\n"
        "theorem t : ∀ f : ℝ → ℝ, outer f = 1 := by\n  sorry\n"
    )
    finding = _one(_findings(body), "BOCHNER_INTEGRAL")
    assert (finding.theorem, finding.declaration, finding.status) == ("t", "inner", "OPEN")
