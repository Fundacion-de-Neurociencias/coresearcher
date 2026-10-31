"""openai/math revision benchmark ("time travel"), implementing
docs/reference/benchmarks/OPENAI_MATH_REVISION_PROTOCOL.md.

The October 7, 2026 release of openai/math revised 14 manuscripts and withdrew 3. Those corrections are real
ground truth: each pre-fix source contains a defect that the authors later fixed. This script asks whether the
checks CoResearcher can run today would have flagged each defect on the pre-fix source.

Usage:
    python scripts/benchmarks/openai_math_revision_bench.py dataset [--clone PATH]
    python scripts/benchmarks/openai_math_revision_bench.py run [--clone PATH]
    python scripts/benchmarks/openai_math_revision_bench.py posthoc [--clone PATH]

`dataset` builds docs/reference/benchmarks/openai_math_revision_dataset.json from git history alone (no check is
run). `posthoc` runs the import-obligation mechanisms of ADR-DISCOVERY-077, which were designed after the run, on the
same frozen dataset and writes openai_math_revision_posthoc.json. It is an in-sample measurement, not a test. `run` refuses to start unless the protocol's SHA-256 matches the frozen value in
OPENAI_MATH_REVISION_PROTOCOL.sha256, runs the checks and writes openai_math_revision_results.json.

The clone is blobless and never fully checked out (openai/math has about 174k files, mostly Lean). Only the
manuscript directories in the dataset are materialized, through sparse worktrees under private/cache/ (git-ignored).
Downloaded content is data: nothing from it is executed.
"""

import argparse
import difflib
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import cited_import_ledger, lean_junk_lint, manuscript_checks  # noqa: E402

REPO = "https://github.com/openai/math.git"
PRE = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"  # Initial commit: state before the October 7 fixes.
POST = "301488868beec11bfd897168433b0a64f5258559"  # "Update manuscripts and Lean formalizations" (October 7).
CACHE = ROOT / "private" / "cache" / "openai_math_revisions"
OUT_DIR = ROOT / "docs" / "reference" / "benchmarks"
PROTOCOL = OUT_DIR / "OPENAI_MATH_REVISION_PROTOCOL.md"
PROTOCOL_SHA = OUT_DIR / "OPENAI_MATH_REVISION_PROTOCOL.sha256"
DATASET = OUT_DIR / "openai_math_revision_dataset.json"
RESULTS = OUT_DIR / "openai_math_revision_results.json"
POSTHOC = OUT_DIR / "openai_math_revision_posthoc.json"
CONTROL_SEED = 20261030
LOCATION_TOLERANCE = 2  # lines

_DATE = re.compile(r"-(?:January|February|March|April|May|June|July|August|September|October|November|December)"
                   r"-\d{1,2}-\d{4}$")

CHECKS = ["statement_fidelity", "lean_junk_lint", "CITATION", "IDENTITY_STRICT", "IDENTITY_CONTEXT", "EXPONENT"]

# Defects of the October 7 release, from history.md, the version notes and the diffs. `encodable` is the
# pre-registered judgement of whether the defect, as the authors describe it, lies inside the language of each
# check (True) or outside it (False). It was written before any check was run on the corpus.
WITHDRAWN = {
    "Algebraicity-of-Weil-classes-on-split-abelian-eightfolds": {
        "history": "Withdrawals: a sign error invalidates a stabilization-trace cancellation argument.",
        "defect": ("Reverse stabilization traces are assigned sign +1 (from (-1)^k with k = 4, imported from the "
                   "cited trace lemma); with the opposite source orientations of the cusp branches the sign is -1, "
                   "so the signed double-point count is I(f_1) - m = -2m, not 0, and the Eliashberg-Murphy "
                   "cancellation hypothesis fails. The displayed arithmetic I(f_1)+m = 0 is consistent with the "
                   "wrong sign."),
        "type": "sign convention imported from a cited lemma",
        "locations": {"sections/03-topology.tex": [479, 492]},
    },
    "Algebraicity-of-Kuga-Satake-Correspondences-for-K3-Surfaces": {
        "history": "Withdrawals: relies on the flawed stabilization-trace construction.",
        "defect": ("Adapts the same stabilization-trace step: reverse traces of sign (-1)^l make the count "
                   "I + m(-1)^l = 0; the sign error of the Weil-eightfold paper carries over."),
        "type": "sign convention imported from a cited lemma; dependency on a withdrawn construction",
        "locations": {"manuscript.tex": [1962, 1975]},
    },
    "The-rational-Hodge-conjecture-for-products-of-K3-surfaces": {
        "history": "Withdrawals: relies on the flawed stabilization-trace construction.",
        "defect": ("Adapts the same stabilization-trace step (trace signs (-1)^{k-1}, (-1)^k; d reverse traces make "
                   "the count zero); the sign error carries over."),
        "type": "sign convention imported from a cited lemma; dependency on a withdrawn construction",
        "locations": {"manuscript/topology.tex": [502, 515]},
    },
}

_KAHLER = "Kähler minimal model programs and abundance (6 manuscripts): expanded positivity and contraction arguments " \
          "and clarified which results are used as inputs, with their required hypotheses."
_LIPSCHITZ = "Lipschitz heights and Ashkin-Teller currents (4 manuscripts): repaired crossing, boundary-attachment, " \
             "conditioning and convergence arguments."
_TAMING = "Taming and hypersymplectic deformation (2 manuscripts)."

REVISED = {
    "Gaussian-free-field-limits-of-weighted-integer-Lipschitz-heights": (_LIPSCHITZ, "proof gap (missing argument)"),
    "The-Gaussian-free-field-limit-of-integer-Lipschitz-heights-with-two-arc-boundary-data":
        (_LIPSCHITZ, "proof gap (estimates re-derived from a companion theorem)"),
    "Uniform-real-Lipschitz-surfaces-on-the-triangular-lattice": (_LIPSCHITZ, "proof gap (several repaired steps)"),
    "The-joint-scaling-limit-of-critical-Ashkin-Teller-currents":
        (_LIPSCHITZ, "incorrect argument replaced (transmission, boundary collar, excursion convergence)"),
    "Conditional-good-minimal-models-for-compact-Kahler-fourfolds": (_KAHLER, "unstated hypotheses of used inputs"),
    "Finite-ordinary-minimal-model-programs-on-compact-Kahler-fourfolds": (_KAHLER, "proof gap (contraction induction)"),
    "Log-abundance-for-compact-Kahler-spaces-under-logarithmic-Iitaka-subadditivity":
        (_KAHLER, "proof gap (induction steps)"),
    "Numerical-semiampleness-of-nef-adjoint-classes-on-compact-Kahler-manifolds":
        (_KAHLER, "unstated hypotheses of used inputs"),
    "Termination-of-generalized-canonical-flips-on-compact-Kahler-fourfolds":
        (_KAHLER, "unclear dependency on a companion paper"),
    "Termination-of-generalized-log-canonical-flips-on-compact-Kahler-fourfolds":
        (_KAHLER, "unclear dependency on companion inputs"),
    "Taming-implies-compatibility-on-four-manifolds":
        (_TAMING + " Corrected the cone-equality claim, added a strict-inclusion example.",
         "claim beyond the hypotheses of a cited theorem (cone sum equality asserted without h_J^- = b_2^+ - 1); "
         "false in general (four-torus strict inclusion)"),
    "Deforming-hypersymplectic-four-manifolds-to-hyperkahler-triples":
        (_TAMING + " Removed an unnecessary cone-comparison dependency.",
         "dependency on the incorrect cone comparison of a companion paper"),
    "Incompressible-Box-Transport-and-Finite-Computation":
        ("Incompressible Box Transport and Finite Computation: revised the torus-projection and common-clock "
         "estimates.", "effective estimates asserted without an effective proof"),
    "Exact-Birch-Swinnerton-Dyer-Formula-from-Low-Selmer-Corank":
        ("Exact Birch-Swinnerton-Dyer Formula from Low Selmer Corank: removed an obsolete introductory citation to "
         "a removed supporting manuscript.", "citation to a removed supporting manuscript"),
}

# Pre-registered encodability (see the protocol, section 5). statement_fidelity and lean_junk_lint need a Lean
# statement; none of these families had one at PRE, so they are recorded per item from CONTENTS.md, not here.
# Families of two revised manuscripts have a Lean note at PRE. What the Lean statement covers, from lean/docs:
LEAN_SCOPE = {
    "Taming-implies-compatibility-on-four-manifolds":
        "Lean note 342 formalizes only the main theorem (taming implies compatibility); the defect is in the "
        "cone corollary, which has no Lean statement",
    "Incompressible-Box-Transport-and-Finite-Computation":
        "Lean note 376 formalizes the sheet-program and halting-detection statements; the defect is in the "
        "prose proof of the projection and decay estimates, not in a formal statement",
}

ENCODABLE = {
    "Exact-Birch-Swinnerton-Dyer-Formula-from-Low-Selmer-Corank": {"CITATION"},
}


def long_path(path: Path) -> Path:
    """Windows extended-length path: manuscript paths in the sparse worktrees exceed MAX_PATH."""
    if os.name == "nt" and not str(path).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(path.resolve()))
    return path


def sh(*args, cwd=None, check=True) -> str:
    # A blobless clone fetches missing blobs on demand; retry a stalled fetch instead of hanging.
    for attempt in range(3):
        try:
            out = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                                 errors="replace", timeout=600)
            break
        except subprocess.TimeoutExpired:
            if attempt == 2:
                raise
    if check and out.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def ensure_clone(clone: Path) -> Path:
    if not (clone / ".git").exists() and not (clone / "HEAD").exists():
        clone.parent.mkdir(parents=True, exist_ok=True)
        sh("git", "-c", "core.longpaths=true", "clone", "--filter=blob:none", "--no-checkout", REPO, str(clone))
    sh("git", "config", "core.longpaths", "true", cwd=clone)
    return clone


def git_show(clone: Path, commit: str, path: str) -> str:
    return sh("git", "show", f"{commit}:{path}", cwd=clone)


def manuscript_dirs(clone: Path, commit: str) -> list:
    names = sh("git", "ls-tree", "--name-only", commit, "preprints/", cwd=clone).split()
    return sorted(n.split("/", 1)[1] for n in names)


def tree_id(clone: Path, commit: str, path: str) -> str:
    return sh("git", "rev-parse", f"{commit}:{path}", cwd=clone).strip()


def materialize(clone: Path, commit: str, dirs: list) -> Path:
    """Sparse worktree of `commit` holding only the given manuscript directories (sources, no PDFs)."""
    wt = CACHE / f"wt-{commit[:12]}"
    if not wt.exists():
        sh("git", "worktree", "add", "--no-checkout", str(wt), commit, cwd=clone)
        sh("git", "sparse-checkout", "init", "--no-cone", cwd=wt)
    patterns = [f"/preprints/{d}/**/*.{ext}" for d in dirs for ext in ("tex", "bib", "bbl", "md")]
    patterns += [f"/preprints/{d}/*.md" for d in dirs]
    proc = subprocess.run(["git", "sparse-checkout", "set", "--no-cone", "--stdin"], cwd=wt, input="\n".join(patterns),
                          capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    sh("git", "-c", "core.longpaths=true", "checkout", "-q", commit, cwd=wt)
    return wt


# ---------------------------------------------------------------- dataset


def title_of(dirname: str) -> str:
    return _DATE.sub("", dirname)


def families(contents: str) -> dict:
    """manuscript directory -> (family number, family has a Lean note)."""
    out = {}
    for block in re.split(r"(?m)^(?=\*\*\d{3}\. )", contents):
        m = re.match(r"\*\*(\d{3})\. ", block)
        if not m:
            continue
        head = block.split("\n", 1)[0]
        lean = "[Lean](lean/docs/" in head
        for d in re.findall(r"\]\(preprints/([^/)]+)/", block):
            out[d] = (m.group(1), lean)
    return out


def changed_locations(pre_root: Path, post_root: Path) -> dict:
    """Pre-version lines changed by the fix: replaced or deleted lines, and the two lines around each insertion.
    Hunks that only change a \\date line or a link to another manuscript's edition are excluded (they follow from
    the release, not from the defect)."""
    trivial = re.compile(r"\\date\{|preprints/|OAI:|^\s*year\s*=|^\s*\}?,?\s*$")
    out = {}
    for pre in sorted(pre_root.rglob("*")):
        if not pre.is_file() or pre.suffix not in (".tex", ".bib", ".bbl"):
            continue
        rel = pre.relative_to(pre_root).as_posix()
        a = pre.read_text(encoding="utf-8", errors="replace").split("\n")
        post = post_root / rel
        b = post.read_text(encoding="utf-8", errors="replace").split("\n") if post.exists() else []
        lines = set()
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            old, new = a[i1:i2], b[j1:j2]
            if all(trivial.search(x) for x in old + new):
                continue
            if tag == "insert":
                lines.update({i1, i1 + 1})  # 1-based lines around the insertion point
            else:
                lines.update(range(i1 + 1, i2 + 1))
        if lines:
            out[rel] = sorted(lines)
    return out


def ranges(lines: list) -> list:
    out = []
    for n in lines:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return out


def build_dataset(clone: Path) -> dict:
    pre_dirs, post_dirs = manuscript_dirs(clone, PRE), manuscript_dirs(clone, POST)
    head = sh("git", "rev-parse", "HEAD", cwd=clone).strip()
    head_dirs = manuscript_dirs(clone, head)
    new_editions = sorted(set(post_dirs) - set(pre_dirs))
    by_title = {}
    for d in pre_dirs:
        by_title.setdefault(title_of(d), []).append(d)
    pairs = []
    for new in new_editions:
        olds = sorted(by_title.get(title_of(new), []), key=lambda d: _date_key(d))
        if olds:
            pairs.append((olds[-1], new))
    fam_pre = families(git_show(clone, PRE, "CONTENTS.md"))
    history = git_show(clone, POST, "history.md")
    items = []
    wt_pre = materialize(clone, PRE, sorted({o for o, _ in pairs} | {d for d in pre_dirs if title_of(d) in WITHDRAWN}))
    wt_post = materialize(clone, POST, [n for _, n in pairs])
    for old, new in pairs:
        t = title_of(old)
        note = git_show(clone, POST, f"preprints/{new}/README.md")
        m = re.search(r"## Version note\s*\n+(.*?)(?:; see the \[previous version\]|\n\n|\Z)", note, re.S)
        group = "revised" if t in REVISED else "citation_update"
        item = {
            "id": t,
            "group": group,
            "family": fam_pre.get(old, (None, False))[0],
            "family_has_lean": fam_pre.get(old, (None, False))[1],
            "pre": {"commit": PRE, "dir": old, "tree": tree_id(clone, PRE, f"preprints/{old}")},
            "post": {"commit": POST, "dir": new, "tree": tree_id(clone, POST, f"preprints/{new}")},
            "version_note": m.group(1).strip() if m else None,
        }
        if group == "revised":
            hist, kind = REVISED[t]
            locs = changed_locations(long_path(wt_pre / "preprints" / old / "build"),
                                     long_path(wt_post / "preprints" / new / "build"))
            item.update({"history": hist, "defect": item["version_note"], "defect_type": kind,
                         "locations": {f: ranges(v) for f, v in locs.items()},
                         "encodable": sorted(ENCODABLE.get(t, set())), "lean_scope": LEAN_SCOPE.get(t)})
        items.append(item)
    for d in pre_dirs:
        t = title_of(d)
        if t not in WITHDRAWN:
            continue
        w = WITHDRAWN[t]
        notice = git_show(clone, POST, f"preprints/{d}/README.md")
        items.append({
            "id": t, "group": "withdrawn", "family": fam_pre.get(d, (None, False))[0],
            "family_has_lean": fam_pre.get(d, (None, False))[1],
            "pre": {"commit": PRE, "dir": d, "tree": tree_id(clone, PRE, f"preprints/{d}")}, "post": None,
            "version_note": notice.split("\n## ")[0].strip(), "history": w["history"], "defect": w["defect"],
            "defect_type": w["type"], "locations": {f: [r] for f, r in w["locations"].items()},
            "encodable": sorted(ENCODABLE.get(t, set())),
        })
    # Never-revised controls: present at PRE, no other edition at PRE, POST or HEAD, not withdrawn.
    touched = {title_of(d) for d in post_dirs + head_dirs if d not in pre_dirs} | set(WITHDRAWN)
    multi = {t for t, ds in by_title.items() if len(ds) > 1}
    never = [d for d in pre_dirs if title_of(d) not in touched and title_of(d) not in multi]
    rng = random.Random(CONTROL_SEED)
    chosen = []
    for item in sorted((i for i in items if i["group"] in ("revised", "withdrawn")), key=lambda i: i["id"]):
        same = sorted(d for d in never if fam_pre.get(d, (None,))[0] == item["family"] and d not in chosen)
        pool = same or sorted(d for d in never if d not in chosen)
        pick = rng.choice(pool)
        chosen.append(pick)
        items.append({
            "id": title_of(pick), "group": "control", "matched_to": item["id"], "same_family": bool(same),
            "family": fam_pre.get(pick, (None, False))[0], "family_has_lean": fam_pre.get(pick, (None, False))[1],
            "pre": {"commit": PRE, "dir": pick, "tree": tree_id(clone, PRE, f"preprints/{pick}")}, "post": None,
        })
    return {
        "source": {"repository": REPO, "pre_commit": PRE, "post_commit": POST, "head_at_build": head,
                   "history_md_sha256": hashlib.sha256(history.encode("utf-8")).hexdigest()},
        "control_seed": CONTROL_SEED,
        "location_tolerance": LOCATION_TOLERANCE,
        "items": items,
    }


def _date_key(d: str):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    m = re.search(r"-(\w+)-(\d{1,2})-(\d{4})$", d)
    return (int(m.group(3)), months.index(m.group(1)), int(m.group(2)))


# ---------------------------------------------------------------- run


def lean_files(clone: Path, family: str) -> list:
    """Comparator challenge files linked from the family's Lean note at PRE."""
    try:
        note = git_show(clone, PRE, f"lean/docs/{family}.md")
    except RuntimeError:
        return []
    return sorted(set(re.findall(r"\]\(\.\./(ComparatorChallenges/[^)]+\.lean)\)", note)))


def run_version(clone: Path, wt: Path, commit: str, dirname: str, snapshot: set) -> dict:
    root = long_path(wt / "preprints" / dirname / "build")
    if not root.exists():
        root = long_path(wt / "preprints" / dirname)
    flags, coverage, lines = manuscript_checks.run_all(root, snapshot)
    return {"flags": [f.to_dict() for f in flags], "coverage": coverage.__dict__, "tex_lines": lines}


def in_location(flag: dict, locations: dict) -> bool:
    for f, rs in locations.items():
        if flag["file"] != f:
            continue
        for a, b in rs:
            if a - LOCATION_TOLERANCE <= flag["line"] <= b + LOCATION_TOLERANCE:
                return True
    return False


def score(item: dict, pre: dict, post: dict | None) -> dict:
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


def protocol_frozen() -> str:
    digest = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    frozen = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    if digest != frozen:
        raise SystemExit(f"protocol changed after freezing: {digest} != {frozen}")
    return digest


def run(clone: Path) -> dict:
    digest = protocol_frozen()
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    snap_pre, snap_post = set(manuscript_dirs(clone, PRE)), set(manuscript_dirs(clone, POST))
    wt_pre = materialize(clone, PRE, sorted({i["pre"]["dir"] for i in data["items"]}))
    wt_post = materialize(clone, POST, sorted({i["post"]["dir"] for i in data["items"] if i["post"]}))
    out_items = []
    for item in data["items"]:
        pre = run_version(clone, wt_pre, PRE, item["pre"]["dir"], snap_pre)
        post = run_version(clone, wt_post, POST, item["post"]["dir"], snap_post) if item["post"] else None
        rec = {"id": item["id"], "group": item["group"], "pre": pre, "post": post}
        if post:
            post_keys = {(f["check"], f["key"]) for f in post["flags"]}
            rec["persistent"] = [f for f in pre["flags"] if (f["check"], f["key"]) in post_keys]
        if item["group"] in ("revised", "withdrawn"):
            rec["score"] = score(item, pre, post)
        if item["family_has_lean"]:
            lint = []
            for path in lean_files(clone, item["family"]):
                report = lean_junk_lint.lint(git_show(clone, PRE, f"lean/{path}"), file=path)
                lint.append({"file": path, "open": len(report.open_findings()),
                             "findings": len(report.findings)})
            rec["lean_junk_lint"] = lint
        out_items.append(rec)
        print(item["group"], item["id"][:70], rec.get("score", {}).get("verdict", ""), flush=True)
    return {"protocol_sha256": digest, "dataset_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
            "summary": summarize(out_items), "items": out_items}


def summarize(items: list) -> dict:
    out = {"defects": {}, "false_alarms": {}}
    defects = [i for i in items if "score" in i]
    for v in ("HIT", "MISS", "NOT_ENCODABLE"):
        out["defects"][v] = sorted(i["id"] for i in defects if i["score"]["verdict"] == v)
    for check in CHECKS[2:]:
        out["defects"][f"hits_{check}"] = sum(i["score"]["per_check"][check]["verdict"] == "HIT" for i in defects)

    def rate(group_items, key):
        flags = lines = 0
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


def posthoc(clone: Path) -> dict:
    """ADR-077 import obligations on the frozen dataset. In-sample: the mechanisms were designed after reading the
    defects, so this measures where obligations land and what alarm load they create, not detection power."""
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    kinds = [cited_import_ledger.CONVENTION_TRANSFER, cited_import_ledger.HYPOTHESIS_MATCH,
             cited_import_ledger.EFFECTIVE_CONSTANT]
    wt_pre = materialize(clone, PRE, sorted({i["pre"]["dir"] for i in data["items"]}))
    wt_post = materialize(clone, POST, sorted({i["post"]["dir"] for i in data["items"] if i["post"]}))

    def sources(wt: Path, dirname: str) -> tuple:
        root = long_path(wt / "preprints" / dirname / "build")
        if not root.exists():
            root = long_path(wt / "preprints" / dirname)
        files = manuscript_checks.read_sources(root)
        return files, sum(t.count("\n") + 1 for n, t in files.items() if n.endswith(".tex"))

    items, links = [], {}
    for item in data["items"]:
        files, lines = sources(wt_pre, item["pre"]["dir"])
        links[item["pre"]["dir"]] = cited_import_ledger.internal_links(files)
        imports = [i.to_dict() for i in cited_import_ledger.scan(files)]
        rec = {"id": item["id"], "group": item["group"], "tex_lines": lines,
               "counts": {k: sum(i["kind"] == k for i in imports) for k in kinds}}
        if item["group"] in ("revised", "withdrawn"):
            at = [i for i in imports if in_location(i, item["locations"])]
            loc_lines = sum(b - a + 1 + 2 * LOCATION_TOLERANCE for rs in item["locations"].values() for a, b in rs)
            rec["at_location"] = at
            rec["at_location_by_kind"] = {k: sum(i["kind"] == k for i in at) for k in kinds}
            rec["expected_chance"] = {k: round(min(1.0, rec["counts"][k] * loc_lines / max(lines, 1)), 4)
                                      for k in kinds}
        if item["post"]:
            post_files, _ = sources(wt_post, item["post"]["dir"])
            post_keys = {(i.kind, i.key, i.locator) for i in cited_import_ledger.scan(post_files)}
            rec["persistent"] = {k: sum(i["kind"] == k and (i["kind"], i["key"], i["locator"]) in post_keys
                                        for i in imports) for k in kinds}
        items.append(rec)
        print(item["group"], item["id"][:60], rec.get("at_location_by_kind", ""), flush=True)

    # Propagation: once a manuscript is known to be withdrawn or corrected, which manuscripts in the dataset rest on
    # it? Only the 74 materialized directories are scanned, not the whole collection.
    seeds = {"Algebraicity-of-Weil-classes-on-split-abelian-eightfolds-September-18-2026": "withdrawn",
             "Taming-implies-compatibility-on-four-manifolds-September-23-2026": "corrected"}
    dependents = cited_import_ledger.propagate(links, seeds)
    group_of = {i["pre"]["dir"]: i["group"] for i in data["items"]}
    propagation = {dep: {"rests_on": chain, "group": group_of.get(dep)} for dep, chain in sorted(dependents.items())}

    def load(group: str) -> dict:
        sel = [r for r in items if r["group"] == group]
        lines = sum(r["tex_lines"] for r in sel)
        return {"manuscripts": len(sel), "tex_lines": lines,
                "obligations": {k: sum(r["counts"][k] for r in sel) for k in kinds},
                "per_1000_lines": {k: round(1000 * sum(r["counts"][k] for r in sel) / max(lines, 1), 3)
                                   for k in kinds}}

    defects = [r for r in items if "at_location" in r]
    summary = {
        "defects_with_obligation_at_location": {k: sorted(r["id"] for r in defects if r["at_location_by_kind"][k])
                                                for k in kinds},
        "defects_with_any_obligation_at_location": sorted(r["id"] for r in defects if r["at_location"]),
        "propagation": propagation,
        "load": {g: load(g) for g in ("withdrawn", "revised", "citation_update", "control")},
    }
    return {"in_sample": True, "dataset_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
            "seeds": seeds, "summary": summary, "items": items}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["dataset", "run", "posthoc"])
    ap.add_argument("--clone", type=Path, default=CACHE / "clone")
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    clone = ensure_clone(args.clone)
    if args.command == "dataset":
        data = build_dataset(clone)
        DATASET.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {DATASET} ({len(data['items'])} items)")
    elif args.command == "posthoc":
        out = posthoc(clone)
        POSTHOC.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(out["summary"], indent=2))
    else:
        results = run(clone)
        RESULTS.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(results["summary"], indent=2))


if __name__ == "__main__":
    main()
