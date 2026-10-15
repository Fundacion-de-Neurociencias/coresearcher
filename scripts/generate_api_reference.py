"""Generates docs/reference/API.md from the committed OpenAPI contract.

The reference is derived, never edited by hand. Regenerate after changing routes:

    python scripts/export_openapi.py
    python scripts/generate_api_reference.py

Pass ``--check`` to fail when the committed reference is out of date (used in CI).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "schemas" / "openapi.json"
OUTPUT = ROOT / "docs" / "reference" / "API.md"
WRITE_METHODS = {"post", "put", "delete", "patch"}


def render() -> str:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    rows = []
    for path in sorted(spec["paths"]):
        for method, operation in spec["paths"][path].items():
            if method not in {"get", "post", "put", "delete", "patch"}:
                continue
            auth = "API key" if method in WRITE_METHODS else "Public"
            if "webhooks" in path:
                auth = "HMAC signature"
            summary = operation.get("summary", operation.get("operationId", ""))
            rows.append(f"| `{method.upper()}` | `{path}` | {auth} | {summary} |")
    header = [
        "# REST API reference",
        "",
        "> Generated from [`schemas/openapi.json`](../../schemas/openapi.json). Do not edit by hand.",
        "",
        f"Operations: {len(rows)}. Interactive documentation is served at `/docs` when the API runs.",
        "",
        "Authentication: write operations (`POST`, `PUT`, `DELETE`) require the `X-API-Key` header",
        "matching `CORESEARCHER_API_KEY`. Read operations are public on the bound interface.",
        "Webhooks are verified with the `X-Hub-Signature-256` header.",
        "",
        "| Method | Path | Auth | Operation |",
        "| --- | --- | --- | --- |",
    ]
    return "\n".join(header + rows) + "\n"


def main(argv: list[str]) -> int:
    content = render()
    if "--check" in argv:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != content:
            print(f"{OUTPUT.relative_to(ROOT)} is stale. Run: python scripts/generate_api_reference.py")
            return 1
        print("API reference is up to date.")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
