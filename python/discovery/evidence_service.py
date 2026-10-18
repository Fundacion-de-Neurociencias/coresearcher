"""
python/discovery/evidence_service.py - EvidenceRequest -> EvidenceGraph, the contract EdiTXT consumes (ADR-DISCOVERY-067).

EdiTXT sends an EvidenceRequest for a claim in a manuscript; CoResearcher answers with an EvidenceGraph built only
from what it actually holds:

| Target type | Built from |
| --- | --- |
| LIFECYCLE_PROJECT | a lifecycle project (ADR-063): gates, check results, artifacts with live hash status, releases, findings |
| RESEARCH_PACKAGE | a published `.crpkg` in docs/reference/packages (ADR-065), verified, with its published digest checked |
| REGISTERED_CLAIM | a row of docs/reference/CLAIMS_REGISTER.md, with its script and status |
| FORMAL_HYPOTHESIS | a formal hypothesis object (ADR-059/060): content verdict, consequences, rivals and discriminating states |
| FORMAL_CASE | a formal case module (pTau217 two-cutoff rule, Alzheimer rivals, ED polarity) |
| QUESTION | free text: nothing is invented; the graph says no evidence is linked and how to link some |

Rules, from docs/architecture/BOUNDARY_WITH_EDITXT.md:
- CoResearcher reports evidence and its provenance. It does not grade manuscripts or say whether prose is good.
- Verifier results (z3, Lean, Comparator, the formal evaluator) are reported as what the tool decided, with the tool
  named. They are evidence, not CoResearcher's opinion.
- Every gap is reported, never hidden.

The graph is content-addressed: `graph_id` and `provenance.digest` are the SHA-256 of the canonical target, nodes,
edges and gaps. The same evidence gives the same id; changed evidence gives a new id. EdiTXT stores the digest in its
EvidenceTraceArtifact, and a changed digest marks the manuscript's evidence as stale.
"""

from __future__ import annotations

import functools
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

SCHEMA = "coresearcher.evidence/v1"
ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES_DIR = ROOT / "docs" / "reference" / "packages"
CLAIMS_REGISTER = ROOT / "docs" / "reference" / "CLAIMS_REGISTER.md"
TARGET_TYPES = (
    "LIFECYCLE_PROJECT",
    "RESEARCH_PACKAGE",
    "REGISTERED_CLAIM",
    "FORMAL_HYPOTHESIS",
    "FORMAL_CASE",
    "QUESTION",
)
FORMAL_CASES = ("ptau217_two_cutoff", "alzheimer_rivals", "ed_polarity")
MAX_RIVALS = 5
MAX_CONSEQUENCES = 10
# Where a premise came from. Provenance only: it never changes a verdict (ADR-DISCOVERY-066, ADR-DISCOVERY-067).
PREMISE_ORIGINS = ("SUPPLIED", "LITERATURE", "PERSON", "SYSTEM", "UNDECLARED")


class EvidenceRequestError(ValueError):
    """The request is malformed or names a target that does not exist."""


class _Graph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.gaps: List[Dict[str, Any]] = []
        self.sources: List[str] = []

    def node(self, node_id: str, kind: str, label: str, /, **attributes: Any) -> str:
        self.nodes.setdefault(node_id, {"id": node_id, "kind": kind, "label": label, "attributes": attributes})
        return node_id

    def edge(self, source: str, target: str, relation: str, justification: str = "") -> None:
        self.edges.append({"source": source, "target": target, "relation": relation, "justification": justification})

    def gap(self, kind: str, description: str, node: Optional[str] = None) -> None:
        self.gaps.append({"kind": kind, "description": description, "node": node})


def _canonical(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- request validation


def normalize_request(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and complete an EvidenceRequest. Raises EvidenceRequestError with a precise message."""
    if not isinstance(raw, dict):
        raise EvidenceRequestError("The request must be a JSON object.")
    unknown = set(raw) - {"request_id", "target", "scope", "claim_ids", "requested_by"}
    if unknown:
        raise EvidenceRequestError(f"Unknown request fields: {sorted(unknown)}.")
    target = raw.get("target")
    if not isinstance(target, dict) or target.get("type") not in TARGET_TYPES:
        raise EvidenceRequestError(f"target.type must be one of {list(TARGET_TYPES)}.")
    kind = target["type"]
    if kind == "FORMAL_HYPOTHESIS":
        if not isinstance(target.get("hypothesis"), dict):
            raise EvidenceRequestError(
                "A FORMAL_HYPOTHESIS target needs target.hypothesis (a formal hypothesis object)."
            )
    elif kind == "QUESTION":
        if not str(target.get("text", "")).strip():
            raise EvidenceRequestError("A QUESTION target needs target.text.")
    elif not isinstance(target.get("id"), str) or not target["id"].strip() or len(target["id"]) > 200:
        raise EvidenceRequestError(f"A {kind} target needs target.id (a string of at most 200 characters).")
    if kind == "QUESTION" and len(str(target["text"])) > 1000:
        raise EvidenceRequestError("target.text is limited to 1000 characters.")
    request_id = raw.get("request_id")
    if request_id is not None and not re.match(r"^ER-[A-Za-z0-9-]{1,64}$", str(request_id)):
        raise EvidenceRequestError("request_id must look like ER-<letters, digits or dashes>.")
    scope = raw.get("scope") or {}
    if not isinstance(scope, dict) or set(scope) - {"consequences", "rivals"}:
        raise EvidenceRequestError("scope accepts only consequences and rivals.")
    consequences = scope.get("consequences") or []
    rivals = scope.get("rivals") or []
    if len(consequences) > MAX_CONSEQUENCES or len(rivals) > MAX_RIVALS:
        raise EvidenceRequestError(f"At most {MAX_CONSEQUENCES} consequences and {MAX_RIVALS} rivals per request.")
    if not isinstance(consequences, list) or not isinstance(rivals, list):
        raise EvidenceRequestError("scope.consequences and scope.rivals must be lists.")
    if (consequences or rivals) and kind != "FORMAL_HYPOTHESIS":
        raise EvidenceRequestError("scope.consequences and scope.rivals apply only to FORMAL_HYPOTHESIS targets.")
    claim_ids = raw.get("claim_ids") or []
    if not isinstance(claim_ids, list) or not all(isinstance(c, str) and len(c) <= 200 for c in claim_ids):
        raise EvidenceRequestError("claim_ids must be a list of strings of at most 200 characters.")
    return {
        "request_id": request_id,
        "target": target,
        "scope": {"consequences": list(consequences), "rivals": list(rivals)},
        "claim_ids": list(claim_ids),
        "requested_by": str(raw.get("requested_by", ""))[:200],
    }


# --------------------------------------------------------------------------- resolvers


def _lifecycle(g: _Graph, service, project_id: str, root: Optional[Path], package_objects=None) -> str:
    """Graph of a lifecycle project. Artifact status is checked against `root` (live files) or `package_objects`."""
    from python.discovery.research_lifecycle import STAGES, CheckKind, LifecycleWatcher

    try:
        project = service.get(project_id)
    except KeyError as exc:
        raise EvidenceRequestError(f"No lifecycle project {project_id!r}.") from exc
    pid = g.node(
        f"project:{project_id}",
        "lifecycle_project",
        project.title,
        project_id=project_id,
        template=project.template,
        stage=project.stage.value,
        version=project.version,
        digest=project.digest,
        forked_from=project.forked_from,
    )
    kinds = {c.check_id: c for stage in STAGES for c in project.checks(stage)}
    relation = {
        CheckKind.VERIFIER: ("verification", "verified_by"),
        CheckKind.HUMAN: ("review", "reviewed_by"),
        CheckKind.ARTIFACT: ("artifact", "recorded_in"),
        CheckKind.RUBRIC: ("measure", "measured_by"),
    }
    for gate in project.active_gates():
        gid = g.node(
            f"gate:{project_id}:{gate.stage.value}",
            "gate",
            f"{gate.stage.value} gate passed (v{gate.version})",
            stage=gate.stage.value,
            version=gate.version,
            digest=gate.digest,
            passed_at=gate.at,
        )
        g.edge(pid, gid, "derived_from", "The project's version chain includes this gate.")
        for check_id, result in sorted(gate.evidence.items()):
            template = kinds.get(check_id)
            kind, rel = relation.get(template.kind if template else None, ("measure", "measured_by"))
            attrs = {k: v for k, v in result.items() if v not in (None, "", {}, [])}
            if kind == "artifact" and result.get("artifact_path"):
                attrs["status"] = _artifact_status(result, root, package_objects)
                if attrs["status"] != "intact":
                    g.gap(
                        f"artifact_{attrs['status']}",
                        f"{result['artifact_path']} ({check_id}) is {attrs['status']} compared with the hash the gate "
                        "accepted.",
                        f"check:{project_id}:{check_id}",
                    )
            nid = g.node(
                f"check:{project_id}:{check_id}", kind, template.description if template else check_id, **attrs
            )
            g.edge(gid, nid, rel, f"Accepted at the {gate.stage.value} gate as {check_id}.")
            if not result.get("ok", True):
                g.gap("failed_check", f"{check_id} was reported as failed: {result.get('note', '')}".strip(), nid)
    if not project.passed(project.stage):
        evaluation = service.evaluate_gate(project_id)
        for item in evaluation.checks:
            if item.check.required and item.status.value != "SATISFIED":
                g.gap(
                    "open_check",
                    f"{project.stage.value}: {item.check.check_id} is {item.status.value.lower()} ({item.reason}).",
                    pid,
                )
    for release in project.releases:
        rid = g.node(
            f"release:{release.release_id}",
            "release",
            f"Release {release.release_id} ({release.kind.value})",
            kind=release.kind.value,
            version=release.version,
            digest=release.digest,
            released_at=release.at,
        )
        g.edge(pid, rid, "derived_from", "Released version of the project.")
        for criterion, outcome in sorted(release.criteria.items()):
            cid = g.node(f"criterion:{release.release_id}:{criterion}", "criterion", criterion, outcome=outcome)
            g.edge(rid, cid, "measured_by", "Pre-registered criterion scored in the analysis stage.")
            g.edge(cid, pid, "supports" if outcome == "MET" else "contradicts", f"Criterion {outcome}.")
            if outcome != "MET":
                g.gap("criterion_not_met", f"Pre-registered criterion {criterion} was not met.", cid)
    if not project.releases:
        g.gap("not_released", "The project has no release yet; its evidence is still in progress.", pid)
    if project.forked_from:
        fid = g.node(
            f"origin:{project.forked_from.get('manifest_sha256', '')[:16]}",
            "provenance",
            f"Forked from {project.forked_from.get('project_id')}",
            **project.forked_from,
        )
        g.edge(pid, fid, "forked_from", "The project's history was copied from an imported package.")
    if root is not None and package_objects is None:
        for finding in LifecycleWatcher(service, root=root).scan():
            if finding.project_id == project_id and finding.kind.value in ("STALLED", "UNRELEASED"):
                g.gap(finding.kind.value.lower(), finding.detail, pid)
    return pid


def _artifact_status(result: Dict[str, Any], root: Optional[Path], package_objects) -> str:
    if package_objects is not None:
        return "intact" if result.get("sha256") in package_objects else "omitted"
    if root is None:
        return "unchecked"
    path = (root / result["artifact_path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return "missing"
    return "intact" if _sha256_file(path) == result.get("sha256") else "changed"


def _published_digests() -> Dict[str, Tuple[str, str]]:
    """file name -> (lifecycle digest, manifest sha256) from the package index README."""
    index = PACKAGES_DIR / "README.md"
    if not index.exists():
        return {}
    out = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| \[([^\]]+\.crpkg)\]\([^)]*\) \|.*\| `([0-9a-f]{64})` \| `([0-9a-f]{64})` \|$", line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3))
    return out


def _package(g: _Graph, name: str) -> str:
    from python.discovery.research_package import PackageError, import_package

    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,120}\.crpkg$", name):
        raise EvidenceRequestError("A RESEARCH_PACKAGE id is a .crpkg file name from docs/reference/packages.")
    path = PACKAGES_DIR / name
    if not path.is_file():
        raise EvidenceRequestError(f"No published package {name!r}.")
    kid = f"package:{name}"
    try:
        package = import_package(path.read_bytes())
    except PackageError as exc:
        g.node(kid, "research_package", name, valid=False, error=str(exc))
        g.gap("package_invalid", f"The package does not verify: {exc}", kid)
        return kid
    published = _published_digests().get(name)
    digest = package.manifest["source"]["digest"]
    match = bool(published) and published == (digest, package.manifest_sha256)
    g.node(
        kid,
        "research_package",
        name,
        valid=True,
        manifest_sha256=package.manifest_sha256,
        lifecycle_digest=digest,
        published_digest_matches=match,
        note=package.manifest.get("note"),
    )
    if not published:
        g.gap("unpublished_digest", "The package's digest is not listed in docs/reference/packages/README.md.", kid)
    elif not match:
        g.gap("digest_mismatch", "The package's digests differ from the ones published in the package index.", kid)
    for omission in package.manifest.get("omissions", []):
        g.gap("package_omission", f"{omission['kind']}: {omission['artifact_path']}. {omission['detail']}", kid)
    pid = _lifecycle(g, package.service, package.project_id, None, package_objects=package.objects)
    g.edge(kid, pid, "derived_from", "The package carries this project's history, verified on import.")
    return kid


def _register_rows() -> Dict[str, Dict[str, str]]:
    rows = {}
    if not CLAIMS_REGISTER.exists():
        return rows
    for line in CLAIMS_REGISTER.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0].isdigit():
            rows[cells[0]] = {
                "row": cells[0],
                "claim": cells[1],
                "script": cells[2],
                "data_origin": cells[3],
                "status": cells[4],
                "notes": " | ".join(cells[5:]),
            }
    return rows


def _registered_claim(g: _Graph, row: str) -> str:
    rows = _register_rows()
    key = str(row).strip().lstrip("#")
    if key not in rows:
        raise EvidenceRequestError(f"No row {row!r} in the claims register.")
    r = rows[key]
    status = re.sub(r"[*`]", "", r["status"]).strip()
    rid = g.node(
        f"register:{key}",
        "registered_claim",
        re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", r["claim"]),
        row=key,
        status=status,
        data_origin=r["data_origin"],
        notes=r["notes"],
    )
    for name, link in re.findall(r"\[`?([^\]`]+)`?\]\(([^)]+)\)", r["script"]):
        sid = g.node(f"script:{name}", "script", name, path=link.replace("../../", ""))
        g.edge(rid, sid, "verified_by", "The register names this script or test as the support of the row.")
    if not status.upper().startswith("PASS"):
        g.gap("not_validated", f"Claims register row {key} has status {status!r}.", rid)
    return rid


def _premise_provenance(spec: Dict[str, Any], assumptions: List[str]) -> Dict[str, Dict[str, Any]]:
    """Reads the optional `premise_provenance` of a hypothesis object: for each assumption, its origin, whether data
    tested it, and a source. Undeclared assumptions are reported as UNDECLARED and untested, never guessed.
    """
    raw = spec.get("premise_provenance") or {}
    if not isinstance(raw, dict):
        raise EvidenceRequestError(
            "premise_provenance must map each assumption to {origin, tested_against_data, source}."
        )
    unknown = set(raw) - set(assumptions)
    if unknown:
        raise EvidenceRequestError(
            f"premise_provenance names assumptions the hypothesis does not have: {sorted(unknown)}."
        )
    out = {}
    for assumption in assumptions:
        entry = raw.get(assumption) or {}
        if not isinstance(entry, dict):
            raise EvidenceRequestError(f"premise_provenance for {assumption!r} must be an object.")
        origin = entry.get("origin", "UNDECLARED")
        if origin not in PREMISE_ORIGINS:
            raise EvidenceRequestError(f"Premise origin must be one of {list(PREMISE_ORIGINS)}.")
        tested = entry.get("tested_against_data", False)
        if not isinstance(tested, bool):
            raise EvidenceRequestError("tested_against_data must be true or false.")
        out[assumption] = {
            "origin": origin,
            "tested_against_data": tested,
            "source": str(entry.get("source", ""))[:300],
        }
    return out


def _premise_nodes(g: _Graph, owner: str, owner_id: str, premises: Dict[str, Dict[str, Any]], extra=None) -> None:
    """One assumption node per premise, linked by `requires`, and a gap for each premise no data has tested."""
    for name, provenance in premises.items():
        attrs = {**(extra or {}).get(name, {}), **provenance}
        aid = g.node(f"assumption:{owner_id}:{name}", "assumption", name, **attrs)
        why = f"Premise of {owner_id}, origin {provenance['origin'].lower()}"
        if "necessity" in attrs:
            why += f"; dropping it breaks the proof: {attrs['necessity']}"
        g.edge(owner, aid, "requires", why + ".")
        if not provenance["tested_against_data"]:
            g.gap(
                "premise_untested",
                f"The premise {name!r} ({provenance['origin'].lower()}) has not been tested against data. "
                "Its origin does not affect validity; whether it holds does.",
                aid,
            )


def _origin_summary(premises: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for provenance in premises.values():
        summary[provenance["origin"]] = summary.get(provenance["origin"], 0) + 1
    return dict(sorted(summary.items()))


def _hypothesis_graph(g: _Graph, spec: Dict[str, Any], consequences: List[str], rivals: List[Dict[str, Any]]) -> str:
    from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, hypothesis_from_dict
    from python.discovery.formal_lean import consequence_theorem

    try:
        hypothesis = hypothesis_from_dict(spec)
        report = HypothesisEvaluator.evaluate(hypothesis, max_examples=3)
    except FormalHypothesisError as exc:
        raise EvidenceRequestError(f"The formal hypothesis is invalid: {exc}") from exc
    premises = _premise_provenance(spec, [p.expression for p in hypothesis._assumptions])
    hid = g.node(
        f"hypothesis:{hypothesis.hypothesis_id}",
        "formal_hypothesis",
        hypothesis.hypothesis_id,
        variables=hypothesis.variable_names,
        claims=[p.expression for p in hypothesis._claims],
        premise_origins=_origin_summary(premises),
    )
    _premise_nodes(g, hid, hypothesis.hypothesis_id, premises)
    verdict = report.content_verdict.value
    vid = g.node(
        f"verdict:{hypothesis.hypothesis_id}",
        "verification",
        f"Content verdict: {verdict}",
        tool=f"formal evaluator ({report.backend})",
        content_verdict=verdict,
        excluded_fraction_of_applicable=report.excluded_fraction_of_applicable,
        falsifier_examples=report.falsifier_examples,
    )
    g.edge(hid, vid, "verified_by", "Exact evaluation over the declared variables and domains.")
    explain = {
        "VACUOUS": "No state satisfies the scope and assumptions: the hypothesis speaks about nothing.",
        "SELF_CONTRADICTORY": "Every applicable state is forbidden: the claims contradict the assumptions.",
        "UNFALSIFIABLE": "No state is forbidden: no observation could refute the claims as stated.",
    }
    if verdict in explain:
        g.gap(verdict.lower(), explain[verdict], vid)
    for i, consequence in enumerate(consequences):
        try:
            result = HypothesisEvaluator.entails(hypothesis, consequence, max_examples=2)
        except FormalHypothesisError as exc:
            raise EvidenceRequestError(f"Consequence {consequence!r} is invalid: {exc}") from exc
        cid = g.node(
            f"consequence:{hypothesis.hypothesis_id}:{i}",
            "consequence",
            consequence,
            entailed=result.entailed,
            tool=f"formal evaluator ({result.backend})",
            counterexamples=result.counterexamples,
            lean_status="NOT_KERNEL_CHECKED",
        )
        g.edge(cid, hid, "supports" if result.entailed else "contradicts", "Entailment decided by the evaluator.")
        if not result.entailed:
            g.gap("not_entailed", f"{consequence!r} does not follow from the hypothesis.", cid)
        else:
            try:
                consequence_theorem(hypothesis, consequence)
                lean = "its Lean theorem can be exported (POST /api/hypotheses/entails with include_lean), but"
            except FormalHypothesisError as exc:
                lean = f"it cannot be exported to Lean ({exc}) and"
            g.gap(
                "not_kernel_checked",
                f"{consequence!r} is entailed according to {result.backend}; {lean} no proof kernel has checked it.",
                cid,
            )
    for spec_b in rivals:
        try:
            rival = hypothesis_from_dict(spec_b)
            comparison = HypothesisEvaluator.compare(hypothesis, rival, max_examples=3)
        except FormalHypothesisError as exc:
            raise EvidenceRequestError(f"A rival is invalid or not comparable: {exc}") from exc
        rid = g.node(f"rival:{rival.hypothesis_id}", "rival", rival.hypothesis_id, relation=comparison.relation.value)
        g.edge(
            hid,
            rid,
            "discriminates",
            f"Relation {comparison.relation.value}; states that separate them: "
            f"{json.dumps(comparison.discriminating_examples, default=str)[:400]}",
        )
        if comparison.relation.value == "INCOMPARABLE":
            g.gap("unresolved_rival", f"{rival.hypothesis_id} is a live rival; an observation can separate them.", rid)
    return hid


@functools.lru_cache(maxsize=None)
def _case_report(case: str) -> str:
    """Formal case reports are deterministic and some are slow (ED polarity ~20 s), so they are computed once."""
    if case == "ptau217_two_cutoff":
        from python.discovery import ptau217_cutoff_case as m

        hypothesis = m.ptau217_hypothesis()
        report = {
            "status": m.STATUS,
            "source": m.SOURCE,
            "verdict": m.verdict(hypothesis),
            "necessity": m.necessity_table(),
            "claims": [p.expression for p in hypothesis._claims],
        }
    elif case == "alzheimer_rivals":
        from python.discovery import alzheimer_formal_scenario as m

        report = m.scenario_report()
    else:
        from python.discovery import ed_polarity_case as m

        report = m.case_report()
    return json.dumps(report, default=str)


def _formal_case(g: _Graph, case: str) -> str:
    if case not in FORMAL_CASES:
        raise EvidenceRequestError(f"Unknown formal case {case!r}; use one of {list(FORMAL_CASES)}.")
    report = json.loads(_case_report(case))
    if case == "ptau217_two_cutoff":
        kid = g.node(
            f"case:{case}",
            "formal_case",
            "pTau217 two-cutoff triage rule",
            status=report["status"],
            source=report["source"],
            claims=report["claims"],
        )
        v = report["verdict"]
        vid = g.node(
            f"verdict:{case}",
            "verification",
            f"{v['status']} under the stated assumptions",
            tool="formal evaluator (SMT)",
            **v,
        )
        g.edge(kid, vid, "verified_by", "The claims follow from the assumptions when status is PROVED.")
        if v.get("status") == "PROVED" and v.get("content_verdict") == "UNFALSIFIABLE":
            g.gap(
                "content_in_assumptions",
                "The claims follow from the assumptions alone, so the rule forbids nothing beyond them: its "
                "empirical content lies in the assumptions, which must be checked against data.",
                vid,
            )
        premises = {
            name: {"origin": "LITERATURE", "tested_against_data": False, "source": report["source"]}
            for name in sorted(report["necessity"])
        }
        g.nodes[kid]["attributes"]["premise_origins"] = _origin_summary(premises)
        _premise_nodes(g, kid, case, premises, {n: {"necessity": v} for n, v in report["necessity"].items()})
        g.gap(
            "model_scope",
            "A formal case shows the claim holds under its stated assumptions; whether patients "
            "meet them is an empirical question outside this check.",
            kid,
        )
        return kid
    if case == "alzheimer_rivals":
        kid = g.node(
            f"case:{case}",
            "formal_case",
            "Formal Alzheimer rival hypotheses",
            status=report["status"],
            omega_size=report["omega_size"],
        )
        for rival in report["rivals"]:
            hid_ = rival["hypothesis_id"]
            evaluation = report["evaluations"].get(hid_, {})
            nid = g.node(
                f"rival:{hid_}",
                "rival",
                hid_,
                statement=rival["statement"],
                content_verdict=evaluation.get("content_verdict"),
                not_formalized=rival["not_formalized"],
            )
            g.edge(kid, nid, "derived_from", "Rival formalised in the scenario.")
            if evaluation.get("content_verdict") in ("VACUOUS", "UNFALSIFIABLE", "SELF_CONTRADICTORY"):
                g.gap(evaluation["content_verdict"].lower(), f"{hid_} is {evaluation['content_verdict']}.", nid)
        for c in report["comparisons"]:
            a, b = c["hypothesis_a"], c["hypothesis_b"]
            g.edge(
                f"rival:{a}",
                f"rival:{b}",
                "discriminates",
                f"Relation {c['relation']}; {c.get('forbidden_only_by_a')} states forbidden only by {a}, "
                f"{c.get('forbidden_only_by_b')} only by {b}.",
            )
        g.gap(
            "draft",
            "The formal rivals are the maintainers' reading of one-sentence statements, pending review by "
            "neuroscientists (claims register, row 25).",
            kid,
        )
        return kid
    kid = g.node(
        f"case:{case}",
        "formal_case",
        "Error Diffusion polarity claim",
        status=report.get("status"),
        source=report.get("source"),
    )
    for name, item in sorted(report.get("main_claim", {}).items()):
        vid = g.node(
            f"verdict:{case}:{name}",
            "verification",
            f"{name}: {item.get('status')}",
            tool="formal evaluator (SMT)",
            status=item.get("status"),
        )
        g.edge(kid, vid, "verified_by", "Decided for this network size.")
    necessity = {n: v for n, v in sorted((report.get("assumption_necessity") or {}).items()) if isinstance(v, str)}
    premises = {
        name: {"origin": "LITERATURE", "tested_against_data": False, "source": str(report.get("source", ""))}
        for name in necessity
    }
    g.nodes[kid]["attributes"]["premise_origins"] = _origin_summary(premises)
    _premise_nodes(g, kid, case, premises, {n: {"necessity": v} for n, v in necessity.items()})
    return kid


# --------------------------------------------------------------------------- catalogues


def list_packages() -> List[Dict[str, Any]]:
    """Published research packages with the digests listed in the package index."""
    published = _published_digests()
    return [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
            "lifecycle_digest": published.get(path.name, (None, None))[0],
            "manifest_sha256": published.get(path.name, (None, None))[1],
            "listed_in_index": path.name in published,
        }
        for path in sorted(PACKAGES_DIR.glob("*.crpkg"))
    ]


def list_targets(lifecycle_service=None) -> Dict[str, Any]:
    """Everything an EvidenceRequest can point at, so a client can offer it instead of guessing ids."""
    projects = []
    if lifecycle_service is not None:
        projects = [
            {"id": p.project_id, "title": p.title, "template": p.template, "stage": p.stage.value}
            for p in lifecycle_service.projects.values()
        ]
    return {
        "schema": SCHEMA,
        "LIFECYCLE_PROJECT": projects,
        "RESEARCH_PACKAGE": [{"id": p["name"], "listed_in_index": p["listed_in_index"]} for p in list_packages()],
        "REGISTERED_CLAIM": [
            {
                "id": r["row"],
                "claim": re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", r["claim"]),
                "status": re.sub(r"[*`]", "", r["status"]).strip(),
            }
            for r in _register_rows().values()
        ],
        "FORMAL_CASE": [
            {"id": "ptau217_two_cutoff", "title": "Plasma pTau217 two-cutoff triage rule"},
            {"id": "alzheimer_rivals", "title": "Formal Alzheimer rival hypotheses"},
            {"id": "ed_polarity", "title": "Error Diffusion polarity claim (first request takes about 20 s)"},
        ],
        "FORMAL_HYPOTHESIS": "Send the hypothesis object in target.hypothesis (POST /api/hypotheses/formalize drafts one).",
        "QUESTION": "Free text in target.text; the graph reports that no evidence is linked.",
    }


# --------------------------------------------------------------------------- entry point


def resolve(
    raw: Dict[str, Any],
    lifecycle_service=None,
    root: Path = ROOT,
    clock: Callable[[], str] = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
) -> Dict[str, Any]:
    """Answer an EvidenceRequest with an EvidenceGraph (schema `coresearcher.evidence/v1`)."""
    request = normalize_request(raw)
    target = request["target"]
    g = _Graph()
    kind = target["type"]
    if kind == "LIFECYCLE_PROJECT":
        if lifecycle_service is None:
            raise EvidenceRequestError("No lifecycle service is available on this server.")
        focus = _lifecycle(g, lifecycle_service, target["id"], root)
        g.sources.append("python/discovery/research_lifecycle.py")
    elif kind == "RESEARCH_PACKAGE":
        focus = _package(g, target["id"])
        g.sources.append("python/discovery/research_package.py")
    elif kind == "REGISTERED_CLAIM":
        focus = _registered_claim(g, target["id"])
        g.sources.append("docs/reference/CLAIMS_REGISTER.md")
    elif kind == "FORMAL_HYPOTHESIS":
        focus = _hypothesis_graph(g, target["hypothesis"], request["scope"]["consequences"], request["scope"]["rivals"])
        g.sources.append("python/discovery/formal_hypothesis.py")
    elif kind == "FORMAL_CASE":
        focus = _formal_case(g, target["id"])
        g.sources.append(f"formal case {target['id']}")
    else:
        focus = g.node("question", "question", str(target["text"])[:1000])
        g.gap(
            "no_linked_evidence",
            "CoResearcher holds no evidence linked to free text. Link the claim to a lifecycle project, a registered "
            "claim, a research package or a formal hypothesis (POST /api/hypotheses/formalize drafts one).",
            focus,
        )
    for claim_id in request["claim_ids"]:
        cid = g.node(f"manuscript_claim:{claim_id}", "claim", claim_id)
        g.edge(cid, focus, "derived_from", "The requesting system linked this claim to the target.")
    body = {
        "target": {k: v for k, v in target.items() if k != "hypothesis"}
        | ({"hypothesis_id": target["hypothesis"].get("hypothesis_id")} if kind == "FORMAL_HYPOTHESIS" else {}),
        "nodes": sorted(g.nodes.values(), key=lambda n: n["id"]),
        "edges": sorted(g.edges, key=lambda e: (e["source"], e["target"], e["relation"])),
        "gaps": sorted(g.gaps, key=lambda x: (x["kind"], x["node"] or "", x["description"])),
    }
    digest = hashlib.sha256(_canonical(body)).hexdigest()
    graph_id = f"EG-{digest[:16]}"
    return {
        "schema": SCHEMA,
        "graph_id": graph_id,
        "request_id": request["request_id"] or f"ER-{digest[16:28]}",
        **body,
        "focus": focus,
        "provenance": {
            "generated_by": "coresearcher",
            "generated_at": clock(),
            "digest": digest,
            "sources": g.sources,
            "requested_by": request["requested_by"],
            "boundary": "Evidence and its provenance only; no grading of manuscripts (BOUNDARY_WITH_EDITXT.md).",
        },
        "links": {"self": f"/api/evidence/graphs/{graph_id}"},
    }
