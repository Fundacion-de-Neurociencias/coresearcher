"""
python/discovery/openai_math_strategy.py - Reverse engineering the problem-solving strategy visible in the openai/math
release: corpus structure, self-citation graph, and a coded reading of the ten released reasoning summaries.

Scope: what the released texts show about how results were produced, and what that implies for checking such
results. It does not judge whether any result is correct, its credit or its novelty. Everything is pinned to one
commit and was read as untrusted data.

Pure functions (parsing, graph statistics, aggregation) live here and are tested offline. Downloading the pinned
sources and writing `examples/openai-math-strategy/corpus_stats.json` is done by
`scripts/cases/openai_math_corpus.py`.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Set, Tuple

COMMIT = "7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a"
REPOSITORY = "https://github.com/openai/math"
SOURCE_SHA256 = {
    "overview.tex": "39de58f1bf2185eb11d444a58aec4c7c7530419f3127deb9261fa46e044a4135",
    "lean/formalization.yaml": "b8e7072ab9ac195a290110d78c3a3497608ce76ac5b67d307685f38408299b39",
    "CONTENTS.md": "080badcb677fb80be0e695c21a8ec88bcb3a46dd3e3078ca10061e6b289be175",
}
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"

# ---------------------------------------------------------------------------
# Corpus parsing
# ---------------------------------------------------------------------------


def _brace_args(src: str, i: int, k: int) -> Tuple[List[str], int]:
    out = []
    for _ in range(k):
        i = src.index("{", i)
        depth, j = 0, i
        while True:
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(src[i + 1 : j])
        i = j + 1
    return out, i


def parse_overview(src: str) -> List[Dict[str, Any]]:
    """Families from overview.tex: number, discipline, title, description, manuscripts (directory and date)."""
    families, discipline, pos = [], None, 0
    for m in re.finditer(r"\\(cataloguesection|resultentry)\b", src):
        if m.start() < pos:
            continue
        if m.group(1) == "cataloguesection":
            (discipline, _), pos = _brace_args(src, m.end(), 2)
            continue
        (num, title, desc, links), pos = _brace_args(src, m.end(), 4)
        manuscripts = []
        for path, directory in re.findall(
            r"\\href\{https://github.com/openai/math/blob/main/(preprints/([^/]+)/[^}]+)\}\{", links
        ):
            date = re.search(rf"({MONTHS})-(\d+)-(\d{{4}})$", directory)
            manuscripts.append(
                {"dir": directory, "path": path, "date": f"{date.group(1)} {date.group(2)}" if date else None}
            )
        lead = re.match(r"\W*(\w+)", desc)
        families.append(
            {
                "num": num,
                "discipline": discipline,
                "title": title,
                "lead_verb": lead.group(1) if lead else "",
                "manuscripts": manuscripts,
            }
        )
    return families


OAI_KEY = re.compile(rf"OAI:([A-Za-z0-9().,'_+-]+?-(?:{MONTHS})-\d+-\d{{4}})")


def citation_edges(bib_texts: Dict[str, Iterable[str]]) -> Dict[str, Set[str]]:
    """Map each preprint directory to the OAI preprints its bibliography files cite (self-citations dropped)."""
    edges: Dict[str, Set[str]] = defaultdict(set)
    for directory, texts in bib_texts.items():
        for text in texts:
            for key in OAI_KEY.findall(text):
                if key != directory:
                    edges[directory].add(key)
    return dict(edges)


def formalized_dirs(formalization_yaml: str) -> Set[str]:
    return set(re.findall(r"id: \.\./preprints/([^/]+)/", formalization_yaml))


# ---------------------------------------------------------------------------
# Graph statistics (no networkx dependency)
# ---------------------------------------------------------------------------


def strongly_connected_components(edges: Dict[str, Set[str]]) -> List[Set[str]]:
    """Tarjan's algorithm, iterative."""
    nodes = set(edges) | {c for cs in edges.values() for c in cs}
    index: Dict[str, int] = {}
    low: Dict[str, int] = {}
    on_stack: Set[str] = set()
    stack: List[str] = []
    comps: List[Set[str]] = []
    counter = 0
    for root in sorted(nodes):
        if root in index:
            continue
        work = [(root, iter(sorted(edges.get(root, ()))))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, it = work[-1]
            advanced = False
            for nxt in it:
                if nxt not in index:
                    index[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack.add(nxt)
                    work.append((nxt, iter(sorted(edges.get(nxt, ())))))
                    advanced = True
                    break
                if nxt in on_stack:
                    low[node] = min(low[node], index[nxt])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                comp = set()
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.add(w)
                    if w == node:
                        break
                comps.append(comp)
    return comps


def longest_chain(edges: Dict[str, Set[str]]) -> int:
    """Number of strongly connected components on the longest path of the condensed citation DAG."""
    comps = strongly_connected_components(edges)
    comp_of = {n: i for i, c in enumerate(comps) for n in c}
    succ: Dict[int, Set[int]] = defaultdict(set)
    for a, cs in edges.items():
        for c in cs:
            if comp_of[a] != comp_of[c]:
                succ[comp_of[a]].add(comp_of[c])
    memo: Dict[int, int] = {}
    order = sorted(range(len(comps)))  # Tarjan emits components in reverse topological order
    for i in order:
        memo[i] = 1 + max((memo[j] for j in succ[i] if j in memo), default=0)
    return max(memo.values(), default=0)


def _date_key(directory: str):
    m = re.search(r"(September|October)-(\d+)-2026$", directory)
    return (0 if m.group(1) == "September" else 1, int(m.group(2))) if m else None


def corpus_stats(
    families: List[Dict[str, Any]], edges: Dict[str, Set[str]], formalized: Set[str], dirs_with_bib: int
) -> Dict[str, Any]:
    dir2fam = {m["dir"]: f["num"] for f in families for m in f["manuscripts"]}
    fam = {f["num"]: f for f in families}
    n_edges = sum(len(c) for c in edges.values())
    intra = sum(1 for a, cs in edges.items() for c in cs if dir2fam.get(a) and dir2fam.get(a) == dir2fam.get(c))
    fam_pairs = {
        (dir2fam[a], dir2fam[c])
        for a, cs in edges.items()
        for c in cs
        if a in dir2fam and c in dir2fam and dir2fam[a] != dir2fam[c]
    }
    cross_disc = sum(fam[a]["discipline"] != fam[b]["discipline"] for a, b in fam_pairs)
    direction = Counter()
    for a, cs in edges.items():
        for c in cs:
            ka, kc = _date_key(a), _date_key(c)
            if ka and kc:
                direction["earlier" if kc < ka else "same day" if kc == ka else "later"] += 1
    sccs = [c for c in strongly_connected_components(edges) if len(c) > 1]
    formal_fams = {dir2fam[d] for d in formalized if d in dir2fam}
    lead = Counter(f["lead_verb"] for f in families)
    negative = [f["num"] for f in families if f["lead_verb"] in ("Disproves", "Constructs")]
    dates = Counter(m["date"] for f in families for m in f["manuscripts"])
    return {
        "families": len(families),
        "manuscripts": sum(len(f["manuscripts"]) for f in families),
        "disciplines": dict(Counter(f["discipline"] for f in families).most_common()),
        "family_size_distribution": dict(sorted(Counter(len(f["manuscripts"]) for f in families).items())),
        "multi_manuscript_families": sum(len(f["manuscripts"]) > 1 for f in families),
        "manuscripts_by_date_top": dict(dates.most_common(8)),
        "lead_verbs": dict(lead.most_common(8)),
        "citations": {
            "dirs_with_bib": dirs_with_bib,
            "citing_papers": len(edges),
            "edges": n_edges,
            "intra_family_edges": intra,
            "cross_family_pairs": len(fam_pairs),
            "cross_discipline_pairs": cross_disc,
            "direction": dict(direction),
            "mutual_citation_components": len(sccs),
            "mutual_citation_component_sizes": dict(sorted(Counter(len(c) for c in sccs).items())),
            "longest_chain": longest_chain(edges),
        },
        "formalization": {
            "formalized_papers": len(formalized),
            "families_with_formalized_paper": len(formal_fams),
            "negative_or_constructive_families": len(negative),
            "negative_or_constructive_formalized": sum(n in formal_fams for n in negative),
            "by_discipline": {
                d: [sum(f["num"] in formal_fams for f in families if f["discipline"] == d), n]
                for d, n in Counter(f["discipline"] for f in families).most_common()
            },
        },
    }


# ---------------------------------------------------------------------------
# Coded reading of the ten released reasoning summaries
# ---------------------------------------------------------------------------

# Hand-coded from a full reading of each summary (four parallel readers, spot-checked against the text). Counts of
# abandoned routes are approximate (the summaries paraphrase); counts of sections and verbatim excerpts are exact
# (`trace_text_counts`). "pivot" is the move the summary presents as the turning point. "audit_share" is the fraction
# of sections that are mainly self-audit. "endgame" is the summarizer's characterization of how the run ended.
TRACES: List[Dict[str, Any]] = [
    {
        "family": "007",
        "file": "ordinary-two-point-correlations",
        "prompt": "conjecture stated; Part II 'Prove that'",
        "opening": "literature-gap map (exceptional scales, log averaging)",
        "abandoned_routes": 10,
        "falsification": ["prime-phase counterexample attempt", "benchmark theorems"],
        "pivot": "adapt one model paper (Pilatte divisor graphs) with inclusion-exclusion",
        "positivity_or_sign_trick": True,
        "cross_field_import": False,
        "audit_share": 0.2,
        "endgame": "conditional on named lemmas",
        "builds_on_own_output": False,
    },
    {
        "family": "017",
        "file": "irrationality-exponent-of-pi",
        "prompt": "goal-driven (mu < 5/2, then mu = 2); no prompt block shown",
        "opening": "reduce Flint-Hills to mu < 5/2; analogy to OpenAI's Catalan paper",
        "abandoned_routes": 35,
        "falsification": ["proves-too-much tests (Liouville numbers, every transcendental)", "Dirichlet barrier"],
        "pivot": "interpolation determinant with ampleness on a blow-up",
        "positivity_or_sign_trick": True,
        "cross_field_import": True,
        "audit_share": 0.27,
        "endgame": "claimed; hypotheses of vanishing theorems unchecked; 'too strong' warning noted, not acted on",
        "builds_on_own_output": True,
    },
    {
        "family": "087",
        "file": "symmetric-and-general-mahler-conjectures",
        "prompt": "yes/no question; 'prove or disprove'; 'resolve the conjecture'",
        "opening": "literature recall, then a single conic/Laplace reformulation (orthant as equality model)",
        "abandoned_routes": 60,
        "falsification": ["extremal bodies: simplex, orthant, ball, cross-polytope, PSD/Lorentz cones"],
        "pivot": "Part I: complexified slabs + complex-Hessian positivity + flux; Part III: Gaussian Riccati profiles",
        "positivity_or_sign_trick": True,
        "cross_field_import": True,
        "audit_share": 0.2,
        "endgame": "Part I complete; Part III conditional on scalar inequalities",
        "builds_on_own_output": False,
    },
    {
        "family": "102",
        "file": "basic-semidefinite-threshold-np-hardness",
        "prompt": "'prove or refute'; conventions and refutation criteria fixed",
        "opening": "loophole check of conventions; observes the claim implies UGC-type hardness",
        "abandoned_routes": 30,
        "falsification": ["cheating provers against its own tests", "known algorithms (GW, CMM)"],
        "pivot": "nonlinear-vs-linear decoder gadget",
        "positivity_or_sign_trick": False,
        "cross_field_import": True,
        "audit_share": 0.5,
        "endgame": "proposed affirmative argument; uniformity provisionally accepted",
        "builds_on_own_output": False,
    },
    {
        "family": "159",
        "file": "quasipolynomial-arithmetic-progressions",
        "prompt": "'prove or disprove'; Part II: 'Use the previous bounds you have done'",
        "opening": "quantitative restatement; anchor on best bounds; locate where losses compound",
        "abandoned_routes": 30,
        "falsification": ["Keleti/Rankin counterexample probes", "explicit examples (Heisenberg, quadratic phase)"],
        "pivot": "negative cross-kernel turns an AP deficit into a density excess",
        "positivity_or_sign_trick": True,
        "cross_field_import": False,
        "audit_share": 0.28,
        "endgame": "proposed; a circularity concern left unresolved",
        "builds_on_own_output": True,
    },
    {
        "family": "197",
        "file": "kaplansky-direct-finiteness-characteristic-two",
        "prompt": "'resolve by proof or rigorous counterexample'; references and milestones supplied",
        "opening": "map known sufficient hypotheses; organize around the idempotent defect",
        "abandoned_routes": 40,
        "falsification": ["consistency with known positive theorems (sofic, surjunctive)"],
        "pivot": "affine-line hypergraph / quantum-code construction over F_2",
        "positivity_or_sign_trick": False,
        "cross_field_import": True,
        "audit_share": 0.45,
        "endgame": "counterexample claimed; Linnik and local-lemma dependencies open",
        "builds_on_own_output": False,
    },
    {
        "family": "221",
        "file": "mezard-parisi-formula",
        "prompt": "'complete rigorous solution ... even if open'; computer assistance discouraged",
        "opening": "frame as missing lower bound; counterexample sweep over four boundary cases",
        "abandoned_routes": 7,
        "falsification": ["boundary-case counterexample hunt"],
        "pivot": "shift branching depths by one; squared-difference positivity",
        "positivity_or_sign_trick": True,
        "cross_field_import": False,
        "audit_share": 0.33,
        "endgame": "full proof claimed; mild hedging",
        "builds_on_own_output": False,
    },
    {
        "family": "271",
        "file": "spontaneous-magnetization-quantum-heisenberg-ferromagnet",
        "prompt": "'prove or refute'; negative resolution defined",
        "opening": "survey probabilistic representations (Toth interchange)",
        "abandoned_routes": 12,
        "falsification": ["'proves too much' audit"],
        "pivot": "determinant / exterior-power stability (algebraic positivity)",
        "positivity_or_sign_trick": True,
        "cross_field_import": False,
        "audit_share": 0.67,
        "endgame": "claimed; uniform estimates 'claimed'",
        "builds_on_own_output": False,
    },
    {
        "family": "287",
        "file": "free-group-factor-isomorphism",
        "prompt": "'determine whether ... and prove the answer'",
        "opening": "survey invariants (bets on non-isomorphism first)",
        "abandoned_routes": 35,
        "falsification": ["self-made toy counterexamples"],
        "pivot": "flip to constructive side via ergodic-theory analogy (Ornstein-Weiss); ODE flow on generators",
        "positivity_or_sign_trick": False,
        "cross_field_import": True,
        "audit_share": 0.1,
        "endgame": "isomorphism claimed against community expectation; conditional on flow and generation steps",
        "builds_on_own_output": False,
    },
    {
        "family": "362",
        "file": "relativistic-vlasov-maxwell",
        "prompt": "'determine whether the following assertion is true'; negative resolution defined",
        "opening": "reduce to a known continuation criterion; repair a hypothesis gap first",
        "abandoned_routes": 6,
        "falsification": ["'is there a conservation law obstructing?'", "exponent contradiction"],
        "pivot": "signed integration by parts before absolute values",
        "positivity_or_sign_trick": True,
        "cross_field_import": False,
        "audit_share": 0.8,
        "endgame": "asserted; summarizer: key estimates not established by the cited theorem",
        "builds_on_own_output": False,
    },
]

PHASES = [
    "pose a decision problem with fixed conventions",
    "map the literature gap; reduce to a known criterion",
    "falsification sweep (counterexamples, proves-too-much, extremal cases)",
    "breadth-first route search with named quantitative kill criteria",
    "pivot on a structural trick (often positivity/sign or a cross-field import)",
    "build the architecture; fix parameter order and constants",
    "self-audit by re-derivation",
    "claim, with named open obligations",
]


def trace_aggregates(traces: List[Dict[str, Any]] = TRACES) -> Dict[str, Any]:
    n = len(traces)
    routes = sorted(t["abandoned_routes"] for t in traces)
    return {
        "traces": n,
        "positivity_or_sign_pivot": sum(t["positivity_or_sign_trick"] for t in traces),
        "cross_field_import_pivot": sum(t["cross_field_import"] for t in traces),
        "builds_on_own_output": sum(t["builds_on_own_output"] for t in traces),
        "abandoned_routes_median": (routes[n // 2 - 1] + routes[n // 2]) / 2 if n % 2 == 0 else routes[n // 2],
        "abandoned_routes_range": [routes[0], routes[-1]],
        "audit_share_median": sorted(t["audit_share"] for t in traces)[n // 2],
        "decision_form_prompts": sum(
            bool(re.search(r"prove or|determine whether|resolve|yes/no", t["prompt"])) for t in traces
        ),
    }


def trace_text_counts(text: str) -> Dict[str, int]:
    """Exact counts from a summary's text: numbered sections and verbatim excerpts of raw reasoning."""
    return {
        "sections": len(re.findall(r"\n\d{1,2} [A-Z][^\n]{3,100}\n", text)),
        "verbatim_excerpts": text.count("VERBATIM EXCERPT"),
    }
