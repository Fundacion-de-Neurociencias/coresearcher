"""
python/cli/main.py - CoResearcher Unified CLI Entry Point (ADR-QA-002)
Inspired by OpenScience and modern developer toolchains.
Provides unified commands:
    coresearcher verify --claim <statement> [--rcs <level>]
    coresearcher serve [--host <host>] [--port <port>]
    coresearcher test
    coresearcher info
    coresearcher formal run | analyze | doctor   (ADR-DISCOVERY-068)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BANNER = r"""
   ______      ____                                __
  / ____/___  / __ \___  ________  ____ ___________/ /_  ___  _____
 / /   / __ \/ /_/ / _ \/ ___/ _ \/ __ `/ ___/ ___/ __ \/ _ \/ ___/
/ /___/ /_/ / _, _/  __(__  )  __/ /_/ / /  / /__/ / / /  __/ /
\____/\____/_/ |_|\___/____/\___/\__,_/_/   \___/_/ /_/\___/_/
   The Autonomous Epistemic Discovery & Formal Verification Engine
"""


def cmd_verify(args: argparse.Namespace) -> int:
    """Verifies a scientific claim against Reality Contact Firewall and physical laws."""
    from python.discovery.epistemic_stigmergy import RealityContactFirewall

    print(f"[*] Auditing Claim: '{args.claim}'")
    print(f"[*] Claimed RCS Level: {args.rcs}")
    anchors = [a.strip() for a in args.anchors.split(",")] if args.anchors else []

    report = RealityContactFirewall.audit_promotion_request(
        hypothesis_id="CLI-CLAIM-VERIFY",
        claimed_regularity=args.claim,
        rcs_level=args.rcs,
        empirical_anchors=anchors,
    )

    if report.is_firewall_passed:
        print("\n[VERDICT: PASSED]")
        print(f"Directive: {report.epistemic_directive}")
        print(f"Cryptographic Hash: {report.som_firewall_hash}")
        return 0
    else:
        print("\n[VERDICT: QUARANTINED]")
        print(f"Rejection: {report.rejection_reason}")
        print(f"Directive: {report.epistemic_directive}")
        return 1


def cmd_serve(args: argparse.Namespace) -> int:
    """Launches the production FastAPI server."""
    import uvicorn

    print(f"[*] Starting CoResearcher REST API on {args.host}:{args.port}")
    uvicorn.run("api.server:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    """Runs the verified pytest test suite."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    if args.k:
        cmd.extend(["-k", args.k])
    return subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode


def cmd_info(args: argparse.Namespace) -> int:
    """Displays CoResearcher architecture, active local AI wiring, and engines."""
    print(BANNER)
    print("CoResearcher Version: 4.1.0")
    print(f"Repository Root:    {REPO_ROOT}")
    print(f"Python Runtime:     {sys.version.split()[0]}")
    print(f"Local AI System 1:  {os.getenv('LAYA_ENDPOINT', 'http://localhost:11434')} (Laya / Ollama)")
    print(f"Local AI System 2:  {os.getenv('LOCAL_IA_ENDPOINT', 'http://localhost:1234')} (Local IA / LM Studio)")
    print("\nCore Engines Active:")
    print("  * PhysicalCoherenceCourt (Sobolev-Gronwall proof verification)")
    print("  * CommutativeDiagramAuditor (Categorical Holonomy Defect ||Delta M||)")
    print("  * RealityContactFirewall (Strict anti-hallucination RCS >= 2.0 gate)")
    print("  * EpistemicPheromoneField (Decentralized Agora swarm coordination)")
    print("  * AdversarialDestructionEngine (50-case failure trap stress-testing)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="coresearcher",
        description="CoResearcher CLI - Autonomous Scientific Discovery & Epistemic Audit",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # audit

    # verify
    p_verify = subparsers.add_parser("verify", help="Audit an empirical claim against the Reality Contact Firewall")
    p_verify.add_argument("--claim", required=True, help="Hypothesis statement or regularity claim")
    p_verify.add_argument("--rcs", type=int, default=2, help="Claimed Reality Contact Score level (0 to 4)")
    p_verify.add_argument("--anchors", default="", help="Comma-separated physical anchors / datasets")

    # serve
    p_serve = subparsers.add_parser("serve", help="Launch the CoResearcher FastAPI discovery server")
    p_serve.add_argument("--host", default="127.0.0.1", help="Bind host")
    p_serve.add_argument("--port", type=int, default=8000, help="Bind port")
    p_serve.add_argument("--reload", action="store_true", help="Enable live code reload")

    # test
    p_test = subparsers.add_parser("test", help="Execute the complete pytest verification suite")
    p_test.add_argument("-k", default=None, help="Pytest filter expression")

    # info
    subparsers.add_parser("info", help="Display system architecture and active AI endpoints")

    # formal run | analyze | doctor (ADR-DISCOVERY-068)
    from python.cli import formal

    formal.add_parser(subparsers)

    args = parser.parse_args()
    if not args.command:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "verify": cmd_verify,
        "serve": cmd_serve,
        "test": cmd_test,
        "info": cmd_info,
        "formal": formal.main,
    }

    exit_code = dispatch[args.command](args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
