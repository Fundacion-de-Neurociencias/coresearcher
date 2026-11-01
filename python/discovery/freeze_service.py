"""
python/discovery/freeze_service.py - Freeze acceptance criteria before any evaluation (ADR-DISCOVERY-085).

Method M3 of docs/architecture/VERIFICATION_METHODOLOGY.md: fix the acceptance criteria before seeing the work. A
freeze records, before anything is evaluated:

- for a submitted hypothesis, the discriminating states between it and its rivals: which applicable states it forbids
  (an observation of one refutes it) and, for each rival, the states only one of the two forbids (an observation of
  one supports one over the other). They are computed from the formal objects alone, with no observations;
- for a protocol or checklist, the document itself.

Each freeze has a SHA-256, a time and an author, and is an event in a hash-chained log (the ADR-083 style,
`hash_chain`). Digests are the research lifecycle's own (ADR-063): canonical JSON for criteria, raw bytes for a
document, so a frozen protocol has the digest its `protocol.document` ARTIFACT check records and the lifecycle watcher
re-checks. A freeze can be anchored to a lifecycle check, and is refused when the two digests differ.

An evaluation that references a freeze verifies it first. If the freeze record no longer matches its digest, the
digest is not the one the caller expected, or the hypothesis or its rivals differ from the frozen ones, the
evaluation is refused with the non-verdict BLOCKED (`formal_status.FrozenCriteriaChanged`). Verification never
recomputes the criteria, so it does not depend on which witness a solver happens to return.

Scope: formal soundness. A freeze fixes what counts as support or refutation; it does not judge whether the criteria
are good, and the author field is provenance, never evidence (ADR-066).
"""

from __future__ import annotations

import copy
import json
import os
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from python.discovery import formal_provenance, formal_status, hash_chain, research_lifecycle
from python.discovery.formal_hypothesis import HypothesisEvaluator, hypothesis_from_dict, hypothesis_to_dict

SCHEMA = "coresearcher.freezes/v1"
CRITERIA_SCHEMA = "coresearcher.freeze.criteria/v1"
STORE_ENV = "CORESEARCHER_FREEZE_PATH"

HYPOTHESIS = "discriminating_states"
DOCUMENT = "document"
KINDS = (HYPOTHESIS, DOCUMENT)

VERIFIED = "VERIFIED"
CHANGED = "CHANGED"
UNKNOWN = "UNKNOWN"

MAX_DOCUMENT_BYTES = 2_000_000
MAX_STORED_TEXT = 200_000  # documents up to this size keep their text in the store, for diffs

# A lifecycle lookup: (project_id, check_id) -> the SHA-256 the lifecycle recorded for that check, or None.
LifecycleLookup = Callable[[str, str], Optional[str]]


class FreezeError(ValueError):
    """A malformed freeze request, an unknown id, or a store that was edited outside the service."""


# ---------------------------------------------------------------------------
# What is frozen
# ---------------------------------------------------------------------------


def subject(hypothesis: Dict[str, Any], rivals: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """The hypothesis and its rivals in normal form (parsed and re-serialized), so defaults do not change a digest."""
    return {
        "hypothesis": hypothesis_to_dict(hypothesis_from_dict(hypothesis)),
        "rivals": [hypothesis_to_dict(hypothesis_from_dict(r)) for r in rivals or []],
    }


def subject_sha256(hypothesis: Dict[str, Any], rivals: Optional[List[Dict[str, Any]]] = None) -> str:
    return research_lifecycle.content_sha256(subject(hypothesis, rivals))


def _without_seal(report: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in report.items() if k not in ("provenance", "mandatory_relays", "formal_status")}


def hypothesis_criteria(
    hypothesis: Dict[str, Any],
    rivals: Optional[List[Dict[str, Any]]] = None,
    stated: Optional[Dict[str, Any]] = None,
    max_examples: int = 5,
    backend: str = "auto",
) -> Dict[str, Any]:
    """The acceptance criteria of a hypothesis against its rivals, from the formal objects alone.

    No observation is read. A solver that cannot decide raises its non-verdict (SolverUndecided, ThresholdExceeded,
    a missing z3); nothing is frozen then, because criteria that were not decided cannot be frozen as decided.
    `stated` holds criteria the author writes down in addition (free JSON, frozen verbatim).
    """
    subj = subject(hypothesis, rivals)
    h = hypothesis_from_dict(subj["hypothesis"])
    evaluation = HypothesisEvaluator.evaluate(h, [], max_examples=max_examples, backend=backend).to_dict()
    discrimination = []
    for rival in subj["rivals"]:
        report = HypothesisEvaluator.compare(h, hypothesis_from_dict(rival), max_examples, backend).to_dict()
        discrimination.append({
            "rival": report["hypothesis_b"],
            "relation": report["relation"],
            "forbidden_only_by_hypothesis": report["forbidden_only_by_a"],
            "forbidden_only_by_rival": report["forbidden_only_by_b"],
            "discriminating_examples": report["discriminating_examples"],
            "rule": (
                "Observing a state forbidden only by the rival supports the hypothesis over it; observing a state "
                "forbidden only by the hypothesis supports the rival."
            ),
        })
    return {
        "schema": CRITERIA_SCHEMA,
        "kind": HYPOTHESIS,
        "subject": subj,
        "subject_sha256": research_lifecycle.content_sha256(subj),
        "refutation": {
            "content_verdict": evaluation["content_verdict"],
            "possible": evaluation["content_verdict"] not in ("UNFALSIFIABLE", "VACUOUS", "SELF_CONTRADICTORY"),
            "applicable_states": evaluation["applicable_states"],
            "forbidden_states": evaluation["forbidden_states"],
            "falsifier_examples": evaluation["falsifier_examples"],
            "rule": "Observing an applicable state the hypothesis forbids refutes it.",
        },
        "discrimination": discrimination,
        "stated": copy.deepcopy(stated) if stated else {},
        "backend": evaluation["backend"],
        "max_examples": max_examples,
        "evaluation_digest": research_lifecycle.content_sha256(_without_seal(evaluation)),
    }


def record_problems(record: Dict[str, Any]) -> List[str]:
    """Why a freeze record does not match its own digest (empty when it does)."""
    problems = []
    kind, sha = record.get("kind"), record.get("sha256")
    if kind not in KINDS:
        return [f"unknown freeze kind {kind!r}"]
    if not research_lifecycle.is_sha256(sha):
        return ["the record has no valid SHA-256"]
    content = record.get("content") or {}
    if kind == HYPOTHESIS:
        if research_lifecycle.content_sha256(content) != sha:
            problems.append("the frozen criteria no longer match the freeze's SHA-256")
        elif research_lifecycle.content_sha256(content.get("subject")) != content.get("subject_sha256"):
            problems.append("the frozen subject no longer matches its SHA-256")
    elif "text" in content and research_lifecycle.bytes_sha256(content["text"].encode("utf-8")) != sha:
        problems.append("the stored document text no longer matches the freeze's SHA-256")
    if record.get("id") != freeze_id(sha):
        problems.append("the freeze id does not match its SHA-256")
    return problems


def freeze_id(sha256: str) -> str:
    return f"FZ-{sha256[:16]}"


def verify_embedded(
    record: Dict[str, Any],
    expected_sha256: Optional[str] = None,
    hypothesis: Optional[Dict[str, Any]] = None,
    rivals: Optional[List[Dict[str, Any]]] = None,
    document: Optional[bytes] = None,
) -> Dict[str, Any]:
    """Verifies one freeze record against what an evaluation is about to use. Pure: no store, no solver.

    VERIFIED (formal_status DECIDED) only when the record matches its digest, the digest is the expected one (when one
    is given), and the subject is the frozen one: the same hypothesis and rivals in normal form, or the same document
    bytes. Anything else is CHANGED with formal_status BLOCKED and the reasons.
    """
    problems = record_problems(record)
    sha = record.get("sha256")
    if expected_sha256 is not None and expected_sha256 != sha:
        problems.append(f"the freeze's SHA-256 is {sha}, not the expected {expected_sha256}")
    content = record.get("content") or {}
    if record.get("kind") == HYPOTHESIS:
        if hypothesis is None:
            problems.append("the evaluation names no hypothesis to compare with the frozen one")
        else:
            try:
                now = subject_sha256(hypothesis, rivals)
            except (TypeError, ValueError) as exc:
                problems.append(f"the evaluated hypothesis cannot be normalized: {exc}")
            else:
                if now != content.get("subject_sha256"):
                    problems.append(
                        "the hypothesis or its rivals differ from the ones whose criteria were frozen "
                        f"(subject SHA-256 {now} != frozen {content.get('subject_sha256')})"
                    )
    elif record.get("kind") == DOCUMENT and document is not None:
        if research_lifecycle.bytes_sha256(document) != sha:
            problems.append("the document differs from the frozen one")
    verified = not problems
    return {
        "freeze_id": record.get("id"),
        "kind": record.get("kind"),
        "frozen_sha256": sha,
        "author": record.get("author"),
        "frozen_at": record.get("frozen_at"),
        "status": VERIFIED if verified else CHANGED,
        "formal_status": (formal_status.FormalStatus.DECIDED if verified else formal_status.FormalStatus.BLOCKED).value,
        "problems": problems,
    }


def require_verified(check: Dict[str, Any]) -> Dict[str, Any]:
    """Raises the BLOCKED non-verdict unless the verification passed."""
    if check["status"] != VERIFIED:
        raise formal_status.FrozenCriteriaChanged(
            f"Freeze {check.get('freeze_id')} does not hold: {'; '.join(check['problems'])}", check
        )
    return check


def lifecycle_lookup(service) -> LifecycleLookup:
    """Reads the SHA-256 a lifecycle project recorded for a check: the latest result, else the gate evidence."""

    def lookup(project_id: str, check_id: str) -> Optional[str]:
        try:
            project = service.get(project_id)
        except KeyError:
            return None
        results = project.results.get(check_id) or []
        if results and results[-1].sha256:
            return results[-1].sha256
        for gate in reversed(project.active_gates()):
            if check_id in gate.evidence:
                return gate.evidence[check_id].get("sha256")
        return None

    return lookup


# ---------------------------------------------------------------------------
# The store
# ---------------------------------------------------------------------------


class FreezeStore:
    """Freeze records with a hash-chained event log; persisted as JSON when a path is given."""

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        self.freezes: Dict[str, Dict[str, Any]] = {}
        self.events: List[Dict[str, Any]] = []
        if self.path and self.path.is_file():
            self._load()

    def _load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("schema") != SCHEMA:
            raise FreezeError(f"{self.path} is not a {SCHEMA} store.")
        self.freezes = data.get("freezes", {})
        self.events = data.get("events", [])
        self.verify()

    def _save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)

    def to_dict(self) -> Dict[str, Any]:
        return {"schema": SCHEMA, "freezes": self.freezes, "events": self.events}

    def verify(self) -> None:
        """Refuses a store whose log or records were edited: every record must match its digest and its event."""
        hash_chain.verify(self.events, FreezeError, "freeze store")
        logged = {e["payload"]["id"]: e["payload"] for e in self.events if e["kind"] == "freeze"}
        if set(logged) != set(self.freezes):
            raise FreezeError("The freeze records and the event log list different freezes.")
        for fid, record in self.freezes.items():
            problems = record_problems(record)
            event = logged[fid]
            if any(event.get(k) != record.get(k) for k in ("sha256", "kind", "author", "frozen_at")):
                problems.append("the record differs from its logged event")
            if problems:
                raise FreezeError(f"Freeze {fid} was edited outside the service: {'; '.join(problems)}.")

    def get(self, fid: str) -> Dict[str, Any]:
        record = self.freezes.get(fid)
        if record is None:
            raise FreezeError(f"No freeze {fid!r}.")
        return copy.deepcopy(record)

    def _add(
        self,
        kind: str,
        sha: str,
        content: Dict[str, Any],
        author: str,
        label: str,
        lifecycle: Optional[Dict[str, str]],
        lookup: Optional[LifecycleLookup],
    ) -> Dict[str, Any]:
        if not isinstance(author, str) or not author.strip():
            raise FreezeError("A freeze needs an author: who fixed these criteria.")
        anchor = None
        if lifecycle:
            project_id, check_id = lifecycle.get("project_id", ""), lifecycle.get("check_id", "protocol.document")
            if lookup is None:
                raise FreezeError("A lifecycle anchor needs the lifecycle service.")
            recorded = lookup(project_id, check_id)
            if recorded is None:
                raise FreezeError(f"Lifecycle project {project_id!r} has no recorded SHA-256 for {check_id!r}.")
            if recorded != sha:
                raise FreezeError(
                    f"The lifecycle recorded {recorded} for {project_id}/{check_id}, but this freeze is {sha}; "
                    "they are not the same artifact."
                )
            anchor = {"project_id": project_id, "check_id": check_id, "sha256": recorded}
        fid = freeze_id(sha)
        with self._lock:
            if fid in self.freezes:  # The earliest freeze of the same content stands.
                return dict(copy.deepcopy(self.freezes[fid]), already_frozen=True)
            record = {
                "id": fid,
                "kind": kind,
                "sha256": sha,
                "author": author.strip(),
                "frozen_at": formal_provenance.utc_now(),
                "label": label,
                "content": content,
                "lifecycle": anchor,
            }
            hash_chain.append(self.events, "freeze", {k: record[k] for k in (
                "id", "kind", "sha256", "author", "frozen_at", "label", "lifecycle")})
            self.freezes[fid] = record
            self._save()
            return dict(copy.deepcopy(record), already_frozen=False)

    def freeze_hypothesis(
        self,
        hypothesis: Dict[str, Any],
        rivals: Optional[List[Dict[str, Any]]],
        author: str,
        label: str = "",
        stated: Optional[Dict[str, Any]] = None,
        max_examples: int = 5,
        backend: str = "auto",
        lifecycle: Optional[Dict[str, str]] = None,
        lookup: Optional[LifecycleLookup] = None,
    ) -> Dict[str, Any]:
        """Freezes the discriminating states of a hypothesis and its rivals. Non-verdicts raise; nothing is frozen."""
        if not isinstance(author, str) or not author.strip():
            raise FreezeError("A freeze needs an author: who fixed these criteria.")
        content = hypothesis_criteria(hypothesis, rivals, stated, max_examples, backend)
        sha = research_lifecycle.content_sha256(content)
        return self._add(HYPOTHESIS, sha, content, author, label, lifecycle, lookup)

    def freeze_document(
        self,
        data: bytes,
        author: str,
        label: str = "",
        name: str = "",
        lifecycle: Optional[Dict[str, str]] = None,
        lookup: Optional[LifecycleLookup] = None,
    ) -> Dict[str, Any]:
        """Freezes a protocol or checklist by the SHA-256 of its bytes, as a lifecycle ARTIFACT check does."""
        if not isinstance(data, bytes) or not data:
            raise FreezeError("A document freeze needs a non-empty document.")
        if len(data) > MAX_DOCUMENT_BYTES:
            raise FreezeError(f"A frozen document is limited to {MAX_DOCUMENT_BYTES} bytes.")
        content: Dict[str, Any] = {"name": name, "bytes": len(data)}
        if len(data) <= MAX_STORED_TEXT:
            try:
                content["text"] = data.decode("utf-8")
            except UnicodeDecodeError:
                pass
        sha = research_lifecycle.bytes_sha256(data)
        return self._add(DOCUMENT, sha, content, author, label, lifecycle, lookup)

    def verify_reference(
        self,
        fid: str,
        expected_sha256: Optional[str] = None,
        hypothesis: Optional[Dict[str, Any]] = None,
        rivals: Optional[List[Dict[str, Any]]] = None,
        document: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """`verify_embedded` against the stored record; an unknown id is UNKNOWN, also BLOCKED."""
        record = self.freezes.get(fid)
        if record is None:
            return {
                "freeze_id": fid,
                "kind": None,
                "frozen_sha256": None,
                "author": None,
                "frozen_at": None,
                "status": UNKNOWN,
                "formal_status": formal_status.FormalStatus.BLOCKED.value,
                "problems": [f"no freeze {fid!r} in this store"],
            }
        return verify_embedded(record, expected_sha256, hypothesis, rivals, document)

    def reference(self, fid: str, expected_sha256: Optional[str] = None) -> Dict[str, Any]:
        """The freeze as a request carries it, so a later offline re-analysis can verify it without the store."""
        record = self.get(fid)
        return {"freeze_id": fid, "expected_sha256": expected_sha256 or record["sha256"], "record": record}


def default_store() -> Optional[Path]:
    value = os.getenv(STORE_ENV)
    return Path(value) if value else None


def load(path: Optional[Path] = None) -> FreezeStore:
    return FreezeStore(path if path is not None else default_store())


def check_reference(reference: Dict[str, Any], hypothesis: Dict[str, Any], rivals: List[Dict[str, Any]]):
    """Verifies a request's embedded freeze reference (`FreezeStore.reference`) against the evaluated subject."""
    if not isinstance(reference, dict) or not isinstance(reference.get("record"), dict):
        raise formal_status.FrozenCriteriaChanged("The freeze reference carries no freeze record.", {})
    return verify_embedded(reference["record"], reference.get("expected_sha256"), hypothesis, rivals)


__all__ = [
    "FreezeStore", "FreezeError", "hypothesis_criteria", "verify_embedded", "require_verified", "subject",
    "subject_sha256", "lifecycle_lookup", "check_reference", "load", "HYPOTHESIS", "DOCUMENT", "VERIFIED", "CHANGED",
]
