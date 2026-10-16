"""
python/discovery/ed_polarity_case.py - Showcase case: the Error Diffusion polarity claim as a formal hypothesis.

Source: Sakana AI, "Agentic Scientist" (arXiv:2610.18933), appendix G.4 and Table 6. Their strict Error Diffusion
(ED) rubric asks, in natural language, for no backpropagation and no transport through transposed weights, a local
update driven by one global error sign, and "polarity invariance". Their agent grades its own work against such
rubrics; Table 6 shows a loose rubric under which the agent reached 0.9694 validation accuracy without implementing
ED. This module turns the mathematical content of the rubric into a decidable claim (ADR-DISCOVERY-059/060) and
shows which assumptions it needs.

Network (layers 0..L, width w per stream, layer 0 is the input):

    p_i = f(p_{i-1} W_pp^i - n_{i-1} W_np^i + b_p^i)
    n_i = f(n_{i-1} W_nn^i - p_{i-1} W_pn^i + b_n^i)

The output is y = p_L[0] and the loss is e^2 / 2 with e = y - target. Write s^p_i[k] = dy/dp_i[k],
s^n_i[k] = dy/dn_i[k] and d^p_i[k], d^n_i[k] for f' at the pre-activation of p_i[k], n_i[k]. The chain rule gives
the scope of the hypothesis (definitions, not assumptions):

    s^p_L = (1, 0, ..., 0),  s^n_L = 0
    s^p_{i-1}[j] = sum_k s^p_i[k] d^p_i[k] W_pp^i[j,k] - sum_k s^n_i[k] d^n_i[k] W_pn^i[j,k]
    s^n_{i-1}[j] = - sum_k s^p_i[k] d^p_i[k] W_np^i[j,k] + sum_k s^n_i[k] d^n_i[k] W_nn^i[j,k]
    sg = sign(e)

A weight w of family F at layer i, from unit j of stream a to unit k of stream b, enters with sign tau_F (+1 for
W_pp and W_nn, -1 for W_np and W_pn). Its true gradient is

    dL/dw = e * tau_F * x^a_{i-1}[j] * d^b_i[k] * s^b_i[k]

where x^a_{i-1}[j] is the presynaptic activity, and the ED update, which uses only the global error sign and the
stream polarity sigma_b (+1 for p, -1 for n), is

    dw_ED = -(sigma_b * tau_F) * x^a_{i-1}[j] * d^b_i[k] * sg          (learning rate 1; any eta > 0 scales it)

Claims:
- polarity invariance: s^p_i >= 0 and s^n_i <= 0 at every layer 1..L-1;
- sign sufficiency: dw_ED * dL/dw <= 0 for every weight (the ED update never points uphill along any weight).

Assumptions (the auxiliaries the rubric leaves implicit or states in prose): each weight family is non-negative,
and f' >= 0 in each stream.

Abstraction: activities x and derivatives d are free real variables, not tied to a particular f. The claims are
universal, so a proof over this larger space holds for every real network; a counterexample over it could in
principle be unrealizable, which is why each refuted variant is also replayed on a concrete network with a concrete
activation by finite differences (`replay`).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from python.discovery.formal_hypothesis import FormalHypothesisError, Hypothesis, HypothesisEvaluator, Variable

STATUS = "SHOWCASE: written by the CoResearcher maintainers from the Sakana rubric text (arXiv:2610.18933, G.4)"
SOURCE = "arXiv:2610.18933, appendix G.4 and Table 6"

# Weight families: name -> (presynaptic stream, postsynaptic stream, sign with which the weight enters).
FAMILIES: Dict[str, Tuple[str, str, int]] = {
    "Wpp": ("p", "p", 1),
    "Wnp": ("n", "p", -1),
    "Wnn": ("n", "n", 1),
    "Wpn": ("p", "n", -1),
}
POLARITY = {"p": 1, "n": -1}

ASSUMPTIONS = ("Wpp>=0", "Wnp>=0", "Wnn>=0", "Wpn>=0", "fprime_p>=0", "fprime_n>=0")

SIGN_DEFINITION = "(e > 0 and sg == 1) or (e < 0 and sg == -1) or (e == 0 and sg == 0)"


def _w(family: str, layer: int, j: int, k: int) -> str:
    return f"{family}_{layer}_{j}_{k}"


def _d(stream: str, layer: int, k: int) -> str:
    return f"d{stream}_{layer}_{k}"


def _s(stream: str, layer: int, k: int) -> str:
    return f"s{stream}_{layer}_{k}"


def _x(stream: str, layer: int, j: int) -> str:
    return f"x{stream}_{layer}_{j}"


@dataclass(frozen=True)
class Weight:
    family: str
    layer: int
    j: int
    k: int

    @property
    def name(self) -> str:
        return _w(self.family, self.layer, self.j, self.k)

    def gradient(self) -> str:
        """dL/dw as a predicate-language expression."""
        pre, post, tau = FAMILIES[self.family]
        return (
            f"e * {tau} * {_x(pre, self.layer - 1, self.j)} * {_d(post, self.layer, self.k)}"
            f" * {_s(post, self.layer, self.k)}"
        )

    def ed_update(self) -> str:
        """The ED update with learning rate 1: global error sign times stream polarity."""
        pre, post, tau = FAMILIES[self.family]
        return f"{-POLARITY[post] * tau} * {_x(pre, self.layer - 1, self.j)} * {_d(post, self.layer, self.k)} * sg"


def weights(depth: int, width: int) -> List[Weight]:
    return [
        Weight(f, i, j, k) for i in range(1, depth + 1) for f in FAMILIES for j in range(width) for k in range(width)
    ]


def variables(depth: int, width: int) -> List[Variable]:
    names = ["e", "sg"]
    names += [w.name for w in weights(depth, width)]
    for i in range(1, depth + 1):
        for stream in ("p", "n"):
            names += [_d(stream, i, k) for k in range(width)]
            names += [_s(stream, i, k) for k in range(width)]
    for i in range(depth):
        for stream in ("p", "n"):
            names += [_x(stream, i, j) for j in range(width)]
    return [Variable(n, continuous=True) for n in names]


def chain_rule(depth: int, width: int) -> List[str]:
    """The scope: output sensitivities, the backward recursion of the chain rule, and sg = sign(e)."""
    defs = [SIGN_DEFINITION]
    defs += [f"{_s('p', depth, k)} == {1 if k == 0 else 0}" for k in range(width)]
    defs += [f"{_s('n', depth, k)} == 0" for k in range(width)]
    for i in range(depth, 1, -1):
        for j in range(width):
            pos = " + ".join(f"{_s('p', i, k)} * {_d('p', i, k)} * {_w('Wpp', i, j, k)}" for k in range(width))
            neg = " + ".join(f"{_s('n', i, k)} * {_d('n', i, k)} * {_w('Wpn', i, j, k)}" for k in range(width))
            defs.append(f"{_s('p', i - 1, j)} == ({pos}) - ({neg})")
            neg = " + ".join(f"{_s('p', i, k)} * {_d('p', i, k)} * {_w('Wnp', i, j, k)}" for k in range(width))
            pos = " + ".join(f"{_s('n', i, k)} * {_d('n', i, k)} * {_w('Wnn', i, j, k)}" for k in range(width))
            defs.append(f"{_s('n', i - 1, j)} == ({pos}) - ({neg})")
    return defs


def assumption_predicates(depth: int, width: int) -> Dict[str, str]:
    out = {}
    for family in FAMILIES:
        out[f"{family}>=0"] = " and ".join(
            f"{_w(family, i, j, k)} >= 0" for i in range(1, depth + 1) for j in range(width) for k in range(width)
        )
    for stream in ("p", "n"):
        out[f"fprime_{stream}>=0"] = " and ".join(
            f"{_d(stream, i, k)} >= 0" for i in range(1, depth + 1) for k in range(width)
        )
    return out


def polarity_claims(depth: int, width: int) -> List[str]:
    claims = []
    for i in range(1, depth):
        claims += [f"{_s('p', i, k)} >= 0" for k in range(width)]
        claims += [f"{_s('n', i, k)} <= 0" for k in range(width)]
    return claims


def sign_sufficiency_claims(depth: int, width: int) -> List[str]:
    return [f"({w.ed_update()}) * ({w.gradient()}) <= 0" for w in weights(depth, width)]


def ed_hypothesis(
    depth: int,
    width: int,
    drop: Tuple[str, ...] = (),
    claims: str = "all",
    hypothesis_id: Optional[str] = None,
) -> Hypothesis:
    """The ED polarity claim at a fixed depth and width, optionally without some assumptions.

    `claims`: "polarity", "sign" or "all".
    """
    unknown = set(drop) - set(ASSUMPTIONS)
    if unknown:
        raise ValueError(f"Unknown assumptions {sorted(unknown)}; choose from {ASSUMPTIONS}.")
    chosen: List[str] = []
    if claims in ("polarity", "all"):
        chosen += polarity_claims(depth, width)
    if claims in ("sign", "all"):
        chosen += sign_sufficiency_claims(depth, width)
    preds = assumption_predicates(depth, width)
    suffix = "" if not drop else "-without-" + "-".join(d.replace(">=0", "").replace("fprime_", "fp") for d in drop)
    return Hypothesis(
        hypothesis_id=hypothesis_id or f"ED-POLARITY-L{depth}-W{width}-{claims}{suffix}",
        variables=variables(depth, width),
        scope=" and ".join(f"({c})" for c in chain_rule(depth, width)),
        assumptions=[preds[a] for a in ASSUMPTIONS if a not in drop],
        claims=chosen,
        statement=(
            f"Dual-stream network of depth {depth} and width {width}: with non-negative weights and f' >= 0, the "
            "sign of dy/d(neuron) is fixed by stream membership, so the ED update -eta*pre*f'(post)*sign(e) never "
            "points uphill along any weight."
        ),
    )


def transport_hypothesis(depth: int, width: int) -> Hypothesis:
    """Rival: the broadcast ED update equals the W^T-transported (backprop) update up to one positive scale.

    Encoded as proportionality of (ED update, gradient) between a weight of the top layer and a W_pp weight of the
    layer below: u_a * g_b == u_b * g_a. Needs depth >= 2. All assumptions are kept.
    """
    if depth < 2:
        raise ValueError("The transport rival needs depth >= 2.")
    a, b = Weight("Wpp", depth, 0, 0), Weight("Wpp", depth - 1, 0, 0)
    preds = assumption_predicates(depth, width)
    # Non-degenerate networks only: every weight and f' strictly positive, activities and error non-zero, so a
    # counterexample cannot come from a weight that has no gradient at all.
    nondegenerate = [f"{w.name} > 0" for w in weights(depth, width)]
    nondegenerate += [f"{_d(st, i, k)} > 0" for i in range(1, depth + 1) for st in ("p", "n") for k in range(width)]
    nondegenerate += [f"{_x(st, i, j)} != 0" for i in range(depth) for st in ("p", "n") for j in range(width)]
    nondegenerate.append("e != 0")
    return Hypothesis(
        hypothesis_id=f"ED-TRANSPORT-L{depth}-W{width}",
        variables=variables(depth, width),
        scope=" and ".join(f"({c})" for c in chain_rule(depth, width) + nondegenerate),
        assumptions=[preds[x] for x in ASSUMPTIONS],
        claims=[f"({a.ed_update()}) * ({b.gradient()}) == ({b.ed_update()}) * ({a.gradient()})"],
        statement=(
            "The ED broadcast update carries the same information as backprop through W^T: it equals the "
            "transported update up to one positive scale."
        ),
    )


def verdict(hypothesis: Hypothesis, max_examples: int = 1) -> Dict[str, Any]:
    """Court verdict for a mathematical claim.

    For a claim derived from definitions, PROVED means the court finds no applicable state that violates a claim
    (content verdict UNFALSIFIABLE) while some applicable state exists (not VACUOUS) and the assumptions are
    jointly satisfiable. REFUTED means the court produced a state that satisfies scope and assumptions and violates
    a claim.
    """
    try:
        report = HypothesisEvaluator.evaluate(hypothesis, max_examples=max_examples)
    except FormalHypothesisError as exc:
        if "could not decide" not in str(exc):
            raise
        return {
            "hypothesis_id": hypothesis.hypothesis_id,
            "backend": "smt",
            "content_verdict": None,
            "status": "UNDECIDED",
            "reason": str(exc),
            "conflicting_assumption_sets": [],
            "witness": None,
            "violated_claims": [],
        }
    content = report.content_verdict.value
    if content == "UNFALSIFIABLE" and not report.conflicting_assumption_sets:
        status = "PROVED"
    elif content in ("FALSIFIABLE", "SELF_CONTRADICTORY"):
        status = "REFUTED"
    else:
        status = f"FLAGGED_{content}"
    witness = report.falsifier_examples[0] if report.falsifier_examples else None
    violated = hypothesis.violated_claims(witness) if witness is not None else []
    return {
        "hypothesis_id": hypothesis.hypothesis_id,
        "backend": report.backend,
        "content_verdict": content,
        "status": status,
        "conflicting_assumption_sets": report.conflicting_assumption_sets,
        "witness": _nonzero(witness) if witness is not None else None,
        "violated_claims": violated[:3],
    }


def _nonzero(state: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in state.items() if v != 0}


def decide(depth: int, width: int, drop: Tuple[str, ...] = ()) -> Dict[str, Any]:
    """Polarity invariance and sign sufficiency checked as two hypotheses (smaller solver calls), then combined.

    The combined status is REFUTED when either part is refuted, PROVED when every part is proved, UNDECIDED
    otherwise. Depth 1 has no hidden layer, so only sign sufficiency is checked there.
    """
    parts = {"sign": verdict(ed_hypothesis(depth, width, drop=drop, claims="sign"))}
    if depth > 1:
        parts["polarity"] = verdict(ed_hypothesis(depth, width, drop=drop, claims="polarity"))
    statuses = {v["status"] for v in parts.values()}
    if "REFUTED" in statuses:
        status = "REFUTED"
    elif statuses == {"PROVED"}:
        status = "PROVED"
    else:
        status = "UNDECIDED"
    return {"depth": depth, "width": width, "dropped": list(drop), "status": status, "parts": parts}


def necessity_table(depth: int, width: int) -> Dict[str, str]:
    """For each assumption: NECESSARY when dropping it lets the court refute the claim at this depth and width,
    REDUNDANT when the claim is still proved without it, UNDECIDED when the solver timed out."""
    meaning = {"REFUTED": "NECESSARY", "PROVED": "REDUNDANT"}
    return {a: meaning.get(decide(depth, width, drop=(a,))["status"], "UNDECIDED") for a in ASSUMPTIONS}


# ---------------------------------------------------------------------------
# Replay on concrete networks (independent of the solver)
# ---------------------------------------------------------------------------

Activation = Tuple[Callable[[float], float], Callable[[float], float]]
SIGMOID: Activation = (lambda z: 1 / (1 + math.exp(-z)), lambda z: math.exp(-z) / (1 + math.exp(-z)) ** 2)
SQUARE: Activation = (lambda z: z * z, lambda z: 2 * z)  # f' < 0 for z < 0: violates f' >= 0.


@dataclass
class Network:
    """A concrete dual-stream network. W[family][layer-1][j][k]; b[stream][layer-1][k]."""

    W: Dict[str, List[List[List[float]]]]
    b: Dict[str, List[List[float]]]
    activation: Activation

    @property
    def depth(self) -> int:
        return len(self.W["Wpp"])

    @property
    def width(self) -> int:
        return len(self.W["Wpp"][0])

    def forward(self, p0: List[float], n0: List[float]):
        f = self.activation[0]
        ps, ns, zps, zns = [p0], [n0], [], []
        for i in range(self.depth):
            p, n = ps[-1], ns[-1]
            zp = [
                sum(p[j] * self.W["Wpp"][i][j][k] - n[j] * self.W["Wnp"][i][j][k] for j in range(self.width))
                + self.b["p"][i][k]
                for k in range(self.width)
            ]
            zn = [
                sum(n[j] * self.W["Wnn"][i][j][k] - p[j] * self.W["Wpn"][i][j][k] for j in range(self.width))
                + self.b["n"][i][k]
                for k in range(self.width)
            ]
            zps.append(zp)
            zns.append(zn)
            ps.append([f(z) for z in zp])
            ns.append([f(z) for z in zn])
        return ps, ns, zps, zns

    def output(self, p0, n0) -> float:
        return self.forward(p0, n0)[0][-1][0]


def replay(net: Network, p0: List[float], n0: List[float], h: float = 1e-6, tol: float = 1e-9) -> Dict[str, Any]:
    """Finite-difference dy/dw for every weight, compared with the sign ED attributes to it.

    ED treats dy/dw as having the sign sigma_post * tau * sign(pre * f'(post)). A disagreement means a single
    global error sign sends that weight uphill for one sign of the error.
    """
    ps, ns, zps, zns = net.forward(p0, n0)
    fprime = net.activation[1]
    acts = {"p": ps, "n": ns}
    pres = {"p": zps, "n": zns}
    disagreements = []
    checked = 0
    for family, (pre, post, tau) in FAMILIES.items():
        for i in range(net.depth):
            for j in range(net.width):
                for k in range(net.width):
                    original = net.W[family][i][j][k]
                    net.W[family][i][j][k] = original + h
                    up = net.output(p0, n0)
                    net.W[family][i][j][k] = original - h
                    down = net.output(p0, n0)
                    net.W[family][i][j][k] = original
                    numeric = (up - down) / (2 * h)
                    predicted = POLARITY[post] * tau * acts[pre][i][j] * fprime(pres[post][i][k])
                    checked += 1
                    if abs(numeric) > tol and numeric * predicted < 0:
                        disagreements.append(
                            {"weight": _w(family, i + 1, j, k), "dy_dw": numeric, "ed_predicted": predicted}
                        )
    return {"weights_checked": checked, "disagreements": disagreements}


def random_network(depth: int, width: int, rng: random.Random, activation: Activation = SIGMOID) -> Network:
    return Network(
        W={
            f: [[[rng.uniform(0, 2) for _ in range(width)] for _ in range(width)] for _ in range(depth)]
            for f in FAMILIES
        },
        b={s: [[rng.uniform(-1, 1) for _ in range(width)] for _ in range(depth)] for s in ("p", "n")},
        activation=activation,
    )


def _one(value: float) -> List[List[List[float]]]:
    return [[[value]]]


def witness_negative_weight() -> Network:
    """Depth 2, width 1, sigmoid, W_pp at the top layer = -1: breaks W >= 0 only."""
    return Network(
        W={"Wpp": [[[1.0]], [[-1.0]]], "Wnp": [[[0.5]], [[0.5]]], "Wnn": [[[1.0]], [[1.0]]], "Wpn": [[[0.5]], [[0.5]]]},
        b={"p": [[0.0], [0.0]], "n": [[0.0], [0.0]]},
        activation=SIGMOID,
    )


def witness_decreasing_activation() -> Network:
    """Depth 2, width 1, f(z) = z^2 with a negative top pre-activation: breaks f' >= 0 only (weights >= 0)."""
    return Network(
        W={"Wpp": [[[1.0]], [[1.0]]], "Wnp": [[[0.5]], [[0.5]]], "Wnn": [[[1.0]], [[1.0]]], "Wpn": [[[0.5]], [[0.5]]]},
        b={"p": [[0.5], [-3.0]], "n": [[0.5], [0.0]]},
        activation=SQUARE,
    )


WITNESS_INPUT = ([1.0], [1.0])


GRID = ((1, 1), (2, 1), (3, 1), (4, 1), (1, 2), (2, 2), (3, 2))
ALL_WEIGHTS = ("Wpp>=0", "Wnp>=0", "Wnn>=0", "Wpn>=0")
ALL_FPRIME = ("fprime_p>=0", "fprime_n>=0")


def case_report(grid=GRID) -> Dict[str, Any]:
    """Everything the results document reports, recomputed."""
    main = {f"L{d}-W{w}": decide(d, w) for d, w in grid}
    variants = {}
    for d in (2, 3):
        variants[f"L{d}-W1 without W>=0"] = decide(d, 1, drop=ALL_WEIGHTS)
        variants[f"L{d}-W1 without f'>=0"] = decide(d, 1, drop=ALL_FPRIME)
        variants[f"L{d}-W1 sign-equivalent to W^T transport"] = decide(d, 1)
        variants[f"L{d}-W1 value-equivalent to W^T transport"] = verdict(transport_hypothesis(d, 1))
    necessity = {f"L{d}-W{w}": necessity_table(d, w) for d, w in grid}
    rng = random.Random(0)
    positive = [replay(random_network(3, 2, rng), [rng.uniform(0, 1)] * 2, [rng.uniform(0, 1)] * 2) for _ in range(50)]
    return {
        "status": STATUS,
        "source": SOURCE,
        "main_claim": main,
        "variants": variants,
        "assumption_necessity": necessity,
        "replay": {
            "random_nonnegative_sigmoid_networks": {
                "networks": len(positive),
                "weights_checked": sum(r["weights_checked"] for r in positive),
                "disagreements": sum(len(r["disagreements"]) for r in positive),
            },
            "negative_weight_witness": replay(witness_negative_weight(), *WITNESS_INPUT),
            "decreasing_activation_witness": replay(witness_decreasing_activation(), *WITNESS_INPUT),
        },
    }
