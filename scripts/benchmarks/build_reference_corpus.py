"""Reference corpus for the hypothesis inspiration protocol (section 5.3). Needs network access to OpenAlex.

    python scripts/benchmarks/build_reference_corpus.py anchors   # once: freezes anchors.json
    python scripts/benchmarks/build_reference_corpus.py corpus    # one hop of references and citations, freezes corpus.jsonl

Both steps record the SHA-256 of their output. The corpus is built once and shared by every arm; per-arm date
boundaries are applied later, from the corpus, and never change it. `fetch` is injectable so the logic is tested
without the network. OpenAlex is the only external source.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INSPIRATION = ROOT / "docs" / "reference" / "benchmarks" / "inspiration"
QUERIES = INSPIRATION / "anchor_queries.json"
ANCHORS = INSPIRATION / "anchors.json"
CORPUS = INSPIRATION / "corpus.jsonl"
API = "https://api.openalex.org"
PAGE = 200


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _default_fetch(url: str, params: dict) -> dict:
    import httpx

    if os.environ.get("OPENALEX_MAILTO"):
        params = {**params, "mailto": os.environ["OPENALEX_MAILTO"]}
    response = httpx.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    return response.json()


def abstract_text(inverted: dict | None) -> str:
    """OpenAlex stores abstracts as word -> positions. Rebuild the text in order."""
    if not inverted:
        return ""
    positions = {}
    for word, places in inverted.items():
        for place in places:
            positions[place] = word
    return " ".join(positions[k] for k in sorted(positions))


def in_window(date: str | None, window: dict) -> bool:
    return bool(date) and window["from"] <= date <= window["to"]


def record(work: dict, source: str, anchor: str) -> dict:
    return {
        "id": work["id"].rsplit("/", 1)[-1],
        "doi": work.get("doi"),
        "title": work.get("title") or "",
        "publication_date": work.get("publication_date"),
        "abstract": abstract_text(work.get("abstract_inverted_index")),
        "source": source,
        "anchor": anchor,
    }


def select_anchors(fetch=_default_fetch) -> dict:
    """The top-cited works per domain query in the anchor window, once."""
    spec = json.loads(QUERIES.read_text(encoding="utf-8"))
    window = spec["anchor_window"]
    anchors = {}
    for domain, query in spec["queries"].items():
        data = fetch(
            f"{API}/works",
            {
                "search": query,
                "filter": f"from_publication_date:{window['from']},to_publication_date:{window['to']},type:article",
                "sort": "cited_by_count:desc",
                "per-page": spec["anchors_per_domain"],
            },
        )
        anchors[domain] = [
            {
                "id": w["id"].rsplit("/", 1)[-1],
                "title": w.get("title") or "",
                "publication_date": w.get("publication_date"),
            }
            for w in data.get("results", [])[: spec["anchors_per_domain"]]
        ]
    payload = {"queries_sha256": _sha256(QUERIES), "anchors": anchors}
    ANCHORS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def _referenced(fetch, anchor_id: str) -> list:
    """Works this anchor cites, fetched in one batch."""
    data = fetch(f"{API}/works/{anchor_id}", {})
    ids = [u.rsplit("/", 1)[-1] for u in data.get("referenced_works", [])]
    works = []
    for start in range(0, len(ids), PAGE):
        batch = ids[start : start + PAGE]
        result = fetch(f"{API}/works", {"filter": "openalex:" + "|".join(batch), "per-page": PAGE})
        works.extend(result.get("results", []))
    return works


def _citing(fetch, anchor_id: str, cap: int) -> list:
    """Works that cite this anchor, up to `cap`."""
    works, cursor = [], "*"
    while len(works) < cap:
        data = fetch(
            f"{API}/works",
            {"filter": f"cites:{anchor_id}", "per-page": min(PAGE, cap - len(works)), "cursor": cursor},
        )
        works.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor or not data.get("results"):
            break
    return works[:cap]


def build_corpus(fetch=_default_fetch) -> dict:
    spec = json.loads(QUERIES.read_text(encoding="utf-8"))
    if not ANCHORS.exists():
        raise SystemExit("anchors.json is missing: run the 'anchors' step first.")
    anchors = json.loads(ANCHORS.read_text(encoding="utf-8"))["anchors"]
    window = spec["traversal"]["window"]
    cap = spec["traversal"]["max_citing_per_anchor"]
    seen, rows = set(), []
    for domain, items in anchors.items():
        for anchor in items:
            for source, works in (
                ("reference", _referenced(fetch, anchor["id"])),
                ("citation", _citing(fetch, anchor["id"], cap)),
            ):
                for work in works:
                    rec = record(work, source, anchor["id"])
                    if rec["id"] in seen or not in_window(rec["publication_date"], window):
                        continue
                    seen.add(rec["id"])
                    rows.append({**rec, "domain": domain})
    rows.sort(key=lambda r: r["id"])
    CORPUS.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return {"works": len(rows), "sha256": _sha256(CORPUS)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["anchors", "corpus"])
    args = parser.parse_args(argv)
    if args.step == "anchors":
        payload = select_anchors()
        print(f"Wrote {ANCHORS.relative_to(ROOT)}: {sum(len(v) for v in payload['anchors'].values())} anchors")
    else:
        summary = build_corpus()
        print(f"Wrote {CORPUS.relative_to(ROOT)}: {summary['works']} works, sha256 {summary['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
