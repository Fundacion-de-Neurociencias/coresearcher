"""
python/discovery/formal_status.py - Non-verdict statuses and mandatory caveats of the formal layer (ADR-DISCOVERY-068).

Status vocabulary
-----------------
Every formal result carries `formal_status`. Only DECIDED carries a verdict (a content verdict, a relation, an
entailment, an accepted formalization). Every other status says why there is none, and no code path may turn one into
a verdict:

| Status                    | Meaning                                                              | CLI exit |
|---------------------------|----------------------------------------------------------------------|----------|
| DECIDED                   | The question was decided exactly; the report holds the verdict.      | 0        |
| UNDECIDED                 | z3 returned unknown (timeout, resource limit, incompleteness).        | 10       |
| BLOCKED                   | A required capability or setting is missing (z3, the formalizer      | 4/7/8/13 |
|                           | model or endpoint, a threshold), or the question exceeds a threshold |          |
|                           | (max_states). Nothing was decided.                                   |          |
| INVALID_INPUT             | The formal object or request is malformed; the engine will not guess. | 9        |
| FORMALIZATION_AMBIGUOUS   | Formalizer samples disagree (ADR-064); no reading is evaluated.       | 11       |
| FORMALIZATION_FAILED      | No formalizer sample produced a valid formal object.                  | 11       |
| NOT_KERNEL_CHECKED        | A Lean theorem was stated but no Lean kernel checked it.             | n/a      |

The existing enums (`ContentVerdict`, `Relation`, `GateStatus`, `FormalizationStatus`) keep their values; this module
maps them onto the shared vocabulary.

Mandatory relays
----------------
A relay is a caveat with a stable code, attached to every report it applies to under `mandatory_relays` (OASE's
field name and shape: `{"code", "message"}`). Codes are registered here; `relay()` rejects an unregistered code. Some
relays fire on every verdict (FORMAL_NOT_EMPIRICAL), because the clean, decided result is exactly the one most likely to
be over-read.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

from python.discovery.formal_thresholds import ThresholdError


class FormalStatus(str, Enum):
    DECIDED = "DECIDED"
    UNDECIDED = "UNDECIDED"
    BLOCKED = "BLOCKED"
    INVALID_INPUT = "INVALID_INPUT"
    FORMALIZATION_AMBIGUOUS = "FORMALIZATION_AMBIGUOUS"
    FORMALIZATION_FAILED = "FORMALIZATION_FAILED"
    NOT_KERNEL_CHECKED = "NOT_KERNEL_CHECKED"


NON_VERDICT = frozenset(s for s in FormalStatus if s is not FormalStatus.DECIDED)


def is_verdict(status: Any) -> bool:
    return FormalStatus(getattr(status, "value", status)) is FormalStatus.DECIDED


class CapabilityUnavailable(RuntimeError):
    """A capability the formal pipeline needs is absent (z3, a formalizer model, a Lean binary)."""

    def __init__(self, capability: str, detail: str = "", endpoint: bool = False):
        self.capability = capability
        self.endpoint = endpoint  # True when it is configured but cannot be reached (retry later may help).
        super().__init__(f"{capability} is unavailable{': ' + detail if detail else ''}.")


class FrozenCriteriaChanged(RuntimeError):
    """An evaluation references frozen acceptance criteria that no longer match (ADR-DISCOVERY-085). BLOCKED.

    `check` is the freeze service's verification record: which freeze, what was expected, what changed.
    """

    def __init__(self, message: str, check: Optional[Dict[str, Any]] = None):
        self.check = check or {}
        super().__init__(message)


# Exit codes. 0-9 follow OASE's taxonomy (core/errors.py); 10 and 11 are the formal layer's own non-verdicts.
EXIT_CODES: Dict[FormalStatus, int] = {
    FormalStatus.DECIDED: 0,
    FormalStatus.INVALID_INPUT: 9,  # Refusal: change the input.
    FormalStatus.UNDECIDED: 10,  # Raise the solver timeout or simplify; retrying unchanged will not help.
    FormalStatus.FORMALIZATION_AMBIGUOUS: 11,
    FormalStatus.FORMALIZATION_FAILED: 11,
}
EXIT_ARTIFACT = 3  # A stored artifact is missing, malformed or does not match its checksum.
EXIT_THRESHOLD = 4  # BLOCKED by an unresolved or malformed threshold (OASE ThresholdError).
EXIT_ENDPOINT = 7  # BLOCKED: the formalizer endpoint is configured but unreachable (OASE EndpointUnavailable).
EXIT_DEPENDENCY = 8  # BLOCKED by a missing capability (OASE DependencyError).
EXIT_REFUSAL = 9  # Refusal, including a refusal to overwrite a differing record.
EXIT_NOT_REPRODUCED = 12  # `formal analyze` recomputed a different result under the same thresholds.
EXIT_FREEZE_CHANGED = 13  # BLOCKED: the frozen acceptance criteria or the evaluated subject changed (ADR-085).


def classify(exc: BaseException) -> FormalStatus:
    """The non-verdict status an exception stands for. Unknown exceptions are not swallowed: they re-raise."""
    from python.discovery.formal_hypothesis import FormalHypothesisError, SolverUndecided, ThresholdExceeded

    if isinstance(exc, SolverUndecided):
        return FormalStatus.UNDECIDED
    if isinstance(exc, (ThresholdError, ThresholdExceeded, CapabilityUnavailable, FrozenCriteriaChanged)):
        return FormalStatus.BLOCKED
    if isinstance(exc, ImportError) and (exc.name or "").split(".")[0] == "z3":
        return FormalStatus.BLOCKED
    if isinstance(exc, FormalHypothesisError):
        return FormalStatus.INVALID_INPUT
    raise exc


def exit_code(status: FormalStatus, exc: Optional[BaseException] = None) -> int:
    if status is FormalStatus.BLOCKED:
        from python.discovery.formal_hypothesis import ThresholdExceeded

        if isinstance(exc, (ThresholdError, ThresholdExceeded)):
            return EXIT_THRESHOLD
        if isinstance(exc, FrozenCriteriaChanged):
            return EXIT_FREEZE_CHANGED
        return EXIT_ENDPOINT if getattr(exc, "endpoint", False) else EXIT_DEPENDENCY
    return EXIT_CODES[status]


def from_gate_status(value: str) -> FormalStatus:
    """GateStatus (ADR-064) onto the shared vocabulary. A passing gate is DECIDED: a reading was accepted."""
    if value in ("CONSISTENT", "SINGLE_SAMPLE"):
        return FormalStatus.DECIDED
    return FormalStatus(value)


# ---------------------------------------------------------------------------
# Relays
# ---------------------------------------------------------------------------

RELAY_CODES: Dict[str, str] = {
    "FORMAL_NOT_EMPIRICAL": (
        "A formal verdict is about the formal object only. Consistent, falsifiable or entailed does not mean "
        "empirically true; whether the premises hold in the world is outside this check."
    ),
    "SMT_FIXED_SIZE_ONLY": (
        "Decided by z3 for the declared variables and bounds only. It is not a proof for other sizes, other "
        "variables or a general (parametric) case."
    ),
    "ENUMERATION_DECLARED_DOMAINS_ONLY": (
        "Decided by enumerating the declared finite domains. Values outside those domains were never considered."
    ),
    "LEAN_NOT_KERNEL_CHECKED": (
        "A Lean 4 theorem was stated but no Lean kernel checked it here. Treat it as a claim, not a proof."
    ),
    "FORMALIZATION_IS_DRAFT": (
        "The formal object came from a language model. Samples agreeing with each other is evidence of a stable "
        "reading, not proof that it says what the prose meant; a researcher must confirm it."
    ),
    "GATE_SINGLE_SAMPLE": (
        "The formalizer was sampled once, so the self-consistency gate gives no evidence either way."
    ),
    "VACUOUS_ENTAILMENT": (
        "No applicable state is allowed by the hypothesis, so every consequence is entailed trivially."
    ),
    "ENTAILED_BY_ASSUMPTIONS_ALONE": (
        "The consequence already follows from the domains, scope and assumptions; the claims add nothing to it."
    ),
    "THRESHOLDS_OVERRIDDEN": (
        "At least one formal threshold differs from the versioned default; see threshold_sources."
    ),
    "VACUOUS_RELATIVE_TO_INTENT": (
        "A state the hypothesis declares as a non-witness satisfies its claims (see intent_probe). The claims hold "
        "of an object they were meant to exclude, such as the zero, free or a lower-dimensional model."
    ),
    "TRIVIAL_WITNESS_SATISFIES_CLAIMS": (
        "A generic trivial witness (variables at zero or at a bound) satisfies the claims. This is advisory and does "
        "not change the verdict; declare it as a non-witness if the claims must exclude it."
    ),
    "CLAIM_BELOW_KERNEL_CHECKED": (
        "At least one claim is below KERNEL_CHECKED on the trust ladder: no recorded Lean kernel check (toolchain, "
        "file SHA-256, permitted axioms) covers it. See claim_trust for the rung of each claim and what is missing."
    ),
    "FIDELITY_RANGE_ONLY": (
        "Statement fidelity is decided for the hypothesis range only. Conclusions are not compared, and the range "
        "transcriptions are taken as given; the solver decides the encodings, not the transcription."
    ),
    "LINT_IS_SYNTACTIC": (
        "The junk-value lint is a static pass over the text. It can miss junk values hidden in Mathlib definitions; "
        "OPEN means a human decides, DISCHARGED names the text that rules the junk branch out."
    ),
    "IMPORTS_ARE_LEXICAL": (
        "Import obligations are found by lexical rules (citations with locators, sign and convention words, "
        "'effective' with an unspecified constant). They place an OPEN obligation at a line; they do not decide the "
        "mathematics, and a MATCHED hypothesis is a textual match, not a proof."
    ),
    "IMPORT_OBLIGATIONS_OPEN": (
        "The manuscript has OPEN import obligations. Its claims are not verified until each one is discharged "
        "(ADR-076): a claim is never stronger than its weakest obligation."
    ),
    "CRITERIA_FROZEN": (
        "The acceptance criteria were frozen before this evaluation, and the freeze's SHA-256, time and author were "
        "verified (see freeze_check). A freeze fixes what counts as support or refutation; it does not make the "
        "criteria right."
    ),
    "CRITERIA_FROZEN_IN_SAME_RUN": (
        "The criteria were frozen in this run, before the evaluation and without observations. That rules out tuning "
        "them on this result, not on data seen earlier; a freeze recorded on an earlier date is stronger evidence of "
        "pre-registration."
    ),
    "LEDGER_NOT_PROVED": (
        "The obligation ledger has at least one obligation that is not proved (OPEN, numeric, author-certified or "
        "REFUTED). The hypothesis is never stronger than its weakest obligation (ADR-076); see obligation_ledger."
    ),
    "CITATIONS_UNRESOLVED": (
        "At least one citation key has no bibliography entry, or a collection link names a manuscript that does not "
        "exist. The cited result cannot be checked."
    ),
}


def relay(code: str, detail: str = "") -> Dict[str, str]:
    if code not in RELAY_CODES:
        raise KeyError(f"Unregistered relay code {code!r}; register it in formal_status.RELAY_CODES.")
    message = RELAY_CODES[code] + (f" {detail}" if detail else "")
    return {"code": code, "message": message}


def relays(codes: Iterable[str]) -> List[Dict[str, str]]:
    seen: List[str] = []
    for code in codes:
        if code not in seen:
            seen.append(code)
    return [relay(c) for c in seen]


def backend_relay(backend: str) -> str:
    return "SMT_FIXED_SIZE_ONLY" if backend == "smt" else "ENUMERATION_DECLARED_DOMAINS_ONLY"
