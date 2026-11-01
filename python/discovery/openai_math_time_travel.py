"""
python/discovery/openai_math_time_travel.py - Scoring of the openai/math time-travel benchmark, and its offline
replay from vendored excerpts (ADR-DISCOVERY-077, ADR-DISCOVERY-084).

The benchmark (docs/reference/benchmarks/OPENAI_MATH_REVISION_PROTOCOL.md) runs the manuscript checks on the pre-fix
and corrected sources of real openai/math corrections and records, per defect, HIT, MISS or NOT_ENCODABLE, plus the
false alarms on corrected and never-revised manuscripts. The full run needs a clone of openai/math
(scripts/benchmarks/openai_math_revision_bench.py). This module holds the scoring shared by that script and the
offline regression replay.

An excerpt keeps, for each version of each manuscript, only the lines the score depends on: every math segment or
citation that the checks flag, every math segment that touches a defect location, and the defect locations
themselves (with the location tolerance). Lines keep their original numbers: the replay pads the gaps with blank
lines, so flags land on the same lines and the locations of the dataset apply unchanged. The bibliography is kept as
its set of keys only, and the snapshot of manuscript names as the names that the excerpts link to. The builder
checks that the replay of every excerpt reproduces the full run's flags exactly before it writes the fixture.
"""

from __future__ import annotations

import bisect
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from python.discovery import cited_import_ledger, manuscript_checks

CHECKS = ["statement_fidelity", "lean_junk_lint", "CITATION", "IDENTITY_STRICT", "IDENTITY_CONTEXT", "EXPONENT"]
LOCATION_TOLERANCE = 2  # lines

# Families of two revised manuscripts have a Lean note at PRE. What the Lean statement covers, from lean/docs:
LEAN_SCOPE = {
    "Taming-implies-compatibility-on-four-manifolds":
        "Lean note 342 formalizes only the main theorem (taming implies compatibility); the defect is in the "
        "cone corollary, which has no Lean statement",
    "Incompressible-Box-Transport-and-Finite-Computation":
        "Lean note 376 formalizes the sheet-program and halting-detection statements; the defect is in the "
        "prose proof of the projection and decay estimates, not in a formal statement",
}

KEYS_FILE = "__bibliography_keys__.bib"  # Synthetic: one `@misc{key,}` per bibliography key of the full sources.


# ---------------------------------------------------------------------------
# Scoring (shared with scripts/benchmarks/openai_math_revision_bench.py)
# ---------------------------------------------------------------------------


def in_location(flag: dict, locations: dict) -> bool:
    for f, rs in locations.items():
        if flag["file"] != f:
            continue
        for a, b in rs:
            if a - LOCATION_TOLERANCE <= flag["line"] <= b + LOCATION_TOLERANCE:
                return True
    return False


def score(item: dict, pre: dict, post: Optional[dict]) -> dict:
    post_keys = {(f["check"], f["key"]) for f in post["flags"]} if post else set()
    per_check = {}
    hits = []
    for check in CHECKS[2:]:
        at_loc = [f for f in pre["flags"] if f["check"] == check and in_location(f, item["locations"])]
        resolved = [f for f in at_loc if (f["check"], f["key"]) not in post_keys]
        if resolved:
            verdict = "HIT"
            hits += resolved
        elif check in item["encodable"]:
            verdict = "MISS"
        else:
            verdict = "NOT_ENCODABLE"
        per_check[check] = {"verdict": verdict, "flags_at_location": len(at_loc), "resolved_at_location": len(resolved)}
    for check in CHECKS[:2]:
        # Lean checks see only the Comparator statement; a defect in the prose can never sit at a .tex location.
        reason = LEAN_SCOPE.get(item.get("id"), "no Lean note for the family at PRE")
        per_check[check] = {"verdict": "HIT" if check in item.get("lean_hits", []) else "NOT_ENCODABLE",
                            "reason": reason}
    verdicts = [v["verdict"] for v in per_check.values()]
    overall = "HIT" if "HIT" in verdicts else "MISS" if "MISS" in verdicts else "NOT_ENCODABLE"
    loc_lines = sum(b - a + 1 + 2 * LOCATION_TOLERANCE for rs in item["locations"].values() for a, b in rs)
    chance = {}
    for check in CHECKS[2:]:
        n = sum(f["check"] == check for f in pre["flags"])
        chance[check] = round(min(1.0, n * loc_lines / max(pre["tex_lines"], 1)), 4)
    return {"verdict": overall, "per_check": per_check, "hits": hits, "location_lines": loc_lines,
            "expected_chance_hits": chance}


def summarize(items: list) -> dict:
    out = {"defects": {}, "false_alarms": {}}
    defects = [i for i in items if "score" in i]
    for v in ("HIT", "MISS", "NOT_ENCODABLE"):
        out["defects"][v] = sorted(i["id"] for i in defects if i["score"]["verdict"] == v)
    for check in CHECKS[2:]:
        out["defects"][f"hits_{check}"] = sum(i["score"]["per_check"][check]["verdict"] == "HIT" for i in defects)

    def rate(group_items, key):
        lines = 0
        per_ms = []
        for i in group_items:
            fs = i[key] if key == "persistent" else i["pre"]["flags"]
            n = {c: sum(f["check"] == c for f in fs) for c in CHECKS[2:]}
            per_ms.append(n)
            lines += i["pre"]["tex_lines"]
        totals = {c: sum(n[c] for n in per_ms) for c in CHECKS[2:]}
        return {
            "manuscripts": len(group_items), "tex_lines": lines, "flags": totals,
            "flags_per_1000_lines": {c: round(1000 * totals[c] / max(lines, 1), 3) for c in CHECKS[2:]},
            "manuscripts_with_flag": {c: sum(n[c] > 0 for n in per_ms) for c in CHECKS[2:]},
        }

    revised = [i for i in items if i["group"] == "revised"]
    out["false_alarms"]["persistent_on_corrected"] = rate(revised, "persistent")
    out["false_alarms"]["citation_update_persistent"] = rate([i for i in items if i["group"] == "citation_update"],
                                                             "persistent")
    out["false_alarms"]["never_revised_controls"] = rate([i for i in items if i["group"] == "control"], "pre")
    return out


def score_items(dataset_items: List[dict], versions: Dict[str, Tuple[dict, Optional[dict]]]) -> List[dict]:
    """Per-item records as in the full run: `versions` maps an item id to its (pre, post) check results."""
    out = []
    for item in dataset_items:
        pre, post = versions[item["id"]]
        rec = {"id": item["id"], "group": item["group"], "pre": pre, "post": post}
        if post:
            post_keys = {(f["check"], f["key"]) for f in post["flags"]}
            rec["persistent"] = [f for f in pre["flags"] if (f["check"], f["key"]) in post_keys]
        if item["group"] in ("revised", "withdrawn"):
            rec["score"] = score(item, pre, post)
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# Excerpts
# ---------------------------------------------------------------------------


def check_files(files: Dict[str, str], snapshot: Optional[Set[str]]) -> List[dict]:
    """The manuscript checks on in-memory sources (the same calls as manuscript_checks.run_all)."""
    coverage = manuscript_checks.Coverage()
    flags = manuscript_checks.check_citations(files, snapshot, coverage) + manuscript_checks.check_math(files, coverage)
    return [f.to_dict() for f in flags]


def _segment_spans(text: str) -> List[Tuple[int, int]]:
    """1-based (first, last) line of every math segment and citation command, from the comment-stripped body."""
    body = manuscript_checks.strip_tex_comments(text)
    starts = [0] + [m.end() for m in re.finditer("\n", body)]
    spans = []

    def line(offset: int) -> int:
        return bisect.bisect_right(starts, offset)

    for offset, content in manuscript_checks.math_segments(text):
        spans.append((line(offset), line(offset + max(len(content), 1))))
    env_names = "|".join(re.escape(e) for e in manuscript_checks._DISPLAY_ENVS)
    for pattern in (r"\\begin\{(" + env_names + r")\}(.*?)\\end\{\1\}", r"\\\[(.*?)\\\]", r"\$\$(.*?)\$\$",
                    r"\\\((.*?)\\\)", r"(?<![\\$])\$([^$]+?)\$(?!\$)", manuscript_checks._CITE.pattern):
        for m in re.finditer(pattern, body, re.S):
            spans.append((line(m.start()), line(max(m.end() - 1, m.start()))))
    return sorted(set(spans))


def window(text: str, lines: Iterable[int]) -> List[int]:
    """The given lines, closed under whole math segments and citation commands that touch them."""
    spans = _segment_spans(text)
    keep = set(lines)
    changed = True
    while changed:
        changed = False
        for a, b in spans:
            if any(n in keep for n in range(a, b + 1)) and not all(n in keep for n in range(a, b + 1)):
                keep.update(range(a, b + 1))
                changed = True
    total = text.count("\n") + 1
    return sorted(n for n in keep if 1 <= n <= total)


def numeric_lines(text: str) -> List[int]:
    """Lines of every relation that `check_math` tests numerically. Its random points come from one generator shared
    by all relations in file order, so an excerpt keeps all of them to draw the same points as the full run."""
    body = manuscript_checks.strip_tex_comments(text)
    out = set()
    for offset, content in manuscript_checks.math_segments(text):
        chain = manuscript_checks.relation_chain(content)
        for (left, rel), (right, _) in zip(chain, chain[1:]):
            if rel != "=":
                continue
            try:
                a, _b = manuscript_checks.to_sympy(left), manuscript_checks.to_sympy(right)
            except Exception:
                continue
            if not manuscript_checks._is_definition(a):
                out.add(manuscript_checks._line_of(body, offset))
    return sorted(out)


def import_window(text: str, lines: Iterable[int]) -> List[int]:
    """Lines the ADR-077 import scan needs around the given lines: the whole paragraphs that contain them (its
    sentence windows stop at a paragraph break) and the \\begin and \\end lines of every proof or result environment
    that encloses or starts in what is kept (its environment matching pairs each \\begin with the next \\end)."""
    body = manuscript_checks.strip_tex_comments(text)
    source = body.split("\n")
    total = len(source)
    keep: Set[int] = set()
    for n in lines:
        if not 1 <= n <= total:
            continue
        a = b = n
        while a > 1 and source[a - 2].strip():
            a -= 1
        while b < total and source[b].strip():
            b += 1
        keep.update(range(a, b + 1))
    starts = [0] + [m.end() for m in re.finditer("\n", body)]
    envs = cited_import_ledger._environments(body)
    changed = True
    while changed:
        changed = False
        for start, end, _ in envs:
            first, last = bisect.bisect_right(starts, start), bisect.bisect_right(starts, end)
            touches = any(first <= n <= last for n in keep)
            if touches and not {first, last} <= keep:
                keep.update((first, last))
                changed = True
    return sorted(keep)


def imports_at(files: Dict[str, str], locations: dict) -> List[Tuple[str, str, int, str, str, str]]:
    """ADR-077 import obligations at a defect location: (kind, file, line, key, locator, environment)."""
    found = cited_import_ledger.scan(files)
    return sorted((i.kind, i.file, i.line, i.key, i.locator, i.environment) for i in found
                  if in_location(i.to_dict(), locations))


def blocks(text: str, lines: List[int]) -> List[List[Any]]:
    """[[first_line, [text lines]], ...] for runs of consecutive kept lines."""
    source = text.split("\n")
    out: List[List[Any]] = []
    for n in lines:
        if out and n == out[-1][0] + len(out[-1][1]):
            out[-1][1].append(source[n - 1])
        else:
            out.append([n, [source[n - 1]]])
    return out


def unblock(file_blocks: List[List[Any]]) -> str:
    """Rebuild a source with the kept lines at their original numbers and blank lines elsewhere."""
    lines: List[str] = []
    for first, chunk in file_blocks:
        lines.extend([""] * (first - 1 - len(lines)))
        lines.extend(chunk)
    return "\n".join(lines)


def excerpt_version(files: Dict[str, str], flags: List[dict], locations: Optional[dict],
                    snapshot: Optional[Set[str]], tex_lines: int) -> Dict[str, Any]:
    """The excerpt of one version: the lines flagged, the defect locations, the bibliography keys and the links."""
    wanted: Dict[str, Set[int]] = {}
    for f in flags:
        wanted.setdefault(f["file"], set()).add(f["line"])
    for name, rs in (locations or {}).items():
        for a, b in rs:
            wanted.setdefault(name, set()).update(range(a - LOCATION_TOLERANCE, b + LOCATION_TOLERANCE + 1))
    for name, text in files.items():
        if name.endswith(".tex"):
            lines = numeric_lines(text)
            if lines:
                wanted.setdefault(name, set()).update(lines)
    out_files = {}
    for name, lines in sorted(wanted.items()):
        if name not in files:
            continue
        kept = set(lines)
        if locations and name in locations and name.endswith(".tex"):
            at = [n for a, b in locations[name] for n in range(a - LOCATION_TOLERANCE, b + LOCATION_TOLERANCE + 1)]
            kept.update(import_window(files[name], at))
        out_files[name] = blocks(files[name], window(files[name], kept))
    text = "\n".join(unblock(b) for b in out_files.values())
    links = sorted({m.group(1) for m in manuscript_checks._INTERNAL.finditer(text)} & snapshot) if snapshot else []
    return {
        "tex_lines": tex_lines,
        "bibliography_keys": sorted(manuscript_checks.bibliography_keys(files)),
        "snapshot_links": links,
        "files": out_files,
    }


def excerpt_files(version: Dict[str, Any]) -> Dict[str, str]:
    """The sources of an excerpt, with the bibliography as a synthetic file of its keys."""
    files = {name: unblock(b) for name, b in version["files"].items()}
    keys = version["bibliography_keys"]
    if keys:
        files[KEYS_FILE] = "\n".join(f"@misc{{{k},}}" for k in keys) + "\n"
    return files


def replay_version(version: Dict[str, Any]) -> Dict[str, Any]:
    """Check results of one excerpt, in the shape of the full run (`flags`, `tex_lines`)."""
    files = excerpt_files(version)
    snapshot = set(version["snapshot_links"])
    flags = [f for f in check_files(files, snapshot) if f["file"] != KEYS_FILE]
    return {"flags": flags, "tex_lines": version["tex_lines"]}


def replay(dataset_items: List[dict], fixture: Dict[str, Any]) -> Dict[str, Any]:
    """Score every dataset item from its excerpt: per-item records and the benchmark summary."""
    versions = {}
    for item in dataset_items:
        entry = fixture["items"][item["id"]]
        pre = replay_version(entry["pre"])
        post = replay_version(entry["post"]) if entry.get("post") else None
        versions[item["id"]] = (pre, post)
    items = score_items(dataset_items, versions)
    return {"summary": summarize(items), "items": items}


def flag_signature(flags: List[dict]) -> List[Tuple[str, str, int, str]]:
    """Order-free, detail-free identity of a flag list (details depend on set iteration order)."""
    return sorted((f["check"], f["file"], f["line"], f["key"]) for f in flags)
