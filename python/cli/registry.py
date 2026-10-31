"""
python/cli/registry.py - `coresearcher registry`: the cited-results registry from the command line (ADR-DISCOVERY-083).

    coresearcher registry register  --entry entry.json            add an entry or a new version
    coresearcher registry show      ID [--version N]               print an entry and its flag
    coresearcher registry cite-check ID --context context.json     check one use; exit 0 CLEAR, 1 FINDINGS, 10 INCOMPLETE
    coresearcher registry depend    NODE ON                        record that NODE uses ON
    coresearcher registry retract   ID --reason TEXT [--downgrade-to RUNG]
    coresearcher registry impact    NODE                           every transitive dependent
    coresearcher registry reevaluated NODE --note TEXT             clear a re-evaluation flag

The store is a JSON file: --store, else CORESEARCHER_REGISTRY_PATH, else .coresearcher/registry.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from python.discovery import cited_registry
from python.discovery.formal_hypothesis import FormalHypothesisError

DEFAULT_STORE = Path(".coresearcher") / "registry.json"
EXIT_FINDINGS = 1
EXIT_INCOMPLETE = 10  # a non-verdict, as UNDECIDED elsewhere in the formal CLI
EXIT_REFUSED = 9


def _store(args: argparse.Namespace) -> Path:
    if args.store:
        return Path(args.store)
    return cited_registry.default_store() or DEFAULT_STORE


def _read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _print(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, default=str))


def add_parser(subparsers) -> None:
    p = subparsers.add_parser("registry", help="Cited results and premises: conventions, hypotheses, retraction")
    p.add_argument("--store", help="Registry JSON file (default: CORESEARCHER_REGISTRY_PATH or .coresearcher/)")
    sub = p.add_subparsers(dest="registry_command")
    r = sub.add_parser("register", help="Add an entry, or a new version of one")
    r.add_argument("--entry", required=True, help="Entry JSON file")
    s = sub.add_parser("show", help="Print an entry and its re-evaluation flag")
    s.add_argument("id")
    s.add_argument("--version", type=int)
    c = sub.add_parser("cite-check", help="Check one use of a registered result")
    c.add_argument("id")
    c.add_argument("--context", required=True, help="Citing context JSON: variables, assumptions, conventions, text")
    c.add_argument("--version", type=int)
    d = sub.add_parser("depend", help="Record that NODE uses ON")
    d.add_argument("node")
    d.add_argument("on")
    x = sub.add_parser("retract", help="Retract or downgrade an entry and flag its dependents")
    x.add_argument("id")
    x.add_argument("--reason", required=True)
    x.add_argument("--downgrade-to", choices=cited_registry.RUNG_ORDER)
    x.add_argument("--date")
    i = sub.add_parser("impact", help="Every transitive dependent of a node")
    i.add_argument("node")
    v = sub.add_parser("reevaluated", help="Clear a re-evaluation flag")
    v.add_argument("node")
    v.add_argument("--note", required=True)


def main(args: argparse.Namespace) -> int:
    command = getattr(args, "registry_command", None)
    if not command:
        print("usage: coresearcher registry {register,show,cite-check,depend,retract,impact,reevaluated} ...",
              file=sys.stderr)
        return 2
    try:
        reg = cited_registry.Registry(_store(args))
        if command == "register":
            _print({"entry": asdict(reg.register(_read_json(args.entry)))})
        elif command == "show":
            _print({"entry": asdict(reg.get(args.id, args.version)), "flag": reg.flags.get(args.id)})
        elif command == "cite-check":
            report = cited_registry.cite_check(reg.get(args.id, args.version), _read_json(args.context))
            _print(report)
            return {cited_registry.CLEAR: 0, cited_registry.FINDINGS: EXIT_FINDINGS}.get(report["outcome"],
                                                                                      EXIT_INCOMPLETE)
        elif command == "depend":
            _print(reg.depend(args.node, args.on))
        elif command == "retract":
            _print(reg.retract(args.id, args.reason, args.downgrade_to, args.date))
        elif command == "impact":
            _print(reg.impact(args.node))
        elif command == "reevaluated":
            _print(reg.reevaluated(args.node, args.note))
        return 0
    except (cited_registry.RegistryError, FormalHypothesisError, TypeError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REFUSED
