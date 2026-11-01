"""
python/cli/freeze.py - `coresearcher freeze`: fix acceptance criteria before any evaluation (ADR-DISCOVERY-085).

    coresearcher freeze hypothesis --hypothesis H.json [--rival R.json ...] --author NAME [--criteria C.json]
                                   [--out DIR]          freeze the discriminating states of H against its rivals
    coresearcher freeze document   --file PROTOCOL --author NAME     freeze a protocol or checklist by its bytes
    coresearcher freeze show       ID                                print a freeze record
    coresearcher freeze verify     ID [--hypothesis H.json --rival R.json | --file F] [--sha256 S]
                                   exit 0 VERIFIED, 13 CHANGED or UNKNOWN (BLOCKED)

`--lifecycle-project P [--lifecycle-check protocol.document]` anchors a freeze to a research lifecycle check
(ADR-063, log CORESEARCHER_LIFECYCLE_LOG): the freeze is refused unless the lifecycle recorded the same SHA-256.
`freeze hypothesis --out DIR` writes the frozen criteria as canonical JSON to DIR/<id>.json; the file's SHA-256 is the
freeze's, so it can be submitted as the `protocol.document` ARTIFACT result.

The store is a JSON file: --store, else CORESEARCHER_FREEZE_PATH, else .coresearcher/freezes.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from python.discovery import formal_status, freeze_service, research_lifecycle
from python.discovery.formal_hypothesis import FormalHypothesisError

DEFAULT_STORE = Path(".coresearcher") / "freezes.json"


def _store(args: argparse.Namespace) -> Path:
    if args.store:
        return Path(args.store)
    return freeze_service.default_store() or DEFAULT_STORE


def _read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _print(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, default=str))


def _lifecycle(args: argparse.Namespace):
    if not args.lifecycle_project:
        return None, None
    log = os.getenv("CORESEARCHER_LIFECYCLE_LOG")
    if not log:
        raise freeze_service.FreezeError("--lifecycle-project needs CORESEARCHER_LIFECYCLE_LOG (the lifecycle log).")
    service = research_lifecycle.LifecycleService(Path(log))
    anchor = {"project_id": args.lifecycle_project, "check_id": args.lifecycle_check}
    return anchor, freeze_service.lifecycle_lookup(service)


def add_parser(subparsers) -> None:
    p = subparsers.add_parser("freeze", help="Freeze acceptance criteria before any evaluation (ADR-085)")
    p.add_argument("--store", help="Freeze store JSON (default: CORESEARCHER_FREEZE_PATH or .coresearcher/)")
    sub = p.add_subparsers(dest="freeze_command")

    def authored(q) -> None:
        q.add_argument("--author", required=True, help="Who fixes these criteria")
        q.add_argument("--label", default="")
        q.add_argument("--lifecycle-project", help="Lifecycle project whose check must hold the same SHA-256")
        q.add_argument("--lifecycle-check", default="protocol.document")

    h = sub.add_parser("hypothesis", help="Freeze the discriminating states of a hypothesis and its rivals")
    h.add_argument("--hypothesis", required=True, help="Formal hypothesis JSON file")
    h.add_argument("--rival", action="append", help="Rival formal hypothesis JSON file (repeatable)")
    h.add_argument("--criteria", help="JSON with criteria the author states in addition (frozen verbatim)")
    h.add_argument("--max-examples", type=int, default=5)
    h.add_argument("--backend", default="auto", choices=("auto", "enumeration", "smt"))
    h.add_argument("--out", help="Directory for the canonical JSON of the frozen criteria (<id>.json)")
    authored(h)
    d = sub.add_parser("document", help="Freeze a protocol or checklist by the SHA-256 of its bytes")
    d.add_argument("--file", required=True)
    authored(d)
    s = sub.add_parser("show", help="Print a freeze record")
    s.add_argument("id")
    v = sub.add_parser("verify", help="Verify a freeze against a hypothesis and rivals, or a document")
    v.add_argument("id")
    v.add_argument("--hypothesis")
    v.add_argument("--rival", action="append")
    v.add_argument("--file")
    v.add_argument("--sha256", help="The SHA-256 the freeze must have")


def _freeze(args: argparse.Namespace, store: freeze_service.FreezeStore) -> dict:
    anchor, lookup = _lifecycle(args)
    if args.freeze_command == "document":
        path = Path(args.file)
        return store.freeze_document(path.read_bytes(), args.author, args.label, path.as_posix(), anchor, lookup)
    record = store.freeze_hypothesis(
        _read_json(args.hypothesis),
        [_read_json(r) for r in args.rival or []],
        args.author,
        args.label,
        _read_json(args.criteria) if args.criteria else None,
        args.max_examples,
        args.backend,
        anchor,
        lookup,
    )
    if args.out:
        out = Path(args.out) / f"{record['id']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(research_lifecycle.canonical_bytes(record["content"]))
        record["written"] = str(out)
    return record


def main(args: argparse.Namespace) -> int:
    command = getattr(args, "freeze_command", None)
    if not command:
        print("usage: coresearcher freeze {hypothesis,document,show,verify} ...", file=sys.stderr)
        return 2
    try:
        store = freeze_service.FreezeStore(_store(args))
        if command in ("hypothesis", "document"):
            _print(_freeze(args, store))
        elif command == "show":
            _print(store.get(args.id))
        else:
            document = Path(args.file).read_bytes() if args.file else None
            hypothesis = _read_json(args.hypothesis) if args.hypothesis else None
            rivals = [_read_json(r) for r in args.rival or []]
            check = store.verify_reference(args.id, args.sha256, hypothesis, rivals, document)
            _print(check)
            return 0 if check["status"] == freeze_service.VERIFIED else formal_status.EXIT_FREEZE_CHANGED
        return 0
    except (freeze_service.FreezeError, OSError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return formal_status.EXIT_REFUSAL
    except (FormalHypothesisError, ValueError, ImportError) as exc:
        # A solver non-verdict while computing the criteria (UNDECIDED, a threshold, no z3): nothing was frozen.
        try:
            status = formal_status.classify(exc)
        except Exception:
            print(f"error: {exc}", file=sys.stderr)
            return formal_status.EXIT_REFUSAL
        print(f"{status.value}: {type(exc).__name__}: {exc}; nothing was frozen", file=sys.stderr)
        return formal_status.exit_code(status, exc)
