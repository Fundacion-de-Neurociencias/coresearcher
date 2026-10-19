"""Compare an OASE checker's findings before and after the adapter is applied.

    python3 compare_checks.py relay|threshold <pristine-output> <pristine-exit> <patched-output> <patched-exit>

At the pinned commit, OASE's own `check_relay_codes.py` and `check_threshold_names.py`
already report problems in upstream files (2 and 10 at b7e5e35). Requiring exit 0
would fail on upstream's state; ignoring the exit would pass anything. So the
gate is: neither run is "could not run" (exit 2), the patched run reports no
problem the pristine run did not, and no reported problem mentions the adapter.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CANNOT_RUN = 2


def problems(kind: str, text: str) -> set[str]:
    lines = text.splitlines()
    if kind == "relay":
        return {line.strip() for line in lines if re.match(r"^\s+check [123]: ", line)}
    out: set[str] = set()
    collecting = False
    for line in lines:
        if re.match(r"^\d+ problem\(s\):", line):
            collecting = True
            continue
        if collecting:
            if not line.startswith("  "):
                break
            out.add(line.strip())
    return out


def main(argv: list[str]) -> int:
    kind, before_path, before_rc, after_path, after_rc = argv
    if int(before_rc) == CANNOT_RUN or int(after_rc) == CANNOT_RUN:
        print(f"{kind}: the checker could not run (exit 2); that is not a pass", file=sys.stderr)
        return 1
    before = problems(kind, Path(before_path).read_text(encoding="utf-8"))
    after = problems(kind, Path(after_path).read_text(encoding="utf-8"))
    new = sorted(after - before)
    ours = sorted(p for p in after if re.search(r"\bformal\b|formal-hypothesis-verification", p))
    print(f"{kind}: upstream baseline {len(before)} problem(s); with the adapter {len(after)}")
    if int(after_rc) not in (0, 1):
        print(f"{kind}: unexpected exit {after_rc}", file=sys.stderr)
        return 1
    if new or ours:
        for line in sorted(set(new) | set(ours)):
            print(f"  introduced by the adapter: {line}", file=sys.stderr)
        return 1
    print(f"{kind}: the adapter introduces no problem")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
