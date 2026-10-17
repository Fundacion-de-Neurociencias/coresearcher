"""
python/discovery/research_package.py - Portable, verifiable research packages (ADR-DISCOVERY-065).

A research package is one file that carries a lifecycle project (ADR-DISCOVERY-063) to another machine: its event
log, every artifact a check recorded, a human summary and RO-Crate metadata. The receiver can verify it and trace how
each result was reached, read-only; to change anything they fork it into their own lifecycle.

Layout (a gzip-compressed tar, written deterministically):

    manifest.json            format, schema version, source project, inventory with SHA-256, omissions
    events.jsonl             the project's lifecycle events, unchanged
    README.md                what the package contains, written from the log
    ro-crate-metadata.json   RO-Crate 1.1 description of the package and its files
    objects/<sha256>         each artifact, stored once under its own hash

Rules taken from AIPOCH Open-Science's `.science` packages and from this repository's own:

- Only those five kinds of path are ever read from an archive; links, devices and any other entry are refused, and
  nothing is extracted with `extractall`.
- Every artifact a check recorded is either inside, with the same hash, or listed under `omissions` with the reason
  (missing, changed since it was recorded). A gap is never silent.
- Checksums alone do not prove the history is consistent, so an import also replays the log into a fresh, read-only
  lifecycle and checks that it rebuilds the version and digest the manifest declares.
- Export refuses content that looks like a credential unless the caller explicitly accepts it.
- A package newer than this code (schema version or required feature) is refused rather than misread.

What verification does not do: it does not re-run the work or show that the results are right. It shows that the
package is complete, untampered, and internally consistent with its own history.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import re
import tarfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from python.discovery.research_lifecycle import (
    STAGES,
    LifecycleError,
    LifecycleService,
    Project,
)

FORMAT = "coresearcher-research-package"
SCHEMA_VERSION = 1
SUPPORTED_FEATURES: Tuple[str, ...] = ()
EXTENSION = ".crpkg"
NOTE = "Verifying a package checks integrity and replays its history; it does not reproduce the results."

MAX_MANIFEST_BYTES = 8 * 1024**2
MAX_FILE_BYTES = 4 * 1024**3
MAX_PACKAGE_BYTES = 16 * 1024**3
_ENTRY = re.compile(r"^(manifest\.json|events\.jsonl|README\.md|ro-crate-metadata\.json|objects/[0-9a-f]{64})$")
_RO_CRATE = "https://w3id.org/ro/crate/1.1"

# Patterns for content that must not leave the machine by accident. A match stops the export; the report shows
# where, never the value itself.
_SENSITIVE = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "secret assignment",
        re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passw(?:or)?d)\b\s*[:=]\s*[\"']?[^\s\"']{8,}"),
    ),
]


class PackageError(ValueError):
    """The package is malformed, incomplete, inconsistent, or newer than this code."""


class SensitiveContentError(PackageError):
    def __init__(self, findings: List[Dict[str, str]]):
        self.findings = findings
        where = ", ".join(f"{f['kind']} in {f['location']}" for f in findings[:5])
        super().__init__(f"Possible credentials found ({where}); export refused. Remove them or accept explicitly.")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(data: Any) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _artifact_refs(events: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[str]]:
    """(path, sha256) -> check ids, for every artifact any result in the log recorded."""
    refs: Dict[Tuple[str, str], List[str]] = {}
    for event in events:
        payload = event["payload"]
        if event["type"] == "result_submitted" and payload.get("artifact_path") and payload.get("sha256"):
            refs.setdefault((payload["artifact_path"], payload["sha256"]), []).append(payload["check_id"])
    return refs


def scan_sensitive(location: str, data: bytes) -> List[Dict[str, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    return [{"kind": kind, "location": location} for kind, pattern in _SENSITIVE if pattern.search(text)]


# --------------------------------------------------------------------------- export


def _readme(project: Project, service: LifecycleService, manifest: Dict[str, Any]) -> str:
    gate = service.evaluate_gate(project.project_id)
    lines = [
        f"# {project.title}",
        "",
        f"Research package of lifecycle project `{project.project_id}` (template `{project.template}`).",
        "",
        f"- Stage: {project.stage.value} ({STAGES.index(project.stage) + 1} of {len(STAGES)}); "
        f"current gate: {'PASSED' if project.passed(project.stage) else gate.decision.value}",
        f"- Version {project.version}, digest `{project.digest or 'none'}`",
        f"- Artifacts included: {sum(1 for e in manifest['inventory'] if e['kind'] == 'artifact')}; "
        f"omissions: {len(manifest['omissions'])}",
        "",
        NOTE,
        "",
    ]
    if manifest["omissions"]:
        lines += ["## Omissions", ""]
        lines += [
            f"- {o['kind']}: `{o['artifact_path']}` ({', '.join(o['check_ids'])}). {o['detail']}"
            for o in manifest["omissions"]
        ]
        lines.append("")
    if gate.decision.value != "PASS" and not project.passed(project.stage):
        waiting = [c.check.check_id for c in gate.checks if c.status.value != "SATISFIED" and c.check.required]
        lines += ["## Open checks", "", f"- {project.stage.value}: {', '.join(waiting)}", ""]
    if project.releases:
        lines += ["## Latest release", "", project.releases[-1].notes]
    else:
        lines += ["## Gates", ""]
        lines += [f"- v{g.version} {g.stage.value}" for g in project.active_gates()] or ["- none passed yet"]
        lines.append("")
    lines += [
        "## Verify",
        "",
        "```",
        "python scripts/research_package.py inspect <this file>",
        "```",
    ]
    return "\n".join(lines) + "\n"


def _ro_crate(project: Project, manifest: Dict[str, Any]) -> Dict[str, Any]:
    files = [e for e in manifest["inventory"] if e["path"] != "ro-crate-metadata.json"]
    graph: List[Dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": {"@id": _RO_CRATE},
            "about": {"@id": "./"},
        },
        {
            "@id": "./",
            "@type": "Dataset",
            "name": project.title,
            "identifier": project.project_id,
            "datePublished": manifest["created_at"],
            "description": f"CoResearcher research package, lifecycle stage {project.stage.value}, version "
            f"{project.version}. {NOTE}",
            "hasPart": [{"@id": e["path"]} for e in files],
        },
    ]
    for entry in files:
        node = {"@id": entry["path"], "@type": "File", "contentSize": entry["size"], "sha256": entry["sha256"]}
        if entry.get("artifact_path"):
            node["name"] = entry["artifact_path"]
            node["description"] = "Artifact recorded by " + ", ".join(entry["check_ids"])
        graph.append(node)
    return {"@context": "https://w3id.org/ro/crate/1.1/context", "@graph": graph}


def export_package(
    service: LifecycleService,
    project_id: str,
    root: Path,
    out_path: Optional[Path] = None,
    allow_sensitive: bool = False,
    created_at: Optional[str] = None,
) -> Tuple[bytes, Dict[str, Any]]:
    """Build the package of one project. Artifact paths in the log are read relative to `root`.

    Returns the package bytes and its manifest, and writes the file when `out_path` is given.
    """
    project = service.get(project_id)
    events = service.project_events(project_id)
    root = Path(root).resolve()
    events_bytes = "".join(json.dumps(e, sort_keys=True, ensure_ascii=False) + "\n" for e in events).encode("utf-8")

    objects: Dict[str, bytes] = {}
    inventory: List[Dict[str, Any]] = []
    omissions: List[Dict[str, Any]] = []
    sensitive = scan_sensitive("events.jsonl", events_bytes)
    for (rel, sha), check_ids in sorted(_artifact_refs(events).items()):
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            omissions.append(
                {"kind": "missing", "artifact_path": rel, "sha256": sha, "check_ids": check_ids, "detail": "Not found."}
            )
            continue
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            raise PackageError(f"{rel} exceeds the per-file limit.")
        if _sha256(data) != sha:
            omissions.append(
                {
                    "kind": "changed",
                    "artifact_path": rel,
                    "sha256": sha,
                    "check_ids": check_ids,
                    "detail": "The file no longer has the hash the check recorded; the recorded version is not "
                    "available.",
                }
            )
            continue
        sensitive += scan_sensitive(rel, data)
        objects[sha] = data
        inventory.append(
            {
                "path": f"objects/{sha}",
                "size": len(data),
                "sha256": sha,
                "kind": "artifact",
                "artifact_path": rel,
                "check_ids": check_ids,
            }
        )
    if sensitive and not allow_sensitive:
        raise SensitiveContentError(sensitive)

    manifest: Dict[str, Any] = {
        "format": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "required_features": [],
        "created_at": created_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": NOTE,
        "source": {
            "project_id": project.project_id,
            "title": project.title,
            "template": project.template,
            "stage": project.stage.value,
            "version": project.version,
            "digest": project.digest,
            "event_count": len(events),
            "releases": [r.release_id for r in project.releases],
        },
        "sensitive_content_accepted": bool(sensitive),
        "inventory": [],
        "omissions": omissions,
    }
    manifest["inventory"] = [
        {"path": "events.jsonl", "size": len(events_bytes), "sha256": _sha256(events_bytes), "kind": "events"},
        *inventory,
    ]
    readme = _readme(project, service, manifest).encode("utf-8")
    manifest["inventory"].append(
        {"path": "README.md", "size": len(readme), "sha256": _sha256(readme), "kind": "readme"}
    )
    crate = _json_bytes(_ro_crate(project, manifest))
    manifest["inventory"].append(
        {"path": "ro-crate-metadata.json", "size": len(crate), "sha256": _sha256(crate), "kind": "metadata"}
    )
    members = {
        "manifest.json": _json_bytes(manifest),
        "events.jsonl": events_bytes,
        "README.md": readme,
        "ro-crate-metadata.json": crate,
        **{f"objects/{sha}": data for sha, data in objects.items()},
    }

    buffer = io.BytesIO()
    # Deterministic: fixed order, times, owners and modes, and no time in the gzip header.
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name in sorted(members, key=lambda n: (n != "manifest.json", n)):
                info = tarfile.TarInfo(name)
                info.size, info.mtime, info.mode = len(members[name]), 0, 0o644
                tar.addfile(info, io.BytesIO(members[name]))
    data = buffer.getvalue()
    if len(data) > MAX_PACKAGE_BYTES:
        raise PackageError("The package exceeds the size limit.")
    if out_path:
        Path(out_path).write_bytes(data)
    return data, manifest


# --------------------------------------------------------------------------- import


@dataclass
class ImportedPackage:
    manifest: Dict[str, Any]
    manifest_sha256: str
    service: LifecycleService  # read-only
    project_id: str
    objects: Dict[str, bytes] = field(repr=False)
    readme: str = ""

    def summary(self) -> Dict[str, Any]:
        project = self.service.get(self.project_id)
        return {
            "valid": True,
            "manifest_sha256": self.manifest_sha256,
            "project_id": self.project_id,
            "title": project.title,
            "template": project.template,
            "stage": project.stage.value,
            "version": project.version,
            "digest": project.digest,
            "events": self.manifest["source"]["event_count"],
            "artifacts": sorted(e["artifact_path"] for e in self.manifest["inventory"] if e["kind"] == "artifact"),
            "omissions": self.manifest["omissions"],
            "releases": [
                {"release_id": r.release_id, "kind": r.kind.value, "criteria": r.criteria} for r in project.releases
            ],
            "read_only": self.service.read_only,
            "note": NOTE,
        }


def _read_members(data: bytes) -> Dict[str, bytes]:
    if len(data) > MAX_PACKAGE_BYTES:
        raise PackageError("The package exceeds the size limit.")
    members: Dict[str, bytes] = {}
    total = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            for info in tar:
                if not _ENTRY.match(info.name):
                    raise PackageError(f"Unexpected entry {info.name!r}; packages hold only known paths.")
                if not info.isreg():
                    raise PackageError(f"{info.name} is not a regular file.")
                if info.name in members:
                    raise PackageError(f"Duplicate entry {info.name}.")
                limit = MAX_MANIFEST_BYTES if info.name == "manifest.json" else MAX_FILE_BYTES
                total += info.size
                if info.size > limit or total > MAX_PACKAGE_BYTES:
                    raise PackageError(f"{info.name} exceeds the size limit.")
                handle = tar.extractfile(info)
                members[info.name] = handle.read() if handle else b""
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise PackageError(f"Not a readable package: {exc}") from exc
    return members


def import_package(data: bytes) -> ImportedPackage:
    """Verify a package and open its project read-only. Raises PackageError on any inconsistency."""
    members = _read_members(data)
    if "manifest.json" not in members:
        raise PackageError("The package has no manifest.")
    try:
        manifest = json.loads(members["manifest.json"])
    except ValueError as exc:
        raise PackageError("The manifest is not valid JSON.") from exc
    if not isinstance(manifest, dict) or manifest.get("format") != FORMAT:
        raise PackageError("Not a CoResearcher research package.")
    version = manifest.get("schema_version")
    unknown = [f for f in manifest.get("required_features", []) if f not in SUPPORTED_FEATURES]
    if not isinstance(version, int) or version > SCHEMA_VERSION or unknown:
        raise PackageError("The package needs a newer version of CoResearcher.")

    # 1. Integrity: every listed file is present with its size and hash, and nothing unlisted is present.
    listed = {"manifest.json"}
    for entry in manifest.get("inventory", []):
        path = entry.get("path", "")
        if path in listed or path not in members:
            raise PackageError(f"Inventory entry {path!r} is duplicated or missing.")
        listed.add(path)
        content = members[path]
        if len(content) != entry.get("size") or _sha256(content) != entry.get("sha256"):
            raise PackageError(f"{path} does not match its recorded size and hash.")
        if path.startswith("objects/") and (entry.get("kind") != "artifact" or path != f"objects/{entry['sha256']}"):
            raise PackageError(f"{path} is not stored under its own hash.")
    if set(members) - listed:
        raise PackageError(f"Unlisted entries: {sorted(set(members) - listed)}.")
    if "events.jsonl" not in members:
        raise PackageError("The package has no event log.")

    # 2. Consistency: the log replays into the project the manifest declares.
    try:
        events = [json.loads(line) for line in members["events.jsonl"].decode("utf-8").splitlines() if line.strip()]
        source = manifest["source"]
        if not events or {e.get("project_id") for e in events} != {source["project_id"]}:
            raise PackageError("The event log does not belong to one project, the declared one.")
        service = LifecycleService.from_events(events, read_only=True)
    except (LifecycleError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, PackageError):
            raise
        raise PackageError(f"The event log does not replay: {exc}") from exc
    project = service.get(source["project_id"])
    declared = (source.get("version"), source.get("digest"), source.get("stage"), source.get("event_count"))
    if declared != (project.version, project.digest, project.stage.value, len(events)):
        raise PackageError("The replayed history does not match the manifest (version, digest, stage or events).")

    # 3. Completeness: every artifact the log recorded is inside or explained as an omission.
    included = {(e.get("artifact_path"), e["sha256"]) for e in manifest["inventory"] if e.get("kind") == "artifact"}
    explained = {(o.get("artifact_path"), o.get("sha256")) for o in manifest.get("omissions", [])}
    silent = [ref for ref in _artifact_refs(events) if ref not in included and ref not in explained]
    if silent:
        raise PackageError(f"Artifacts recorded in the log are neither included nor explained: {silent}.")

    objects = {path[len("objects/") :]: content for path, content in members.items() if path.startswith("objects/")}
    return ImportedPackage(
        manifest=manifest,
        manifest_sha256=_sha256(members["manifest.json"]),
        service=service,
        project_id=source["project_id"],
        objects=objects,
        readme=members.get("README.md", b"").decode("utf-8", "replace"),
    )


def fork_package(
    package: ImportedPackage,
    target: LifecycleService,
    new_project_id: str,
    materialize_root: Optional[Path] = None,
) -> Project:
    """Copy the imported project into a writable lifecycle under a new id, remembering where it came from.

    With `materialize_root`, the included artifacts are also written there at their recorded paths, so the watcher
    can check them for drift. Existing files are never overwritten.
    """
    events = package.service.project_events(package.project_id)
    origin = {
        "project_id": package.project_id,
        "manifest_sha256": package.manifest_sha256,
        "version": package.manifest["source"]["version"],
        "digest": package.manifest["source"]["digest"],
        "forked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if materialize_root is not None:
        root = Path(materialize_root).resolve()
        for entry in package.manifest["inventory"]:
            if entry["kind"] != "artifact":
                continue
            target_path = (root / entry["artifact_path"]).resolve()
            if not target_path.is_relative_to(root):
                raise PackageError(f"{entry['artifact_path']} points outside the target folder.")
            if target_path.exists():
                if _sha256(target_path.read_bytes()) != entry["sha256"]:
                    raise PackageError(f"{entry['artifact_path']} already exists with different content.")
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(package.objects[entry["sha256"]])
    return target.adopt(events, new_project_id, origin)
