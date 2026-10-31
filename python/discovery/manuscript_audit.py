"""
python/discovery/manuscript_audit.py - Manuscript audit as a service (ADR-DISCOVERY-082, on ADR-077, ADR-076, ADR-068).

The time-travel benchmark (ADR-077) found that the real corrected defects of a manuscript corpus sit at its seams
(methodology M6): imported sign conventions, hypotheses of cited theorems, dependencies on companion manuscripts,
citations that resolve to nothing. This service runs the two ADR-077 mechanisms on the LaTeX sources of one
manuscript and returns one sealed report with the status, relays and provenance of ADR-068, so the API
(`POST /api/manuscripts/audit`) and the two-phase CLI (`coresearcher formal manuscript`, then `formal analyze`)
share one computation:

- the citation gate: every citation key resolves to a bibliography entry, and every link to a collection
  manuscript resolves to one that exists (PASS, FAIL, or NO_BIBLIOGRAPHY when there is nothing to check against);
- import obligations: every import from a cited source as an OPEN obligation of the ADR-076 ledger, with its file
  and line (CONVENTION_TRANSFER, HYPOTHESIS_MATCH against an optional registry of cited results, DEPENDENCY on a
  manuscript with a known status, EFFECTIVE_CONSTANT).

Non-verdicts (M8): when the sources have no bibliography the gate cannot judge, and the report says UNDECIDED rather
than PASS. Obligations are never discharged here; a manuscript with OPEN imports is not reported as verified.

Registry hypotheses are given as literal phrases, never as regular expressions: the registry may come from a caller,
and a caller's pattern must not be able to stall the server.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional

from python.discovery import cited_import_ledger as cil
from python.discovery import formal_provenance, formal_status, formal_thresholds, formal_trust, manuscript_checks
from python.discovery.formal_hypothesis import FormalHypothesisError
from python.discovery.formal_status import FormalStatus

SCHEMA = "coresearcher.manuscript_audit/v1"
SOURCE_SUFFIXES = (".tex", ".bib", ".bbl")
MAX_FILES = 400
MAX_TOTAL_CHARS = 6_000_000
MAX_PHRASE_CHARS = 200

GATE_PASS = "PASS"
GATE_FAIL = "FAIL"
GATE_NO_BIBLIOGRAPHY = "NO_BIBLIOGRAPHY"


def _validate_files(files: Any) -> Dict[str, str]:
    if not isinstance(files, dict) or not files:
        raise FormalHypothesisError("'files' must be a non-empty object {path: text}.")
    if len(files) > MAX_FILES:
        raise FormalHypothesisError(f"At most {MAX_FILES} source files.")
    total = 0
    out = {}
    for name, text in files.items():
        if not isinstance(name, str) or not name.endswith(SOURCE_SUFFIXES):
            raise FormalHypothesisError(f"Source file names must end in {', '.join(SOURCE_SUFFIXES)}: {name!r}.")
        if not isinstance(text, str):
            raise FormalHypothesisError(f"The content of {name!r} must be a string.")
        total += len(text)
        out[name.replace("\\", "/")] = text
    if total > MAX_TOTAL_CHARS:
        raise FormalHypothesisError(f"The sources exceed {MAX_TOTAL_CHARS} characters.")
    if not any(n.endswith(".tex") for n in out):
        raise FormalHypothesisError("At least one .tex file is needed.")
    return out


def registry_from_list(entries: Any) -> Dict[str, List[cil.CitedResult]]:
    """Cited results from their JSON form: [{key, locator, statement, hypotheses: [{text, phrases}], conventions}].

    A hypothesis counts as stated in the citing context when any of its phrases occurs there (case-insensitive)."""
    if entries is None:
        return {}
    if not isinstance(entries, list):
        raise FormalHypothesisError("'registry' must be a list of cited results.")
    registry: Dict[str, List[cil.CitedResult]] = {}
    for e in entries:
        if not isinstance(e, dict) or not all(isinstance(e.get(k), str) and e[k].strip() for k in ("key", "locator")):
            raise FormalHypothesisError("Each cited result needs non-empty string 'key' and 'locator'.")
        hypotheses = []
        for h in e.get("hypotheses") or []:
            phrases = h.get("phrases") if isinstance(h, dict) else None
            if not (isinstance(h.get("text"), str) and isinstance(phrases, list) and phrases):
                raise FormalHypothesisError("Each hypothesis needs a string 'text' and a non-empty list 'phrases'.")
            if not all(isinstance(p, str) and p.strip() and len(p) <= MAX_PHRASE_CHARS for p in phrases):
                raise FormalHypothesisError(f"Phrases must be non-empty strings of at most {MAX_PHRASE_CHARS} chars.")
            pattern = "|".join(re.escape(p) for p in phrases)
            hypotheses.append(cil.Hypothesis(h["text"], pattern))
        conventions = e.get("conventions") or {}
        if not isinstance(conventions, dict):
            raise FormalHypothesisError("'conventions' must be an object.")
        registry.setdefault(e["key"], []).append(
            cil.CitedResult(e["key"], e["locator"], str(e.get("statement") or ""), hypotheses,
                            {str(k): str(v) for k, v in conventions.items()})
        )
    return registry


def _validate_status(raw: Any) -> Dict[str, str]:
    if raw is None:
        return {}
    if not isinstance(raw, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in raw.items()):
        raise FormalHypothesisError("'manuscript_status' must be an object {manuscript: status}.")
    return dict(raw)


def _validate_collection(raw: Any) -> Optional[set]:
    if raw is None:
        return None
    if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
        raise FormalHypothesisError("'collection' must be a list of manuscript names.")
    return set(raw)


def _relay_codes(*codes: str) -> List[str]:
    out = list(codes)
    if any(src != "default" for src in formal_thresholds.active().sources().values()):
        out.append("THRESHOLDS_OVERRIDDEN")
    return out


def audit(
    files: Dict[str, str],
    registry: Optional[List[Dict[str, Any]]] = None,
    manuscript_status: Optional[Dict[str, str]] = None,
    collection: Optional[List[str]] = None,
    claim: str = "",
) -> Dict[str, Any]:
    """The sealed manuscript audit report. Raises FormalHypothesisError for malformed input."""
    sources = _validate_files(files)
    reg = registry_from_list(registry)
    status_map = _validate_status(manuscript_status)
    snapshot = _validate_collection(collection)

    coverage = manuscript_checks.Coverage()
    unresolved = manuscript_checks.check_citations(sources, snapshot, coverage)
    if not coverage.bibliography_entries and not (snapshot is not None and coverage.internal_links):
        gate = GATE_NO_BIBLIOGRAPHY
    else:
        gate = GATE_FAIL if unresolved else GATE_PASS
    imports = cil.scan(sources, registry=reg, manuscript_status=status_map)
    imports.sort(key=lambda i: (i.file, i.line, i.kind, i.key))
    ledger = cil.to_claim("manuscript", claim or "the manuscript's claims", imports)
    kinds = [cil.CONVENTION_TRANSFER, cil.HYPOTHESIS_MATCH, cil.DEPENDENCY, cil.EFFECTIVE_CONSTANT]
    body = {
        "schema": SCHEMA,
        "files": [
            {"path": n, "sha256": hashlib.sha256(t.encode("utf-8")).hexdigest()} for n, t in sorted(sources.items())
        ],
        "source_lines": sum(t.count("\n") + 1 for n, t in sources.items() if n.endswith(".tex")),
        "citation_gate": {
            "status": gate,
            "citations": coverage.citations,
            "bibliography_entries": coverage.bibliography_entries,
            "internal_links": coverage.internal_links,
            "unresolved": [f.to_dict() for f in unresolved],
        },
        "imports": [i.to_dict() for i in imports],
        "import_counts": {k: sum(i.kind == k for i in imports) for k in kinds},
        "hypothesis_outcomes": {
            o: sum(i.kind == cil.HYPOTHESIS_MATCH and i.outcome == o for i in imports)
            for o in (cil.MATCHED, cil.UNMATCHED, cil.NO_ENTRY)
        },
        "ledger_status": ledger.status.value,
        "open_obligations": len(ledger.obligations),
    }
    codes = ["IMPORTS_ARE_LEXICAL"]
    if imports:
        codes.append("IMPORT_OBLIGATIONS_OPEN")
    if gate == GATE_FAIL:
        codes.append("CITATIONS_UNRESOLVED")
    undecided = gate == GATE_NO_BIBLIOGRAPHY
    inputs = {
        "files": sources,
        "registry": registry or [],
        "manuscript_status": status_map,
        "collection": sorted(snapshot) if snapshot is not None else None,
        "claim": claim,
    }
    return {
        **body,
        "formal_status": (FormalStatus.UNDECIDED if undecided else FormalStatus.DECIDED).value,
        "undecided_reasons": ["No bibliography in the sources: the citation gate cannot judge."] if undecided else [],
        "mandatory_relays": formal_status.relays(_relay_codes(*codes)),
        "provenance": formal_provenance.build("manuscript_audit", inputs, body, None),
    }


def claim_trust(report: Dict[str, Any], claim: str = "") -> Dict[str, Any]:
    """Trust-ladder view (ADR-080) of the manuscript's claim: prose has no pinned formal statement, so it stays
    CLAIMED; the audit never lifts it. A view beside the report, not part of it, so digests do not depend on it."""
    assessment = formal_trust.for_response(
        {"input_kind": "manuscript_audit", "claim": claim}, {"reports": {"manuscript_audit": report}}
    )[0]
    return {
        "schema": formal_trust.SCHEMA,
        "claim_trust": [assessment],
        "mandatory_relays": formal_trust.relays([assessment]),
    }
