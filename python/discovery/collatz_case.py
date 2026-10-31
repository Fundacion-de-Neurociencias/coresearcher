"""
python/discovery/collatz_case.py - What is mechanically checkable about the Collatz (3x+1) conjecture.

The conjecture is open. This case does not attempt a proof and does not claim progress on it. It records:

1. a DAG of the known partial results, with the two open gaps (no divergent orbit, no nontrivial cycle) as open
   nodes, published results as imported leaves, and acyclicity checked by `ProofDependencyDAG`;
2. exact checks of the elementary facts those results rest on: Terras's affine form and parity-vector bijection, the
   measure-preserving 2-adic lift, the cycle equation and product identity, and the continued-fraction lower bound on
   the size of a nontrivial cycle given a computational verification bound. Each check is VERIFIED, REFUTED or
   NOT_ENCODABLE, with its scope (for example "every residue mod 2^k for k <= 14").

Throughout, T is the accelerated map T(n) = n/2 for even n and (3n + 1)/2 for odd n.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, List, Tuple

import mpmath
import sympy as sp

from python.discovery.physical_theorem_court import DeductionRule, ProofDependencyDAG, ProofLemmaNode

VERIFIED = "VERIFIED"
REFUTED = "REFUTED"
NOT_ENCODABLE = "NOT_ENCODABLE"

# Published computational verification bound (imported, not re-run): every n < 2^68 reaches 1.
# D. Barina, "Convergence verification of the Collatz problem", J. Supercomputing 77 (2021) 2681-2688.
VERIFIED_UP_TO_EXPONENT = 68
# Published cross-check: with every n < 2^40 verified, a nontrivial cycle has at least 17,087,915 steps of T.
# S. Eliahou, "The 3x+1 problem: new lower bounds on nontrivial cycle lengths", Discrete Math. 118 (1993) 45-56.
ELIAHOU_1993 = {"exponent": 40, "min_cycle_length": 17087915}
# Our own exhaustive convergence check (small, re-run on every report).
OWN_CHECK_EXPONENT = 20


def T(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


# ---------------------------------------------------------------------------
# Part 1: DAG of partial results
# ---------------------------------------------------------------------------

EXTERNAL: Dict[str, Dict[str, str]] = {
    "Terras1976": {
        "what": "parity vectors of length k are in bijection with residues mod 2^k; stopping time "
        "is finite for a set of density 1",
        "use": "input",
    },
    "Everett1977": {"what": "almost every n has an iterate below n", "use": "input"},
    "Lagarias1985": {
        "what": "T extends to the 2-adic integers, preserves Haar measure, and is conjugate to the " "shift",
        "use": "input",
    },
    "Steiner1977": {"what": "the only cycle with one block of odd steps is the trivial one", "use": "input"},
    "SimonsDeWeger2005": {"what": "no nontrivial m-cycle (m blocks of odd steps) for m <= 68", "use": "input"},
    "Eliahou1993": {
        "what": "lower bound on cycle length from a verification bound (17,087,915 at 2^40)",
        "use": "cross-check",
    },
    "Barina2021": {"what": "every n < 2^68 reaches 1 (computation)", "use": "input"},
    "KrasikovLagarias2003": {"what": "at least x^0.84 integers n <= x reach 1, for large x", "use": "input"},
    "Tao2022": {"what": "almost all orbits (logarithmic density) attain almost bounded values", "use": "input"},
    "Conway1972": {"what": "generalized Collatz problems are undecidable", "use": "meta"},
}

# id -> (title, status, internal premises, imports). Status is "checked here", "imported" or "OPEN".
NODES: Dict[str, Tuple[str, str, List[str], List[str]]] = {
    "AffineForm": ("T^k(r + 2^k t) = T^k(r) + 3^m t for every t", "checked here", [], ["Terras1976"]),
    "ParityBijection": (
        "n mod 2^k determines and is determined by the first k parities",
        "checked here",
        ["AffineForm"],
        ["Terras1976"],
    ),
    "TwoAdicLift": (
        "T preserves Haar measure on the 2-adic integers (cylinder level)",
        "checked here",
        ["ParityBijection"],
        ["Lagarias1985"],
    ),
    "Drift": ("mean log-factor per step is log(3/4)/2 < 0", "checked here", [], []),
    "DensityCore": (
        "fraction of parity vectors with 3^m < 2^k tends to 1",
        "checked here",
        ["ParityBijection", "Drift"],
        [],
    ),
    "StoppingDensity1": (
        "almost every n has finite stopping time",
        "imported",
        ["AffineForm", "DensityCore"],
        ["Terras1976", "Everett1977"],
    ),
    "AlmostBounded": ("almost all orbits attain almost bounded values", "imported", ["StoppingDensity1"], ["Tao2022"]),
    "CountReaching1": ("#{n <= x reaching 1} >= x^0.84", "imported", [], ["KrasikovLagarias2003"]),
    "CycleEquation": (
        "a cycle with k steps and m odd steps has n (2^k - 3^m) = c > 0",
        "checked here",
        ["AffineForm"],
        [],
    ),
    "ProductIdentity": ("2^k / 3^m = prod over odd cycle elements of (1 + 1/(3x))", "checked here", [], []),
    "OwnVerification": ("every n < 2^20 reaches 1 (re-run here)", "checked here", [], []),
    "CycleSizeBound": (
        "a nontrivial cycle has at least m_min odd steps, given a verification bound",
        "checked here",
        ["CycleEquation", "ProductIdentity"],
        ["Barina2021", "Eliahou1993"],
    ),
    "OneCycles": ("no nontrivial 1-cycles", "imported", ["CycleEquation"], ["Steiner1977"]),
    "FewBlockCycles": ("no nontrivial m-cycles, m <= 68", "imported", ["CycleEquation"], ["SimonsDeWeger2005"]),
    "NoNontrivialCycle": ("GAP: no nontrivial cycle", "OPEN", ["CycleSizeBound", "OneCycles", "FewBlockCycles"], []),
    "NoDivergentOrbit": ("GAP: no orbit tends to infinity", "OPEN", ["AlmostBounded", "CountReaching1"], []),
    "Collatz": (
        "every orbit reaches 1",
        "OPEN",
        ["NoNontrivialCycle", "NoDivergentOrbit", "OwnVerification"],
        ["Conway1972"],
    ),
}


def build_dag() -> ProofDependencyDAG:
    dag = ProofDependencyDAG(theorem_id="Collatz", root_lemma_id="Collatz")
    for key, info in EXTERNAL.items():
        dag.add_lemma(
            ProofLemmaNode(
                f"EXT:{key}",
                info["what"],
                [],
                DeductionRule.AXIOMATIC_ASSERTION,
                info["what"],
                "",
                is_axiom_without_proof=True,
            )
        )
    for key, (title, status, premises, imports) in NODES.items():
        rule = DeductionRule.AXIOMATIC_ASSERTION if status == "OPEN" else DeductionRule.MODUS_PONENS
        dag.add_lemma(
            ProofLemmaNode(
                key,
                title,
                premises + [f"EXT:{e}" for e in imports],
                rule,
                title,
                "",
                is_axiom_without_proof=status == "OPEN",
            )
        )
    return dag


def dag_report() -> Dict[str, Any]:
    audit = build_dag().verify_dag_acyclicity_and_completeness()
    return {
        "is_acyclic": audit["is_acyclic"],
        "missing_premises": audit["missing_premises"],
        "open_nodes": [k for k, v in NODES.items() if v[1] == "OPEN"],
        "nodes": [
            {"id": k, "title": v[0], "status": v[1], "premises": v[2], "imports": v[3]} for k, v in NODES.items()
        ],
        "external": EXTERNAL,
    }


# ---------------------------------------------------------------------------
# Part 2: checks
# ---------------------------------------------------------------------------


@dataclass
class Check:
    id: str
    claim: str
    scope: str
    status: str = ""
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    values: Dict[str, Any] = field(default_factory=dict)


def _symbolic_iterate(r: int, k: int) -> Tuple[int, int, List[int]]:
    """Iterate T on r + 2^k t for symbolic integer t: the state is a + b t with b even while parities depend on a."""
    a, b, parities = r, 2**k, []
    for _ in range(k):
        assert b % 2 == 0  # so the parity of a + b t is the parity of a, for every t
        par = a % 2
        parities.append(par)
        a, b = ((3 * a + 1) // 2, 3 * b // 2) if par else (a // 2, b // 2)
    return a, b, parities


def check_affine_form(c: Check) -> None:
    ok = True
    for k in range(1, 15):
        for r in range(2**k):
            a, b, parities = _symbolic_iterate(r, k)
            ok &= b == 3 ** sum(parities) and a == _iterate(r, k)
    c.assertions.append(
        {"assertion": "T^k(r + 2^k t) = T^k(r) + 3^m t, all r < 2^k, k <= 14, every integer t", "holds": ok}
    )
    t = sp.Symbol("t", integer=True)
    a, b, _ = _symbolic_iterate(5, 6)
    c.values["example_r5_k6"] = str(a + b * t)


def _iterate(n: int, k: int) -> int:
    for _ in range(k):
        n = T(n)
    return n


def check_parity_bijection(c: Check) -> None:
    ok = True
    for k in range(1, 17):
        vectors = {tuple(_symbolic_iterate(r, k)[2]) for r in range(2**k)}
        ok &= len(vectors) == 2**k
    c.assertions.append(
        {"assertion": "r mod 2^k -> first k parities is a bijection onto {0,1}^k, k <= 16", "holds": ok}
    )


def check_two_adic_lift(c: Check) -> None:
    ok = True
    for k in range(1, 15):
        counts = [0] * (2**k)
        for s in range(2 ** (k + 1)):
            counts[T(s) % 2**k] += 1
        ok &= all(x == 2 for x in counts)
    c.assertions.append(
        {
            "assertion": "each class mod 2^k has exactly 2 preimage classes mod 2^(k+1) "
            "(Haar measure preserved on cylinders), k <= 14",
            "holds": ok,
        }
    )
    # Not an assertion: N is a Haar-null subset of Z_2 (the integers below 2^k fill a fraction 2^-k of Z/2^(2k)),
    # which is why the clean 2-adic picture says nothing about natural numbers.
    c.values["note"] = "N has Haar measure 0 in Z_2"


def check_drift(c: Check) -> None:
    drift = sp.Rational(1, 2) * sp.log(sp.Rational(1, 2)) + sp.Rational(1, 2) * sp.log(sp.Rational(3, 2))
    c.assertions.append(
        {
            "assertion": "E[log factor] = log(1/2)/2 + log(3/2)/2 = log(3/4)/2",
            "holds": sp.simplify(drift - sp.log(sp.Rational(3, 4)) / 2) == 0,
        }
    )
    c.assertions.append({"assertion": "log(3/4)/2 < 0", "holds": bool(sp.log(sp.Rational(3, 4)) < 0)})


def check_density_core(c: Check) -> None:
    alpha = math.log2(3)
    values = {}
    for k in (25, 50, 100, 200, 400):
        good = sum(math.comb(k, m) for m in range(k + 1) if 3**m < 2**k)  # exact integer test
        values[k] = float(Fraction(good, 2**k))
    c.values["fraction_with_3^m<2^k"] = values
    c.assertions.append(
        {
            "assertion": "fraction of length-k parity vectors with 3^m < 2^k exceeds 0.999 at "
            "k = 400 (exact binomial sum)",
            "holds": values[400] > 0.999,
        }
    )
    c.assertions.append(
        {"assertion": "threshold m < k / log2 3 has slope 1/log2 3 > 1/2, the binomial mean", "holds": 1 / alpha > 0.5}
    )


def check_cycle_equation(c: Check) -> None:
    ok = True
    for n in range(1, 3000):
        for k in (1, 5, 17, 40):
            # 2^k T^k(n) = 3^m n + c with c = sum_j 3^(m-1-j) 2^(s_j), s_j = steps before the j-th odd step
            x, odd_steps = n, []
            for step in range(k):
                if x % 2:
                    odd_steps.append(step)
                x = T(x)
            m = len(odd_steps)
            c_val = sum(3 ** (m - 1 - j) * 2**s for j, s in enumerate(odd_steps))
            ok &= x * 2**k == 3**m * n + c_val
    c.assertions.append(
        {"assertion": "2^k T^k(n) = 3^m n + sum_j 3^(m-1-j) 2^(s_j), n < 3000, k in {1,5,17,40}", "holds": ok}
    )
    c.assertions.append(
        {"assertion": "hence a cycle (T^k(n) = n) has n (2^k - 3^m) = c > 0, so 2^k > 3^m", "holds": ok}
    )
    c.assertions.append(
        {
            "assertion": "trivial cycle 1 -> 2 -> 1: k = 2, m = 1, c = 1, n = 1",
            "holds": T(1) == 2 and T(2) == 1 and 1 * (2**2 - 3) == 1,
        }
    )


def check_product_identity(c: Check) -> None:
    x = sp.Symbol("x", positive=True)
    c.assertions.append(
        {
            "assertion": "odd step: T(x)/x = (3/2)(1 + 1/(3x))",
            "holds": sp.simplify((3 * x + 1) / (2 * x) - sp.Rational(3, 2) * (1 + 1 / (3 * x))) == 0,
        }
    )
    c.assertions.append(
        {"assertion": "trivial cycle: 2^2/3^1 = 1 + 1/3", "holds": Fraction(4, 3) == 1 + Fraction(1, 3)}
    )
    # Taking log2 of 1 < prod (1 + 1/(3 x_i)) <= (1 + 1/(3N))^m; checked on every cycle of T we can enumerate
    # (only the trivial one, where it is an equality with N = 1) and symbolically for the bound's monotonicity.
    k, m, N = 2, 1, 1
    gap = sp.Integer(k) - m * sp.log(3, 2)
    c.assertions.append(
        {
            "assertion": "trivial cycle: 0 < k - m log2 3 = m log2(1 + 1/(3N)) with k = 2, m = 1, N = 1",
            "holds": bool(gap > 0) and sp.simplify(gap - m * sp.log(1 + sp.Rational(1, 3 * N), 2)) == 0,
        }
    )
    Ns = sp.Symbol("N", positive=True)
    c.assertions.append(
        {
            "assertion": "log2(1 + 1/(3N)) is decreasing in N, so N = smallest cycle element gives the bound",
            "holds": bool(sp.simplify(sp.diff(sp.log(1 + 1 / (3 * Ns), 2), Ns)).is_negative),
        }
    )


def check_own_verification(c: Check) -> None:
    limit = 2**OWN_CHECK_EXPONENT
    reached = bytearray(limit)
    reached[1] = 1
    ok = True
    for n in range(2, limit):
        x, path = n, []
        while x >= n:  # an orbit that drops below n reaches 1 by induction
            path.append(x)
            x = T(x)
            if len(path) > 10000:
                ok = False
                break
        ok &= x < n and reached[x] == 1
        reached[n] = 1
    c.assertions.append({"assertion": f"every 1 <= n < 2^{OWN_CHECK_EXPONENT} reaches 1 (induction on n)", "holds": ok})


def _simplest_fraction(a: Fraction, b: Fraction) -> Fraction:
    """Fraction with the smallest denominator in the open interval (a, b), 0 < a < b."""
    fl = math.floor(a)
    if fl + 1 < b:
        return Fraction(fl + 1)
    return fl + 1 / _simplest_fraction(1 / (b - fl), 1 / (a - fl))


def _to_fraction(x: mpmath.mpf) -> Fraction:
    man, exp = mpmath.mpf(x).man_exp
    return Fraction(int(man)) * Fraction(2) ** exp


def min_cycle_size(exponent: int, digits: int = 120) -> Dict[str, int]:
    """Smallest (m, k) with k/m in (log2 3, log2 3 + log2(1 + 1/(3 * 2^exponent))): a nontrivial cycle needs at least
    m odd steps and k steps of T once every n < 2^exponent is known to reach 1. Endpoints are moved inward by
    10^-(digits - 10), which can only drop fractions with denominators far above the answer."""
    with mpmath.workdps(digits):
        alpha = mpmath.log(3, 2)
        eps = mpmath.log(1 + mpmath.mpf(1) / (3 * mpmath.mpf(2) ** exponent), 2)
        nudge = mpmath.mpf(10) ** -(digits - 10)
        q = _simplest_fraction(_to_fraction(alpha + nudge), _to_fraction(alpha + eps - nudge))
        inside = alpha < mpmath.mpf(q.numerator) / q.denominator < alpha + eps
    return {"m": q.denominator, "k": q.numerator, "inside": bool(inside)}


def check_cycle_size_bound(c: Check) -> None:
    eli = min_cycle_size(ELIAHOU_1993["exponent"])
    c.values["at_2^40"] = eli
    c.assertions.append(
        {
            "assertion": "reproduces Eliahou (1993): at 2^40 the minimal cycle length is 17,087,915",
            "holds": eli["k"] == ELIAHOU_1993["min_cycle_length"] and eli["inside"],
        }
    )
    lo, hi = min_cycle_size(VERIFIED_UP_TO_EXPONENT), min_cycle_size(VERIFIED_UP_TO_EXPONENT, digits=200)
    c.values[f"at_2^{VERIFIED_UP_TO_EXPONENT}"] = lo
    c.assertions.append(
        {
            "assertion": "the answer is stable between 120 and 200 digits of precision",
            "holds": lo == hi and lo["inside"],
        }
    )


CHECKS: List[Tuple[Check, Callable[[Check], None]]] = [
    (
        Check("terras.affine", "T^k(r + 2^k t) = T^k(r) + 3^m t", "every r < 2^k, k <= 14, symbolic t"),
        check_affine_form,
    ),
    (Check("terras.bijection", "parity vectors <-> residues mod 2^k", "exhaustive, k <= 16"), check_parity_bijection),
    (
        Check("lift.haar", "the 2-adic extension preserves Haar measure", "cylinder sets mod 2^(k+1), k <= 14"),
        check_two_adic_lift,
    ),
    (Check("heuristic.drift", "negative mean drift of log n", "exact"), check_drift),
    (Check("terras.density_core", "most parity vectors contract", "exact binomial sums, k <= 400"), check_density_core),
    (
        Check("cycle.equation", "the cycle equation n(2^k - 3^m) = c", "n < 3000, four values of k"),
        check_cycle_equation,
    ),
    (Check("cycle.product", "2^k/3^m = prod (1 + 1/(3x))", "symbolic step identity"), check_product_identity),
    (
        Check("verification.own", f"all n < 2^{OWN_CHECK_EXPONENT} reach 1", "exhaustive, re-run"),
        check_own_verification,
    ),
    (
        Check(
            "cycle.size_bound",
            "minimal size of a nontrivial cycle from a verification bound",
            f"exact continued fractions; conditional on the imported bound 2^{VERIFIED_UP_TO_EXPONENT}",
        ),
        check_cycle_size_bound,
    ),
]

NOT_ENCODED = [
    Check("gap.cycles", "no nontrivial cycle exists", "open problem", NOT_ENCODABLE),
    Check("gap.divergence", "no orbit diverges", "open problem", NOT_ENCODABLE),
    Check("tao.almost_bounded", "Tao's almost-all theorem", "analytic; imported, not re-proved", NOT_ENCODABLE),
]


def run_checks() -> List[Dict[str, Any]]:
    out = []
    for template, fn in CHECKS:
        check = Check(template.id, template.claim, template.scope)
        fn(check)
        check.status = VERIFIED if check.assertions and all(a["holds"] for a in check.assertions) else REFUTED
        out.append(asdict(check))
    out.extend(asdict(c) for c in NOT_ENCODED)
    return out


def case_report() -> Dict[str, Any]:
    checks = run_checks()
    return {
        "case": "Collatz: what is mechanically checkable",
        "claim_status": "OPEN: no proof is claimed",
        "dag": dag_report(),
        "checks": checks,
        "negative_controls": negative_controls(),
        "summary": {s: sum(1 for c in checks if c["status"] == s) for s in (VERIFIED, REFUTED, NOT_ENCODABLE)},
    }


# ---------------------------------------------------------------------------
# Negative controls: the same procedures must detect failure where failure is real.
# ---------------------------------------------------------------------------


def _t_minus(n: int) -> int:
    """The 3x - 1 variant, which is known to have nontrivial cycles."""
    return n // 2 if n % 2 == 0 else (3 * n - 1) // 2


def negative_controls() -> List[Dict[str, Any]]:
    cycle, x = [5], _t_minus(5)
    while x != 5 and len(cycle) < 50:
        cycle.append(x)
        x = _t_minus(x)
    # A descent check like verification.own must fail on the 3x - 1 map: 5 never drops below 5.
    y, steps = 5, 0
    while y >= 5 and steps < 1000:
        y, steps = _t_minus(y), steps + 1
    wrong = min_cycle_size(ELIAHOU_1993["exponent"] - 1)
    return [
        {"label": "3x-1 map: 5 -> 7 -> 10 -> 5 is a nontrivial cycle", "detected": x == 5 and cycle == [5, 7, 10]},
        {"label": "3x-1 map: the descent check does not certify n = 5", "detected": y >= 5},
        {
            "label": "verification bound 2^39 does not reproduce Eliahou's 17,087,915",
            "detected": wrong["k"] != ELIAHOU_1993["min_cycle_length"],
        },
    ]
