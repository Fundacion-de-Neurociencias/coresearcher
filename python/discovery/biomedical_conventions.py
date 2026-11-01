"""
python/discovery/biomedical_conventions.py - A controlled vocabulary of biomedical conventions for the cited-results
registry (ADR-DISCOVERY-086, on ADR-083).

A biomarker cutoff, a scale or a reference value is a "lemma" that a hypothesis imports. It holds under the
conditions it was validated in: an assay on a platform, a sample matrix (plasma, CSF), units, a population, a
reference standard, the direction of a scale and the method that derived the cutoff. ADR-083 compared these tags by
normalized string equality. That is safe but blunt: "pg/mL" and "ng/L" are the same unit and were a MISMATCH, while
"assay" and "validated_assay" were two different tags.

This module gives each kind a fixed meaning and a canonical form:

- tag aliases (`assay` -> `validated_assay`, `population` -> `validated_population`, ...);
- units compared by unit algebra (`biomedical_units.same_unit`): the same unit is a MATCH, the same dimension at a
  different scale is a MISMATCH that names the factor, and an unreadable unit falls back to string equality;
- synonym tables for matrix, reference standard, scale direction and cutoff derivation. A value outside the table is
  compared as a normalized string and marked `in_vocabulary: false`.

Only spellings of the same thing are merged. Distinct things stay distinct: EDTA plasma is not plasma, a fixed
sensitivity of 90% is not one of 95%. When in doubt the comparison is a MISMATCH, the safe direction (ADR-083).
Scope: whether two uses share a convention. Whether a convention is clinically appropriate is never judged.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from python.discovery import biomedical_units

SCHEMA = "coresearcher.biomedical_conventions/v1"

KINDS: Dict[str, Dict[str, Any]] = {
    "validated_assay": {"description": "Assay (kit, antibody pair, method) under which a threshold or result was "
                                       "validated", "aliases": ["assay"]},
    "platform": {"description": "Analytical platform (e.g. an immunoassay analyzer, Simoa, LC-MS/MS)",
                 "aliases": ["analytical_platform", "instrument"]},
    "matrix": {"description": "Sample matrix (plasma, serum, CSF, ...)", "aliases": ["sample_matrix", "specimen"]},
    "units": {"description": "Units of the quantity, compared by unit algebra", "aliases": ["unit"]},
    "validated_population": {"description": "Population under which a threshold or result was validated",
                             "aliases": ["population"]},
    "reference_standard": {"description": "Reference standard the threshold was calibrated against",
                           "aliases": ["reference", "gold_standard"]},
    "scale_direction": {"description": "Direction of a scale: higher_is_worse or higher_is_better",
                        "aliases": ["direction"]},
    "cutoff_derivation": {"description": "Method that derived the cutoff (Youden index, fixed sensitivity, ...)",
                          "aliases": ["cutoff_method", "threshold_derivation"]},
}

# Canonical value -> spellings that mean exactly it (after normalization).
_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
    "matrix": {
        "plasma": ["plasma", "blood plasma"],
        "serum": ["serum", "blood serum"],
        "csf": ["csf", "cerebrospinal fluid", "liquor"],
        "edta plasma": ["edta plasma", "k2 edta plasma", "k2edta plasma"],
        "whole blood": ["whole blood"],
        "urine": ["urine"],
        "saliva": ["saliva"],
    },
    "reference_standard": {
        "amyloid pet": ["amyloid pet", "abeta pet", "aβ pet", "amyloid-beta pet", "amyloid β pet"],
        "tau pet": ["tau pet"],
        "csf abeta42/40": ["csf abeta42/40", "csf aβ42/40", "csf ab42/40", "csf abeta42/abeta40", "csf aβ42/aβ40"],
        "neuropathology": ["neuropathology", "autopsy", "post mortem neuropathology", "postmortem neuropathology"],
    },
    "scale_direction": {
        "higher_is_worse": ["higher is worse", "higher worse", "higher_is_worse", "increasing is worse",
                            "higher values are worse", "lower is better"],
        "higher_is_better": ["higher is better", "higher better", "higher_is_better", "increasing is better",
                             "higher values are better", "lower is worse"],
    },
    "cutoff_derivation": {
        "youden": ["youden", "youden index", "maximal youden index", "max youden"],
        "gaussian mixture model": ["gaussian mixture model", "gmm", "mixture model"],
    },
}
_ALIAS = {alias: kind for kind, spec in KINDS.items() for alias in spec["aliases"]}


def _norm(value: Any) -> str:
    text = str(value).strip().lower().replace("_", " ")
    return re.sub(r"\s+", " ", text)


def canonical_tag(tag: str) -> str:
    """`assay` -> `validated_assay`; tags outside the vocabulary are kept as given."""
    key = str(tag).strip()
    return _ALIAS.get(key.lower(), key)


def canonical_tags(conventions: Optional[Dict[str, Any]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for tag, value in (conventions or {}).items():
        out.setdefault(canonical_tag(tag), str(value))
    return out


def canonical_value(kind: str, value: Any) -> Tuple[str, bool]:
    """The canonical spelling of a value and whether the vocabulary knows it."""
    norm = _norm(value)
    for canonical, spellings in _SYNONYMS.get(kind, {}).items():
        if norm in (_norm(s) for s in spellings):
            return canonical, True
    return norm, kind not in _SYNONYMS


def compare(tag: str, cited: Any, citing: Any) -> Dict[str, Any]:
    """MATCH or MISMATCH for one convention, with the canonical values and how they were compared."""
    kind = canonical_tag(tag)
    if kind == "units":
        unit = biomedical_units.same_unit(str(cited), str(citing))
        if unit["outcome"] != biomedical_units.UNREADABLE:
            outcome = "MATCH" if unit["outcome"] == biomedical_units.SAME else "MISMATCH"
            return {"outcome": outcome, "compared_by": "unit algebra", "unit": unit}
    a, known_a = canonical_value(kind, cited)
    b, known_b = canonical_value(kind, citing)
    out = {"outcome": "MATCH" if a == b else "MISMATCH", "compared_by": "canonical value" if kind in _SYNONYMS
           else "normalized string", "canonical": [a, b]}
    if kind in _SYNONYMS:
        out["in_vocabulary"] = [known_a, known_b]
    return out


def vocabulary() -> Dict[str, Any]:
    """The kinds, their aliases and the canonical values with their accepted spellings."""
    return {"schema": SCHEMA, "kinds": KINDS, "values": _SYNONYMS,
            "units": "compared by unit algebra: same unit MATCH, same dimension at another scale MISMATCH (with "
                     "the factor), unreadable units by normalized string"}


__all__ = ["KINDS", "canonical_tag", "canonical_tags", "canonical_value", "compare", "vocabulary", "SCHEMA"]
