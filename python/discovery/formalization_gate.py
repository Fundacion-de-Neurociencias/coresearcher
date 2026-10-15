"""
python/discovery/formalization_gate.py - Self-consistency gate on the formalizer (ADR-DISCOVERY-063).

The formalizer (ADR-DISCOVERY-061) is a language model, and a single output can silently mean something other than
the prose. The gate draws N independent formalizations of the same prose (different seeds, a positive temperature,
optionally different models) and asks the exact evaluator whether they mean the same thing: two formalizations are in
the same class only when `HypothesisEvaluator.compare` proves them EQUIVALENT (enumeration, or z3 when a variable is
continuous). No language model judges agreement.

Outcomes:
- CONSISTENT: a strict majority of the N samples falls in one equivalence class. Its first member is accepted.
- FORMALIZATION_AMBIGUOUS: no class holds a strict majority. Nothing is accepted and nothing is evaluated as if it were
  the hypothesis; the rival readings are returned so the researcher can see where they differ.
- FORMALIZATION_FAILED: no sample produced a valid formal object over the requested variables.
- SINGLE_SAMPLE: N = 1 and the sample parsed. The gate gives no evidence either way; the output is accepted as before.

Agreement among samples is evidence of a stable reading, not proof that the reading is the prose's meaning: every
accepted object stays a draft (ADR-DISCOVERY-061). The gate never reports VERIFIED.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, Relation
from python.discovery.formalizer import (
    Formalization,
    FormalizationStatus,
    build_messages,
    parse_formalization,
)

DEFAULT_SAMPLES = 5  # Ablation in FORMALIZER_GATE_RESULTS.md: fewer false acceptances than N = 3.
DEFAULT_TEMPERATURE = 0.7
MAX_SAMPLES = 7


class GateStatus(str, Enum):
    SINGLE_SAMPLE = "SINGLE_SAMPLE"
    CONSISTENT = "CONSISTENT"
    FORMALIZATION_AMBIGUOUS = "FORMALIZATION_AMBIGUOUS"
    FORMALIZATION_FAILED = "FORMALIZATION_FAILED"


PASSING = (GateStatus.SINGLE_SAMPLE, GateStatus.CONSISTENT)


@dataclass(frozen=True)
class SampleSpec:
    model: str
    temperature: float
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        return {"model": self.model, "temperature": self.temperature, "seed": self.seed}


def sampling_schedule(models: Sequence[str], n: int, temperature: float = DEFAULT_TEMPERATURE) -> List[SampleSpec]:
    """N sample specifications, cycling through the models.

    The first pass over the models uses the frozen decoding (temperature 0, seed 0), so sample 0 is exactly the
    ungated formalizer output and N = 1 reproduces it. Later passes use a positive temperature and seeds 1, 2, ...
    """
    if not models:
        raise ValueError("The gate needs at least one model.")
    if n < 1:
        raise ValueError("The gate needs at least one sample.")
    specs = []
    for i in range(n):
        round_ = i // len(models)
        specs.append(SampleSpec(models[i % len(models)], 0.0 if round_ == 0 else temperature, round_))
    return specs


@dataclass
class GateResult:
    status: GateStatus
    samples: List[Formalization]
    specs: List[SampleSpec]
    verdicts: List[Optional[str]]  # Content verdict of each sample that parsed and evaluated, else None.
    sample_errors: List[str]
    classes: List[List[int]]  # Equivalence classes of the valid samples, largest first; members are sample indices.
    pairwise: List[Dict[str, Any]]
    accepted: Optional[int]
    reason: str

    @property
    def n_samples(self) -> int:
        return len(self.samples)

    @property
    def passes(self) -> bool:
        return self.status in PASSING

    @property
    def agreement(self) -> float:
        """Size of the largest equivalence class over all samples drawn (failed samples count against it)."""
        return round(len(self.classes[0]) / self.n_samples, 4) if self.classes else 0.0

    @property
    def formalization(self) -> Optional[Formalization]:
        return self.samples[self.accepted] if self.accepted is not None else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "passes": self.passes,
            "reason": self.reason,
            "n_samples": self.n_samples,
            "agreement": self.agreement,
            "accepted_sample": self.accepted,
            "samples": [
                {
                    "index": i,
                    **spec.to_dict(),
                    "status": sample.status.value if not self.sample_errors[i] else FormalizationStatus.INVALID.value,
                    "error": self.sample_errors[i] or sample.error,
                    "content_verdict": self.verdicts[i],
                }
                for i, (sample, spec) in enumerate(zip(self.samples, self.specs))
            ],
            "classes": [
                {
                    "members": members,
                    "size": len(members),
                    "content_verdict": self.verdicts[members[0]],
                    "formal_hypothesis": self.samples[members[0]].data,
                }
                for members in self.classes
            ],
            "pairwise": self.pairwise,
        }


def _equivalence_classes(n: int, equivalent: Dict[tuple, bool]) -> List[List[int]]:
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for (a, b), same in equivalent.items():
        if same:
            parent[find(a)] = find(b)
    groups: Dict[int, List[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=lambda members: (-len(members), members[0]))


def gate(samples: Sequence[Formalization], specs: Optional[Sequence[SampleSpec]] = None) -> GateResult:
    """Groups already drawn formalizations into exact equivalence classes and decides the gate status.

    Only PARSED samples vote; NO_JSON, INVALID and SCHEMA_MISMATCH samples, and samples the evaluator rejects,
    count in N but join no class. A class wins only with a strict majority of all N samples, and only if every pair
    inside it was proved EQUIVALENT (a pair the solver could not decide never counts as agreement).
    """
    samples = list(samples)
    n = len(samples)
    if n == 0:
        raise ValueError("The gate needs at least one sample.")
    specs = list(specs) if specs is not None else [SampleSpec("unknown", 0.0, i) for i in range(n)]
    verdicts: List[Optional[str]] = [None] * n
    errors = [""] * n
    valid: List[int] = []
    for i, sample in enumerate(samples):
        if sample.status != FormalizationStatus.PARSED or sample.hypothesis is None:
            continue
        try:
            verdicts[i] = HypothesisEvaluator.evaluate(sample.hypothesis, max_examples=1).content_verdict.value
        except FormalHypothesisError as exc:
            errors[i] = f"Evaluator rejected the object: {exc}"
            continue
        valid.append(i)

    pairwise: List[Dict[str, Any]] = []
    equivalent: Dict[tuple, bool] = {}
    for x, a in enumerate(valid):
        for b in valid[x + 1 :]:
            try:
                relation = HypothesisEvaluator.compare(
                    samples[a].hypothesis, samples[b].hypothesis, max_examples=1
                ).relation.value
                error = ""
            except FormalHypothesisError as exc:  # Different variables, or the solver could not decide.
                relation, error = "UNDECIDED", str(exc)
            equivalent[(a, b)] = relation == Relation.EQUIVALENT.value
            pairwise.append({"a": a, "b": b, "relation": relation, **({"error": error} if error else {})})

    local = _equivalence_classes(len(valid), {(valid.index(a), valid.index(b)): s for (a, b), s in equivalent.items()})
    classes = [[valid[i] for i in members] for members in local]

    def result(status: GateStatus, accepted: Optional[int], reason: str) -> GateResult:
        return GateResult(status, samples, specs, verdicts, errors, classes, pairwise, accepted, reason)

    if not classes:
        return result(GateStatus.FORMALIZATION_FAILED, None, "No sample produced a valid formal object.")
    if n == 1:
        return result(GateStatus.SINGLE_SAMPLE, 0, "One sample: no self-consistency evidence either way.")
    top = classes[0]
    if 2 * len(top) <= n:
        return result(
            GateStatus.FORMALIZATION_AMBIGUOUS,
            None,
            f"No reading holds a strict majority: largest class {len(top)} of {n} samples "
            f"({len(classes)} distinct readings, {n - len(valid)} failed samples).",
        )
    unproved = [p for p in pairwise if p["a"] in top and p["b"] in top and p["relation"] != "EQUIVALENT"]
    if unproved:
        return result(
            GateStatus.FORMALIZATION_AMBIGUOUS,
            None,
            f"The majority class contains {len(unproved)} pair(s) not proved equivalent.",
        )
    return result(GateStatus.CONSISTENT, top[0], f"{len(top)} of {n} samples are logically equivalent.")


def draw_samples(
    prose: str,
    clients: Dict[str, Any],
    specs: Sequence[SampleSpec],
    hypothesis_id: str = "H",
    variable_schema: Optional[List[Dict[str, Any]]] = None,
) -> List[Formalization]:
    """Draws one formalization per spec. `clients` maps a model name to a client with `complete(messages, ...)`."""
    messages = build_messages(prose, variable_schema)
    out = []
    for spec in specs:
        text = clients[spec.model].complete(messages, temperature=spec.temperature, seed=spec.seed)
        out.append(parse_formalization(text, hypothesis_id, variable_schema))
    return out


def formalize_gated(
    prose: str,
    clients: Dict[str, Any],
    n: int = DEFAULT_SAMPLES,
    hypothesis_id: str = "H",
    variable_schema: Optional[List[Dict[str, Any]]] = None,
    temperature: float = DEFAULT_TEMPERATURE,
) -> GateResult:
    """Prose -> N formalizations -> exact equivalence classes -> gate status."""
    specs = sampling_schedule(list(clients), n, temperature)
    return gate(draw_samples(prose, clients, specs, hypothesis_id, variable_schema), specs)
