"""Reference check for benchmark protocols (docs/reference/benchmarks/PROTOCOL_TEMPLATE.md, section 8). Needs network
access to OpenAlex.

    python scripts/benchmarks/check_references.py references.json [--out checked.json]

The input is a JSON list of {"key": str, "doi": str or null, "title": str}. Each item gets one status:
VERIFIED when its DOI resolves to a work with the same title, MISMATCH when the DOI resolves to a different title
(the usual sign of an invented citation), NOT_FOUND when OpenAlex has no such DOI, and NO_DOI when there is nothing to
look up. No item is dropped. `fetch` is injectable so the logic is tested without the network.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

API = "https://api.openalex.org"


def _default_fetch(url: str) -> tuple:
    """Returns (status code, parsed JSON or None). A 404 is a normal answer here, not an error."""
    import httpx

    params = {"mailto": os.environ["OPENALEX_MAILTO"]} if os.environ.get("OPENALEX_MAILTO") else {}
    response = httpx.get(url, params=params, timeout=30.0)
    if response.status_code == 404:
        return 404, None
    response.raise_for_status()
    return response.status_code, response.json()


def normalise_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def normalise_doi(doi: str) -> str:
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            return doi[len(prefix) :]
    return doi


def check(item: dict, fetch) -> dict:
    result = {"key": item["key"], "doi": item.get("doi")}
    if not item.get("doi"):
        return {**result, "status": "NO_DOI", "openalex_id": None, "openalex_title": None}
    doi = normalise_doi(item["doi"])
    status, data = fetch(f"{API}/works/doi:{doi}")
    if status == 404 or data is None:
        return {**result, "status": "NOT_FOUND", "openalex_id": None, "openalex_title": None}
    found = data.get("title") or ""
    result.update({"openalex_id": data["id"].rsplit("/", 1)[-1], "openalex_title": found})
    if not item.get("title"):
        return {**result, "status": "VERIFIED", "reason": "no title given to compare"}
    same = normalise_title(item["title"]) == normalise_title(found)
    return {**result, "status": "VERIFIED" if same else "MISMATCH"}


def check_all(items: list, fetch=_default_fetch) -> dict:
    rows = [check(item, fetch) for item in items]
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {"total": len(rows), "counts": counts, "items": rows}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("references", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    items = json.loads(args.references.read_text(encoding="utf-8"))
    summary = check_all(items, _default_fetch)
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
