"""Recomputes the openai/math corpus statistics (python/discovery/openai_math_strategy.py).

python scripts/cases/openai_math_corpus.py --cache <empty dir> [--traces <dir of pdftotext .txt files>]

Downloads, at the pinned commit, overview.tex, lean/formalization.yaml, the preprints tree and every .bib file under
preprints/ (about 520 files) into --cache, then writes examples/openai-math-strategy/corpus_stats.json. The downloads
are data: nothing from them is executed. Use a fresh, empty cache directory.
"""

import argparse
import concurrent.futures
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import openai_math_strategy as oms  # noqa: E402

RAW = f"https://raw.githubusercontent.com/openai/math/{oms.COMMIT}/"
API = "https://api.github.com/repos/openai/math/git/trees/"


def fetch(url: str, dest: Path) -> bytes:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=60) as resp:
            dest.write_bytes(resp.read())
    return dest.read_bytes()


def safe_name(rel: str) -> str:
    # Short flat names: preprint paths exceed the Windows path-length limit.
    return hashlib.sha256(rel.encode("utf-8")).hexdigest()[:20] + "_" + rel.rsplit("/", 1)[-1][-40:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--traces", type=Path, help="directory of reasoning-summary .txt files (pdftotext output)")
    parser.add_argument("--out", type=Path, default=ROOT / "examples" / "openai-math-strategy" / "corpus_stats.json")
    args = parser.parse_args()
    cache = args.cache
    for name, digest in oms.SOURCE_SHA256.items():
        data = fetch(RAW + name, cache / safe_name(name))
        if hashlib.sha256(data).hexdigest() != digest:
            raise SystemExit(f"{name}: SHA-256 mismatch")
    root_tree = json.loads(fetch(API + oms.COMMIT, cache / "root_tree.json"))
    sha = next(e["sha"] for e in root_tree["tree"] if e["path"] == "preprints")
    tree = json.loads(fetch(API + sha + "?recursive=1", cache / "preprints_tree.json"))
    assert not tree["truncated"]
    bibs = [e["path"] for e in tree["tree"] if e["type"] == "blob" and e["path"].endswith(".bib")]

    def get(rel: str):
        return rel, fetch(RAW + "preprints/" + rel, cache / "bib" / safe_name(rel)).decode("utf-8", "replace")

    texts = {}
    with concurrent.futures.ThreadPoolExecutor(16) as pool:
        for rel, text in pool.map(get, bibs):
            texts.setdefault(rel.split("/")[0], []).append(text)
    families = oms.parse_overview((cache / safe_name("overview.tex")).read_text(encoding="utf-8"))
    formalized = oms.formalized_dirs((cache / safe_name("lean/formalization.yaml")).read_text(encoding="utf-8"))
    edges = oms.citation_edges(texts)
    stats = oms.corpus_stats(families, edges, formalized, dirs_with_bib=len(texts))
    stats["commit"] = oms.COMMIT
    stats["preprint_dirs"] = len({e["path"].split("/")[0] for e in tree["tree"]})
    stats["traces"] = oms.trace_aggregates()
    if args.traces:
        stats["trace_text_counts"] = {
            t["file"]: oms.trace_text_counts((args.traces / f"{t['file']}.txt").read_text("utf-8", "replace"))
            for t in oms.TRACES
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    print(json.dumps(stats["citations"], indent=1))


if __name__ == "__main__":
    main()
