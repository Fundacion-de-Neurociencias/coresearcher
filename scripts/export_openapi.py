"""Exports the FastAPI OpenAPI contract to schemas/openapi.json.

The file is the language-neutral contract between the Python core and the
TypeScript packages (MCP server, agents). CI regenerates it and fails when the
committed copy is stale, so the contract cannot drift silently.

Usage:
    python scripts/export_openapi.py          # write schemas/openapi.json
    python scripts/export_openapi.py --check  # exit 1 if the committed file is stale
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "schemas" / "openapi.json"


def render() -> str:
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("CORESEARCHER_API_KEY", "contract-export")
    from api.server import app

    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    content = render()
    if "--check" in argv:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != content:
            print(f"{OUTPUT.relative_to(ROOT)} is stale. Run: python scripts/export_openapi.py")
            return 1
        print("OpenAPI contract is up to date.")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
