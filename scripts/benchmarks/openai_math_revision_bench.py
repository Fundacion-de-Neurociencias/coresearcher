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
import gzip
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
from python.discovery import openai_math_chain as omc  # noqa: E402
from python.discovery import openai_math_time_travel as tt  # noqa: E402
from python.discovery.openai_math_time_travel import (  # noqa: E402
    CHECKS, LEAN_SCOPE, LOCATION_TOLERANCE, in_location, score, summarize)

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
FIXTURE = ROOT / "benchmarks" / "regression" / "fixtures" / "openai_math_time_travel.json.gz"
CONTROL_SEED = 20261030
CHAIN_PROTOCOL = OUT_DIR / "OPENAI_MATH_CHAIN_PROTOCOL.md"
CHAIN_PROTOCOL_SHA = OUT_DIR / "OPENAI_MATH_CHAIN_PROTOCOL.sha256"
CHAIN_SELECTION = OUT_DIR / "openai_math_chain_selection.json"
CHAIN_REGISTRY = OUT_DIR / "openai_math_chain_registry.json"
CHAIN_CONTEXTS = OUT_DIR / "openai_math_chain_contexts.json"
CHAIN_RESULTS = OUT_DIR / "openai_math_chain_results.json"
CHAIN_WORK = CACHE / "chain"  # Packets for the blind writers and encoders; they quote openai/math sources.
DECOY_SEED = 20261101
DECOY_DRAW = 12
DECOYS_WANTED = 8

_DATE = re.compile(r"-(?:January|February|March|April|May|June|July|August|September|October|November|December)"
                   r"-\d{1,2}-\d{4}$")

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


def fixture(clone: Path) -> dict:
    """Excerpts for the offline regression replay (ADR-DISCOVERY-084). Each excerpt is verified to reproduce the
    full run's flags exactly; a mismatch stops the build instead of writing a fixture that would drift."""
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    snap_pre, snap_post = set(manuscript_dirs(clone, PRE)), set(manuscript_dirs(clone, POST))
    wt_pre = materialize(clone, PRE, sorted({i["pre"]["dir"] for i in data["items"]}))
    wt_post = materialize(clone, POST, sorted({i["post"]["dir"] for i in data["items"] if i["post"]}))

    def version(wt: Path, dirname: str, snapshot: set, locations) -> dict:
        root = long_path(wt / "preprints" / dirname / "build")
        if not root.exists():
            root = long_path(wt / "preprints" / dirname)
        files = manuscript_checks.read_sources(root)
        full = tt.check_files(files, snapshot)
        lines = sum(t.count("\n") + 1 for n, t in files.items() if n.endswith(".tex"))
        out = tt.excerpt_version(files, full, locations, snapshot, lines)
        replayed = tt.replay_version(out)["flags"]
        if tt.flag_signature(replayed) != tt.flag_signature(full):
            missing = set(tt.flag_signature(full)) - set(tt.flag_signature(replayed))
            extra = set(tt.flag_signature(replayed)) - set(tt.flag_signature(full))
            raise SystemExit(f"excerpt of {dirname} does not reproduce the full run: missing {sorted(missing)[:5]}, "
                             f"extra {sorted(extra)[:5]}")
        if locations:
            full_imports, excerpt_imports = tt.imports_at(files, locations), tt.imports_at(tt.excerpt_files(out), locations)
            if full_imports != excerpt_imports:
                raise SystemExit(f"excerpt of {dirname} does not reproduce the import obligations at the location: "
                                 f"{full_imports} != {excerpt_imports}")
        return out

    items = {}
    for item in data["items"]:
        locations = item.get("locations")
        items[item["id"]] = {
            "group": item["group"],
            "pre": version(wt_pre, item["pre"]["dir"], snap_pre, locations),
            "post": version(wt_post, item["post"]["dir"], snap_post, None) if item["post"] else None,
        }
        print(item["group"], item["id"][:70], flush=True)
    dataset_bytes = DATASET.read_bytes().replace(b"\r\n", b"\n")
    return {
        "source": {"repository": REPO, "license": "Apache-2.0", "pre_commit": PRE, "post_commit": POST,
                   "note": "Excerpts of openai/math manuscript sources (Apache-2.0); lines keep their original "
                           "numbers, everything else is blank. Built by `openai_math_revision_bench.py fixture`."},
        "dataset_sha256": hashlib.sha256(dataset_bytes).hexdigest(),
        "items": items,
    }


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


# ---------------------------------------------------------------- full chain (OPENAI_MATH_CHAIN_PROTOCOL.md)

# Pre-registered encodability of the two new checks (protocol, section 5), judged from history.md and the version
# notes before any entry was written: the defect is an imported convention or a hypothesis of a cited result, and a
# numbered cited result is used at the defect location.
CHAIN_ENCODABLE = {
    "Algebraicity-of-Weil-classes-on-split-abelian-eightfolds": set(omc.CHAIN_CHECKS),
    "Algebraicity-of-Kuga-Satake-Correspondences-for-K3-Surfaces": set(omc.CHAIN_CHECKS),
    "The-rational-Hodge-conjecture-for-products-of-K3-surfaces": set(omc.CHAIN_CHECKS),
    "Taming-implies-compatibility-on-four-manifolds": set(omc.CHAIN_CHECKS),
    "Conditional-good-minimal-models-for-compact-Kahler-fourfolds": set(omc.CHAIN_CHECKS),
    "The-Gaussian-free-field-limit-of-integer-Lipschitz-heights-with-two-arc-boundary-data": set(omc.CHAIN_CHECKS),
}


def chain_protocol_frozen() -> str:
    digest = hashlib.sha256(_lf(CHAIN_PROTOCOL)).hexdigest()
    frozen = CHAIN_PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    if digest != frozen:
        raise SystemExit(f"chain protocol changed after freezing: {digest} != {frozen}")
    return digest


def _version_sources(wt_pre: Path, wt_post: Path, item: dict, version: str) -> dict:
    wt = wt_pre if version == "pre" else wt_post
    root = long_path(wt / "preprints" / item[version]["dir"] / "build")
    if not root.exists():
        root = long_path(wt / "preprints" / item[version]["dir"])
    return manuscript_checks.read_sources(root)


def _units(data: dict):
    for item in data["items"]:
        for version in ("pre", "post"):
            if item[version]:
                yield item, version


def chain_select(clone: Path) -> dict:
    """Section 3 of the chain protocol: the cited results to register and every occurrence of them. No check runs."""
    chain_protocol_frozen()
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    wt_pre = materialize(clone, PRE, sorted({i["pre"]["dir"] for i in data["items"]}))
    wt_post = materialize(clone, POST, sorted({i["post"]["dir"] for i in data["items"] if i["post"]}))
    per_unit, bib = {}, {}
    for item, version in _units(data):
        files = _version_sources(wt_pre, wt_post, item, version)
        titles = omc.bibliography_titles(files)
        occs = omc.occurrences(files)
        for o in occs:
            bib.setdefault(o["result"], {}).setdefault(o["key"], titles[o["key"]][1])
        per_unit[(item["id"], version)] = occs
    defects = [i for i in data["items"] if i["group"] in ("revised", "withdrawn")]
    involved = sorted({o["result"] for i in defects for o in per_unit[(i["id"], "pre")]
                       if in_location(o, i["locations"])})
    pool = sorted({o["result"] for i in defects for o in per_unit[(i["id"], "pre")]} - set(involved))
    decoys = random.Random(DECOY_SEED).sample(pool, DECOY_DRAW)
    candidates = involved + decoys
    occurrences = []
    for item, version in _units(data):
        for o in per_unit[(item["id"], version)]:
            if o["result"] in candidates:
                at = item["group"] in ("revised", "withdrawn") and version == "pre" and in_location(o, item["locations"])
                occurrences.append({"item": item["id"], "group": item["group"], "version": version, **o,
                                    "at_location": at})
    for n, o in enumerate(occurrences):
        o["occ"] = "o" + hashlib.sha256(f"{DECOY_SEED}|{o['item']}|{o['version']}|{o['file']}|{o['line']}|"
                                        f"{o['key']}|{o['ref']}".encode()).hexdigest()[:10]
    return {
        "protocol_sha256": chain_protocol_frozen(),
        "dataset_sha256": hashlib.sha256(_lf(DATASET)).hexdigest(),
        "decoy_seed": DECOY_SEED, "decoy_pool_size": len(pool),
        "involved": involved, "decoys_in_draw_order": decoys,
        "results": {r: {"ref": r.split("|", 1)[1], "role": "involved" if r in involved else "decoy",
                        "bibliography": bib[r]} for r in candidates},
        "occurrences": occurrences,
    }


def chain_writer_packets(selection: dict) -> None:
    """One packet per candidate result for the blind registry writers: the bibliography entries and the locator.
    Nothing about the citing manuscripts is included."""
    CHAIN_WORK.mkdir(parents=True, exist_ok=True)
    packets = []
    for r, spec in selection["results"].items():
        packets.append({"result": r, "ref": spec["ref"], "bibliography_entries": sorted(set(spec["bibliography"].values()))})
    (CHAIN_WORK / "writer_packets.json").write_text(json.dumps(packets, indent=1, ensure_ascii=False), encoding="utf-8")


def chain_encoder_packets(clone: Path, selection: dict, registry: dict) -> None:
    """Shuffled, opaque packets for the blind context encoders: the passage around each occurrence of a registered
    result and that result's registry entry. No manuscript name, version or role."""
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    items = {i["id"]: i for i in data["items"]}
    wt_pre = materialize(clone, PRE, sorted({i["pre"]["dir"] for i in data["items"]}))
    wt_post = materialize(clone, POST, sorted({i["post"]["dir"] for i in data["items"] if i["post"]}))
    entries = {w["result"]: w for w in registry["written"] if w["status"] == "WRITTEN"}
    cache: dict = {}
    packets = []
    for o in selection["occurrences"]:
        if o["result"] not in entries:
            continue
        k = (o["item"], o["version"])
        if k not in cache:
            cache = {k: _version_sources(wt_pre, wt_post, items[o["item"]], o["version"])}
        text = cache[k][o["file"]]
        w = entries[o["result"]]
        packets.append({"id": o["occ"], "cited_key": o["key"], "cited_locator": o["locator"],
                        "result_used": o["ref"], "citation_line": o["line"],
                        "passage": omc.passage(manuscript_checks.strip_tex_comments(text), o["line"]),
                        "registry_entry": {k2: w["entry"].get(k2) for k2 in ("statement", "hypotheses", "conventions")}})
    random.Random(DECOY_SEED + 1).shuffle(packets)
    (CHAIN_WORK / "encoder_packets.json").write_text(json.dumps(packets, indent=1, ensure_ascii=False),
                                                     encoding="utf-8")
    print(f"{len(packets)} encoder packets")


CHAIN_FREEZES = OUT_DIR / "openai_math_chain_freezes.json"


def _lf(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def chain_freeze(path: Path, label: str) -> dict:
    """Freezes an input of the chain run (protocol, registry, contexts) in the ADR-085 freeze log."""
    from python.discovery import freeze_service

    store = freeze_service.FreezeStore(CHAIN_FREEZES)
    return store.freeze_document(_lf(path), "openai-math-chain-benchmark", label, name=path.name)


def chain_verify_freezes() -> dict:
    """Every input must match its freeze; anything else stops the run (a non-answer never becomes an answer)."""
    from python.discovery import freeze_service

    store = freeze_service.FreezeStore(CHAIN_FREEZES)
    out = {}
    for path in (CHAIN_PROTOCOL, CHAIN_REGISTRY, CHAIN_CONTEXTS):
        sha = hashlib.sha256(_lf(path)).hexdigest()
        fid = freeze_service.freeze_id(sha)
        check = store.verify_reference(fid, sha, document=_lf(path))
        if check["status"] != freeze_service.VERIFIED:
            raise SystemExit(f"{path.name} does not match a freeze: {check['problems']}")
        out[path.name] = {"freeze_id": fid, "sha256": sha, "frozen_at": check["frozen_at"]}
    return out


def chain_run(clone: Path) -> dict:
    """Section 4 of the chain protocol: the manuscript audit with the registry on every version that uses a registered
    result, and the 8-step chain on every encoded occurrence. Then the scoring of section 6."""
    import tempfile

    from python.discovery import cited_registry, freeze_service, manuscript_audit, verification_chain

    digest = chain_protocol_frozen()
    frozen = chain_verify_freezes()
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    items = {i["id"]: i for i in data["items"]}
    selection = json.loads(CHAIN_SELECTION.read_text(encoding="utf-8"))
    registry = json.loads(CHAIN_REGISTRY.read_text(encoding="utf-8"))
    contexts = {c["id"]: c for c in json.loads(CHAIN_CONTEXTS.read_text(encoding="utf-8"))["contexts"]}
    written = {w["result"]: w for w in registry["written"] if w["status"] == "WRITTEN"}
    keys_of: dict = {}
    for o in selection["occurrences"]:
        keys_of.setdefault(o["result"], set()).add(o["key"])
    entries = omc.registry_entries(written.values(), {r: sorted(k) for r, k in keys_of.items()})
    work = Path(tempfile.mkdtemp(prefix="omc-"))
    reg = cited_registry.Registry(work / "registry.json")
    for e in entries:
        reg.register(json.loads(json.dumps(e)))
    freezes = freeze_service.FreezeStore(work / "freezes.json")
    audit_registry = []
    for e in entries:  # The manuscript audit takes hypotheses as literal phrases only (ADR-082).
        if e.get("key"):
            audit_registry.append(dict(e, hypotheses=[h for h in e.get("hypotheses", []) if h.get("phrases")]))
    wt_pre = materialize(clone, PRE, sorted({i["pre"]["dir"] for i in data["items"]}))
    wt_post = materialize(clone, POST, sorted({i["post"]["dir"] for i in data["items"] if i["post"]}))
    occs = [dict(o) for o in selection["occurrences"] if o["result"] in written]
    by_unit: dict = {}
    for o in occs:
        by_unit.setdefault((o["item"], o["version"]), []).append(o)
    lines, audits = {}, {}
    for (item_id, version), unit_occs in sorted(by_unit.items()):
        files = _version_sources(wt_pre, wt_post, items[item_id], version)
        report = manuscript_audit.audit(files, registry=audit_registry)
        lines[(item_id, version)] = report["source_lines"]
        audits[f"{item_id}/{version}"] = {"ledger_status": report["ledger_status"],
                                          "open_obligations": report["open_obligations"],
                                          "hypothesis_outcomes": report["hypothesis_outcomes"],
                                          "citation_gate": report["citation_gate"]["status"]}
        hm = {(i["file"], i["line"], i["key"]): i for i in report["imports"]
              if i["kind"] == cited_import_ledger.HYPOTHESIS_MATCH}
        for o in unit_occs:
            imp = hm.get((o["file"], o["line"], o["key"]))
            o["audit_outcome"] = imp["outcome"] if imp else None
            o["audit_missing"] = imp["missing"] if imp else []
            ctx = contexts.get(o["occ"])
            if ctx is None:
                o["chain"] = None
                continue
            request = omc.chain_request(ctx, written[o["result"]]["entry_id"], ctx.get("citing_text", ""))
            try:
                o["chain"] = omc.chain_record(verification_chain.run(request, freezes, reg))
            except verification_chain.ChainInputError as exc:
                o["chain"] = {"formal_status": "INVALID_INPUT", "reason": str(exc), "seams_outcome": None}
        print(item_id[:60], version, len(unit_occs), flush=True)
    defects = {}
    for item in data["items"]:
        if item["group"] in ("revised", "withdrawn"):
            defects[item["id"]] = omc.score_defect(item, occs, sorted(CHAIN_ENCODABLE.get(item["id"], ())),
                                                   lines.get((item["id"], "pre"), 0))
    baseline = json.loads(RESULTS.read_text(encoding="utf-8"))
    base = {r["id"]: r["score"] for r in baseline["items"] if "score" in r}
    combined = {}
    for item_id, sc in defects.items():
        verdicts = [base[item_id]["verdict"], sc["verdict"]]
        combined[item_id] = {"baseline": base[item_id]["verdict"], "chain": sc["verdict"],
                             "combined": "HIT" if "HIT" in verdicts else "MISS" if "MISS" in verdicts
                             else "NOT_ENCODABLE"}
    summary = {
        "defects": {v: sorted(k for k, c in combined.items() if c["combined"] == v)
                    for v in ("HIT", "MISS", "NOT_ENCODABLE")},
        "chain_only": {v: sorted(k for k, c in defects.items() if c["verdict"] == v)
                       for v in ("HIT", "MISS", "NOT_ENCODABLE")},
        "hits_by_check": {c: sorted(k for k, d in defects.items() if d["per_check"][c]["verdict"] == "HIT")
                          for c in omc.CHAIN_CHECKS},
        "alarm_load": omc.alarm_load(occs, items),
        "registered_results": len(written),
        "unavailable_results": sorted(w["result"] for w in registry["written"] if w["status"] != "WRITTEN"),
        "occurrences": len(occs),
        "encoded_occurrences": sum(o.get("chain") is not None for o in occs),
        "seams_outcomes": {str(k): sum((o.get("chain") or {}).get("seams_outcome") == k for o in occs)
                           for k in ("CLEAR", "FINDINGS", "INCOMPLETE", None)},
    }
    return {"protocol_sha256": digest, "frozen_inputs": frozen, "dataset_sha256": hashlib.sha256(_lf(DATASET)).hexdigest(),
            "summary": summary, "combined": combined, "defects": defects, "audits": audits, "occurrences": occs}


def chain_registry(entries_dir: Path) -> dict:
    """Assembles the blind writers' records (section 4.1). Involved results are registered when WRITTEN; decoys in
    draw order until DECOYS_WANTED are WRITTEN, the rest are recorded as NOT_USED. Content is never edited."""
    selection = json.loads(CHAIN_SELECTION.read_text(encoding="utf-8"))
    records = {}
    for path in sorted(entries_dir.glob("w*_entries.json")):
        for rec in json.loads(path.read_text(encoding="utf-8")):
            records[rec["result"]] = dict(rec, writer=path.name.split("_")[0])
    missing = [r for r in selection["results"] if r not in records]
    if missing:
        raise SystemExit(f"no writer record for {missing}")
    written, decoys_used = [], 0
    for r in selection["involved"] + selection["decoys_in_draw_order"]:
        rec = dict(records[r], role=selection["results"][r]["role"])
        if rec["role"] == "decoy" and rec["status"] == "WRITTEN":
            if decoys_used >= DECOYS_WANTED:
                rec["status"] = "NOT_USED"
            else:
                decoys_used += 1
        written.append(rec)
    return {"procedure": "OPENAI_MATH_CHAIN_PROTOCOL.md section 4.1; writers' instructions in "
                         "openai_math_chain_procedure/WRITER_INSTRUCTIONS.md",
            "selection_sha256": hashlib.sha256(_lf(CHAIN_SELECTION)).hexdigest(),
            "repairs": [], "written": written}


def chain_contexts(encodings_dir: Path) -> dict:
    """Assembles the blind encoders' records (section 4.2). Content is never edited."""
    contexts = []
    for path in sorted(encodings_dir.glob("e*_contexts.json")):
        for rec in json.loads(path.read_text(encoding="utf-8")):
            contexts.append(dict(rec, encoder=path.name.split("_")[0]))
    return {"procedure": "OPENAI_MATH_CHAIN_PROTOCOL.md section 4.2; encoders' instructions in "
                         "openai_math_chain_procedure/ENCODER_INSTRUCTIONS.md",
            "registry_sha256": hashlib.sha256(_lf(CHAIN_REGISTRY)).hexdigest(),
            "repairs": [], "contexts": sorted(contexts, key=lambda c: c["id"])}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["dataset", "run", "posthoc", "fixture", "chain-select", "chain-freeze",
                                        "chain-registry", "chain-packets", "chain-contexts", "chain"])
    ap.add_argument("--clone", type=Path, default=CACHE / "clone")
    ap.add_argument("--file", type=Path, help="chain-freeze: the input to freeze; chain-registry, "
                                              "chain-contexts: the directory of the blind records")
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if args.command in ("chain-registry", "chain-contexts"):
        out = chain_registry(args.file) if args.command == "chain-registry" else chain_contexts(args.file)
        target = CHAIN_REGISTRY if args.command == "chain-registry" else CHAIN_CONTEXTS
        target.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {target}")
        return
    if args.command == "chain-freeze":
        record = chain_freeze(args.file, args.file.name)
        print(record["id"], record["sha256"], record["frozen_at"])
        return
    clone = ensure_clone(args.clone)
    if args.command == "dataset":
        data = build_dataset(clone)
        DATASET.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {DATASET} ({len(data['items'])} items)")
    elif args.command == "fixture":
        out = fixture(clone)
        payload = (json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        FIXTURE.write_bytes(gzip.compress(payload, mtime=0))
        print(f"wrote {FIXTURE} ({len(payload)} bytes before compression)")
    elif args.command == "chain-select":
        out = chain_select(clone)
        CHAIN_SELECTION.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                   newline="\n")
        chain_writer_packets(out)
        print(f"{len(out['involved'])} involved, {len(out['decoys_in_draw_order'])} decoys drawn, "
              f"{len(out['occurrences'])} occurrences")
    elif args.command == "chain-packets":
        chain_encoder_packets(clone, json.loads(CHAIN_SELECTION.read_text(encoding="utf-8")),
                              json.loads(CHAIN_REGISTRY.read_text(encoding="utf-8")))
    elif args.command == "chain":
        out = chain_run(clone)
        CHAIN_RESULTS.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                 newline="\n")
        print(json.dumps(out["summary"], indent=2))
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
