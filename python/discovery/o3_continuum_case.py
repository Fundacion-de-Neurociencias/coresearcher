"""
python/discovery/o3_continuum_case.py - Rehearsal of the pre-registered existence audit (ADR-DISCOVERY-077) on
openai/math family 215, "The canonical massive continuum limit of the two-dimensional O(3) model".

The paper claims a continuum theory: OS axioms, a nonzero connected four-point function, a unique vacuum and a
mass gap (Theorem 1.1, Theorem 1.2, Corollary 1.3). The family's only Lean statement,
lean/ComparatorChallenges/ClassicalON.lean, proves exponential decay of lattice correlations on finite subgraphs of
Z^2. Four parts, all about formal statement fidelity (not the proof's correctness, credit or announcement):

1. coverage: the Lean statement is transcribed into the checklist vocabulary (each fact quotes the Lean text) and
   every obligation of the paper's claim is decided: COVERED, OBJECT_DIFFERS or NOT_ADDRESSED;
2. trivial-witness probe of the paper's claim (it should exclude every catalogued cheap model) and of the part of
   the claim the Lean statement covers (a cheap model satisfying it means the formal artifact cannot certify the
   claimed object);
3. exclusion lint of the Lean file (syntactic; a human confirms);
4. a coverage map of the family's papers and their formal status.

Sources are pinned to one commit of github.com/openai/math and read as data. ClassicalON.lean/.json are vendored
(Apache-2.0) in examples/o3-continuum-rehearsal/ and checked against their SHA-256 before use.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List

from python.discovery import preregistration
from python.discovery.preregistration import Coverage
from python.discovery.trivial_witness import lint_exclusions, probe

ROOT = Path(__file__).resolve().parent.parent.parent
CASE_DIR = ROOT / "examples" / "o3-continuum-rehearsal"
CHECKLIST = CASE_DIR / "o3_continuum_claim.v1.json"

SOURCE = {
    "repository": "https://github.com/openai/math",
    "commit": "4eaee87548250b2682affda7d05d947c05554bae",
    "retrieved": "2026-10-30",
    "family": "215. Canonical O(3) continuum limit and exact O(4) mass asymptotics",
    "paper": "preprints/The-canonical-massive-continuum-limit-of-the-two-dimensional-O3-model-October-4-2026/"
    "massive-continuum-o3.pdf",
    "paper_sha256": "e75bfb353c2d3374503bbb899eb01dc21c94ed49fede6b3eb48f7ffce64527b2",
    "paper_readme_sha256": "6b32afbadf435843c325fd3be749f009a45fd764387f9f2d7293bc0c9f5cb9b8",
    "contents": "CONTENTS.md",
    "contents_sha256": "080badcb677fb80be0e695c21a8ec88bcb3a46dd3e3078ca10061e6b289be175",
    "scope_note": "lean/docs/215.md",
    "scope_note_sha256": "41ed31b3d5b0f9c0ce5df3604527f17b26eec23b225a7a2184f5a9c2d936ac30",
    "lean_statements": "lean/ComparatorChallenges/ClassicalON.lean",
    "lean_statements_sha256": "c2f5f88455b811eb6b56c1ae80ff91f4e398e18e7c7fbeee6daca8da4122d696",
    "comparator_config": "lean/ComparatorChallenges/ClassicalON.json",
    "comparator_config_sha256": "47cb3623915c8cfcc35099fabd0c44173afa72b706eb0526c4b8d3855e789252",
    "solution_main": "lean/OAI/Probability/ClassicalON/Main.lean",
    "solution_main_sha256": "0e4bca8c6b8fe89ffec32eda5d3222af85062a2e3e685729f41578076b528c8a",
    "solution_model": "lean/OAI/Probability/ClassicalON/Model.lean",
    "solution_model_sha256": "1db13f5d22a51650533bc85ae609b23eb9b4a9927cac11e50c5642b52b1da378",
    "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"],
}

VENDORED = {
    "ClassicalON.lean": SOURCE["lean_statements_sha256"],
    "ClassicalON.json": SOURCE["comparator_config_sha256"],
}


def vendored(name: str) -> str:
    data = (CASE_DIR / name).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != VENDORED[name]:
        raise ValueError(f"{name} does not match the pinned SHA-256 ({digest} != {VENDORED[name]}).")
    return data.decode("utf-8")


def checklist() -> preregistration.Checklist:
    return preregistration.load(CHECKLIST)


# ---------------------------------------------------------------------------
# Part 1: what the Lean statement says, in the checklist vocabulary
# ---------------------------------------------------------------------------

# The n = 3 instance of `OAI.ClassicalON.main : ExponentialDecay`. Each fact quotes the Lean text it rests on.
LEAN_TRANSCRIPTION: Dict[str, Any] = {
    "statement": "OAI.ClassicalON.main : ExponentialDecay (instance n = 3)",
    "facts": [
        "field == 'O3_sigma'",
        "dim == 2",
        "volume == 'finite_box'",
        "spacing == 1",
        "continuum_limit == 'none'",
        "two_point_decay == 'exponential'",
    ],
    "fact_sources": {
        "field == 'O3_sigma'": "abbrev Spin (n : ℕ) := ↥(Metric.sphere (0 : EuclideanSpace ℝ (Fin n)) 1); "
        "interaction = ∑ e, b e * ⟪σ e.1, σ e.2⟫ over nearest-neighbour edges; ∀ (n : ℕ), 3 ≤ n → ... (n = 3)",
        "dim == 2": "abbrev Site := ℤ × ℤ",
        "volume == 'finite_box'": "structure LatticeGraph where vertices : Finset Site; edges : Finset ...",
        "spacing == 1": "sites in ℤ × ℤ, distances by siteDistance in lattice units; no spacing parameter",
        "continuum_limit == 'none'": "no limit of any kind appears in the statement",
        "two_point_decay == 'exponential'": "correlation n G b x y ≤ A * Real.exp (-m * siteDistance x.val y.val)",
    },
    "quotes": {
        "O3-FIELD": "Spin n = unit sphere in EuclideanSpace ℝ (Fin n); ∀ n ≥ 3",
        "O3-DIM2": "abbrev Site := ℤ × ℤ",
        "O3-INFINITE-VOLUME": "vertices : Finset Site",
        "O3-CONTINUUM": "Site := ℤ × ℤ; no spacing, no limit",
        "LAT-DECAY": "0 ≤ correlation n G b x y ∧ correlation n G b x y ≤ A * Real.exp (-m * siteDistance x.val y.val)",
    },
    "notes": {
        "O3-FIELD": "The Lean statement quantifies over every n ≥ 3, so in this coordinate it is stronger than needed: "
        "n = 3 is one instance.",
        "O3-INFINITE-VOLUME": "The bound is uniform over all finite subgraphs, a volume-uniform estimate, but no "
        "infinite-volume measure is defined or asserted. lean/docs/215.md says the infinite-volume limit is not "
        "included.",
        "O3-CONTINUUM": "The object is the lattice model at unit spacing; the statement has no rescaled field (1.3), "
        "no susceptibility or correlation-length normalization and no beta -> infinity limit.",
        "O3-INTERNAL-SYMMETRY": "The lattice measure is O(n)-invariant by construction, but the statement asserts no "
        "invariance and the paper's claim is about the continuum hierarchy.",
        "O3-MASS-GAP": "Exponential decay in lattice units at fixed beta is a lattice correlation-length statement, "
        "not the continuum Hamiltonian gap of Theorem 1.2 (iii), which needs the decay in physical units uniformly "
        "as beta -> infinity.",
        "O3-NONTRIVIAL": "Nothing about four-point functions appears.",
        "LAT-DECAY": "Matches the companion paper's abstract: every n ≥ 3, every beta > 0, uniform over finite "
        "free-boundary subgraphs and edge strengths in [0, beta].",
    },
}


def coverage_rows() -> List[Dict[str, Any]]:
    rows = preregistration.coverage(checklist(), LEAN_TRANSCRIPTION)
    return [row.__dict__ for row in rows]


def covered_clauses(rows: List[Dict[str, Any]], claim_ids: List[str]) -> Dict[str, str]:
    """The part of the claim the formal statement establishes: its COVERED obligations among `claim_ids`."""
    return {r["obligation"]: r["clause"] for r in rows if r["coverage"] == Coverage.COVERED.value and r["obligation"] in claim_ids}


# ---------------------------------------------------------------------------
# Part 4: the family's papers and their formal status
# ---------------------------------------------------------------------------

COMPARATOR = "COMPARATOR"  # A Comparator reference statement exists.
NOT_FORMALIZED = "NOT_FORMALIZED"  # No Lean statement located; lean/docs/215.md lists none.

FAMILY_COVERAGE: List[Dict[str, str]] = [
    {
        "item": "O(3) continuum, Theorem 1.1 (i)",
        "claim": "the rescaled fields (1.3) converge jointly in law and in all moments through all real beta -> infinity",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "no continuum field, no limit in any Lean statement of the family",
    },
    {
        "item": "O(3) continuum, Theorem 1.1 (ii)",
        "claim": "Schwinger distributions converge in the strong topology of S'((R^2)^n)",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "no Schwinger distribution is defined",
    },
    {
        "item": "O(3) continuum, Theorem 1.1 (iii)",
        "claim": "unit susceptibility and second-moment length; equals the Theorem 1.2 hierarchy after rescaling",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "-",
    },
    {
        "item": "O(3) continuum, Theorem 1.2 (i)",
        "claim": "convergence along the prescribed trajectory beta_N; same limit from tori tending to the plane",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "-",
    },
    {
        "item": "O(3) continuum, Theorem 1.2 (ii) and Corollary 1.3",
        "claim": "Euclidean and internal O(3) invariance, reflection positivity, symmetry, clustering, factorial "
        "bounds; reconstruction of a local unitary relativistic theory",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "none of the OS axioms is stated (exclusion lint: no marker)",
    },
    {
        "item": "O(3) continuum, Theorem 1.2 (iii)",
        "claim": "unique vacuum, nonzero vacuum complement, H_phys >= m > 0 on it",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "lattice exponential decay at fixed beta is not the continuum gap",
    },
    {
        "item": "O(3) continuum, Theorem 1.2 (iv)",
        "claim": "nonzero connected four-point distribution on separated time supports",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "non-triviality is not stated",
    },
    {
        "item": "Isolated particle pole (October 4, 2026)",
        "claim": "the vector two-point spectral measure has an isolated atom at the lowest mass",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "-",
    },
    {
        "item": "Exact O(4) mass asymptotics (October 5, 2026)",
        "claim": "m_lat(beta) ~ 32 exp(pi/4 - 1/2) sqrt(beta) exp(-pi beta)",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "lean/docs/215.md: the O(4) spectral-gap claim is not included",
    },
    {
        "item": "Sharp O(4) mass bounds (September 23, 2026)",
        "claim": "full transfer gap within constant multiples of sqrt(beta) exp(-pi beta); positive gap at every beta",
        "status": NOT_FORMALIZED,
        "lean": "-",
        "fidelity": "lean/docs/215.md: the O(4) spectral-gap claim is not included",
    },
    {
        "item": "Exponential decay in classical O(n) models (September 23, 2026)",
        "claim": "exponential decay for n >= 3, every beta > 0, uniform over finite free-boundary subgraphs",
        "status": COMPARATOR,
        "lean": "OAI.ClassicalON.main : ExponentialDecay",
        "fidelity": "matches the abstract (n >= 3, beta > 0, finite subgraphs, edge strengths in [0, beta]); "
        "range not audited with z3 here",
    },
]

FILES_READ = [
    "CONTENTS.md (family 215 entry)",
    "lean/docs/215.md",
    "lean/ComparatorChallenges/ClassicalON.lean",
    "lean/ComparatorChallenges/ClassicalON.json",
    "lean/OAI/Probability/ClassicalON/Main.lean",
    "lean/OAI/Probability/ClassicalON/Model.lean",
    "the file list of lean/OAI/Probability/ClassicalON/ (117 modules; no continuum, Schwinger or OS module name)",
    "the paper massive-continuum-o3.pdf, Section 1 (Theorems 1.1, 1.2, Corollary 1.3) and the abstract",
]


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def case_report() -> Dict[str, Any]:
    c = checklist()
    rows = coverage_rows()
    paper_claim = {o.id: o.formal_clause for o in c.in_claim("O3")}
    covered = covered_clauses(rows, list(paper_claim))
    probes = {
        "paper_claim": probe(c, paper_claim, statement="paper: Theorem 1.1, Theorem 1.2, Corollary 1.3").to_dict(),
        "lean_covered_part_of_claim": probe(
            c, covered, statement="the part of the paper's claim that ClassicalON.main covers"
        ).to_dict(),
    }
    lint = lint_exclusions(vendored("ClassicalON.lean"), c, theorem="main", file=SOURCE["lean_statements"], claim="O3")
    counts = {s.value: sum(r["coverage"] == s.value for r in rows) for s in Coverage}
    return {
        "source": SOURCE,
        "checklist": {"id": c.id, "version": c.version, "sha256": c.sha256, "lock": c.lock},
        "lean_transcription": LEAN_TRANSCRIPTION,
        "coverage": rows,
        "coverage_counts": counts,
        "probes": probes,
        "exclusion_lint": lint.to_dict(),
        "family_coverage": FAMILY_COVERAGE,
        "files_read": FILES_READ,
        "kernel_check": {
            "status": "NOT RUN",
            "reason": "Comparator needs landrun (Linux Landlock) and a full openai/math build; neither was run in "
            "this session. Nothing here depends on whether ClassicalON.main is proved.",
        },
    }
