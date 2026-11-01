"""
python/cli/chain.py - `coresearcher chain run`: the composed verification chain (ADR-DISCOVERY-085).

    coresearcher chain run --request CHAIN.json [--freeze-store F] [--registry R] [--out RESULT.json]

CHAIN.json holds exactly one of `hypothesis` (a formal object) and `prose`, plus optional `rivals`, `consequences`,
`observations`, `citations` (uses of registry entries, ADR-083), `fidelity_spec` (ADR-070) and `claim_evidence`, and
either `freeze: {freeze_id, expected_sha256}` (criteria frozen earlier) or `author` (the chain then freezes the
criteria itself, before evaluating). Prose needs a configured formalizer model; without one the chain is BLOCKED.

Prints one line per step (freeze, formalize, fidelity, vacuity, obligations, seams, discharge, trust ladder) and
writes the full result to --out when given. Exit codes follow `coresearcher formal`: 0 decided; 13 the frozen criteria
or the hypothesis changed; 10 UNDECIDED; 11 formalization ambiguous or failed; 8 a missing capability; 9 refused input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from python.discovery import cited_registry, formal_status, freeze_service, verification_chain
from python.discovery.formal_status import FormalStatus

_EXIT = {
    FormalStatus.DECIDED.value: 0,
    FormalStatus.UNDECIDED.value: 10,
    FormalStatus.INVALID_INPUT.value: formal_status.EXIT_REFUSAL,
    FormalStatus.FORMALIZATION_AMBIGUOUS.value: 11,
    FormalStatus.FORMALIZATION_FAILED.value: 11,
}


def add_parser(subparsers) -> None:
    p = subparsers.add_parser("chain", help="Run the composed verification chain on one hypothesis (ADR-085)")
    sub = p.add_subparsers(dest="chain_command")
    r = sub.add_parser(
        "run", help="freeze, formalize, fidelity, vacuity, obligations, seams, discharge, trust ladder"
    )
    r.add_argument("--request", required=True, help="Chain request JSON")
    r.add_argument("--freeze-store", help="Freeze store (default: CORESEARCHER_FREEZE_PATH or .coresearcher/)")
    r.add_argument("--registry", help="Registry store (default: CORESEARCHER_REGISTRY_PATH or .coresearcher/)")
    r.add_argument("--out", help="Write the full chain result here")


def exit_code(result) -> int:
    status = result["formal_status"]
    if status == FormalStatus.BLOCKED.value:
        steps = {s["name"]: s for s in result["steps"]}
        frozen = steps["freeze"]["state"] == status or steps["formalize"]["outcome"] == "READING_NOT_FROZEN"
        return formal_status.EXIT_FREEZE_CHANGED if frozen else formal_status.EXIT_DEPENDENCY
    return _EXIT.get(status, formal_status.EXIT_REFUSAL)


def main(args: argparse.Namespace) -> int:
    if getattr(args, "chain_command", None) != "run":
        print("usage: coresearcher chain run --request CHAIN.json", file=sys.stderr)
        return 2
    from python.cli import freeze as freeze_cli
    from python.cli import registry as registry_cli

    try:
        spec = json.loads(Path(args.request).read_text(encoding="utf-8"))
        freezes = freeze_service.FreezeStore(
            Path(args.freeze_store) if args.freeze_store else freeze_service.default_store() or freeze_cli.DEFAULT_STORE
        )
        registry = cited_registry.Registry(
            Path(args.registry) if args.registry else cited_registry.default_store() or registry_cli.DEFAULT_STORE
        )
        clients = None
        if isinstance(spec, dict) and spec.get("prose") is not None:
            from python.cli.formal import formalizer_clients

            try:
                clients = formalizer_clients()
            except ValueError:
                clients = {}
        result = verification_chain.run(spec, freezes, registry, clients)
    except (
        verification_chain.ChainInputError,
        freeze_service.FreezeError,
        cited_registry.RegistryError,
        OSError,
        ValueError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return formal_status.EXIT_REFUSAL
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(verification_chain.summary(result))
    if result["reason"]:
        print(f"{result['formal_status']}: {result['reason']}", file=sys.stderr)
    return exit_code(result)
