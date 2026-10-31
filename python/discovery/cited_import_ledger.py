"""
python/discovery/cited_import_ledger.py - Obligations for results imported from cited sources (ADR-DISCOVERY-077).

The openai/math revision benchmark (docs/reference/benchmarks/OPENAI_MATH_REVISION_RESULTS.md) found that the
corrected defects of that corpus do not sit in displayed algebra. They sit where a proof imports something from a
cited source:

- a sign or normalization taken from a cited lemma under a different convention (the three withdrawals);
- a cited theorem applied without one of its hypotheses (the taming cone corollary, the Kähler inputs);
- a dependency on a companion manuscript that was later corrected or withdrawn.

This module turns each such import into an obligation of the ADR-076 ledger. It proves nothing. It makes the import
visible, with its file and line, and keeps it OPEN until someone discharges it. Four kinds:

- CONVENTION_TRANSFER: a cited result is used in a passage that fixes a sign, an orientation or a normalization.
  The obligation is "the imported value is valid under this paper's conventions".
- HYPOTHESIS_MATCH: a cited result with a locator (Theorem, Corollary, Lemma, Proposition, ...) is used inside a
  proof or a result statement. With a registry entry for the cited result, each registered hypothesis is looked for
  in the citing context; a hypothesis that cannot be found makes the obligation UNMATCHED. Without an entry the
  obligation is NO_ENTRY: OPEN, nothing more is known.
- DEPENDENCY: a link to another manuscript of the collection whose status is known to be withdrawn or corrected.
- EFFECTIVE_CONSTANT: a passage that calls a bound effective, explicit or computable while leaving a constant
  unspecified (C_{...} "depending on", O(...)).

Detection is lexical and documented as such. The point is to put an OPEN obligation at the right line, not to
decide the mathematics; the alarm load this creates is measured in the revision benchmark.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from python.discovery import obligation_ledger
from python.discovery.manuscript_checks import strip_tex_comments

CONVENTION_TRANSFER = "CONVENTION_TRANSFER"
HYPOTHESIS_MATCH = "HYPOTHESIS_MATCH"
DEPENDENCY = "DEPENDENCY"
EFFECTIVE_CONSTANT = "EFFECTIVE_CONSTANT"

# Hypothesis-match outcomes.
MATCHED = "MATCHED"  # every registered hypothesis was found in the citing context (still not a proof)
UNMATCHED = "UNMATCHED"  # at least one registered hypothesis was not found
NO_ENTRY = "NO_ENTRY"  # the cited result is not in the registry

_CITE = re.compile(r"\\(?:[cC]ite[a-zA-Z]*|[a-z]*cite[a-z]*)\*?\s*(?:\[([^\]]*)\]\s*)?(?:\[([^\]]*)\]\s*)?\{([^}]*)\}")
_LOCATOR = re.compile(r"\b(Theorem|Thm|Corollary|Cor|Lemma|Lem|Proposition|Prop|Claim|Remark|Section|Sec|"
                      r"Appendix|Step|Example|Definition|Def)\b\.?~?\s*([A-Z]?[0-9][0-9.]*[a-z]?)?", re.I)
_CONVENTION = re.compile(r"\bsigns?\b|\bsigned\b|\(-1\)\^|\borient(ation|ed|ations)?\b|\bconventions?\b|"
                         r"\bnormali[sz](ation|ed|e)\b|\bsign of\b", re.I)
_EFFECTIVE = re.compile(r"\beffective(ly)?\b|\bcomputable\b|\bexplicit(ly)?\b", re.I)
_UNSPECIFIED = re.compile(r"\bC_\{[^}]*\}|\bC_[A-Za-z0-9]|\bO\(|\bdepend(s|ing)? (only )?on\b|\bsome constant\b|"
                          r"\bconverges? absolutely\b")
_PROOF_ENVS = ("proof",)
_RESULT_ENVS = ("theorem", "corollary", "lemma", "proposition", "claim")
_INTERNAL = re.compile(r"(?:preprints/|OAI:)([A-Za-z0-9][A-Za-z0-9\-]*?-(?:January|February|March|April|May|June|"
                       r"July|August|September|October|November|December)-\d{1,2}-\d{4})")


@dataclass
class Hypothesis:
    text: str  # as the cited source states it
    pattern: str  # regex that must occur in the citing context for the hypothesis to count as stated there


@dataclass
class CitedResult:
    key: str  # bibliography key or a stable identifier (author-year)
    locator: str  # e.g. "Corollary 1.1"
    statement: str
    hypotheses: List[Hypothesis] = field(default_factory=list)
    conventions: Dict[str, str] = field(default_factory=dict)  # e.g. {"double-point sign": "..."}


@dataclass
class Import:
    kind: str
    file: str
    line: int
    key: str  # cited key, internal manuscript, or the effective phrase
    locator: str
    context: str  # the passage (truncated) that triggered the obligation
    environment: str  # proof | theorem | ... | text
    outcome: str = ""  # MATCHED / UNMATCHED / NO_ENTRY for HYPOTHESIS_MATCH; status for DEPENDENCY
    missing: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _environments(body: str) -> List[Tuple[int, int, str]]:
    """(start, end, name) of proof and result environments (outermost match per begin)."""
    out = []
    names = "|".join(re.escape(n) + r"\*?" for n in _PROOF_ENVS + _RESULT_ENVS)
    for m in re.finditer(r"\\begin\{(" + names + r")\}", body):
        name = m.group(1).rstrip("*")
        end = body.find("\\end{" + m.group(1) + "}", m.end())
        if end != -1:
            out.append((m.start(), end, name))
    return out


def _enclosing(envs: Sequence[Tuple[int, int, str]], offset: int) -> Tuple[str, int, int]:
    best = ("text", 0, 0)
    for start, end, name in envs:
        if start <= offset <= end and (best[0] == "text" or start >= best[1]):
            best = (name, start, end)
    return best


_SENTENCE_END = re.compile(r"(?<=[.;])\s+(?=[A-Z\\$])|\n\s*\n")


def _window(body: str, offset: int, after: int = 2) -> str:
    """The sentence containing offset and the `after` following sentences."""
    start = 0
    for m in _SENTENCE_END.finditer(body, 0, offset):
        start = m.end()
    end = offset
    for _ in range(after + 1):
        m = _SENTENCE_END.search(body, end + 1)
        if not m:
            end = len(body)
            break
        end = m.start()
    return body[start:end]


def _flat(text: str, limit: int = 400) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _registry_lookup(registry: Dict[str, Sequence[CitedResult]], key: str, locator: str) -> Optional[CitedResult]:
    entries = registry.get(key, ())
    norm = re.sub(r"[\s~.]", "", locator).lower()
    for entry in entries:
        if re.sub(r"[\s~.]", "", entry.locator).lower() in norm:
            return entry
    return None


def scan(files: Dict[str, str], registry: Optional[Dict[str, Sequence[CitedResult]]] = None,
         manuscript_status: Optional[Dict[str, str]] = None) -> List[Import]:
    """All import obligations in a manuscript's sources.

    registry: cited results with hypotheses, by bibliography key.
    manuscript_status: status of other collection manuscripts ("withdrawn", "corrected", ...) by directory name;
      a link to a manuscript with a status yields a DEPENDENCY obligation.
    """
    registry = registry or {}
    manuscript_status = manuscript_status or {}
    found: List[Import] = []
    for name, text in sorted(files.items()):
        if name.endswith(".tex"):
            body = strip_tex_comments(text)
            envs = _environments(body)
            for m in _CITE.finditer(body):
                locator = " ".join(x for x in (m.group(1), m.group(2)) if x) or ""
                keys = [k.strip() for k in m.group(3).split(",") if k.strip()]
                env, env_start, env_end = _enclosing(envs, m.start())
                window = _window(body, m.start())
                line = _line_of(body, m.start())
                for key in keys:
                    if _CONVENTION.search(window) and (env == "proof" or _LOCATOR.search(locator)):
                        found.append(Import(CONVENTION_TRANSFER, name, line, key, locator, _flat(window), env))
                    if _LOCATOR.search(locator) and env != "text":
                        context = body[env_start:env_end]
                        if env == "proof":
                            # The statement being proved precedes its proof.
                            prev = [e for e in envs if e[1] <= env_start and e[2] in _RESULT_ENVS]
                            if prev:
                                context = body[prev[-1][0]:prev[-1][1]] + "\n" + context
                        entry = _registry_lookup(registry, key, locator)
                        if entry is None:
                            outcome, missing = NO_ENTRY, []
                        else:
                            missing = [h.text for h in entry.hypotheses if not re.search(h.pattern, context, re.I | re.S)]
                            outcome = UNMATCHED if missing else MATCHED
                        found.append(Import(HYPOTHESIS_MATCH, name, line, key, locator, _flat(window), env,
                                            outcome, missing))
            for m in _EFFECTIVE.finditer(body):
                window = _window(body, m.start(), after=3)
                if _UNSPECIFIED.search(window):
                    env, _, _ = _enclosing(envs, m.start())
                    found.append(Import(EFFECTIVE_CONSTANT, name, _line_of(body, m.start()), m.group(0).lower(), "",
                                        _flat(window), env))
        for m in _INTERNAL.finditer(text):
            status = manuscript_status.get(m.group(1))
            if status:
                found.append(Import(DEPENDENCY, name, _line_of(text, m.start()), m.group(1), "", _flat(text[
                    max(0, m.start() - 200):m.end() + 50]), "bibliography" if name.endswith(".bib") else "text",
                    status))
    return _dedupe(found)


def _dedupe(items: Iterable[Import]) -> List[Import]:
    seen: Set[Tuple] = set()
    out = []
    for i in items:
        k = (i.kind, i.file, i.line, i.key)
        if k not in seen:
            seen.add(k)
            out.append(i)
    return out


def internal_links(files: Dict[str, str]) -> Set[str]:
    """Collection manuscripts a manuscript links to."""
    return {m.group(1) for text in files.values() for m in _INTERNAL.finditer(text)}


def propagate(links: Dict[str, Set[str]], seeds: Dict[str, str]) -> Dict[str, List[str]]:
    """Transitive dependents of each seed manuscript. links: manuscript -> manuscripts it links to.
    Returns dependent -> chain of seeds it rests on (direct or through other dependents)."""
    reverse: Dict[str, Set[str]] = {}
    for src, targets in links.items():
        for t in targets:
            reverse.setdefault(t, set()).add(src)
    out: Dict[str, List[str]] = {}
    for seed in seeds:
        stack, seen = [seed], {seed}
        while stack:
            cur = stack.pop()
            for dep in sorted(reverse.get(cur, ())):
                if dep not in seen:
                    seen.add(dep)
                    out.setdefault(dep, []).append(seed)
                    stack.append(dep)
    return out


def to_claim(claim_id: str, statement: str, imports: Sequence[Import]) -> obligation_ledger.Claim:
    """Ledger view: every import is an OPEN obligation of the claim (UNMATCHED ones say what is missing).
    No import is discharged here; discharging is a reviewer's or a checker's act (ADR-076)."""
    claim = obligation_ledger.Claim(claim_id, statement, "manuscript")
    for n, imp in enumerate(imports, 1):
        detail = f"{imp.kind} {imp.key} {imp.locator}".strip()
        if imp.missing:
            detail += f"; hypotheses not found in context: {'; '.join(imp.missing)}"
        claim.obligations.append(obligation_ledger.Obligation(
            id=f"I{n}", statement=detail, source=f"{imp.file}:{imp.line}", kind="import"))
    return claim
