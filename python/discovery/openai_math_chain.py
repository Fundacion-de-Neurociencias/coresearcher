"""
python/discovery/openai_math_chain.py - The openai/math time-travel benchmark re-run with the full verification
chain (docs/reference/benchmarks/OPENAI_MATH_CHAIN_PROTOCOL.md).

The first run (ADR-DISCOVERY-077) measured the manuscript checks that existed on 2026-10-30. Blocks A-E of
docs/architecture/VERIFICATION_METHODOLOGY.md added the manuscript audit as a service (ADR-082), the cited-results
registry (ADR-083), the obligation ledger and the composed 8-step chain (ADR-085). This module holds what the full
run (scripts/benchmarks/openai_math_revision_bench.py, commands `chain-select` and `chain`) and the offline
regression replay (ADR-084) share:

- which cited results a manuscript uses: a result is a source, identified by its normalized bibliography title, plus
  a numbered Theorem, Lemma, Corollary, Proposition, Claim or Definition named in the citation's locator;
- every occurrence of a registered result in a manuscript's sources (the ADR-077 import scan);
- the chain request for one occurrence, built from the blind citing-context encoding;
- the scoring: HIT, MISS or NOT_ENCODABLE per defect, and the alarm load off the defect locations.

Nothing here reads the defects' descriptions. The selection of results uses only the defect locations of the frozen
dataset; the registry entries and the citing contexts are inputs written blind by the procedure of the protocol.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from python.discovery import cited_import_ledger as cil
from python.discovery.openai_math_time_travel import LOCATION_TOLERANCE, in_location

RESULT_KINDS = ("Theorem", "Lemma", "Corollary", "Proposition", "Claim", "Definition")
_RESULT = re.compile(r"\b(Theorem|Lemma|Corollary|Proposition|Claim|Definition)s?\.?~?\s*"
                     r"((?:\d[\w.]*\w|\d)(?:\s*(?:,|and|,\s*and)~?\s*(?:\d[\w.]*\w|\d))*)", re.I)
_NUMBER = re.compile(r"\d[\w.]*\w|\d")
IMPORT_KINDS = (cil.CONVENTION_TRANSFER, cil.HYPOTHESIS_MATCH)
PLACEHOLDER = "cited_use"  # The chain needs one variable; a context that declares none gets this one.

# New checks of this run. REGISTRY_AUDIT: the ADR-082 manuscript audit with the registry (hypotheses as literal
# phrases). CHAIN_SEAMS: the seams step (ADR-083 cite_check) of the ADR-085 chain on each occurrence.
CHAIN_CHECKS = ["REGISTRY_AUDIT", "CHAIN_SEAMS"]


def normalize_title(title: str) -> str:
    text = re.sub(r"\\[a-zA-Z]+|[{}\"$]", "", title.lower())
    return re.sub(r"[^a-z0-9]", "", text)[:60]


def bibliography_titles(files: Dict[str, str]) -> Dict[str, Tuple[str, str]]:
    """key -> (normalized title, raw bibliography entry) from .bib entries and \\bibitem items."""
    out: Dict[str, Tuple[str, str]] = {}
    for _, text in sorted(files.items()):
        for m in re.finditer(r"@\w+\{([^,\s]+),(.*?)\n\}", text, re.S):
            tm = re.search(r"\btitle\s*=\s*[{\"](.*?)[}\"],?\s*\n", m.group(2), re.S)
            if tm:
                out.setdefault(m.group(1), (normalize_title(tm.group(1)), m.group(0)))
        for m in re.finditer(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}(.*?)(?=\\bibitem|\\end\{thebibliography\}|$)",
                             text, re.S):
            body = m.group(2)
            tm = re.search(r"\\emph\{(.*?)\}", body, re.S) or re.search(r"\\newblock\s*(.*?)\n", body, re.S)
            if tm:
                out.setdefault(m.group(1), (normalize_title(tm.group(1)), m.group(0)[:1500]))
    return out


def results_in(locator: str) -> List[str]:
    """Numbered results named by a locator: 'Lemma~3.2 and proof of Lemma~3.4' -> ['Lemma 3.2', 'Lemma 3.4']."""
    out: List[str] = []
    for m in _RESULT.finditer(locator or ""):
        kind = m.group(1).capitalize()
        for num in _NUMBER.findall(m.group(2)):
            ref = f"{kind} {num.rstrip('.')}"
            if ref not in out:
                out.append(ref)
    return out


def result_id(title: str, ref: str) -> str:
    return f"{title}|{ref}"


def occurrences(files: Dict[str, str], imports: Optional[Sequence[cil.Import]] = None) -> List[Dict[str, Any]]:
    """Every use of a numbered cited result: one record per (import site, result). Imports of the two kinds that
    name a cited result (CONVENTION_TRANSFER, HYPOTHESIS_MATCH) at the same site are one occurrence."""
    titles = bibliography_titles(files)
    imports = cil.scan(files) if imports is None else imports
    seen: Dict[Tuple[str, int, str, str], Dict[str, Any]] = {}
    for imp in imports:
        if imp.kind not in IMPORT_KINDS or imp.key not in titles:
            continue
        for ref in results_in(imp.locator):
            k = (imp.file, imp.line, imp.key, ref)
            rec = seen.setdefault(k, {"file": imp.file, "line": imp.line, "key": imp.key, "locator": imp.locator,
                                      "ref": ref, "result": result_id(titles[imp.key][0], ref), "kinds": []})
            rec["kinds"] = sorted(set(rec["kinds"]) | {imp.kind})
    return sorted(seen.values(), key=lambda r: (r["file"], r["line"], r["key"], r["ref"]))


def passage(text: str, line: int, before: int = 40, after: int = 15) -> str:
    lines = text.splitlines()
    lo, hi = max(0, line - 1 - before), min(len(lines), line + after)
    return "\n".join(f"{n + 1:5d}  {lines[n]}" for n in range(lo, hi))


# ---------------------------------------------------------------------------
# Registry entries and chain requests
# ---------------------------------------------------------------------------


def registry_entries(written: Iterable[Dict[str, Any]], keys_of: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """ADR-083 entries from the blind writers' records: one entry per result, plus one copy per bibliography key that
    the manuscripts use for it (the manuscript audit matches entries by key and locator). UNAVAILABLE records give
    no entry."""
    out = []
    for w in written:
        if w.get("status") != "WRITTEN":
            continue
        base = {k: w["entry"][k] for k in ("statement", "hypotheses", "conventions") if k in w["entry"]}
        base.update(source=w["entry"].get("source") or w["source"], locator=w["ref"], kind="result")
        out.append(dict(base, id=w["entry_id"]))
        for n, key in enumerate(sorted(keys_of.get(w["result"], [])), 1):
            out.append(dict(base, id=f"{w['entry_id']}.k{n}", key=key))
    return out


def chain_request(occ_context: Dict[str, Any], entry_id: str, citing_text: str) -> Dict[str, Any]:
    """The ADR-085 chain request for one occurrence. The citing context is the hypothesis: its declared variables and
    the assumptions the passage states; the conventions travel with the citation. A context that declares no variable
    gets the placeholder variable, which constrains nothing (the chain needs one variable to freeze and evaluate)."""
    variables = list(occ_context.get("variables") or [])
    claims = ["true"]
    if not variables:
        variables = [{"name": PLACEHOLDER, "domain": [1]}]
        claims = [f"{PLACEHOLDER} == 1"]
    return {
        "hypothesis": {
            "hypothesis_id": "CITING-CONTEXT",
            "statement": citing_text,
            "variables": variables,
            "claims": claims,
            "assumptions": list(occ_context.get("assumptions") or []),
        },
        "citations": [{"entry_id": entry_id, "conventions": dict(occ_context.get("conventions") or {}),
                       "source": f"{occ_context.get('id', '')}"}],
        "author": "openai-math-chain-benchmark",
        "label": f"citing context {occ_context.get('id', '')}",
    }


def chain_record(result: Dict[str, Any]) -> Dict[str, Any]:
    """The part of a chain result the benchmark scores and keeps."""
    cites = ((result.get("response") or {}).get("reports") or {}).get("citations") or []
    cite = cites[0] if cites else {}
    return {
        "formal_status": result["formal_status"],
        "steps": [[s["name"], s["state"], s["outcome"]] for s in result["steps"]],
        "seams_outcome": cite.get("outcome"),
        "findings": cite.get("findings", []),
        "open": cite.get("open", []),
        "hypotheses": [[h["text"], h["outcome"]] for h in cite.get("hypotheses", [])],
        "conventions": [[c["tag"], c["outcome"]] for c in cite.get("conventions", [])],
        "ledger_rollup": (result.get("obligation_ledger") or {}).get("rollup", {}).get("status"),
        "trust_rung": result.get("trust_rung"),
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def flag_of(occ: Dict[str, Any], check: str) -> Optional[Tuple]:
    """The flag an occurrence raises under a check, as a key comparable across versions, or None."""
    if check == "REGISTRY_AUDIT":
        if occ.get("audit_outcome") == cil.UNMATCHED:
            return (check, occ["result"], tuple(sorted(occ.get("audit_missing") or [])))
        return None
    chain = occ.get("chain") or {}
    if chain.get("seams_outcome") == "FINDINGS":
        return (check, occ["result"], tuple(sorted(chain.get("findings") or [])))
    return None


def score_defect(item: Dict[str, Any], occs: List[Dict[str, Any]], encodable: Sequence[str],
                 pre_lines: int) -> Dict[str, Any]:
    """HIT: a flag at a defect location of the pre-fix source whose key the corrected source does not carry (for a
    withdrawal, the flag at the location suffices). MISS: no HIT and encodable. NOT_ENCODABLE otherwise."""
    pre = [o for o in occs if o["item"] == item["id"] and o["version"] == "pre"]
    post = [o for o in occs if o["item"] == item["id"] and o["version"] == "post"]
    loc_lines = sum(b - a + 1 + 2 * LOCATION_TOLERANCE for rs in item["locations"].values() for a, b in rs)
    per_check = {}
    for check in CHAIN_CHECKS:
        post_keys = {flag_of(o, check) for o in post} - {None}
        at_loc = [o for o in pre if in_location(o, item["locations"]) and flag_of(o, check)]
        resolved = [o for o in at_loc if flag_of(o, check) not in post_keys]
        n_flags = sum(flag_of(o, check) is not None for o in pre)
        verdict = "HIT" if resolved else "MISS" if check in encodable else "NOT_ENCODABLE"
        per_check[check] = {
            "verdict": verdict,
            "occurrences_at_location": sum(in_location(o, item["locations"]) for o in pre),
            "flags_at_location": len(at_loc),
            "resolved_at_location": [o["occ"] for o in resolved],
            "expected_chance_hits": round(min(1.0, n_flags * loc_lines / max(pre_lines, 1)), 4),
        }
    verdicts = [v["verdict"] for v in per_check.values()]
    overall = "HIT" if "HIT" in verdicts else "MISS" if "MISS" in verdicts else "NOT_ENCODABLE"
    return {"verdict": overall, "per_check": per_check}


def alarm_load(occs: List[Dict[str, Any]], items: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Flags away from any defect location: on pre-fix sources off the location, persistent on corrected sources,
    on citation-update pairs and on never-revised controls. Every flag is an unconfirmed alarm."""
    def bucket(o: Dict[str, Any]) -> Optional[str]:
        item = items[o["item"]]
        group = item["group"]
        if group in ("revised", "withdrawn") and o["version"] == "pre":
            return None if in_location(o, item["locations"]) else "defect_manuscripts_off_location"
        if group == "revised":
            return "corrected"
        if group == "citation_update":
            return f"citation_update_{o['version']}"
        return "never_revised_controls" if group == "control" else None

    out: Dict[str, Any] = {}
    for check in CHAIN_CHECKS:
        rows: Dict[str, Dict[str, Any]] = {}
        for o in occs:
            b = bucket(o)
            if b is None:
                continue
            row = rows.setdefault(b, {"occurrences": 0, "flags": 0, "manuscripts_with_flag": set()})
            row["occurrences"] += 1
            if flag_of(o, check):
                row["flags"] += 1
                row["manuscripts_with_flag"].add(o["item"])
        for b, row in rows.items():
            row["manuscripts_with_flag"] = len(row["manuscripts_with_flag"])
        out[check] = dict(sorted(rows.items()))
    return out


__all__ = ["normalize_title", "bibliography_titles", "results_in", "occurrences", "passage", "registry_entries",
           "chain_request", "chain_record", "flag_of", "score_defect", "alarm_load", "CHAIN_CHECKS", "RESULT_KINDS"]
