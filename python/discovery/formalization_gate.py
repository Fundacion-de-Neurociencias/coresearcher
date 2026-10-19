"""
python/discovery/formalization_gate.py - Self-consistency gate on the formalizer (ADR-DISCOVERY-064).

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

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from python.discovery import formal_provenance, formal_status, formal_thresholds
from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, Relation, SolverUndecided
from python.discovery.formalizer import (
    PROMPT_VERSION,
    Formalization,
    FormalizationStatus,
    build_messages,
    parse_formalization,
    prompt_sha256,
)

# Versioned defaults; the values in force are the gate_* thresholds (ADR-DISCOVERY-068).
_D = formal_thresholds.FORMAL_DEFAULTS.values
DEFAULT_SAMPLES = _D["gate_samples"]  # Ablation in FORMALIZER_GATE_RESULTS.md: fewer false acceptances than N = 3.
DEFAULT_TEMPERATURE = _D["gate_temperature"]
MAX_SAMPLES = _D["gate_max_samples"]


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


def sampling_schedule(models: Sequence[str], n: int, temperature: Optional[float] = None) -> List[SampleSpec]:
    """N sample specifications, cycling through the models.

    The first pass over the models uses the frozen decoding (thresholds formalizer_temperature and formalizer_seed:
    temperature 0, seed 0), so sample 0 is exactly the ungated formalizer output and N = 1 reproduces it. Later passes
    use a positive temperature (gate_temperature unless given) and the following seeds.
    """
    if not models:
        raise ValueError("The gate needs at least one model.")
    if n < 1:
        raise ValueError("The gate needs at least one sample.")
    if temperature is None:
        temperature = formal_thresholds.get("gate_temperature")
    frozen_temperature = formal_thresholds.get("formalizer_temperature")
    seed0 = formal_thresholds.get("formalizer_seed")
    specs = []
    for i in range(n):
        round_ = i // len(models)
        specs.append(
            SampleSpec(models[i % len(models)], frozen_temperature if round_ == 0 else temperature, seed0 + round_)
        )
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
    undecided: List[int] = field(default_factory=list)  # Samples the solver could not decide, alone or in a pair.
    mandatory_relays: List[Dict[str, str]] = field(default_factory=list)
    provenance: Optional[Dict[str, Any]] = None

    @property
    def formal_status(self) -> formal_status.FormalStatus:
        """GateStatus on the shared vocabulary of ADR-068: DECIDED when a reading was accepted."""
        return formal_status.from_gate_status(self.status.value)

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
            **self.body(),
            "formal_status": self.formal_status.value,
            "mandatory_relays": list(self.mandatory_relays),
            "provenance": self.provenance,
        }

    def body(self) -> Dict[str, Any]:
        """The gate outcome without status, relays or provenance; `output_sha256` is its digest."""
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
                    **({"formal_status": formal_status.FormalStatus.UNDECIDED.value} if i in self.undecided else {}),
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


def gate(
    samples: Sequence[Formalization],
    specs: Optional[Sequence[SampleSpec]] = None,
    request: Optional[Dict[str, Any]] = None,
) -> GateResult:
    """Groups already drawn formalizations into exact equivalence classes and decides the gate status.

    Only PARSED samples vote; NO_JSON, INVALID and SCHEMA_MISMATCH samples, and samples the evaluator rejects,
    count in N but join no class. A class wins only when its size is strictly above gate_majority_fraction (one half)
    of all N samples, and only if every pair inside it was proved EQUIVALENT (a pair the solver could not decide never
    counts as agreement). `request` (prose, hypothesis id, variable schema) only enters the provenance block.
    """
    samples = list(samples)
    n = len(samples)
    if n == 0:
        raise ValueError("The gate needs at least one sample.")
    specs = list(specs) if specs is not None else [SampleSpec("unknown", 0.0, i) for i in range(n)]
    majority = formal_thresholds.get("gate_majority_fraction")
    verdicts: List[Optional[str]] = [None] * n
    errors = [""] * n
    valid: List[int] = []
    undecided: List[int] = []
    backends = set()
    for i, sample in enumerate(samples):
        if sample.status != FormalizationStatus.PARSED or sample.hypothesis is None:
            continue
        try:
            report = HypothesisEvaluator.evaluate(sample.hypothesis, max_examples=1)
        except FormalHypothesisError as exc:
            errors[i] = f"Evaluator rejected the object: {exc}"
            if isinstance(exc, SolverUndecided):
                undecided.append(i)
            continue
        verdicts[i] = report.content_verdict.value
        backends.add(report.backend)
        valid.append(i)

    pairwise: List[Dict[str, Any]] = []
    equivalent: Dict[tuple, bool] = {}
    for x, a in enumerate(valid):
        for b in valid[x + 1 :]:
            try:
                comparison = HypothesisEvaluator.compare(samples[a].hypothesis, samples[b].hypothesis, max_examples=1)
                relation, error = comparison.relation.value, ""
                backends.add(comparison.backend)
            except FormalHypothesisError as exc:  # Different variables, or the solver could not decide.
                relation, error = "UNDECIDED", str(exc)
                if isinstance(exc, SolverUndecided):
                    undecided.extend(i for i in (a, b) if i not in undecided)
            equivalent[(a, b)] = relation == Relation.EQUIVALENT.value
            pairwise.append({"a": a, "b": b, "relation": relation, **({"error": error} if error else {})})

    local = _equivalence_classes(len(valid), {(valid.index(a), valid.index(b)): s for (a, b), s in equivalent.items()})
    classes = [[valid[i] for i in members] for members in local]

    def result(status: GateStatus, accepted: Optional[int], reason: str) -> GateResult:
        out = GateResult(
            status, samples, specs, verdicts, errors, classes, pairwise, accepted, reason, sorted(undecided)
        )
        return _seal(out, request, backends)

    if not classes:
        return result(GateStatus.FORMALIZATION_FAILED, None, "No sample produced a valid formal object.")
    if n == 1:
        return result(GateStatus.SINGLE_SAMPLE, 0, "One sample: no self-consistency evidence either way.")
    top = classes[0]
    if len(top) <= majority * n:
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


def _seal(result: GateResult, request: Optional[Dict[str, Any]], backends: set) -> GateResult:
    """Relays and the provenance block (ADR-068). The input digest covers the raw model outputs, so the gate can be
    re-run offline from them (`coresearcher formal analyze`)."""
    codes = []
    if result.passes:
        codes.append("FORMALIZATION_IS_DRAFT")
    if result.status == GateStatus.SINGLE_SAMPLE:
        codes.append("GATE_SINGLE_SAMPLE")
    if any(src != "default" for src in formal_thresholds.active().sources().values()):
        codes.append("THRESHOLDS_OVERRIDDEN")
    result.mandatory_relays = formal_status.relays(codes)
    specs = [spec.to_dict() for spec in result.specs]
    inputs = {
        "request": request or {},
        "specs": specs,
        "raw_outputs": [sample.raw_output for sample in result.samples],
    }
    backend = None if not backends else (next(iter(backends)) if len(backends) == 1 else "mixed")
    formalizer = {
        "models": sorted({spec["model"] for spec in specs}),
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": prompt_sha256(),
        "seeds": [spec["seed"] for spec in specs],
        "temperatures": [spec["temperature"] for spec in specs],
    }
    result.provenance = formal_provenance.build("formalize_gate", inputs, result.body(), backend, formalizer)
    return result


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
    n: Optional[int] = None,
    hypothesis_id: str = "H",
    variable_schema: Optional[List[Dict[str, Any]]] = None,
    temperature: Optional[float] = None,
) -> GateResult:
    """Prose -> N formalizations -> exact equivalence classes -> gate status. N and the temperature default to the
    gate_samples and gate_temperature thresholds."""
    n = formal_thresholds.get("gate_samples") if n is None else n
    specs = sampling_schedule(list(clients), n, temperature)
    request = {"prose": prose, "hypothesis_id": hypothesis_id, "variable_schema": variable_schema}
    return gate(draw_samples(prose, clients, specs, hypothesis_id, variable_schema), specs, request)
