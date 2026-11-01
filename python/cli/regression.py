"""
python/cli/regression.py - `coresearcher regression`: benchmarks as regression tests (ADR-DISCOVERY-084).

    coresearcher regression list                                   the cases and what they measure
    coresearcher regression check  [--case ID ...] [--json]        exit 0 PASS, 1 any difference, 10 a case errored
    coresearcher regression update --reason TEXT [--case ID ...]   freeze fresh observations as the expectations

A difference in either direction fails `check`: a regression, and also an improvement whose expectation was not
updated in the same change. See docs/reference/REGRESSION_BENCHMARKS.md.
"""

from __future__ import annotations

import argparse
import json
import sys

from python.discovery import capability_regression as cr

EXIT_DIFFERENCE = 1
EXIT_ERROR = 10  # a non-verdict, as UNDECIDED elsewhere in the formal CLI
EXIT_REFUSED = 9


def _print(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, default=str))


def add_parser(subparsers) -> None:
    p = subparsers.add_parser("regression", help="Benchmarks as regression tests: check or update the expectations")
    sub = p.add_subparsers(dest="regression_command")
    sub.add_parser("list", help="The regression cases")
    c = sub.add_parser("check", help="Run the cases and compare them with the frozen expectations")
    c.add_argument("--case", action="append", dest="cases", help="Case id (repeatable; default: all)")
    c.add_argument("--json", action="store_true", help="Print the full report as JSON")
    u = sub.add_parser("update", help="Freeze fresh observations as the expectations")
    u.add_argument("--reason", required=True, help="Why the expectations change; recorded in their history")
    u.add_argument("--case", action="append", dest="cases", help="Case id (repeatable; default: all)")


def _summary(report) -> None:
    print(f"expectations v{report['expectations_version']}: {report['status']}")
    for case in report["cases"]:
        print(f"  {case['status']:<15} {case['case']} ({case['observations']} observations, {case['seconds']} s)")
        if case["error"]:
            print(f"      error: {case['error']}")
        for d in case["differences"]:
            print(f"      {d['class']:<15} {d['key']}: expected {d['expected']!r}, observed {d['observed']!r}")
    if report["status"] not in (cr.PASS, cr.ERROR):
        print("If the change is deliberate, run `coresearcher regression update --reason ...` and commit "
              "benchmarks/regression/expectations.json with it.")


def main(args: argparse.Namespace) -> int:
    command = getattr(args, "regression_command", None)
    if not command:
        print("usage: coresearcher regression {list,check,update} ...", file=sys.stderr)
        return 2
    try:
        if command == "list":
            _print(cr.describe())
            return 0
        if command == "check":
            report = cr.check(args.cases)
            _print(report) if args.json else _summary(report)
            if report["status"] == cr.ERROR:
                return EXIT_ERROR
            return 0 if report["status"] == cr.PASS else EXIT_DIFFERENCE
        out = cr.update(args.reason, args.cases)
        _print(out)
        return 0
    except (cr.ExpectationsError, KeyError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REFUSED
