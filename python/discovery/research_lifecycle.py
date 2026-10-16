"""
python/discovery/research_lifecycle.py - Stage gates for research projects inside CoResearcher (ADR-DISCOVERY-063).

A research project moves through fixed stages (question, hypothesis, protocol, execution, controls, analysis,
report). Each stage ends at a gate with a checklist. A gate passes only when every required check is satisfied by the
right kind of evidence:

- VERIFIER checks need a result from an independent tool (z3, Lean, the formal evaluator, a test suite). The agent
  that produced the work cannot certify it: a self-check is recorded but never satisfies a VERIFIER check.
- HUMAN checks need a person's sign-off.
- ARTIFACT checks need a file path and its SHA-256, so later drift can be detected.
- RUBRIC checks need a number and pass at the template's threshold.

Every passed gate creates a project version whose digest chains the previous digest and the accepted evidence, so the
history is tamper-evident. A project can be reworked: reopening a stage supersedes the gates after it. A release
publishes the result of a project whose report gate has passed. Its kind is EXPLORATORY or PREREGISTERED, decided by
policy, never by the caller, and its notes list every criterion that was not met.

The state is event-sourced: each change is an event, and an optional JSON Lines file makes the log durable. The two
agents at the end are deterministic: `LifecycleWatcher` reports stalled stages, pending sign-offs and artifacts that
changed after a gate accepted them; `release_notes` writes the notes of a release from the log.

This is coordination inside CoResearcher. The fleet-level product lifecycle is OnTrack's job; `ontrack_status`
exports a project in a stable shape (`coresearcher.lifecycle/v1`) that OnTrack can ingest.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

SCHEMA_VERSION = 1
EXPORT_SCHEMA = "coresearcher.lifecycle/v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class LifecycleError(ValueError):
    """An operation the lifecycle rules do not allow."""


class Stage(str, Enum):
    QUESTION = "QUESTION"
    HYPOTHESIS = "HYPOTHESIS"
    PROTOCOL = "PROTOCOL"
    EXECUTION = "EXECUTION"
    CONTROLS = "CONTROLS"
    ANALYSIS = "ANALYSIS"
    REPORT = "REPORT"


STAGES: List[Stage] = list(Stage)


class CheckKind(str, Enum):
    VERIFIER = "VERIFIER"
    HUMAN = "HUMAN"
    ARTIFACT = "ARTIFACT"
    RUBRIC = "RUBRIC"


class ActorRole(str, Enum):
    AGENT = "AGENT"  # the agent that produced the work
    VERIFIER_TOOL = "VERIFIER_TOOL"  # an independent checker: z3, Lean, the formal evaluator, a test suite
    HUMAN = "HUMAN"


class CheckStatus(str, Enum):
    SATISFIED = "SATISFIED"
    FAILED = "FAILED"
    MISSING = "MISSING"


class GateDecision(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"  # a required check failed
    INCOMPLETE = "INCOMPLETE"  # a required non-human check has no accepted result
    PENDING_HUMAN = "PENDING_HUMAN"  # only human sign-offs are missing


class ReleaseKind(str, Enum):
    EXPLORATORY = "EXPLORATORY"
    PREREGISTERED = "PREREGISTERED"


# Which roles may satisfy each kind of check. A self-check (role AGENT) is kept in the log but satisfies nothing
# except rubric and artifact checks, whose evidence is a number or a hash that anyone can recompute.
ACCEPTED_ROLES: Dict[CheckKind, Tuple[ActorRole, ...]] = {
    CheckKind.VERIFIER: (ActorRole.VERIFIER_TOOL,),
    CheckKind.HUMAN: (ActorRole.HUMAN,),
    CheckKind.ARTIFACT: (ActorRole.AGENT, ActorRole.VERIFIER_TOOL, ActorRole.HUMAN),
    CheckKind.RUBRIC: (ActorRole.AGENT, ActorRole.VERIFIER_TOOL, ActorRole.HUMAN),
}


# --------------------------------------------------------------------------- checklist templates


@dataclass(frozen=True)
class CheckTemplate:
    check_id: str
    description: str
    kind: CheckKind
    required: bool = True
    threshold: Optional[float] = None  # RUBRIC only: satisfied when value >= threshold

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "kind": self.kind.value}


def _c(check_id, description, kind, required=True, threshold=None) -> CheckTemplate:
    return CheckTemplate(check_id, description, kind, required, threshold)


V, H, A, R = CheckKind.VERIFIER, CheckKind.HUMAN, CheckKind.ARTIFACT, CheckKind.RUBRIC

# The default checklist. Stage names follow the research workflow; the checks name what CoResearcher already
# produces (formal objects, frozen protocols, z3/Lean verdicts, the claims register).
DEFAULT_TEMPLATE: Dict[Stage, Tuple[CheckTemplate, ...]] = {
    Stage.QUESTION: (
        _c("question.statement", "The research question is written down and hashed.", A),
        _c("question.owner", "A scientist owns the question and agrees it is worth answering.", H),
    ),
    Stage.HYPOTHESIS: (
        _c("hypothesis.formal_object", "The formal evaluator finds the hypothesis falsifiable and consistent.", V),
        _c("hypothesis.rivals", "Number of rival hypotheses compared with it.", R, threshold=1),
        _c("hypothesis.confirmed", "The researcher confirms the formal object says what the prose meant.", H),
    ),
    Stage.PROTOCOL: (
        _c("protocol.document", "The protocol, with pre-registered criteria, is written and hashed.", A),
        _c("protocol.criteria", "Number of pre-registered pass/fail criteria.", R, threshold=1),
        _c("protocol.dataset_frozen", "The evaluation dataset is frozen and hashed.", A),
        _c("protocol.review", "The protocol and dataset were reviewed before any run.", H),
    ),
    Stage.EXECUTION: (
        _c("execution.raw_outputs", "Raw outputs are kept and hashed before any scoring.", A),
        _c("execution.environment", "Tool, model and data versions of the run are recorded.", A),
        _c("execution.integrity", "An independent check finds no leakage or tampering in the run.", V, required=False),
    ),
    Stage.CONTROLS: (
        _c("controls.null_or_baseline", "A null model or baseline was run under the same protocol.", V),
        _c("controls.ablation", "Number of ablations run.", R, required=False, threshold=1),
    ),
    Stage.ANALYSIS: (
        _c("analysis.criteria_evaluated", "Every pre-registered criterion is scored MET or NOT_MET by script.", V),
        _c("analysis.intervals", "Proportions are reported with confidence intervals (1 = yes).", R, threshold=1),
        _c("analysis.deviations", "Deviations from the protocol are listed and acknowledged.", H),
    ),
    Stage.REPORT: (
        _c("report.claims_register", "The claims register row is updated, whatever the outcome.", A),
        _c("report.signoff", "A maintainer signs off the report and its limits.", H),
    ),
}

TEMPLATES: Dict[str, Dict[Stage, Tuple[CheckTemplate, ...]]] = {"default": DEFAULT_TEMPLATE}


def template_to_dict(name: str) -> Dict[str, Any]:
    template = TEMPLATES[name]
    return {"name": name, "stages": {s.value: [c.to_dict() for c in template[s]] for s in STAGES}}


# --------------------------------------------------------------------------- state


@dataclass
class CheckResult:
    check_id: str
    ok: bool
    actor: str
    role: ActorRole
    at: str
    note: str = ""
    value: Optional[float] = None
    artifact_path: Optional[str] = None
    sha256: Optional[str] = None
    criteria: Dict[str, str] = field(default_factory=dict)  # analysis: criterion id -> MET / NOT_MET

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "role": self.role.value}


@dataclass
class GateRecord:
    stage: Stage
    version: int
    digest: str
    at: str
    evidence: Dict[str, Dict[str, Any]]
    superseded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "stage": self.stage.value}


@dataclass
class Release:
    release_id: str
    version: int
    digest: str
    kind: ReleaseKind
    at: str
    actor: str
    criteria: Dict[str, str]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "kind": self.kind.value}


@dataclass
class Project:
    project_id: str
    title: str
    template: str
    created_at: str
    stage: Stage = Stage.QUESTION
    results: Dict[str, List[CheckResult]] = field(default_factory=dict)  # check id -> results, newest last
    gates: List[GateRecord] = field(default_factory=list)
    releases: List[Release] = field(default_factory=list)
    protocol_reworked_after_execution: bool = False
    last_event_at: str = ""

    def checks(self, stage: Stage) -> Tuple[CheckTemplate, ...]:
        return TEMPLATES[self.template][stage]

    def active_gates(self) -> List[GateRecord]:
        return [g for g in self.gates if not g.superseded]

    def passed(self, stage: Stage) -> bool:
        return any(g.stage == stage for g in self.active_gates())

    @property
    def version(self) -> int:
        active = self.active_gates()
        return active[-1].version if active else 0

    @property
    def digest(self) -> str:
        active = self.active_gates()
        return active[-1].digest if active else ""


@dataclass
class CheckEvaluation:
    check: CheckTemplate
    status: CheckStatus
    result: Optional[CheckResult]
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check.to_dict(),
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "reason": self.reason,
        }


@dataclass
class GateEvaluation:
    project_id: str
    stage: Stage
    decision: GateDecision
    checks: List[CheckEvaluation]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "stage": self.stage.value,
            "decision": self.decision.value,
            "checks": [c.to_dict() for c in self.checks],
        }


# --------------------------------------------------------------------------- policies


def _evaluate_check(check: CheckTemplate, results: List[CheckResult]) -> CheckEvaluation:
    """The newest accepted result decides; results from roles that cannot satisfy the check are ignored."""
    accepted = [r for r in results if r.role in ACCEPTED_ROLES[check.kind]]
    if not accepted:
        ignored = (
            f" ({len(results)} result(s) from roles that cannot satisfy it, such as self-checks)" if results else ""
        )
        return CheckEvaluation(check, CheckStatus.MISSING, None, "no accepted result" + ignored)
    latest = accepted[-1]
    if not latest.ok:
        return CheckEvaluation(check, CheckStatus.FAILED, latest, latest.note or "reported as failed")
    if check.kind == CheckKind.RUBRIC and (latest.value is None or latest.value < (check.threshold or 0)):
        return CheckEvaluation(check, CheckStatus.FAILED, latest, f"value {latest.value} below {check.threshold}")
    return CheckEvaluation(check, CheckStatus.SATISFIED, latest, "")


def validate_result(check: CheckTemplate, result: CheckResult) -> None:
    """Shape rules every submitted result must meet, whatever its role."""
    if check.kind == CheckKind.ARTIFACT and result.ok:
        if not result.artifact_path or not result.sha256 or not _SHA256.match(result.sha256):
            raise LifecycleError(f"{check.check_id}: an artifact result needs a path and a lowercase SHA-256.")
    if check.kind == CheckKind.RUBRIC and result.value is None:
        raise LifecycleError(f"{check.check_id}: a rubric result needs a numeric value.")
    for criterion, outcome in result.criteria.items():
        if outcome not in ("MET", "NOT_MET"):
            raise LifecycleError(f"{check.check_id}: criterion {criterion!r} must be MET or NOT_MET, not {outcome!r}.")


def release_kind(project: Project) -> Tuple[ReleaseKind, List[str]]:
    """PREREGISTERED only if the protocol gate held from before execution to the report. Reasons otherwise."""
    reasons = []
    if not project.passed(Stage.PROTOCOL):
        reasons.append("the protocol gate has not passed")
    if project.protocol_reworked_after_execution:
        reasons.append("the protocol was reopened after execution had passed its gate")
    return (ReleaseKind.EXPLORATORY if reasons else ReleaseKind.PREREGISTERED), reasons


def analysis_criteria(project: Project) -> Dict[str, str]:
    for check in project.checks(Stage.ANALYSIS):
        evaluation = _evaluate_check(check, project.results.get(check.check_id, []))
        if evaluation.result and evaluation.result.criteria:
            return dict(evaluation.result.criteria)
    return {}


# --------------------------------------------------------------------------- service


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _canonical(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class LifecycleService:
    """Event-sourced store of research projects. Every change goes through `_record`, so replay rebuilds the state."""

    def __init__(self, log_path: Optional[Path] = None, clock: Callable[[], str] = _now):
        self.projects: Dict[str, Project] = {}
        self.events: List[Dict[str, Any]] = []
        self._clock = clock
        self._log_path = Path(log_path) if log_path else None
        if self._log_path and self._log_path.exists():
            for line in self._log_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._apply(_upgrade(json.loads(line)))

    # ---- public operations

    def create_project(self, project_id: str, title: str, template: str = "default") -> Project:
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$", project_id):
            raise LifecycleError("project_id: 1-64 letters, digits, '.', '_' or '-'.")
        if project_id in self.projects:
            raise LifecycleError(f"Project {project_id!r} already exists.")
        if template not in TEMPLATES:
            raise LifecycleError(f"Unknown template {template!r}.")
        self._record("project_created", project_id, {"title": title, "template": template})
        return self.projects[project_id]

    def submit_result(
        self,
        project_id: str,
        check_id: str,
        ok: bool,
        actor: str,
        role: ActorRole,
        note: str = "",
        value: Optional[float] = None,
        artifact_path: Optional[str] = None,
        sha256: Optional[str] = None,
        criteria: Optional[Dict[str, str]] = None,
    ) -> CheckResult:
        project = self._open(project_id)
        stage, check = self._find_check(project, check_id)
        if stage != project.stage:
            raise LifecycleError(f"{check_id} belongs to {stage.value}; the project is at {project.stage.value}.")
        if not actor.strip():
            raise LifecycleError("actor must name who produced the result.")
        result = CheckResult(
            check_id, ok, actor, ActorRole(role), "", note, value, artifact_path, sha256, dict(criteria or {})
        )
        validate_result(check, result)
        payload = result.to_dict()
        payload.pop("at")
        self._record("result_submitted", project_id, payload)
        return project.results[check_id][-1]

    def evaluate_gate(self, project_id: str) -> GateEvaluation:
        project = self._get(project_id)
        evaluations = [_evaluate_check(c, project.results.get(c.check_id, [])) for c in project.checks(project.stage)]
        required = [e for e in evaluations if e.check.required]
        if any(e.status == CheckStatus.FAILED for e in required):
            decision = GateDecision.FAIL
        elif all(e.status == CheckStatus.SATISFIED for e in required):
            decision = GateDecision.PASS
        elif all(e.status == CheckStatus.SATISFIED or e.check.kind == CheckKind.HUMAN for e in required):
            decision = GateDecision.PENDING_HUMAN
        else:
            decision = GateDecision.INCOMPLETE
        return GateEvaluation(project_id, project.stage, decision, evaluations)

    def pass_gate(self, project_id: str, actor: str) -> GateRecord:
        """Record the gate of the current stage as passed and advance. Refused unless the evaluation is PASS."""
        project = self._open(project_id)
        evaluation = self.evaluate_gate(project_id)
        if evaluation.decision != GateDecision.PASS:
            raise LifecycleError(f"Gate {project.stage.value} is {evaluation.decision.value}; it cannot pass.")
        evidence = {e.check.check_id: e.result.to_dict() for e in evaluation.checks if e.result is not None}
        self._record("gate_passed", project_id, {"actor": actor, "evidence": evidence})
        return project.active_gates()[-1]

    def rework(self, project_id: str, stage: Stage, actor: str, reason: str) -> Project:
        """Reopen an earlier stage: its gate and every later one are superseded, and their results must be redone."""
        project = self._get(project_id)
        if stage not in {s.value for s in STAGES}:
            raise LifecycleError(f"Unknown stage {stage!r}.")
        stage = Stage(stage)
        if STAGES.index(stage) > STAGES.index(project.stage):
            raise LifecycleError(f"{stage.value} has not been reached yet.")
        if not reason.strip():
            raise LifecycleError("A rework needs a reason; it becomes part of the release notes.")
        self._record("stage_reopened", project_id, {"stage": stage.value, "actor": actor, "reason": reason})
        return project

    def release(self, project_id: str, actor: str, summary: str = "") -> Release:
        project = self._get(project_id)
        if not project.passed(Stage.REPORT):
            raise LifecycleError("Only a project whose report gate has passed can be released.")
        if any(r.version == project.version for r in project.releases):
            raise LifecycleError(f"Version {project.version} is already released.")
        self._record("released", project_id, {"actor": actor, "summary": summary})
        return project.releases[-1]

    def get(self, project_id: str) -> Project:
        return self._get(project_id)

    def project_events(self, project_id: str) -> List[Dict[str, Any]]:
        self._get(project_id)
        return [e for e in self.events if e["project_id"] == project_id]

    # ---- event log

    def _record(self, kind: str, project_id: str, payload: Dict[str, Any]) -> None:
        event = {
            "schema_version": SCHEMA_VERSION,
            "seq": len(self.events) + 1,
            "type": kind,
            "project_id": project_id,
            "at": self._clock(),
            "payload": payload,
        }
        # Apply first, so an invalid event never reaches the durable log.
        self._apply(event)
        if self._log_path:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            with self._log_path.open("a", encoding="utf-8") as log:
                log.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _apply(self, event: Dict[str, Any]) -> None:
        kind, pid, at, payload = event["type"], event["project_id"], event["at"], copy.deepcopy(event["payload"])
        if kind == "project_created":
            self.projects[pid] = Project(pid, payload["title"], payload["template"], at, last_event_at=at)
        else:
            project = self.projects[pid]
            project.last_event_at = at
            if kind == "result_submitted":
                payload["role"] = ActorRole(payload["role"])
                project.results.setdefault(payload["check_id"], []).append(CheckResult(at=at, **payload))
            elif kind == "gate_passed":
                previous = project.digest
                version = max((g.version for g in project.gates), default=0) + 1
                digest = hashlib.sha256(
                    _canonical({"previous": previous, "stage": project.stage.value, "evidence": payload["evidence"]})
                ).hexdigest()
                project.gates.append(GateRecord(project.stage, version, digest, at, payload["evidence"]))
                index = STAGES.index(project.stage)
                if index + 1 < len(STAGES):
                    project.stage = STAGES[index + 1]
            elif kind == "stage_reopened":
                stage = Stage(payload["stage"])
                if stage == Stage.PROTOCOL and project.passed(Stage.EXECUTION):
                    project.protocol_reworked_after_execution = True
                reopened = STAGES[STAGES.index(stage) :]
                for gate in project.gates:
                    if gate.stage in reopened:
                        gate.superseded = True
                for check_id in [c.check_id for s in reopened for c in project.checks(s)]:
                    project.results.pop(check_id, None)
                project.stage = stage
            elif kind == "released":
                criteria = analysis_criteria(project)
                kind_, reasons = release_kind(project)
                release = Release(
                    f"{pid}-v{project.version}",
                    project.version,
                    project.digest,
                    kind_,
                    at,
                    payload["actor"],
                    criteria,
                    "",
                )
                release.notes = release_notes(project, release, payload.get("summary", ""), reasons, self)
                project.releases.append(release)
            else:
                raise LifecycleError(f"Unknown event type {kind!r}.")
        self.events.append(event)

    # ---- helpers

    def _get(self, project_id: str) -> Project:
        if project_id not in self.projects:
            raise KeyError(project_id)
        return self.projects[project_id]

    def _open(self, project_id: str) -> Project:
        """The project, if its current stage is still open (the report stage closes when its gate passes)."""
        project = self._get(project_id)
        if project.passed(project.stage):
            raise LifecycleError(f"{project.stage.value} has passed; rework a stage to change the project.")
        return project

    @staticmethod
    def _find_check(project: Project, check_id: str) -> Tuple[Stage, CheckTemplate]:
        for stage in STAGES:
            for check in project.checks(stage):
                if check.check_id == check_id:
                    return stage, check
        raise LifecycleError(f"Unknown check {check_id!r} for template {project.template!r}.")


def _upgrade(event: Dict[str, Any]) -> Dict[str, Any]:
    """Bring a logged event to the current schema. Version 1 is the first; later versions add steps here."""
    version = event.get("schema_version")
    if version != SCHEMA_VERSION:
        raise LifecycleError(
            f"Event {event.get('seq')} has schema version {version}; this code reads {SCHEMA_VERSION}."
        )
    return event


# --------------------------------------------------------------------------- agents


def release_notes(
    project: Project,
    release: Release,
    summary: str = "",
    kind_reasons: Optional[List[str]] = None,
    service: Optional[LifecycleService] = None,
) -> str:
    """Release notes written from the log, never from a model: outcome first, then what was checked and changed."""
    met = sorted(k for k, v in release.criteria.items() if v == "MET")
    not_met = sorted(k for k, v in release.criteria.items() if v == "NOT_MET")
    lines = [
        f"# {project.title}: release {release.release_id}",
        "",
        f"- Kind: **{release.kind.value}**" + (f" ({'; '.join(kind_reasons)})" if kind_reasons else ""),
        f"- Version {release.version}, digest `{release.digest[:16]}`, released by {release.actor} at {release.at}",
        "",
        "## Outcome",
        "",
    ]
    if release.criteria:
        lines += [
            f"- Criteria met: {', '.join(met) or 'none'}",
            f"- Criteria **not met**: {', '.join(not_met) or 'none'}",
        ]
    else:
        lines.append("- No pre-registered criteria were scored.")
    if summary:
        lines += ["", summary]
    lines += ["", "## Gates", ""]
    for gate in project.active_gates():
        verifiers = sorted({e["actor"] for e in gate.evidence.values() if e["role"] == ActorRole.VERIFIER_TOOL.value})
        humans = sorted({e["actor"] for e in gate.evidence.values() if e["role"] == ActorRole.HUMAN.value})
        detail = "; ".join(
            part
            for part in (
                f"verified by {', '.join(verifiers)}" if verifiers else "",
                f"signed off by {', '.join(humans)}" if humans else "",
            )
            if part
        )
        lines.append(f"- v{gate.version} {gate.stage.value}" + (f": {detail}" if detail else ""))
    if service is not None:
        reworks = [e for e in service.project_events(project.project_id) if e["type"] == "stage_reopened"]
        if reworks:
            lines += ["", "## Reworks", ""]
            lines += [
                f"- {e['at']}: {e['payload']['stage']} reopened by {e['payload']['actor']}: {e['payload']['reason']}"
                for e in reworks
            ]
    return "\n".join(lines) + "\n"


class FindingKind(str, Enum):
    STALLED = "STALLED"
    PENDING_HUMAN = "PENDING_HUMAN"
    ARTIFACT_DRIFT = "ARTIFACT_DRIFT"
    ARTIFACT_MISSING = "ARTIFACT_MISSING"
    UNRELEASED = "UNRELEASED"


@dataclass
class Finding:
    project_id: str
    kind: FindingKind
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "kind": self.kind.value, "detail": self.detail}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class LifecycleWatcher:
    """Reads the lifecycle state and reports what needs attention. It never changes a project."""

    def __init__(self, service: LifecycleService, root: Optional[Path] = None, stall_days: int = 14):
        self.service = service
        self.root = Path(root) if root else None
        self.stall_days = stall_days

    def scan(self, now: Optional[datetime] = None) -> List[Finding]:
        now = now or datetime.now(timezone.utc)
        findings: List[Finding] = []
        for project in self.service.projects.values():
            findings += self._scan_project(project, now)
        return findings

    def _scan_project(self, project: Project, now: datetime) -> List[Finding]:
        pid, out = project.project_id, []
        released = bool(project.releases) and project.releases[-1].version == project.version
        if project.passed(Stage.REPORT):
            if not released:
                out.append(Finding(pid, FindingKind.UNRELEASED, f"report gate passed at v{project.version}"))
        else:
            idle = now - datetime.fromisoformat(project.last_event_at)
            if idle > timedelta(days=self.stall_days):
                out.append(
                    Finding(pid, FindingKind.STALLED, f"{project.stage.value}: no activity for {idle.days} days")
                )
            gate = self.service.evaluate_gate(pid)
            if gate.decision == GateDecision.PENDING_HUMAN:
                waiting = [e.check.check_id for e in gate.checks if e.status == CheckStatus.MISSING]
                out.append(
                    Finding(pid, FindingKind.PENDING_HUMAN, f"{project.stage.value} waits on {', '.join(waiting)}")
                )
        if self.root is not None:
            out += self._scan_artifacts(project)
        return out

    def _scan_artifacts(self, project: Project) -> List[Finding]:
        """An artifact accepted at a gate (or submitted at the open stage) must still have the recorded hash."""
        recorded: Dict[str, Tuple[str, str]] = {}
        for gate in project.active_gates():
            for check_id, result in gate.evidence.items():
                if result.get("sha256") and result.get("artifact_path"):
                    recorded[check_id] = (result["artifact_path"], result["sha256"])
        for check in project.checks(project.stage):
            results = project.results.get(check.check_id, [])
            if check.kind == CheckKind.ARTIFACT and results and results[-1].sha256 and results[-1].artifact_path:
                recorded[check.check_id] = (results[-1].artifact_path, results[-1].sha256)
        out = []
        for check_id, (rel, sha) in sorted(recorded.items()):
            path = (self.root / rel).resolve()
            if not path.is_relative_to(self.root.resolve()):
                out.append(
                    Finding(project.project_id, FindingKind.ARTIFACT_MISSING, f"{check_id}: {rel} is outside the root")
                )
            elif not path.is_file():
                out.append(Finding(project.project_id, FindingKind.ARTIFACT_MISSING, f"{check_id}: {rel} not found"))
            elif _sha256_file(path) != sha:
                out.append(
                    Finding(
                        project.project_id,
                        FindingKind.ARTIFACT_DRIFT,
                        f"{check_id}: {rel} changed after it was recorded",
                    )
                )
        return out


# --------------------------------------------------------------------------- export


def project_to_dict(project: Project, service: LifecycleService) -> Dict[str, Any]:
    gate = service.evaluate_gate(project.project_id)
    return {
        "project_id": project.project_id,
        "title": project.title,
        "template": project.template,
        "created_at": project.created_at,
        "stage": project.stage.value,
        "version": project.version,
        "digest": project.digest,
        "current_gate": gate.to_dict(),
        "gates": [g.to_dict() for g in project.gates],
        "releases": [r.to_dict() for r in project.releases],
        "protocol_reworked_after_execution": project.protocol_reworked_after_execution,
    }


def ontrack_status(service: LifecycleService, findings: Optional[List[Finding]] = None) -> Dict[str, Any]:
    """Status of every project in the shape OnTrack ingests (`coresearcher.lifecycle/v1`)."""
    findings = findings if findings is not None else LifecycleWatcher(service).scan()
    projects = []
    for project in service.projects.values():
        gate = service.evaluate_gate(project.project_id)
        done = sum(e.status == CheckStatus.SATISFIED for e in gate.checks if e.check.required)
        total = sum(1 for e in gate.checks if e.check.required)
        latest = project.releases[-1] if project.releases else None
        projects.append(
            {
                "project_id": project.project_id,
                "title": project.title,
                "stage": project.stage.value,
                "stage_index": STAGES.index(project.stage),
                "stage_count": len(STAGES),
                "gate_decision": "PASSED" if project.passed(Stage.REPORT) else gate.decision.value,
                "checklist": {"required_satisfied": done, "required_total": total},
                "version": project.version,
                "digest": project.digest,
                "latest_release": (
                    {"release_id": latest.release_id, "kind": latest.kind.value, "at": latest.at} if latest else None
                ),
                "findings": [f.to_dict() for f in findings if f.project_id == project.project_id],
            }
        )
    return {
        "schema": EXPORT_SCHEMA,
        "product": "coresearcher",
        "stages": [s.value for s in STAGES],
        "projects": projects,
    }
