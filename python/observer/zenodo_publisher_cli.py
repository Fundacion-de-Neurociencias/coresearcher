"""
CLI entrypoint for Zenodo publishing of a ScientificLedger.

Usage:
    python -m observer.zenodo_publisher_cli <ledger.json> [--publish] [--sandbox] [--token TOKEN]

Environment:
    ZENODO_TOKEN: API token (required if --token is not provided)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from observer.scientific_ledger import ScientificLedger
from observer.zenodo_publisher import ZenodoPublisher


def load_ledger(path: str) -> ScientificLedger:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ScientificLedger.from_dict(data)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish a ScientificLedger JSON to Zenodo."
    )
    parser.add_argument("ledger_json", help="Path to ledger JSON file")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish immediately and obtain DOI (default: create draft only)",
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        default=True,
        help="Use Zenodo sandbox (default: True)",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Use Zenodo production (overrides --sandbox)",
    )
    parser.add_argument("--token", help="Zenodo API token (overrides ZENODO_TOKEN)")
    args = parser.parse_args()

    if not os.path.exists(args.ledger_json):
        print(f"Error: ledger file not found: {args.ledger_json}", file=sys.stderr)
        return 1

    token = args.token or os.environ.get("ZENODO_TOKEN")
    if not token:
        print("Error: Zenodo token required. Set ZENODO_TOKEN or pass --token.", file=sys.stderr)
        return 1

    use_sandbox = not args.prod

    try:
        ledger = load_ledger(args.ledger_json)
    except Exception as e:
        print(f"Error loading ledger: {e}", file=sys.stderr)
        return 1

    try:
        publisher = ZenodoPublisher(api_token=token, use_sandbox=use_sandbox)
        if args.publish:
            doi = publisher.publish_and_get_doi(ledger)
            print(f"Published. DOI: {doi}")
        else:
            deposition = publisher.deposit(ledger, publish=False)
            print(f"Draft created. Deposition ID: {deposition.get('id')}")
            print(f"Status      : {deposition.get('status', '')}")
            print(f"URL         : {deposition.get('links', {}).get('self_html', '')}")
    except Exception as e:
        print(f"Error publishing to Zenodo: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())