"""
python/cli/biomedical.py - `coresearcher biomedical`: biomedical checks of formal hypotheses (ADR-DISCOVERY-086).

    coresearcher biomedical check --request REQUEST.json [--out RESULT.json]
    coresearcher biomedical mechanism --request MECHANISM.json [--out RESULT.json]
    coresearcher biomedical units UNIT_A UNIT_B
    coresearcher biomedical vocabulary

`check` reads {hypothesis, consequences, biomedical: {units, conventions, probes}, backend} and decides the units
obligation and the null-biomarker, untreated-arm and population probes. `mechanism` reads {mechanism: {nodes, links or
prose, prediction}, backend}, compiles the mechanistic chain and decides each link, each sign and the compatibility of
the links with the prediction. The whole chain with these checks is `coresearcher chain run` with a `biomedical` block
or a `mechanism`.

Exit codes: 0 every obligation discharged (units: the same unit); 1 an obligation REFUTED (units: a different unit
or dimension); 10 something OPEN (units: unreadable); 11 prose outside the controlled language; 9 refused input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from python.discovery import biomedical_conventions, biomedical_domain, biomedical_units, formal_status
from python.discovery import mechanistic_chain
from python.discovery.formal_hypothesis import FormalHypothesisError
from python.discovery.formal_status import FormalStatus


def add_parser(subparsers) -> None:
    p = subparsers.add_parser("biomedical", help="Biomedical checks: units, probes, mechanisms (ADR-086)")
    sub = p.add_subparsers(dest="biomedical_command")
    for name, what in (("check", "units and domain probes of a formal hypothesis"),
                       ("mechanism", "compile a mechanistic chain and decide its links")):
        c = sub.add_parser(name, help=what)
        c.add_argument("--request", required=True, help="Request JSON")
        c.add_argument("--out", help="Write the full result here")
    u = sub.add_parser("units", help="Compare two unit strings by unit algebra")
    u.add_argument("a")
    u.add_argument("b")
    sub.add_parser("vocabulary", help="The convention vocabulary of the cited-results registry")


def _exit(statuses) -> int:
    if "REFUTED" in statuses:
        return 1
    if "OPEN" in statuses:
        return 10
    return 0


def _write(args, result) -> None:
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def main(args: argparse.Namespace) -> int:
    command = getattr(args, "biomedical_command", None)
    if command == "vocabulary":
        print(json.dumps(biomedical_conventions.vocabulary(), indent=2, ensure_ascii=False))
        return 0
    if command == "units":
        result = biomedical_units.same_unit(args.a, args.b)
        print(json.dumps(result, ensure_ascii=False))
        return {"SAME": 0, "UNREADABLE": 10}.get(result["outcome"], 1)
    if command not in ("check", "mechanism"):
        print("usage: coresearcher biomedical check|mechanism --request FILE | units A B | vocabulary", file=sys.stderr)
        return 2
    try:
        request = json.loads(Path(args.request).read_text(encoding="utf-8"))
        backend = request.get("backend", "auto")
        if command == "mechanism":
            result = mechanistic_chain.check(request["mechanism"], backend)
            if result["formal_status"] != FormalStatus.DECIDED.value:
                _write(args, result)
                print(f"{result['formal_status']}: {result['reason']}", file=sys.stderr)
                return 11
            statuses = [o["status"] for o in result["obligations"]]
            lines = [f"{o['id']}: {o['status']}" for o in result["obligations"]]
        else:
            obligations, report = biomedical_domain.check(
                request["hypothesis"], request.get("biomedical"), request.get("consequences"), backend
            )
            result = {"formal_status": FormalStatus.DECIDED.value, "obligations": [o.to_dict() for o in obligations],
                      "report": report}
            statuses = [o.status.value for o in obligations]
            lines = [f"{o.id}: {o.status.value}" for o in obligations]
    except (KeyError, OSError, ValueError, mechanistic_chain.MechanismError, biomedical_domain.DomainSpecError,
            FormalHypothesisError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return formal_status.EXIT_REFUSAL
    _write(args, result)
    print("\n".join(lines) if lines else "no biomedical obligations requested")
    return _exit(statuses)
