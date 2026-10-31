"""
python/discovery/local_smoothing_anatomy.py - Proof anatomy of OpenAI's "Local smoothing for the Euclidean wave
equation" (October 25, 2026): lemma dependency DAG and symbolic checks of the elementary identities it hinges on.

Companion to the statement-fidelity case (ADR-DISCOVERY-070, `local_smoothing_case`). Scope is formal and
mathematical soundness only: which result rests on which, and whether the closed-form identities in the paper hold.
It does not judge credit, novelty or any announcement.

1. DAG: every numbered result of the paper with its internal premises and the external results it imports. External
   results are leaves; they are recorded, not checked. Acyclicity and completeness are decided by the existing
   `ProofDependencyDAG` of `physical_theorem_court`, and each node is joined with the ADR-070 coverage map.
2. Checks: SymPy / z3 checks of exponent bookkeeping and of the finite-dimensional identities. Each check is
   VERIFIED (every assertion in it holds), REFUTED (one fails; the failing assertion is reported) or NOT_ENCODABLE
   (the claim needs analysis this module does not encode). The `scope` field says exactly what was encoded; a check
   in a real-symmetric model does not verify the quaternionic statement.

Sources are pinned to one commit of github.com/openai/math and were read as data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any, Callable, Dict, List, Tuple

import sympy as sp
import z3

from python.discovery.local_smoothing_case import COVERAGE
from python.discovery.local_smoothing_case import SOURCE as FIDELITY_SOURCE
from python.discovery.physical_theorem_court import DeductionRule, ProofDependencyDAG, ProofLemmaNode

COMMIT = FIDELITY_SOURCE["commit"]

SOURCES: List[Dict[str, Any]] = [
    {
        "role": "target",
        "title": "Local smoothing for the Euclidean wave equation (October 25, 2026)",
        "path": "preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026/paper.pdf",
        "pages": 59,
        "sha256": "9ca156c552f2d940528f7131716326ef0d67a5829e723e1d294d74560c8636ff",
    },
    {
        "role": "precursor",
        "title": "Critical local smoothing for the three-dimensional wave equation (September 24, 2026)",
        "path": "preprints/Critical-local-smoothing-for-the-three-dimensional-wave-equation-September-24-2026/paper.pdf",
        "pages": 165,
        "sha256": "79299093c07ea305c5d094e58ab10d76cc299624b7af6c7e4a1d459435f3b614",
    },
    {
        "role": "precursor",
        "title": "Elliptic capacity propagation and Fourier restriction to the sphere (September 24, 2026)",
        "path": "preprints/Elliptic-capacity-propagation-and-Fourier-restriction-to-the-sphere-September-24-2026/"
        "Elliptic-capacity-propagation-and-Fourier-restriction-to-the-sphere-September-24-2026.pdf",
        "pages": 103,
        "sha256": "669efdbef915014402795e07bfbcb958ae534b6910f05a8737a6fce0c216d394",
    },
    {
        "role": "reasoning summary (family 087)",
        "title": "Symmetric and general Mahler conjectures",
        "path": "reasoning_traces/symmetric-and-general-mahler-conjectures.pdf",
        "sha256": "933c27e3af898878d897adda58bdc5693bbf4a4eaeec37802daedbdb4d0f89f3",
    },
    {
        "role": "reasoning summary (family 362)",
        "title": "The three-dimensional relativistic Vlasov-Maxwell system",
        "path": "reasoning_traces/relativistic-vlasov-maxwell.pdf",
        "sha256": "fbb80877b643c266a65f304b4db652ff8489bf7374266eadf60ea85c9d3a63a0",
    },
    {
        "role": "process statement",
        "title": "README.md",
        "path": "README.md",
        "sha256": "6cb7f0e387b67c051227c6ba27aca87ee82d9dd2530b6452b86b8681a2e2743a",
    },
    {
        "role": "process statement",
        "title": "history.md",
        "path": "history.md",
        "sha256": "ac688a38eb9afdb1f3c339c1df251cdb1aa7d8f18067b3ce5d668a96d690f5fb",
    },
]

# ---------------------------------------------------------------------------
# Part 1: lemma dependency DAG
# ---------------------------------------------------------------------------

# External results, keyed by a short id; "ref" is the paper's bibliography number. "use" says how the paper uses it:
# "input" means a step of the proof relies on it; "model" means the paper names it as the template or precedent for a
# construction it then carries out itself; "reproved" means the paper cites it and gives its own proof.
EXTERNAL: Dict[str, Dict[str, str]] = {
    "Friedrichs1954": {"ref": "25", "what": "bilinear flux of a symmetric hyperbolic system", "use": "input"},
    "BaouendiTreves1982": {"ref": "6", "what": "complex vector fields of tube coordinates", "use": "input"},
    "Kaiser1990": {"ref": "41", "what": "conserved current at imaginary displacement (Klein-Gordon)", "use": "model"},
    "Husimi1940": {"ref": "39", "what": "Husimi density (interpretation of the null component)", "use": "model"},
    "Serre2018": {
        "ref": "69",
        "what": "compensated integrability for positive divergence-free tensors",
        "use": "model",
    },
    "Serre2019": {"ref": "70", "what": "the wave stress tensor need not be positive for n >= 2", "use": "model"},
    "Serre2023": {"ref": "71", "what": "Schur complement isolating a diagonal entry", "use": "model"},
    "Alesker2003a": {"ref": "2", "what": "Moore determinant conventions (Thms 1.1.8-1.1.9)", "use": "input"},
    "Alesker2003b": {"ref": "3", "what": "quaternionic Dirichlet problem on balls; Levi form", "use": "model"},
    "Alesker2013": {"ref": "4", "what": "divergence-free cofactor of a quaternionic Hessian", "use": "reproved"},
    "Zhu2016": {"ref": "81", "what": "quaternionic Dirichlet problem with subsolution", "use": "model"},
    "CNS1985": {"ref": "15", "what": "Caffarelli-Nirenberg-Spruck boundary C2 estimates", "use": "input"},
    "GilbargTrudinger": {"ref": "31", "what": "Schauder theory; Thms 17.14, 17.26'", "use": "input"},
    "EvansKrylov": {"ref": "22,47,48", "what": "Evans-Krylov C^{2,alpha} estimates", "use": "input"},
    "Aubin1984": {"ref": "5", "what": "Aubin J-functional", "use": "model"},
    "Mabuchi1986": {"ref": "52", "what": "Mabuchi energy L (segment integral)", "use": "model"},
    "BBGZ2013": {"ref": "10", "what": "variational approach to complex Monge-Ampere", "use": "model"},
    "Ahag2009": {"ref": "1", "what": "Laplacian of the slice energy on a product domain", "use": "model"},
    "Wan2020": {"ref": "76", "what": "variational principle, quaternionic finite energy", "use": "model"},
    "MortersPeres": {"ref": "57", "what": "harmonic measure of an annulus (interpretation)", "use": "model"},
    "Grafakos2014": {"ref": "32", "what": "Riesz-Thorin, Littlewood-Paley, Mihlin", "use": "input"},
    "HeoNazarovSeeger2011": {"ref": "37", "what": "B = C = 0 in (7.4) for n >= 4 (comparison)", "use": "model"},
    "BRRS2025": {"ref": "9", "what": "radial focusing test", "use": "input"},
    "Stein1993": {"ref": "74", "what": "stationary phase; sharp function inequality", "use": "input"},
    "Fefferman1971": {"ref": "23", "what": "ball multiplier tube geometry", "use": "input"},
    "FernandezDelgadoDeLaSalle": {"ref": "24", "what": "compressed tube unions", "use": "input"},
    "Hormander1973": {"ref": "38", "what": "oscillatory integral to extension", "use": "input"},
    "Tao1999": {"ref": "75", "what": "epsilon removal (Thm 1.2); BR implies restriction; Nikodym", "use": "input"},
    "Kim2017": {"ref": "46", "what": "epsilon removal for compact hypersurfaces", "use": "input"},
    "Nicola2009": {"ref": "61", "what": "slicing from the sphere to the cone", "use": "input"},
    "BCSS1986": {"ref": "7", "what": "random signs on caps", "use": "input"},
    "Bourgain1991": {"ref": "13", "what": "restriction to Kakeya via caps", "use": "input"},
    "Keich1999": {"ref": "44", "what": "grouping radii for Hausdorff dimension", "use": "input"},
    "GaoLiuXi": {"ref": "30", "what": "Nikodym on manifolds, straightening charts", "use": "input"},
    "Nadjimzadah2026": {"ref": "59", "what": "lifting curved Kakeya sets", "use": "input"},
    "BeltranHickmanSogge": {"ref": "8", "what": "local smoothing implies Bochner-Riesz (Props 39-40)", "use": "input"},
    "Sogge1991": {"ref": "72", "what": "local smoothing to summability", "use": "model"},
    "Seeger1988": {"ref": "67", "what": "annular pieces to multiplier estimates", "use": "input"},
    "GuoRoosYung": {"ref": "34", "what": "square-function version of Seeger's method", "use": "input"},
    "LeeRogersSeeger2013": {"ref": "51", "what": "extension to Schrodinger space-time estimates", "use": "input"},
}

# Internal results: id -> (title, section, internal premises, external imports).
NODES: Dict[str, Tuple[str, str, List[str], List[str]]] = {
    "Eq2.2-2.4": ("The symbol determines the Gaussian", "2.1", [], []),
    "Lem2.1": (
        "Lifted bilinear tensor is PSD with divergence-free columns",
        "2.2",
        [],
        ["Friedrichs1954", "BaouendiTreves1982", "Kaiser1990"],
    ),
    "Prop2.2": ("The wave current A0 in quaternionic coordinates", "2.3", ["Lem2.1", "Eq2.2-2.4"], ["Husimi1940"]),
    "Eq2.15": ("Time component on a frequency cap", "2.4", ["Prop2.2"], []),
    "Lem3.1": ("Hessian calculus", "3.1", [], []),
    "Lem3.2": ("Moore determinant and cofactor identities", "3.2", [], ["Alesker2003a"]),
    "Lem3.3": ("Cofactor divergence", "3.3", ["Lem3.1", "Lem3.2"], ["Alesker2013"]),
    "Lem4.1": ("Fiber geometry", "4.1", ["Lem3.1", "Prop2.2"], []),
    "ThmA.1": (
        "Periodic Dirichlet problem",
        "A",
        ["Lem3.1", "Lem3.2"],
        ["Alesker2003b", "Zhu2016", "CNS1985", "GilbargTrudinger", "EvansKrylov"],
    ),
    "Sec4.2": (
        "Regularized current and Dirichlet potential (4.5)-(4.8)",
        "4.2",
        ["Prop2.2", "Lem3.2", "Lem3.3", "Lem4.1", "ThmA.1"],
        ["Serre2018", "Serre2019"],
    ),
    "Prop4.2": (
        "Energy balance",
        "4.3",
        ["Sec4.2", "Lem3.1", "Lem3.2", "Lem3.3", "Lem4.1"],
        ["Serre2023", "Aubin1984", "Mabuchi1986", "Ahag2009"],
    ),
    "Lem4.3": ("Energy comparison", "4.4", ["Sec4.2", "Lem3.2", "Lem3.3"], ["Aubin1984", "BBGZ2013", "Wan2020"]),
    "Prop5.1": (
        "Energy bounds on a fixed fiber",
        "5",
        ["Prop4.2", "Lem4.3", "Lem4.1", "Eq2.15", "Prop2.2", "Sec4.2", "ThmA.1"],
        [],
    ),
    "Lem6.1": ("Propagation across a thin cylinder", "6", [], ["MortersPeres"]),
    "Rem6.2": ("Sharpness of Lemma 6.1 for scalar supersolutions", "6", [], []),
    "Prop6.3": ("Critical estimate on the torus for one cap", "6", ["Lem6.1", "Prop5.1"], []),
    "Thm1.2": ("Critical annular estimate", "7.1", ["Prop6.3"], []),
    "Eq7.3": ("Interpolated annular estimate", "7.2", ["Thm1.2"], ["Grafakos2014"]),
    "Thm1.1": ("Euclidean local smoothing", "7.2", ["Eq7.3"], ["Grafakos2014"]),
    "Cor7.1": ("Logarithmic Sobolev estimate", "7.2", ["Eq7.3"], ["Grafakos2014", "HeoNazarovSeeger2011"]),
    "Prop8.1": ("Radial focusing", "8", [], ["BRRS2025", "Stein1993"]),
    "AppC": ("Disjoint packets and the weak norm", "C", [], ["Fefferman1971", "FernandezDelgadoDeLaSalle"]),
    "Prop8.2": ("Weak spacetime obstruction", "8", ["AppC"], []),
    "Lem9.2": ("Local spherical extension from the wave", "9", ["Thm1.2"], ["Hormander1973", "Tao1999"]),
    "Cor9.3": ("Global sphere and cone extension", "9.1", ["Lem9.2", "Thm1.2"], ["Tao1999", "Nicola2009"]),
    "Lem9.4": ("From caps to tubes", "9.2", ["Lem9.2"], ["BCSS1986", "Bourgain1991"]),
    "Cor9.1": (
        "Spherical extension, Kakeya maximal, Hausdorff dimension",
        "9.3",
        ["Lem9.2", "Lem9.4", "Thm1.2"],
        ["Keich1999"],
    ),
    "Eq9.7": ("Nikodym maximal estimate", "9.4", ["Cor9.1"], ["Tao1999", "GaoLiuXi"]),
    "Sec9.4-curves": ("Nikodym dimension and quadratic curve families", "9.4", ["Cor9.1"], ["Nadjimzadah2026"]),
    "Eq10.3": ("Rescaled wave estimate", "10", ["Thm1.1"], []),
    "Lem10.2": ("Maximal estimate for a thin shell", "10", ["Eq10.3"], ["Grafakos2014"]),
    "Thm10.1": ("Bochner-Riesz means", "10", ["Lem10.2", "Eq10.3"], ["BeltranHickmanSogge", "Sogge1991"]),
    "Lem11.2": ("One interval of radii", "11", ["Eq10.3"], []),
    "Lem11.3": ("Combining dilates", "11", [], ["Seeger1988", "GuoRoosYung", "Stein1993"]),
    "Thm11.1": ("Stein's square function", "11", ["Lem11.2", "Lem11.3"], ["Grafakos2014"]),
    "Cor12.1": (
        "Paraboloid extension and Schrodinger smoothing",
        "12",
        ["Lem9.2", "Thm1.2", "Cor9.3"],
        ["Tao1999", "Kim2017", "LeeRogersSeeger2013"],
    ),
    "ThmB.1": ("Angular endpoint", "B", ["Thm1.2", "Prop8.1"], []),
    "AppD": (
        "Linear Dirichlet problem for the planar wave (n = 2 route)",
        "D",
        ["Prop2.2", "Prop4.2", "Lem6.1", "Prop5.1"],
        [],
    ),
    "ThmE.1": (
        "Curved characteristic sheets of symmetric systems",
        "E",
        ["Lem2.1", "Lem3.1", "Lem4.3", "Prop4.2", "Lem6.1", "Prop5.1", "Prop6.3", "ThmA.1"],
        [],
    ),
}

# Main chain stated in the paper's road map (Sections 1.4 and 7): Theorem 1.1 <- ... <- the Section 2-4 inputs.
MAIN_CHAIN = ["Thm1.1", "Eq7.3", "Thm1.2", "Prop6.3", "Prop5.1", "Prop4.2"]

# Join with the ADR-070 coverage map: DAG node -> coverage "item" prefixes.
COVERAGE_JOIN: Dict[str, List[str]] = {
    "Thm1.1": ["Theorem 1.1"],
    "Thm1.2": ["Theorem 1.2"],
    "Cor7.1": ["Corollary 7.1"],
    "Prop8.1": ["Proposition 8.1"],
    "Prop8.2": ["Proposition 8.2"],
    "Cor9.1": ["Corollary 9.1"],
    "Cor9.3": ["Corollary 9.3"],
    "Eq9.7": ["(9.7)"],
    "Sec9.4-curves": ["Section 9.4, quadratic", "Section 9.4, Nikodym dimension"],
    "Thm10.1": ["Theorem 10.1"],
    "Thm11.1": ["Theorem 11.1"],
    "Cor12.1": ["Corollary 12.1"],
    "ThmA.1": ["Theorem A.1"],
    "ThmB.1": ["Theorem B.1"],
    "ThmE.1": ["Theorem E.1"],
}


def build_dag() -> ProofDependencyDAG:
    """Internal results and external imports as one `ProofDependencyDAG`; imports are the leaves."""
    dag = ProofDependencyDAG(theorem_id="Thm1.1", root_lemma_id="Thm1.1")
    for key, info in EXTERNAL.items():
        dag.add_lemma(
            ProofLemmaNode(
                lemma_id=f"EXT:{key}",
                title=info["what"],
                premises=[],
                deduction_rule=DeductionRule.AXIOMATIC_ASSERTION,
                mathematical_statement=f"[{info['ref']}] {info['what']}",
                formal_expression="",
                is_axiom_without_proof=True,
            )
        )
    for key, (title, section, premises, imports) in NODES.items():
        dag.add_lemma(
            ProofLemmaNode(
                lemma_id=key,
                title=title,
                premises=premises + [f"EXT:{e}" for e in imports],
                deduction_rule=DeductionRule.MODUS_PONENS,
                mathematical_statement=f"Section {section}: {title}",
                formal_expression="",
            )
        )
    return dag


def topological_order() -> List[str]:
    """Internal nodes, premises first (Kahn's algorithm, ties broken by insertion order)."""
    pending = {k: set(p) for k, (_, _, p, _) in NODES.items()}
    order: List[str] = []
    while pending:
        ready = [k for k, p in pending.items() if not p]
        if not ready:
            raise ValueError(f"cycle among {sorted(pending)}")
        for k in ready:
            order.append(k)
            del pending[k]
        for p in pending.values():
            p.difference_update(ready)
    return order


def ancestors(node: str) -> List[str]:
    seen: List[str] = []
    stack = list(NODES[node][2])
    while stack:
        k = stack.pop()
        if k not in seen:
            seen.append(k)
            stack.extend(NODES[k][2])
    return seen


def imports_of(node: str) -> List[str]:
    """External results that a node rests on, directly or through its internal premises."""
    found: List[str] = []
    for k in [node] + ancestors(node):
        for e in NODES[k][3]:
            if e not in found:
                found.append(e)
    return found


def coverage_rows(node: str) -> List[Dict[str, str]]:
    prefixes = COVERAGE_JOIN.get(node, [])
    return [row for row in COVERAGE if any(row["item"].startswith(p) for p in prefixes)]


def dag_report() -> Dict[str, Any]:
    audit = build_dag().verify_dag_acyclicity_and_completeness()
    nodes = []
    for key in topological_order():
        title, section, premises, imports = NODES[key]
        nodes.append(
            {
                "id": key,
                "title": title,
                "section": section,
                "premises": premises,
                "imports": imports,
                "imports_transitive": imports_of(key),
                "formal_status": [
                    {"item": r["item"], "status": r["status"], "lean": r["lean"], "fidelity": r["fidelity"]}
                    for r in coverage_rows(key)
                ],
            }
        )
    return {
        "is_acyclic": audit["is_acyclic"],
        "cycle_path": audit["cycle_path"],
        "missing_premises": audit["missing_premises"],
        # Imported results are leaves by design: they are recorded, not proved here.
        "imported_leaves": len(audit["unproven_axioms"]),
        "internal_nodes": len(NODES),
        "main_chain": MAIN_CHAIN,
        "nodes": nodes,
        "external": EXTERNAL,
    }


# ---------------------------------------------------------------------------
# Part 2: symbolic checks
# ---------------------------------------------------------------------------

VERIFIED = "VERIFIED"
REFUTED = "REFUTED"
NOT_ENCODABLE = "NOT_ENCODABLE"


@dataclass
class Check:
    id: str
    claim: str
    source: str
    tool: str
    scope: str
    status: str = ""
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    note: str = ""


def _zero(expr: sp.Expr) -> bool:
    return sp.simplify(sp.expand(expr)) == 0


class _Asserter:
    def __init__(self, check: Check):
        self.check = check

    def eq(self, label: str, lhs: sp.Expr, rhs: sp.Expr) -> None:
        self.check.assertions.append({"assertion": label, "holds": bool(_zero(lhs - rhs))})

    def true(self, label: str, value: bool) -> None:
        self.check.assertions.append({"assertion": label, "holds": bool(value)})

    def z3_valid(self, label: str, claim: z3.BoolRef, hyps: List[z3.BoolRef]) -> None:
        solver = z3.Solver()
        solver.set("timeout", 20000)
        solver.add(*hyps, z3.Not(claim))
        result = solver.check()
        entry = {"assertion": label, "holds": result == z3.unsat, "z3": str(result)}
        if result == z3.sat:
            entry["counterexample"] = str(solver.model())
        self.check.assertions.append(entry)


n, d, p = sp.symbols("n d p", positive=True)
PC = 2 * n / (n - 1)


def check_critical_exponent(a: _Asserter) -> None:
    q = 1 + 1 / d
    a.eq("2(1 + 1/d) = 2n/(n-1) with d = n - 1", (2 * q).subs(d, n - 1), PC)
    a.eq("pc = 1 + (n+1)/(n-1) (used in Cor 9.3)", PC, 1 + (n + 1) / (n - 1))
    a.eq("s+(pc) = (n-1)/2 - n/pc = 0", (n - 1) / 2 - n / PC, 0)
    a.eq("2/pc = (n-1)/n", 2 / PC, (n - 1) / n)
    a.eq("delta_pc = 1/2 - 1/pc = 1/(2n) (Cor 7.1)", sp.Rational(1, 2) - 1 / PC, 1 / (2 * n))
    a.eq("B*(pc) = beta(pc) + delta_pc = 1/2 + 1/pc (Cor 7.1)", 2 / PC + 1 / (2 * n), sp.Rational(1, 2) + 1 / PC)


def check_focusing_exponent(a: _Asserter) -> None:
    expo = d - d * p / 2  # exponent of u in the Prop 8.1 integral, int_{A/N}^{1/4} u^{d - dp/2} du
    sols = sp.solve(sp.Eq(expo, -1), p)
    a.true("d - dp/2 = -1 has the single solution p = 2(d+1)/d", len(sols) == 1 and _zero(sols[0] - 2 * (d + 1) / d))
    a.eq("that solution is pc = 2n/(n-1)", sols[0].subs(d, n - 1), PC)
    a.eq(
        "p < pc gives exponent > -1 (convergent): exponent - (-1) = d(pc - p)/2",
        expo + 1,
        d * (2 * (d + 1) / d - p) / 2,
    )
    u, eps = sp.symbols("u epsilon", positive=True)
    a.eq(
        "at p = pc the integral is log(N/(4A)): int_eps^{1/4} u^{-1} du = log(1/(4 eps))",
        sp.integrate(1 / u, (u, eps, sp.Rational(1, 4))),
        sp.log(1 / (4 * eps)),
    )


def check_tube_and_scaling_powers(a: _Asserter) -> None:
    q = PC / 2
    A = sp.symbols("A", positive=True)
    a.eq("Lemma 9.4: d p = 2n at p = pc", (n - 1) * PC, 2 * n)
    a.eq("Lemma 9.4: q = p/2 = n/(n-1)", q, n / (n - 1))
    a.eq("Lemma 9.4: A p / q = 2A", A * PC / q, 2 * A)
    a.eq("Lemma 9.2: N^(n/p - d/2) has exponent 0 at pc", n / PC - (n - 1) / 2, 0)
    a.eq("(9.6): 2 A n = 2(n-1) at A = 2/pc", 2 * (2 / PC) * n, 2 * (n - 1))
    a.eq("Kakeya radial test: 1 - 1/n = 2/pc", 1 - 1 / n, 2 / PC)
    dd = sp.symbols("d", positive=True)
    pcd = 2 * (dd + 1) / dd
    a.eq("Cor 12.1 paraboloid: delta^(-d + (d+2)/pc + d/pc) has exponent 0", -dd + (dd + 2) / pcd + dd / pcd, 0)
    a.eq("Cor 12.1 Schrodinger: lambda^(d - (2d+2)/pc) has exponent 0", dd - (2 * dd + 2) / pcd, 0)
    a.eq("Cor 12.1 (12.3) at r = p: s = d - 2(d+1)/p", dd * (1 - 2 / p) - 2 / p, dd - 2 * (dd + 1) / p)
    R, sig = sp.symbols("R sigma", positive=True)
    a.eq(
        "(10.3): R^((n+1)/p) R^(-n/p) R^sigma = R^(1/p + sigma)",
        sp.powsimp(R ** ((n + 1) / p) * R ** (-n / p) * R**sig),
        R ** (1 / p + sig),
    )
    a.eq(
        "Thm 10.1: n(1/2 - 1/p) - 1/2 = s+(p) argument (n-1)/2 - n/p",
        n * (sp.Rational(1, 2) - 1 / p) - sp.Rational(1, 2),
        (n - 1) / 2 - n / p,
    )


def check_interpolation(a: _Asserter) -> None:
    th = sp.symbols("theta")
    # L2 (no log, no h power) and pc (log power 2/pc, no h power): 1/p = (1-th)/2 + th/pc.
    th_low = sp.solve(sp.Eq(1 / p, (1 - th) / 2 + th / PC), th)[0]
    a.eq("(7.3), 2 <= p <= pc: log power theta * 2/pc = d(1 - 2/p)", th_low * 2 / PC, (n - 1) * (1 - 2 / p))
    # pc (log 2/pc, h^0) and infinity (no log, h^(-d/2)): 1/p = (1-th)/pc.
    th_high = sp.solve(sp.Eq(1 / p, (1 - th) / PC), th)[0]
    a.eq("(7.3), p >= pc: log power (1 - theta) * 2/pc = 2/p", (1 - th_high) * 2 / PC, 2 / p)
    a.eq("(7.3), p >= pc: h power theta * d/2 = d/2 - n/p", th_high * (n - 1) / 2, (n - 1) / 2 - n / p)
    a.eq("the two log powers meet at pc", ((n - 1) * (1 - 2 / p) - 2 / p).subs(p, PC), 0)
    # Corollary 9.3: s = 1 + b/a', theta = s/b; E: L1 -> Linf and Ls -> Ls.
    b, ap = sp.symbols("b a_prime", positive=True)
    s = 1 + b / ap
    aa = ap / (ap - 1)
    a.eq("Cor 9.3: theta/s = 1/b at theta = s/b", (s / b) / s, 1 / b)
    a.eq("Cor 9.3: 1 - theta + theta/s = 1/a", 1 - s / b + 1 / b, 1 / aa)
    nz, bz, x = z3.Reals("n b x")  # x = 1/a' in (0, 1]; a < b <=> 1/b < 1 - x
    sz = 1 + bz * x
    hyps = [nz >= 2, x > 0, x <= 1, bz * (nz - 1) > 2 * nz, bz * (nz - 1) * x > (nz + 1)]
    a.z3_valid("Cor 9.3: b > pc and b > (n+1)a'/(n-1) imply s > pc", sz * (nz - 1) > 2 * nz, hyps)
    a.z3_valid("Cor 9.3: and a < b implies s < b", sz < bz, hyps + [bz * (1 - x) > 1])
    # Corollary 7.1: w_j = (1+j)^(beta - B) in l^r, r = 1/delta_p, iff (B - beta) r > 1 iff B > beta + delta_p.
    B, beta, dp = z3.Reals("B beta delta_p")
    a.z3_valid(
        "Cor 7.1: (B - beta)/delta_p > 1 iff B > beta + delta_p (delta_p > 0)",
        ((B - beta) > dp) == (B > beta + dp),
        [dp > 0],
    )


def check_power_and_depth(a: _Asserter) -> None:
    h, s, m, alpha, bet = sp.symbols("h s m alpha beta", positive=True)
    q = n / (n - 1)
    # h^2 s^(2d) (h s)^(-d q) = h^(2 - dq) s^(2d - dq); compare the two exponents with those of sigma^(n-2).
    a.eq("Prop 5.1: h^2 s^(2d) (h s)^(-d q) = sigma^(n-2): exponent of h", 2 - (n - 1) * q, -(n - 2))
    a.eq("Prop 5.1: h^2 s^(2d) (h s)^(-d q) = sigma^(n-2): exponent of s", 2 * (n - 1) - (n - 1) * q, n - 2)
    a.eq("Prop 5.1: depth m^(1/d) times density m is m^q", sp.powsimp(m ** (1 / (n - 1)) * m), m**q)
    g = sp.symbols("g", positive=True)
    a.eq("with m ~ |g|^2: (|g|^2)^q = |g|^pc", sp.powsimp((g**2) ** q, force=True), g**PC)
    for size in (2, 3, 4, 5):
        e = sp.Matrix(sp.symbols(f"e0:{size}"))
        Bm = bet * e * e.T / (e.T * e)[0]
        lhs = (Bm + alpha * sp.eye(size)).det()
        a.eq(
            f"det(beta e e^T/|e|^2 + alpha I) = (beta + alpha) alpha^(m-1), m = {size}",
            sp.simplify(lhs),
            (bet + alpha) * alpha ** (size - 1),
        )


def _sym(size: int, name: str) -> sp.Matrix:
    entries = {}
    for i in range(size):
        for j in range(i, size):
            entries[(i, j)] = entries[(j, i)] = sp.Symbol(f"{name}{i}{j}")
    return sp.Matrix(size, size, lambda i, j: entries[(i, j)])


def _frob(A: sp.Matrix, B: sp.Matrix) -> sp.Expr:
    """Real pairing A : B = tr(A^T B)."""
    return (A.T * B).trace()


def check_cofactor_identities(a: _Asserter) -> None:
    t = sp.symbols("t")
    for size in (2, 3, 4):
        A = _sym(size, "a")
        v = sp.Matrix(sp.symbols(f"v0:{size}"))
        C = A.adjugate()
        a.eq(
            f"(3.7) det(A + t v v^T) = det A + t v^T C(A) v, real symmetric m = {size}",
            (A + t * v * v.T).det(),
            A.det() + t * (v.T * C * v)[0],
        )
        Bm = _sym(size, "b")
        a.eq(
            f"(3.6) C(A) : B = d/dt det(A + tB) at 0, m = {size}",
            sp.diff((A + t * Bm).det(), t).subs(t, 0),
            _frob(C, Bm),
        )
        a.eq(f"Euler: C(A) : A = m det A, m = {size}", _frob(C, A), size * A.det())
    # (3.8) Schur complement in a 3x3 model with D 2x2.
    ell = sp.Symbol("l")
    c = sp.Matrix(sp.symbols("c1:3"))
    D = _sym(2, "d")
    M = sp.Matrix(sp.BlockMatrix([[sp.Matrix([[ell]]), c.T], [c, D]]))
    sigma = ell - (c.T * D.inv() * c)[0]
    a.eq("(3.8) det M = det(D) * sigma, m = 3", M.det(), D.det() * sigma)
    w = sp.Matrix(sp.symbols("w0:3"))
    form = (w.T * (M - sigma * sp.diag(1, 0, 0)) * w)[0]
    y = w[1:, 0] + D.inv() * c * w[0]
    a.eq("(3.8) the form of M - sigma v0 v0^T is (w + D^-1 c b)^T D (w + D^-1 c b)", form, (y.T * D * y)[0])


def check_cofactor_divergence(a: _Asserter) -> None:
    for size in (2, 3):
        xs = sp.symbols(f"x0:{size}")
        u = sp.Function("u")(*xs)
        C = sp.hessian(u, xs).adjugate()
        div = [sp.expand(sum(sp.diff(C[i, j], xs[i]) for i in range(size))) for j in range(size)]
        a.true(
            f"Lemma 3.3 real-Hessian model: every column of C(D^2 u) is divergence free, m = {size}",
            all(sp.simplify(e) == 0 for e in div),
        )


def _ball_integral(poly: sp.Expr, xs: Tuple[sp.Symbol, ...]) -> sp.Expr:
    """Exact integral of a polynomial over the unit ball of R^m (monomial formula prod Gamma / Gamma)."""
    total = sp.Integer(0)
    for monom, coeff in sp.Poly(sp.expand(poly), *xs).terms():
        if any(k % 2 for k in monom):
            continue
        betas = [sp.Rational(k + 1, 2) for k in monom]
        total += coeff * sp.prod([sp.gamma(b) for b in betas]) / sp.gamma(sum(betas) + 1)
    return sp.simplify(total)


ENERGY_MODELS = (
    (2, "x0/3 + x1^2/5"),
    (3, "x0*x2/4"),
)


@lru_cache(maxsize=None)
def _energy_terms(size: int, extra: str) -> Dict[str, sp.Expr]:
    """Lemma 4.3 ingredients for u = (|x|^2 - 1)(1 + extra) on the unit ball of R^size, B = beta e0 e0^T."""
    th, lam, bet = sp.symbols("theta lambda beta", positive=True)
    xs = sp.symbols(f"x0:{size}")
    u = (sum(x**2 for x in xs) - 1) * (1 + sp.sympify(extra, locals={str(x): x for x in xs}))
    Bm = sp.zeros(size)
    Bm[0, 0] = bet  # Hessian of beta x0^2 / 2: rank one
    Du = Bm + sp.hessian(u, xs)
    mu = Du.det() / lam
    C = Du.adjugate()
    seg = sp.expand(((1 - th) * Bm + th * Du).det())
    grad = sp.Matrix([sp.diff(u, x) for x in xs])
    return {
        "seg": seg,
        "two_term": sp.expand(th**size * Du.det() + (1 - th) * th ** (size - 1) * _frob(C, Bm)),
        "X0": _ball_integral(-u * mu, xs),
        "Ez": _ball_integral(u * sp.integrate(seg, (th, 0, 1)) / lam, xs),
        "Q": _ball_integral((grad.T * C * grad)[0], xs),
        "lam": lam,
    }


def check_energy_identity(a: _Asserter) -> None:
    """Lemma 4.3 in a real Monge-Ampere model on the unit ball of R^m with a rank-one constant background."""
    th = sp.Symbol("theta", positive=True)
    x0, x1 = sp.symbols("x0 x1")
    a.eq(
        "ball integrator: |B^2| = pi and int_{B^2} x0^2 = pi/4",
        _ball_integral(sp.Integer(1) + 0 * x0, (x0, x1)) + _ball_integral(x0**2, (x0, x1)),
        sp.pi + sp.pi / 4,
    )
    for size, extra in ENERGY_MODELS:
        e = _energy_terms(size, extra)
        a.eq(
            f"rank-one segment: det((1-theta)B + theta D) = theta^m det D + (1-theta) theta^(m-1) C(D):B, m = {size}",
            e["seg"],
            e["two_term"],
        )
        a.true(
            f"model is not degenerate: X0 != 0 and int grad u^T C grad u != 0, m = {size}",
            not _zero(e["X0"]) and not _zero(e["Q"]),
        )
        rhs = sp.Rational(size - 1, size + 1) * e["X0"] + e["Q"] / (e["lam"] * size * (size + 1))
        a.eq(
            f"Lemma 4.3 identity F = (m-1)/(m+1) X0 + (lambda m (m+1))^-1 int grad u^T C(Du) grad u, m = {size}",
            e["Ez"] + e["X0"],
            rhs,
        )
    # The bounds (4.14) on a convex instance: u = c(|x|^2 - 1), D u = diag(beta + 2c, 2c) > 0.
    cc = sp.Rational(1, 2)
    xs = sp.symbols("x0:2")
    u = cc * (xs[0] ** 2 + xs[1] ** 2 - 1)
    Bm = sp.Matrix([[3, 0], [0, 0]])
    Du = Bm + sp.hessian(u, xs)
    lam_v = 7
    mu = Du.det() / lam_v
    seg = ((1 - th) * Bm + th * Du).det()
    X0 = _ball_integral(-u * mu, xs)
    F = _ball_integral(u * sp.integrate(seg, (th, 0, 1)) / lam_v, xs) + X0
    a.true(
        "(4.14) (m-1)/(m+1) X0 <= F <= m/(m+1) X0 on a convex instance (m = 2, beta = 3, lambda = 7)",
        bool(sp.Rational(1, 3) * X0 <= F <= sp.Rational(2, 3) * X0),
    )
    a.eq(
        "theta integrals: int theta^m = 1/(m+1), int (1-theta) theta^(m-1) = 1/(m(m+1))",
        sp.integrate((1 - th) * th ** (n - 1), (th, 0, 1)),
        1 / (n * (n + 1)),
    )


def check_symbol_and_gaussian(a: _Asserter) -> None:
    T, b, t, s0 = sp.symbols("T b t s0", real=True)
    for dd in (1, 2, 3):
        x = sp.Matrix(sp.symbols(f"y0:{dd}", real=True))
        xib = sp.Symbol("xi_b", real=True)
        xix = sp.Matrix(sp.symbols(f"xi0:{dd}", real=True))
        norm = sp.sqrt(xib**2 + (xix.T * xix)[0])
        kappa = (xib + norm) / sp.sqrt(2)
        v = xix / kappa
        phase_null = kappa * (s0 + (v.T * x)[0] - (v.T * v)[0] * t / 2)
        phase_phys = (xix.T * x)[0] + xib * b - T * norm
        sub = {t: (T + b) / sp.sqrt(2), s0: (b - T) / sp.sqrt(2)}
        a.eq(f"(2.1) null-frame phase equals X.xi - T|xi|, d = {dd}", phase_null.subs(sub), phase_phys)
        a.eq(f"(2.4) |xi| = kappa (1 + |v|^2/2)/sqrt 2, d = {dd}", kappa * (1 + (v.T * v)[0] / 2) / sp.sqrt(2), norm)
        kap = sp.Symbol("kappa", positive=True)
        vv = sp.Matrix(sp.symbols(f"v0:{dd}", real=True))
        mode = sp.exp(sp.I * kap * (s0 + (vv.T * x)[0] - (vv.T * vv)[0] * t / 2))
        wave = 2 * sp.diff(mode, t, s0) + sum(sp.diff(mode, xi, 2) for xi in x)
        a.eq(f"(2.1) mode solves (2 d_t d_s0 + Lap_x) u = 0, d = {dd}", sp.simplify(wave / mode), 0)
        # (2.2): symbol matrices and the quadratic form.
        size = dd + 1
        E = lambda i, j: sp.Matrix(size, size, lambda r, c: 1 if (r, c) == (i, j) else 0)  # noqa: E731
        Ct = 2 * E(0, 0)
        Cx = [E(0, j) + E(j, 0) for j in range(1, size)]
        Cs0 = -sum((E(j, j) for j in range(1, size)), sp.zeros(size))
        pcov = (-(vv.T * vv)[0] / 2, list(vv), 1)
        Cp = pcov[0] * Ct + sum((vj * Cj for vj, Cj in zip(pcov[1], Cx)), sp.zeros(size)) + pcov[2] * Cs0
        expect = sp.Matrix(sp.BlockMatrix([[sp.Matrix([[(vv.T * vv)[0]]]), -vv.T], [-vv, sp.eye(dd)]]))
        a.eq(f"(2.2) -C(p) = [[|v|^2, -v^T], [-v, I]], d = {dd}", sp.Matrix(-Cp - expect).norm(), 0)
        w = sp.Matrix(sp.symbols(f"w0:{size}", real=True))
        a.eq(
            f"(2.2) -w^T C(p) w = |w' - v w0|^2, d = {dd}",
            -(w.T * Cp * w)[0],
            ((w[1:, 0] - vv * w[0]).T * (w[1:, 0] - vv * w[0]))[0],
        )
        Ev = sp.Matrix([1] + list(vv))
        a.eq(f"(2.2) kernel of C(p) contains E(v) = (1, v), d = {dd}", (Cp * Ev).norm(), 0)
        phi = sp.Function("phi")(t, *x, s0)
        f = sp.Matrix([sp.diff(phi, s0)] + [sp.diff(phi, xi) for xi in x])
        Pf = (
            Ct * sp.diff(f, t)
            + sum((Cj * sp.diff(f, xj) for Cj, xj in zip(Cx, x)), sp.zeros(size, 1))
            + Cs0 * sp.diff(f, s0)
        )
        target = 2 * sp.diff(phi, t, s0) + sum(sp.diff(phi, xi, 2) for xi in x)
        a.true(
            f"P(d_s0 phi, grad phi) = ((2 d_t d_s0 + Lap) phi, 0, ..., 0), d = {dd}",
            _zero(Pf[0] - target) and all(_zero(e) for e in Pf[1:]),
        )
        # Flux of a real state, null to physical: q_T = |q_X| and q(E(v)) = (|xi|, xi)/kappa.
        q_t, q_x, q_s0 = w[0] ** 2, w[0] * w[1:, 0], -(w[1:, 0].T * w[1:, 0])[0] / 2
        q_T = (q_t - q_s0) / sp.sqrt(2)
        q_b = (q_t + q_s0) / sp.sqrt(2)
        a.eq(f"flux is null: q_T^2 = q_b^2 + |q_x|^2, d = {dd}", q_T**2, q_b**2 + (q_x.T * q_x)[0])
        a.eq(
            f"q_T = (w0^2 + |w'|^2/2)/sqrt 2, d = {dd}", q_T, (w[0] ** 2 + (w[1:, 0].T * w[1:, 0])[0] / 2) / sp.sqrt(2)
        )
        # (2.4): two real states give the complex modulus.
        w2 = sp.Matrix(sp.symbols(f"z0:{size}", real=True))
        two = sum(-(ww.T * Cp * ww)[0] for ww in (w, w2))
        zR, zz = w[0] + sp.I * w2[0], w[1:, 0] + sp.I * w2[1:, 0]
        diff = zz - vv * zR
        a.eq(f"(2.4) sum of two real squares = |zeta - v R|^2 (complex), d = {dd}", two, sp.expand((diff.H * diff)[0]))
    # Imaginary translation along a light ray: exp(omega.xi - |xi|) = exp(-|xi| |omega - theta|^2 / 2), unit vectors.
    om = sp.Matrix(sp.symbols("o0:3", real=True))
    thv = sp.Matrix(sp.symbols("th0:3", real=True))
    gap = (1 - (om.T * thv)[0]) - ((om - thv).T * (om - thv))[0] / 2
    a.eq(
        "1 - omega.theta - |omega - theta|^2/2 = 1 - (|omega|^2 + |theta|^2)/2, which is 0 on unit vectors",
        gap,
        1 - ((om.T * om)[0] + (thv.T * thv)[0]) / 2,
    )
    kap, xr = sp.symbols("kappa x", positive=True)
    a.eq(
        "normalization: int_C kappa exp(-kappa |zeta|^2) d zeta = pi (one complex variable)",
        sp.integrate(
            sp.integrate(kap * sp.exp(-kap * (xr**2 + sp.Symbol("y") ** 2)), (xr, -sp.oo, sp.oo)),
            (sp.Symbol("y"), -sp.oo, sp.oo),
        ),
        sp.pi,
    )


def check_flux_map(a: _Asserter) -> None:
    for dd in (1, 2, 3):
        R = sp.Symbol("R")
        zeta = sp.symbols(f"zeta0:{dd}")
        om = sp.Symbol("omega")
        src = [R, *zeta, om]
        tgt = [R**2] + [R * z for z in zeta] + [om - sum(z**2 for z in zeta) / 2]
        Jm = sp.Matrix(tgt).jacobian(src)
        a.eq(
            f"(2.11) complex Jacobian of (R, zeta, omega) -> (R^2, R zeta, omega - zeta.zeta/2) is 2 R^(d+1), d = {dd}",
            Jm.det(),
            2 * R ** (dd + 1),
        )
        vv = sp.symbols(f"v0:{dd}")
        dirv = sp.Matrix([1, *vv, 0])
        ME = Jm * dirv
        W = [z / R for z in zeta]
        Vv = sp.Matrix([1] + [(v_ + w_) / 2 for v_, w_ in zip(vv, W)] + [-sum(w_ * v_ for w_, v_ in zip(W, vv)) / 2])
        a.true(
            f"(2.12) M E(v) = (2R, zeta + R v, -zeta.v) = 2R (1, (v+W)/2, -W.v/2), d = {dd}",
            all(_zero(e) for e in (ME - 2 * R * Vv)),
        )
        ww = sp.symbols(f"u0:{dd}")
        pi_w = sp.Matrix([[-sum(x_**2 for x_ in ww) / 2, *ww, 1]])
        a.eq(
            f"(2.13) pi(w) V^v = -(w - W).(w - v)/2, d = {dd}",
            (pi_w * Vv)[0],
            -sum((w_ - W_) * (w_ - v_) for w_, W_, v_ in zip(ww, W, vv)) / 2,
        )
        a.eq(
            f"Prop 2.2 V_T^v = (V_t - V_s0)/sqrt 2 = (1 + W.v/2)/sqrt 2, d = {dd}",
            (Vv[0] - Vv[-1]) / sp.sqrt(2),
            (1 + sum(w_ * v_ for w_, v_ in zip(W, vv)) / 2) / sp.sqrt(2),
        )


def check_remark_6_2(a: _Asserter) -> None:
    s, b, T, r = sp.symbols("s b T r", positive=True)
    D = sp.log(3 / b)
    lap = lambda f: sp.diff(f, s, 2) + sp.diff(f, s) / s  # noqa: E731  radial Laplacian in the tau plane
    pfun = sp.log(3 / s) / D
    g = s**2 * (1 + sp.log(3 / s)) / (4 * D)
    L = pfun * g.subs(s, b) + (1 - pfun) * g.subs(s, 3)
    E = (1 - sp.cos(T)) * pfun + L - g
    a.eq("p(s) = log(3/s)/D is radially harmonic", lap(pfun), 0)
    a.true("p(b) = 1 and p(3) = 0", _zero(pfun.subs(s, b) - 1) and _zero(pfun.subs(s, 3)))
    a.eq("Lap_tau g = p", lap(g), pfun)
    a.eq("L is radially harmonic", lap(L), 0)
    a.eq("Lap_{T,tau} E = (cos T - 1) p", sp.diff(E, T, 2) + lap(E), (sp.cos(T) - 1) * pfun)
    a.eq("trace E(T, b) = 1 - cos T", E.subs(s, b), 1 - sp.cos(T))
    a.eq("E(T, 3) = 0", E.subs(s, 3), 0)
    a.eq("g'(s) = s (1 + 2 log(3/s)) / (4D) (> 0 on (0, 3])", sp.diff(g, s), s * (1 + 2 * sp.log(3 / s)) / (4 * D))
    a.eq(
        "(1 - p(r)) g(3) = 9 log(r/b) / (4 D^2)",
        sp.expand_log((1 - pfun.subs(s, r)) * g.subs(s, 3), force=True),
        sp.expand_log(9 * sp.log(r / b) / (4 * D**2), force=True),
    )
    # E(0, r) = L(r) - g(r) <= (1 - p(r)) g(3) since p(r) g(b) <= g(b) <= g(r); spot values on a grid (exact).
    ok = True
    for bv in (sp.Rational(1, 10), sp.Rational(1, 100)):
        for rv in (bv, 2 * bv, sp.Rational(1, 2), 1, 2, 3):
            val = (L - g).subs({b: bv, s: rv})
            bound = ((1 - pfun) * g.subs(s, 3)).subs({b: bv, s: rv})
            ok = ok and bool(sp.N(val, 30) >= -1e-25) and bool(sp.N(bound - val, 30) >= -1e-25)
    a.true("0 <= E(0, r) <= 9 log(r/b)/(4D^2) at b in {1/10, 1/100}, r in {b, 2b, 1/2, 1, 2, 3}", ok)


def check_lemma_6_1(a: _Asserter) -> None:
    s, b, x, A, z, kap = sp.symbols("s b x A z kappa", positive=True)
    U = sp.Function("U")
    us = U(sp.log(s / b))
    lhs = sp.diff(us, s, 2) + sp.diff(us, s) / s
    a.eq(
        "x = log(s/b): u'' + u'/s = s^-2 u_xx",
        sp.simplify(lhs * s**2 - sp.Subs(sp.diff(U(x), x, 2), x, sp.log(s / b)).doit()),
        0,
    )
    a.eq("radial harmonic functions are affine in log s: Lap log s = 0", sp.diff(sp.log(s), s, 2) + 1 / s**2, 0)
    P, psi = sp.Function("P"), sp.Function("psi")
    volterra = x + sp.Integral((x - z) * P(z) * psi(z), (z, 0, x))
    a.eq(
        "Volterra form psi(x) = x + int_0^x (x-z) P psi solves psi'' = P psi, psi(0) = 0, psi'(0) = 1",
        sp.diff(volterra, x, 2).doit(),
        P(x) * psi(x),
    )
    a.true(
        "Volterra form has psi(0) = 0 and psi'(0) = 1",
        _zero(volterra.subs(x, 0).doit()) and _zero(sp.diff(volterra, x).doit().subs(x, 0).doit() - 1),
    )
    a.eq(
        "dividing by x: psi/x = 1 + int z(x-z)/x (psi(z)/z) P(z) dz (integrands agree)",
        (x - z) * P(z) * psi(z) / x,
        z * (x - z) / x * (psi(z) / z) * P(z),
    )
    zz, xx, AA = z3.Reals("z x A")
    a.z3_valid(
        "z(x - z)/x <= min(z, A - z) for 0 <= z <= x <= A, x > 0",
        z3.And(zz * (xx - zz) <= zz * xx, zz * (xx - zz) <= (AA - zz) * xx),
        [zz >= 0, zz <= xx, xx <= AA, xx > 0],
    )
    t = sp.symbols("t", positive=True)
    a.eq(
        "kappa^2 term: int_0^inf t e^(-2t) dt = 1/4", sp.integrate(t * sp.exp(-2 * t), (t, 0, sp.oo)), sp.Rational(1, 4)
    )
    T = sp.symbols("T")
    H = sp.Function("H")
    k = sp.pi / 3
    anti = sp.sin(k * T) * sp.diff(H(T), T) - k * sp.cos(k * T) * H(T)
    a.eq(
        "sin(pi T/3) H'' = d/dT[sin H' - (pi/3) cos H] - (pi/3)^2 sin H",
        sp.diff(anti, T) - k**2 * sp.sin(k * T) * H(T),
        sp.sin(k * T) * sp.diff(H(T), T, 2),
    )
    a.eq(
        "boundary terms of that antiderivative on [0, 3] are (pi/3)(H(0) + H(3))",
        anti.subs(T, 3) - anti.subs(T, 0),
        k * (H(3) + H(0)),
    )
    hK, cc = sp.symbols("hK c", positive=True)
    integrand = s * sp.log(s / b) * s**-2 * sp.exp(-cc * s / hK)
    sub = sp.simplify((integrand * b).subs(s, b * t).subs(b, 2 * hK))
    a.eq(
        "Prop 6.3: with s = b t, b = 2Kh: s log(s/b) V ds = (log t / t) e^(-2cK t) dt (C = 1)",
        sub,
        sp.log(t) / t * sp.exp(-2 * cc * t),
    )
    # log t / t <= 1 on [1, inf), so the tail is at most int_1^inf e^(-2cK t) dt; checked at 2cK = 1.
    a.eq("Prop 6.3: majorant int_1^inf e^(-t) dt = 1/e", sp.integrate(sp.exp(-t), (t, 1, sp.oo)), sp.exp(-1))
    a.true(
        "Prop 6.3: 0 <= int_1^inf (log t / t) e^(-t) dt <= 1/e (numerical quadrature, 30 digits)",
        0 <= sp.N(sp.Integral(sp.log(t) / t * sp.exp(-t), (t, 1, sp.oo)), 30) <= sp.N(sp.exp(-1), 30),
    )
    a.eq("(6.2) at r = 2b: log(r/b) / D^2 = log 2 / D^2", sp.log(2 * b / b), sp.log(2))


def check_square_function_l2(a: _Asserter) -> None:
    al, u = sp.symbols("alpha u", positive=True)
    val = 2 * al**2 * sp.integrate(u * (1 - u) ** (2 * al - 2), (u, 0, 1), conds="none")
    a.eq(
        "Thm 11.1 at p = 2: 2 alpha^2 int_0^1 u (1-u)^(2 alpha - 2) du = alpha/(2 alpha - 1)",
        sp.gammasimp(val),
        al / (2 * al - 1),
    )
    a.eq(
        "1/2 + s+(p) = n(1/2 - 1/p) above the max",
        sp.Rational(1, 2) + (n - 1) / 2 - n / p,
        n * (sp.Rational(1, 2) - 1 / p),
    )


CHECKS: List[Tuple[Check, Callable[[_Asserter], None]]] = [
    (
        Check(
            "exponent.critical",
            "pc = 2n/(n-1) from 1 + 1/d, and the derived constants at pc",
            "Sec. 1.4, 4.2, 7.2",
            "sympy",
            "symbolic in n; d = n - 1",
        ),
        check_critical_exponent,
    ),
    (
        Check(
            "exponent.focusing",
            "the focusing integral has exponent -1 exactly at pc",
            "Prop 8.1",
            "sympy",
            "symbolic in d and p",
        ),
        check_focusing_exponent,
    ),
    (
        Check(
            "exponent.scaling",
            "dp = 2n, Ap/q = 2A, N^0, paraboloid and Schrodinger powers 0, (10.3)",
            "Lemma 9.2, 9.4, (9.6), Cor 12.1, (10.3), Thm 10.1",
            "sympy",
            "symbolic in n, d, p",
        ),
        check_tube_and_scaling_powers,
    ),
    (
        Check(
            "exponent.interpolation",
            "(7.3) log and h powers; Cor 9.3 interpolation; Cor 7.1 summability",
            "(7.3), Cor 9.3, Cor 7.1",
            "sympy + z3",
            "symbolic; z3 over reals with n >= 2",
        ),
        check_interpolation,
    ),
    (
        Check(
            "exponent.depth",
            "density m forces depth m^(1/d); (-u) mu ~ |g|^pc; rank-one det(B + alpha I)",
            "Sec. 1.4, 4.2, Prop 5.1",
            "sympy",
            "symbolic; det(B + alpha I) in real m x m, m = 2..5",
        ),
        check_power_and_depth,
    ),
    (
        Check(
            "lemma3.2.real",
            "cofactor identities (3.6)-(3.8)",
            "Lemma 3.2",
            "sympy",
            "real symmetric m x m, m = 2..4 (Schur: m = 3); the quaternionic Moore determinant is not encoded",
        ),
        check_cofactor_identities,
    ),
    (
        Check(
            "lemma3.3.real",
            "Hessian cofactor columns are divergence free",
            "Lemma 3.3",
            "sympy",
            "real Hessian (one slot), generic smooth u in m = 2, 3 variables; not the 3- or 4-slot quaternionic case",
        ),
        check_cofactor_divergence,
    ),
    (
        Check(
            "lemma4.3.model",
            "Lemma 4.3 energy identity and (4.14) with a rank-one background",
            "Lemma 4.3",
            "sympy",
            "real Monge-Ampere on the unit ball of R^m, m = 2, 3, constant rank-one B, polynomial u vanishing on the "
            "sphere, exact integrals; bounds (4.14) on one convex instance",
        ),
        check_energy_identity,
    ),
    (
        Check(
            "eq2.2-2.4",
            "null-frame modes, the symbol (2.2), flux, imaginary light-ray Gaussian and (2.4)",
            "(2.1)-(2.4)",
            "sympy",
            "d = 1, 2, 3 symbolic",
        ),
        check_symbol_and_gaussian,
    ),
    (
        Check(
            "eq2.11-2.13",
            "flux map Jacobian (2.11), polarization column (2.12), tangency (2.13), V_T",
            "(2.9)-(2.13), Prop 2.2",
            "sympy",
            "d = 1, 2, 3, complex-bilinear algebra",
        ),
        check_flux_map,
    ),
    (
        Check(
            "remark6.2",
            "explicit supersolution showing the two log losses are sharp",
            "Remark 6.2",
            "sympy",
            "symbolic in b, s, T; the final inequality also on an exact grid of (b, r)",
        ),
        check_remark_6_2,
    ),
    (
        Check(
            "lemma6.1.radial",
            "radial comparison in log r and its integral bounds",
            "Lemma 6.1, Prop 6.3",
            "sympy + z3",
            "algebraic steps of the proof; the maximum principle and weak Harnack are not encoded",
        ),
        check_lemma_6_1,
    ),
    (
        Check(
            "thm11.1.l2", "the L2 identity for Stein's square function", "Thm 11.1", "sympy", "symbolic in alpha > 1/2"
        ),
        check_square_function_l2,
    ),
]

NOT_ENCODED: List[Check] = [
    Check(
        "lemma2.1",
        "the lifted tensor B is PSD with divergence-free columns",
        "Lemma 2.1",
        "-",
        "needs holomorphic extension and tube-coordinate vector fields over a general symmetric system",
        NOT_ENCODABLE,
    ),
    Check(
        "prop2.2",
        "A0 is smooth, PSD, tangent to Phi, with divergence-free real columns",
        "Prop 2.2",
        "-",
        "needs the quaternionic push-forward (2.7) of a finite mode sum",
        NOT_ENCODABLE,
    ),
    Check(
        "lemma3.2.quaternionic",
        "Moore determinant identities for quaternionic Hermitian matrices",
        "Lemma 3.2",
        "-",
        "the Moore determinant is not available in SymPy; only the real-symmetric model was checked",
        NOT_ENCODABLE,
    ),
    Check(
        "prop4.2",
        "energy balance (4.12) on moving fibers",
        "Prop 4.2",
        "-",
        "distributional Green identity on a moving domain",
        NOT_ENCODABLE,
    ),
    Check(
        "prop5.1",
        "fixed-fiber bounds (5.1)-(5.3)",
        "Prop 5.1",
        "-",
        "kernel majorants, comparison principle and Gaussian inversion estimates",
        NOT_ENCODABLE,
    ),
    Check(
        "thmA.1",
        "periodic quaternionic Dirichlet problem",
        "Theorem A.1",
        "-",
        "continuity method and a priori estimates",
        NOT_ENCODABLE,
    ),
]


# Negative controls: each mutant changes one constant or term of a checked identity; every one must come out REFUTED.
def _mutant_lemma_4_3_coefficient(a: _Asserter) -> None:
    e = _energy_terms(*ENERGY_MODELS[0])
    a.eq(
        "Lemma 4.3 with n/(n+1) in place of (n-1)/(n+1)",
        e["Ez"] + e["X0"],
        sp.Rational(2, 3) * e["X0"] + e["Q"] / (e["lam"] * 6),
    )


def _mutant_stein_tomas_exponent(a: _Asserter) -> None:
    pst = 2 * (n + 1) / (n - 1)
    a.eq(
        "focusing exponent d - dp/2 equals -1 at the Stein-Tomas exponent 2(n+1)/(n-1)", (n - 1) - (n - 1) * pst / 2, -1
    )


def _mutant_remark_6_2_without_log(a: _Asserter) -> None:
    s, b = sp.symbols("s b", positive=True)
    D = sp.log(3 / b)
    g = s**2 / (4 * D)
    a.eq("Remark 6.2 with g = s^2/(4D): Lap g = p", sp.diff(g, s, 2) + sp.diff(g, s) / s, sp.log(3 / s) / D)


def _mutant_full_rank_background(a: _Asserter) -> None:
    th, b0, b1 = sp.symbols("theta b0 b1", positive=True)
    D = _sym(2, "d")
    Bm = sp.diag(b0, b1)
    a.eq(
        "two-term segment formula with a rank-two background",
        ((1 - th) * Bm + th * D).det(),
        th**2 * D.det() + (1 - th) * th * _frob(D.adjugate(), Bm),
    )


def _mutant_real_translation(a: _Asserter) -> None:
    om = sp.Matrix(sp.symbols("o0:3", real=True))
    thv = sp.Matrix(sp.symbols("th0:3", real=True))
    a.eq(
        "1 + omega.theta = |omega - theta|^2/2 (sign of the light-ray translation flipped)",
        1 + (om.T * thv)[0] - ((om - thv).T * (om - thv))[0] / 2,
        1 - ((om.T * om)[0] + (thv.T * thv)[0]) / 2,
    )


MUTANTS: List[Tuple[str, str, Callable[[_Asserter], None]]] = [
    ("lemma4.3.model", "coefficient n/(n+1) instead of (n-1)/(n+1)", _mutant_lemma_4_3_coefficient),
    ("exponent.focusing", "Stein-Tomas exponent instead of pc", _mutant_stein_tomas_exponent),
    ("remark6.2", "comparison function without the log term", _mutant_remark_6_2_without_log),
    ("lemma4.3.model", "rank-two background", _mutant_full_rank_background),
    ("eq2.2-2.4", "translation by +i instead of -i", _mutant_real_translation),
]


def run_mutants() -> List[Dict[str, Any]]:
    out = []
    for base, label, fn in MUTANTS:
        check = Check(f"mutant:{base}", label, base, "sympy", "negative control")
        fn(_Asserter(check))
        check.status = VERIFIED if all(x["holds"] for x in check.assertions) else REFUTED
        out.append({"base": base, "label": label, "status": check.status, "expected": REFUTED})
    return out


def run_checks() -> List[Dict[str, Any]]:
    results = []
    for template, fn in CHECKS:
        check = Check(**{k: v for k, v in asdict(template).items() if k not in ("assertions", "status")})
        try:
            fn(_Asserter(check))
            check.status = VERIFIED if check.assertions and all(x["holds"] for x in check.assertions) else REFUTED
        except Exception as exc:  # an encoding failure is not a refutation
            check.status = NOT_ENCODABLE
            check.note = f"encoding raised {type(exc).__name__}: {exc}"
        results.append(asdict(check))
    results.extend(asdict(c) for c in NOT_ENCODED)
    return results


def anatomy_report() -> Dict[str, Any]:
    checks = run_checks()
    return {
        "case": "Local smoothing for the Euclidean wave equation: proof anatomy",
        "commit": COMMIT,
        "repository": FIDELITY_SOURCE["repository"],
        "sources": SOURCES,
        "dag": dag_report(),
        "checks": checks,
        "mutants": run_mutants(),
        "summary": {s: sum(1 for c in checks if c["status"] == s) for s in (VERIFIED, REFUTED, NOT_ENCODABLE)},
    }


def mermaid() -> str:
    """The internal DAG as a Mermaid flowchart (edges point from premise to consequence); imports are omitted."""
    lines = ["flowchart BT"]
    for key in topological_order():
        title = NODES[key][0].replace('"', "'")
        lines.append(f'  {key.replace(".", "_").replace("-", "_")}["{key}: {title}"]')
    for key, (_, _, premises, _) in NODES.items():
        for prem in premises:
            lines.append(f"  {prem.replace('.', '_').replace('-', '_')} --> {key.replace('.', '_').replace('-', '_')}")
    return "\n".join(lines)
