"""
python/discovery/openai_math_coverage.py - Corpus-wide claim-vs-formal coverage map for openai/math (ADR-DISCOVERY-070).

The local smoothing case (`local_smoothing_case`) mapped one family's paper items to its Lean statements by hand. This
module does the same at corpus scale, one row per headline claim: for every result family of openai/math it reads

- the headline claims: the family summary in `CONTENTS.md`, cross-checked against `\\resultentry` in `overview.tex`
  (which also gives the discipline);
- the formal scope: the `## Scope` section and the Comparator link table of `lean/docs/NNN.md`, and the
  `status.main_results` list of `lean/formalization.yaml`;
- the Comparator statements: the theorems of `lean/ComparatorChallenges/*.lean` named in the matching `.json` config.

Each headline claim gets one of four statuses, ordered from most to least formal coverage:

- KERNEL_TARGET_EQUIVALENT: Comparator targets, alone or together, state every assertion of the claim at its strength;
- KERNEL_TARGET_WEAKER: Comparator targets state part of the claim, or all of it in a weaker form (a narrower range,
  an extra hypothesis, finite volume for infinite volume, a weaker bound);
- STATEMENT_ONLY: no Comparator target covers it, but the scope note says the Lean development states it;
- PROSE_ONLY: nothing formal covers it, or the scope note says it is not included.

A status has a basis. `mechanical` means the files alone settle it (a family with no scope note has no formal side).
`z3` means a parameter range was compared by `statement_fidelity.compare_ranges`. Every other status is a reading of
the prose against the formal text, a judgement: it is tagged `[inferred]` and carries its rationale. Comparator
statements are `sorry` stubs; that a solution module proves them is the upstream repository's claim, not checked here.

Scope: formal statement fidelity only. Nothing here judges whether a proof is correct, who deserves credit, or what an
announcement says. All corpus text is untrusted data: it is parsed, never executed or followed.
"""

from __future__ import annotations

import difflib
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from python.discovery import lean_junk_lint

SOURCE_REPOSITORY = "https://github.com/openai/math"
SOURCE_COMMIT = "4eaee87548250b2682affda7d05d947c05554bae"  # 2026-10-29, "Merge pull request #4 ... update-10-29".


class Status(str, Enum):
    KERNEL_TARGET_EQUIVALENT = "KERNEL_TARGET_EQUIVALENT"
    KERNEL_TARGET_WEAKER = "KERNEL_TARGET_WEAKER"
    STATEMENT_ONLY = "STATEMENT_ONLY"
    PROSE_ONLY = "PROSE_ONLY"


STATUS_ORDER = [s.value for s in Status]


class Basis(str, Enum):
    MECHANICAL = "mechanical"  # Settled by the files alone (no scope note, so no formal side).
    Z3 = "z3"  # A range comparison decided by statement_fidelity.
    JUDGEMENT = "judgement"  # A reading of prose against formal text; always tagged [inferred].


INFERRED = "[inferred]"


# ---------------------------------------------------------------------------
# Headline claims: CONTENTS.md and overview.tex
# ---------------------------------------------------------------------------

_ENTRY = re.compile(r"^\*\*(\d{3})\.\s+(.*?)\*\*\s*(.*)$")
_LEAN_LINK = re.compile(r"\s*\(\[Lean\]\((lean/docs/\d{3}\.md)\)\)\s*$")
_PREPRINT = re.compile(r"^&emsp;\[(.*?)\]\((preprints/[^)]+)\)")


@dataclass
class Family:
    family_id: str
    title: str
    summary: str  # Markdown summary from CONTENTS.md, Lean link removed.
    lean_doc: Optional[str]  # lean/docs/NNN.md when CONTENTS.md links one.
    preprints: List[Dict[str, str]] = field(default_factory=list)
    discipline: str = ""
    overview_summary: str = ""


def parse_contents(text: str) -> Dict[str, Family]:
    """Result families of CONTENTS.md, with their summary, Lean scope link and constituent preprints."""
    families: Dict[str, Family] = {}
    current: Optional[Family] = None
    for line in text.splitlines():
        entry = _ENTRY.match(line.strip())
        if entry:
            fid, title, summary = entry.groups()
            link = _LEAN_LINK.search(summary)
            lean_doc = link.group(1) if link else None
            if link:
                summary = summary[: link.start()].rstrip()
            current = Family(fid, title.rstrip(". ").strip(), summary.strip(), lean_doc)
            families[fid] = current
            continue
        preprint = _PREPRINT.match(line.strip())
        if preprint and current is not None:
            current.preprints.append({"title": preprint.group(1), "path": preprint.group(2)})
    return families


def _balanced_groups(text: str, start: int, count: int) -> Tuple[List[str], int]:
    """`count` consecutive {...} groups starting at `start` (whitespace between groups allowed)."""
    groups = []
    i = start
    for _ in range(count):
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "{":
            raise ValueError(f"expected '{{' at offset {i}")
        depth, j = 0, i
        while j < len(text):
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        groups.append(text[i + 1 : j])
        i = j + 1
    return groups, i


def parse_overview(tex: str) -> Dict[str, Dict[str, str]]:
    """{family id: {discipline, title, summary}} from the \\cataloguesection and \\resultentry calls of overview.tex."""
    body = tex[tex.find("\\begin{document}") :]
    out: Dict[str, Dict[str, str]] = {}
    discipline = ""
    for match in re.finditer(r"\\(cataloguesection|resultentry)(?=\{)", body):
        if match.group(1) == "cataloguesection":
            (name, _), _ = _balanced_groups(body, match.end(), 2)
            discipline = name.strip()
            continue
        (fid, title, summary, _), _ = _balanced_groups(body, match.end(), 4)
        out[fid.strip()] = {"discipline": discipline, "title": title.strip(), "summary": summary.strip()}
    return out


def _normalise(text: str) -> str:
    """Lower-case letters and digits only, for comparing the Markdown and LaTeX renderings of one summary."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"\$`?|`?\$|\\[a-zA-Z]+|[{}\\]", " ", text)
    return re.sub(r"[^a-z0-9]+", "", text.lower())


_ABBREVIATIONS = ("e.g.", "i.e.", "cf.", "resp.", "vs.", "et al.", "Thm.", "Prop.", "Cor.", "Sec.", "approx.", "St.")
_MATH = re.compile(r"\$`.*?`\$|\$[^$]*\$")


def split_claims(summary: str) -> List[str]:
    """Splits a summary into sentences, one headline claim each.

    Math spans and common abbreviations are masked first, so `$`n\\ge2.`$` or "e.g." do not end a sentence.
    """
    masks: List[str] = []

    def mask(m: re.Match) -> str:
        masks.append(m.group(0))
        return f"\x00{len(masks) - 1}\x00"

    work = _MATH.sub(mask, summary)
    for abbr in _ABBREVIATIONS:
        work = work.replace(abbr, abbr.replace(".", "\x01"))
    work = re.sub(r"\b([A-Z])\.(?=\s)", "\\1\x01", work)  # Initials.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\x00(\[<“\"])", work)
    claims = []
    for part in parts:
        part = part.replace("\x01", ".")
        part = re.sub(r"\x00(\d+)\x00", lambda m: masks[int(m.group(1))], part)
        if part.strip():
            claims.append(part.strip())
    return claims


# ---------------------------------------------------------------------------
# Formal scope: lean/docs/NNN.md, lean/formalization.yaml
# ---------------------------------------------------------------------------

_ROW_LINK = re.compile(r"\]\(\.\./ComparatorChallenges/([^)#]+\.lean)(?:#L(\d+))?\)")


@dataclass
class ScopeDoc:
    title: str
    papers: List[str]
    scope_paragraphs: List[str]
    rows: List[Dict[str, Any]]  # {label, file, line}


def parse_scope_doc(text: str) -> ScopeDoc:
    title = ""
    papers: List[str] = []
    sections: Dict[str, List[str]] = defaultdict(list)
    section = ""
    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not section:
            paper = re.match(r"^-\s*\[(.*?)\]\(", line)
            if paper:
                papers.append(paper.group(1))
            continue
        sections[section].append(line)
    paragraphs = [p.strip() for p in "\n".join(sections.get("Scope", [])).split("\n\n") if p.strip()]
    rows = []
    for line in sections.get("Comparator links", []):
        if not line.startswith("|") or line.startswith("| Result") or line.startswith("| ---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        label = cells[0] if cells else ""
        for link in _ROW_LINK.finditer(line):
            rows.append({"label": label, "file": link.group(1), "line": int(link.group(2)) if link.group(2) else None})
    return ScopeDoc(title, papers, paragraphs, rows)


def parse_formalization_yaml(text: str) -> Dict[str, Any]:
    """Sources and main results of lean/formalization.yaml (safe loader: the file is data)."""
    import yaml

    data = yaml.safe_load(text) or {}
    status = data.get("status") or {}
    return {
        "scope": status.get("scope"),
        "review": (data.get("review") or {}).get("status"),
        "sources": [s.get("id", "") for s in data.get("sources") or []],
        "main_results": list(status.get("main_results") or []),
    }


# ---------------------------------------------------------------------------
# Comparator statements: lean/ComparatorChallenges/*.lean and *.json
# ---------------------------------------------------------------------------


@dataclass
class ComparatorTarget:
    file: str  # Relative to lean/ComparatorChallenges.
    theorem: str  # Fully qualified name from the JSON config.
    line: int
    end: int
    docstring: str
    statement: str  # Declaration text up to `:=`, comments removed.
    support: str  # Definitions the statement uses (transitively), truncated.


_DOC = re.compile(r"/--(.*?)-/\s*$", re.S)


def _docstring_before(source_lines: Sequence[str], start: int) -> str:
    """The `/-- ... -/` block that ends just above line `start` (1-based), if any."""
    i = start - 2
    while i >= 0 and (not source_lines[i].strip() or source_lines[i].strip().startswith("@[")):
        i -= 1
    if i < 0 or not source_lines[i].rstrip().endswith("-/"):
        return ""
    j = i
    while j >= 0 and "/--" not in source_lines[j]:
        j -= 1
    if j < 0:
        return ""
    match = _DOC.search("\n".join(source_lines[j : i + 1]))
    return " ".join(match.group(1).split()) if match else ""


def _statement(declaration: lean_junk_lint.Declaration) -> str:
    text = declaration.text
    cut = text.find(":=")
    return " ".join((text if cut < 0 else text[:cut]).split())


def comparator_targets(lean_source: str, config: Dict[str, Any], file: str, support_chars: int = 2500) -> List[ComparatorTarget]:
    """The theorems a Comparator config names, located in its challenge file."""
    declarations = lean_junk_lint.parse_declarations(lean_source)
    lines = lean_source.splitlines()
    by_short: Dict[str, List[lean_junk_lint.Declaration]] = defaultdict(list)
    for d in declarations:
        by_short[d.name.rstrip(".").split(".")[-1]].append(d)  # `theorem t.{u}` parses as "t.".
    targets = []
    for name in config.get("theorem_names", []):
        short = name.split(".")[-1]
        candidates = [d for d in by_short.get(short, []) if d.kind in ("theorem", "lemma")]
        qualified = [d for d in candidates if name.endswith(d.name.rstrip("."))]
        decl = (qualified or candidates or [None])[0]
        if decl is None:
            targets.append(ComparatorTarget(file, name, 0, 0, "", "", ""))
            continue
        support_parts, seen, frontier = [], {decl.name}, [decl]
        while frontier:
            current = frontier.pop(0)
            for used in lean_junk_lint._uses(current, declarations):
                if used.name not in seen and used.kind != "theorem":
                    seen.add(used.name)
                    frontier.append(used)
                    support_parts.append(" ".join(used.text.split()))
        support = "\n".join(support_parts)
        if len(support) > support_chars:
            support = support[:support_chars] + " …[truncated]"
        targets.append(
            ComparatorTarget(
                file, name, decl.start, decl.end, _docstring_before(lines, decl.start), _statement(decl), support
            )
        )
    return targets


def targets_for_row(row: Dict[str, Any], targets: Sequence[ComparatorTarget]) -> List[ComparatorTarget]:
    """Targets a scope-note row points at: the one whose text holds its #L anchor, else the first one starting
    just after it (anchors often point at a docstring), else every target of the file."""
    in_file = [t for t in targets if t.file == row["file"]]
    anchor = row.get("line")
    if anchor is None or not in_file:
        return in_file
    containing = [t for t in in_file if t.line <= anchor <= t.end]
    if containing:
        return containing[:1]
    after = [t for t in in_file if anchor < t.line <= anchor + 15]
    return [min(after, key=lambda t: t.line)] if after else in_file


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------


def config_for(lean_file: str, configs: Dict[str, Any]) -> str:
    """The Comparator config of a challenge file: X.json beside X.lean, else main.json in its directory."""
    same = lean_file[: -len(".lean")] + ".json"
    if same in configs:
        return same
    directory = lean_file.rsplit("/", 1)[0] if "/" in lean_file else ""
    return f"{directory}/main.json" if directory else same


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class Corpus:
    root: Path
    families: Dict[str, Family]
    overview: Dict[str, Dict[str, str]]
    yaml: Dict[str, Any]
    scope_docs: Dict[str, ScopeDoc]  # By family id.
    targets: Dict[str, List[ComparatorTarget]]  # By Comparator .lean file.
    configs: Dict[str, Dict[str, Any]]  # By Comparator .json file.
    hashes: Dict[str, str]


def load_corpus(root: Path) -> Corpus:
    """Reads a checkout (or an extract) of openai/math. Only text files are read; nothing is executed."""
    root = Path(root)
    hashes: Dict[str, str] = {}

    def read(rel: str) -> str:
        data = (root / rel).read_bytes()
        hashes[rel] = sha256(data)
        return data.decode("utf-8")

    families = parse_contents(read("CONTENTS.md"))
    overview = parse_overview(read("overview.tex"))
    for fid, family in families.items():
        entry = overview.get(fid, {})
        family.discipline = entry.get("discipline", "")
        family.overview_summary = entry.get("summary", "")
    yaml_data = parse_formalization_yaml(read("lean/formalization.yaml"))
    scope_docs = {fid: parse_scope_doc(read(f.lean_doc)) for fid, f in families.items() if f.lean_doc}
    comparator = root / "lean" / "ComparatorChallenges"
    configs: Dict[str, Dict[str, Any]] = {}
    targets: Dict[str, List[ComparatorTarget]] = {}
    for config_path in sorted(comparator.glob("**/*.json")):
        name = config_path.relative_to(comparator).as_posix()
        configs[name] = json.loads(read(f"lean/ComparatorChallenges/{name}"))
    linked = {row["file"] for doc in scope_docs.values() for row in doc.rows}
    lean_files = {p.relative_to(comparator).as_posix() for p in comparator.glob("*.lean")} | linked
    for name in sorted(lean_files):
        if not (comparator / name).exists():
            continue
        config = configs.get(config_for(name, configs), {"theorem_names": []})
        targets[name] = comparator_targets(read(f"lean/ComparatorChallenges/{name}"), config, name)
    return Corpus(root, families, overview, yaml_data, scope_docs, targets, configs, hashes)


def family_record(corpus: Corpus, fid: str) -> Dict[str, Any]:
    """Everything parsed for one family: claims, scope, Comparator targets (the input of every classifier)."""
    family = corpus.families[fid]
    claims = [{"claim_id": f"{fid}.{i + 1}", "text": c} for i, c in enumerate(split_claims(family.summary))]
    record: Dict[str, Any] = {
        "family_id": fid,
        "title": family.title,
        "discipline": family.discipline,
        "lean_doc": family.lean_doc,
        "summary_overview_similarity": round(
            difflib.SequenceMatcher(None, _normalise(family.summary), _normalise(family.overview_summary)).ratio(), 3
        ),
        "preprints": [p["path"] for p in family.preprints],
        "claims": claims,
        "scope_paragraphs": [],
        "comparator_rows": [],
        "yaml_main_results": [],
    }
    doc = corpus.scope_docs.get(fid)
    if doc is None:
        return record
    record["scope_paragraphs"] = doc.scope_paragraphs
    files = []
    for row in doc.rows:
        matched = targets_for_row(row, corpus.targets.get(row["file"], []))
        record["comparator_rows"].append(
            {"label": row["label"], "file": row["file"], "line": row["line"], "theorems": [t.theorem for t in matched]}
        )
        files.append(row["file"])
    configs = {"ComparatorChallenges/" + config_for(f, corpus.configs) for f in files}
    record["yaml_main_results"] = [
        r.get("declaration") for r in corpus.yaml["main_results"] if str(r.get("comparator_config", "")) in configs
    ]
    record["targets"] = [
        asdict(t) for f in dict.fromkeys(files) for t in corpus.targets.get(f, [])
    ]
    return record


# ---------------------------------------------------------------------------
# Parameter ranges: automatic extraction (evidence) and hand-encoded specs (decisions)
# ---------------------------------------------------------------------------

_GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε", "lambda": "λ",
    "mu": "μ", "nu": "ν", "theta": "θ", "kappa": "κ", "sigma": "σ", "tau": "τ", "rho": "ρ", "omega": "ω",
}
_OPS = {">=": ">=", "<=": "<=", "<": "<", ">": ">", "≥": ">=", "≤": "<="}
_NUM = r"-?\d+(?:\s*/\s*\d+|\.\d+)?"
_VAR = r"(?<![\w'.\\])[A-Za-zα-ωΑ-Ω](?![\w'(])"
_TERM = rf"(?:{_NUM}|{_VAR}|∞)"
_CHAIN = re.compile(rf"({_TERM})\s*(>=|<=|≥|≤|<|>)\s*({_TERM})(?:\s*(>=|<=|≥|≤|<|>)\s*({_TERM}))?")
_FLIP = {">=": "<=", "<=": ">=", "<": ">", ">": "<"}
_ARITH = set("+-*/^·•")


def _prose_math(text: str) -> str:
    """Markdown/LaTeX summary text with relations, infinity and Greek letters in plain symbols."""
    text = html.unescape(re.sub(r"</?(?:i|b|sub|sup|em)>", "", text))
    text = text.replace("$`", " ").replace("`$", " ")
    text = re.sub(r"\\(?:geq?|geqslant)(?![a-zA-Z])", ">=", text)
    text = re.sub(r"\\(?:leq?|leqslant)(?![a-zA-Z])", "<=", text)
    text = re.sub(r"\\lt(?![a-zA-Z])", "<", text)
    text = re.sub(r"\\gt(?![a-zA-Z])", ">", text)
    text = re.sub(r"\\infty(?![a-zA-Z])", "∞", text)
    text = re.sub(r"\\(" + "|".join(_GREEK) + r")(?![a-zA-Z])", lambda m: _GREEK[m.group(1)], text)
    return text


def _atoms(text: str) -> List[Tuple[str, str, str]]:
    """(variable, op, number) atoms from chains like `2 <= p < ∞` or `n ≥ 3`; infinite bounds are dropped."""
    atoms = []
    for m in _CHAIN.finditer(text):
        before, after = text[: m.start()].rstrip()[-1:], text[m.end() :].lstrip()[:1]
        if before in _ARITH or after in _ARITH:
            continue  # `n - 1 < x` or `2 ≤ p * q`: a term of a larger expression, not a bound on a letter.
        terms = [m.group(1), m.group(3)] + ([m.group(5)] if m.group(5) else [])
        ops = [_OPS[m.group(2)]] + ([_OPS[m.group(4)]] if m.group(4) else [])
        for (left, right), op in zip(zip(terms, terms[1:]), ops):
            if "∞" in (left, right):
                continue
            left_num, right_num = bool(re.fullmatch(_NUM, left)), bool(re.fullmatch(_NUM, right))
            if left_num == right_num:
                continue
            left, right = re.sub(r"\s+", "", left), re.sub(r"\s+", "", right)
            atoms.append((right, _FLIP[op], left) if left_num else (left, op, right))
    return list(dict.fromkeys(atoms))


def prose_atoms(claim: str) -> List[Tuple[str, str, str]]:
    return _atoms(_prose_math(claim))


def lean_atoms(statement: str) -> Tuple[List[Tuple[str, str, str]], set]:
    """Atoms of a Lean statement (casts like `(n : ℝ)` unwrapped) and the one-letter variables bound as ℕ or ℤ."""
    text = re.sub(r"\(\s*(\w)\s*:\s*[ℝℚℂ]\s*\)", r"\1", statement)
    text = re.sub(r"\(\s*(\d+)\s*:\s*[ℝℚℕℤ]\s*\)", r"\1", text)
    integers = set()
    for names, _ in re.findall(r"[({]\s*([^(){}:]+?)\s*:\s*(ℕ|ℤ)\s*[)}]", text):
        integers.update(n for n in names.split() if len(n) == 1)
    integers.update(re.findall(r"∀\s*\(?\s*(\w)\s*:\s*(?:ℕ|ℤ)", text))
    return _atoms(text), integers


def auto_range_check(claim: str, statements: Sequence[str]) -> Optional[Dict[str, Any]]:
    """Compares the claim's explicit parameter bounds with the targets' bounds on the letters both mention.

    Evidence only, never a status: the extraction is syntactic, a letter can mean different things on the two
    sides, and a Lean statement can bound one letter in several sub-statements. None when nothing is comparable.
    """
    from python.discovery import statement_fidelity as sf

    paper = prose_atoms(claim)
    lean: List[Tuple[str, str, str]] = []
    integers: set = set()
    for statement in statements:
        atoms, ints = lean_atoms(statement)
        lean += atoms
        integers |= ints
    shared = sorted({a[0] for a in paper} & {a[0] for a in lean})
    if not shared:
        return None
    paper_expr = " and ".join(f"{v} {op} {num}" for v, op, num in paper if v in shared)
    lean_expr = " and ".join(f"{v} {op} {num}" for v, op, num in dict.fromkeys(lean) if v in shared)
    names = {v: f"v{i}" for i, v in enumerate(shared)}  # z3 symbols: ASCII identifiers.
    pattern = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, shared)) + r")(?!\w)")

    def ascii(expr: str) -> str:
        return pattern.sub(lambda m: names[m.group(1)], expr)

    spec = sf.RangeSpec(
        theorem="auto",
        parameters=[sf.Parameter(names[v], integer=v in integers) for v in shared],
        paper=ascii(paper_expr),
        lean=ascii(lean_expr),
        domain=" and ".join(f"{names[v]} >= 0" for v in shared if v in integers) or "True",
    )
    out: Dict[str, Any] = {"variables": shared, "integer": sorted(v for v in shared if v in integers),
                           "paper": paper_expr, "lean": lean_expr}
    try:
        result = sf.compare_ranges(spec)
    except Exception as exc:  # A transcription the predicate language rejects is reported, not raised.
        return out | {"relation": "UNDECIDED", "error": str(exc)}
    # One side bounding a letter inconsistently (two sub-statements share it) gives an empty range: no answer.
    empty = result.paper_nonempty is False or result.lean_nonempty is False
    return out | {
        "relation": "UNDECIDED" if empty else result.relation.value,
        "paper_only_witness": result.paper_only_witness,
        "lean_only_witness": result.lean_only_witness,
    }


def hand_specs() -> Dict[str, Dict[str, Any]]:
    """Hand-encoded range comparisons, keyed by claim id. `decides`: the range is the whole question."""
    from python.discovery import statement_fidelity as sf
    from python.discovery.local_smoothing_case import RANGE_SPECS

    by_name = {s.theorem: s for s in RANGE_SPECS}
    return {
        "079.1": {"spec": by_name["euclidean_local_smoothing"], "decides": True},
        "170.1": {
            "spec": sf.RangeSpec(
                theorem="SharpRamseyFive.main + SharpLogRamsey.main (sharp log exponent of r(s,t))",
                parameters=[sf.Parameter("s", integer=True)],
                paper="s >= 5",
                lean="s == 5 or 6 <= s",
                domain="s >= 0",
                paper_source="CONTENTS.md 170: for every fixed integer s >= 5, r(s,t) = t^{s-1}/(log t)^{s-2+o(1)}.",
                lean_source="SharpRamseyFive.main : SharpBounds ∧ SharpExponent (s = 5 fixed in the definitions); "
                "SharpLogRamsey.main (s : ℕ) (hs : 6 ≤ s) : MainBounds s ∧ MainLimit s",
                encoding=["The two Comparator targets together: the first fixes s = 5, the second binds s : ℕ with 6 ≤ s."],
            ),
            # Found by the automatic check, which saw only `6 ≤ s` and reported WEAKER; together the targets agree.
            "decides": True,
        },
        "215.3": {
            "spec": sf.RangeSpec(
                theorem="ClassicalON.main (O(n) exponential decay)",
                parameters=[sf.Parameter("n", integer=True), sf.Parameter("beta")],
                paper="n >= 3 and beta > 0",
                lean="3 <= n and 0 < beta",
                domain="n >= 0",
                paper_source="CONTENTS.md 215: O(n) models with n >= 3 at every positive temperature.",
                lean_source="ExponentialDecay: ∀ (n : ℕ), 3 ≤ n → ∀ (β : ℝ), 0 < β → ∃ A m : ℝ, 0 < m ∧ "
                "∀ (G : LatticeGraph) (b : G.edges → ℝ), (∀ e, 0 ≤ b e ∧ b e ≤ β) → ...",
                encoding=["n : ℕ is a z3 Int with n >= 0; β is the interaction bound (inverse temperature)."],
            ),
            # The range agrees; the gap is the finite-volume form, which a range comparison cannot see.
            "decides": False,
        },
    }


def paper_item_calibration() -> List[Dict[str, Any]]:
    """Family 079 items below headline level (Theorem 1.2, Corollary 7.1) from the ADR-070 case, re-decided by z3."""
    from python.discovery import statement_fidelity as sf
    from python.discovery.local_smoothing_case import DEVELOPMENT_SPECS

    rows = []
    for spec in DEVELOPMENT_SPECS:
        result = sf.compare_ranges(spec)
        rows.append(
            {
                "family_id": "079",
                "item": spec.theorem,
                "status": Status.STATEMENT_ONLY.value,
                "strength": result.relation.value,
                "basis": Basis.Z3.value,
                "paper": spec.paper,
                "lean": spec.lean,
                "paper_only_witness": result.paper_only_witness,
                "lean_source": spec.lean_source,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Mechanical baseline (no reading): word overlap with the scope note and the Comparator labels
# ---------------------------------------------------------------------------

_STOP = set(
    "the and for with that this from every each also over into such than then their there these those which "
    "proves prove gives give shows show result results family paper papers both only some when where under "
    "upper lower bound bounds theorem conjecture holds positive general case cases".split()
)
_EXCLUDED = re.compile(
    r"\b(not included|not formalized|outside (?:this|the)|is not part|are not part|not covered|omitted|excluded|"
    r"not treated|left out)\b",
    re.I,
)
_RESTRICTED = re.compile(
    r"\b(only|special case|restricted|finite[- ]volume|finite subgraph|partial|weaker|does not|without)\b", re.I
)


def _words(text: str) -> set:
    words = re.findall(r"[a-zà-ÿ]{4,}", _prose_math(text).lower())
    return {w[:6] for w in words if w not in _STOP}


def heuristic_status(claim: str, record: Dict[str, Any], threshold: float = 0.3) -> Tuple[str, float, float]:
    """A reading-free baseline, kept to measure how far word overlap gets: (status, target score, scope score)."""
    words = _words(claim)
    if not record.get("lean_doc") or not words:
        return Status.PROSE_ONLY.value, 0.0, 0.0

    def score(text: str) -> float:
        return len(words & _words(text)) / len(words)

    target_texts = [r["label"] for r in record["comparator_rows"]] + [
        t["docstring"] + " " + t["theorem"].replace("_", " ") for t in record.get("targets", [])
    ]
    sentences = [s for p in record["scope_paragraphs"] for s in split_claims(p)]
    best_target = max((score(t) for t in target_texts), default=0.0)
    scored = sorted(((score(s), s) for s in sentences), reverse=True)
    best_scope, best_sentence = scored[0] if scored else (0.0, "")
    if best_scope >= threshold and _EXCLUDED.search(best_sentence):
        return Status.PROSE_ONLY.value, best_target, best_scope
    if best_target >= threshold:
        restricted = any(_RESTRICTED.search(s) for sc, s in scored[:2] if sc >= threshold)
        status = Status.KERNEL_TARGET_WEAKER if restricted else Status.KERNEL_TARGET_EQUIVALENT
        return status.value, best_target, best_scope
    if best_scope >= threshold:
        return Status.STATEMENT_ONLY.value, best_target, best_scope
    return Status.PROSE_ONLY.value, best_target, best_scope


# ---------------------------------------------------------------------------
# Vacuity / junk-value lint over every Comparator statement
# ---------------------------------------------------------------------------


def lint_comparator_file(source: str, file: str, theorem_names: Sequence[str]) -> Dict[str, Any]:
    """Junk-value findings (lean_junk_lint) of the Comparator targets in one challenge file; OPEN ones listed."""
    report = lean_junk_lint.lint(source, file)
    wanted = {n.split(".")[-1] for n in theorem_names}
    mine = [f for f in report.findings if f.theorem.rstrip(".").split(".")[-1] in wanted]
    open_rows = [
        {
            "file": file,
            "theorem": f.theorem.rstrip("."),
            "kind": f.kind,
            "declaration": f.declaration,
            "line": f.line,
            "operand": f.operand,
            "explanation": f.explanation,
        }
        for f in mine
        if f.status == lean_junk_lint.Status.OPEN.value
    ]
    return {"file": file, "targets": len(wanted), "findings": len(mine), "open": open_rows}


# ---------------------------------------------------------------------------
# Merging and summarising
# ---------------------------------------------------------------------------


def classify_claim(
    record: Dict[str, Any],
    claim: Dict[str, str],
    judgement: Optional[Dict[str, Any]],
    specs: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """One dataset row: the status, its basis and the evidence behind it."""
    heuristic, target_score, scope_score = heuristic_status(claim["text"], record)
    row: Dict[str, Any] = {
        "claim_id": claim["claim_id"],
        "family_id": record["family_id"],
        "discipline": record["discipline"],
        "text": claim["text"],
        "heuristic_status": heuristic,
        "heuristic_scores": {"target": round(target_score, 3), "scope": round(scope_score, 3)},
        "auto_range_check": None,
        "range_check": None,
    }
    if not record.get("lean_doc"):
        row.update(
            status=Status.PROSE_ONLY.value, basis=Basis.MECHANICAL.value, tag=None, targets=[], strength="UNKNOWN",
            weaker_kind=None, confidence="high",
            rationale="CONTENTS.md links no Lean scope note for this family, so it has no formal side.",
        )
        return row
    if judgement is None:
        row.update(
            status=heuristic, basis="heuristic", tag=INFERRED, targets=[], strength="UNKNOWN", weaker_kind=None,
            confidence="low", rationale="No reading judgement recorded; word-overlap baseline.",
        )
    else:
        row.update(
            status=judgement["status"], basis=Basis.JUDGEMENT.value, tag=INFERRED,
            targets=list(judgement.get("targets") or []), strength=judgement.get("strength") or "UNKNOWN",
            weaker_kind=judgement.get("weaker_kind"), confidence=judgement.get("confidence") or "medium",
            rationale=judgement.get("rationale", ""),
        )
    statements = [t["statement"] for t in record.get("targets", []) if t["theorem"] in row["targets"]]
    if statements:
        row["auto_range_check"] = auto_range_check(claim["text"], statements)
    hand = specs.get(claim["claim_id"])
    if hand is not None:
        from python.discovery import statement_fidelity as sf

        result = sf.compare_ranges(hand["spec"]).to_dict()
        keys = ("theorem", "relation", "paper", "lean", "paper_only_witness", "lean_only_witness", "paper_source",
                "lean_source", "method")
        row["range_check"] = {k: result[k] for k in keys}
        if hand["decides"] and row["status"].startswith("KERNEL_TARGET"):
            equivalent = result["relation"] == "EQUIVALENT"
            row["status"] = (Status.KERNEL_TARGET_EQUIVALENT if equivalent else Status.KERNEL_TARGET_WEAKER).value
            row["basis"], row["tag"] = Basis.Z3.value, None
    return row


def summarise(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Share of headline claims at each status, overall and by discipline."""

    def table(subset: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        counts = Counter(r["status"] for r in subset)
        total = len(subset)
        return {
            "claims": total,
            "families": len({r["family_id"] for r in subset}),
            "counts": {s: counts.get(s, 0) for s in STATUS_ORDER},
            "shares": {s: round(counts.get(s, 0) / total, 3) if total else 0.0 for s in STATUS_ORDER},
        }

    by_discipline: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    families: Dict[str, List[str]] = defaultdict(list)
    for r in rows:
        by_discipline[r["discipline"]].append(r)
        families[r["family_id"]].append(r["status"])
    with_lean = [r for r in rows if r["basis"] != Basis.MECHANICAL.value]
    kernel_eq = Status.KERNEL_TARGET_EQUIVALENT.value
    agree = sum(1 for r in with_lean if r["heuristic_status"] == r["status"])
    return {
        "overall": table(rows),
        "families_with_scope_note": table(with_lean),
        "by_discipline": {d: table(v) for d, v in sorted(by_discipline.items())},
        "families": {
            "total": len(families),
            "with_scope_note": len({r["family_id"] for r in with_lean}),
            "every_claim_kernel_equivalent": sum(1 for s in families.values() if all(x == kernel_eq for x in s)),
            "some_claim_kernel_target": sum(
                1 for s in families.values() if any(x.startswith("KERNEL_TARGET") for x in s)
            ),
        },
        "basis": dict(Counter(r["basis"] for r in rows)),
        "heuristic_agreement": {
            "claims": len(with_lean),
            "agree": agree,
            "rate": round(agree / len(with_lean), 3) if with_lean else None,
        },
    }
