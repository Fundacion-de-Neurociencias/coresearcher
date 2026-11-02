"""Builds the capability map of CoResearcher from the code, plus a small hand-written annotations file.

What comes from the code (introspection, nothing typed by hand):

- REST endpoints: every `@router.<verb>` / `@app.<verb>` in api/, read with the Python AST and checked against the
  committed OpenAPI contract (schemas/openapi.json), with the python/ modules each endpoint function refers to;
- CLI commands: every leaf subcommand of `python.cli.main.build_parser()`;
- maturity: the level of each python/discovery module in schemas/module_maturity.json
  (scripts/generate_module_maturity.py);
- ADRs: the ADR identifiers cited in each capability's own source files, resolved to docs/decisions/;
- tests: the files in tests/ that mention a capability's modules, scripts or endpoint paths.

What comes from docs/architecture/capability_annotations.toml (hand-written): the grouping into capabilities, the
plain-language description, the verification-chain role (ADR-085) and the honest caveats.

Every tracked unit must belong to exactly one capability: each endpoint, each CLI command, each module under python/
and api/, each file under scripts/ (except scripts/archive/), each entry under examples/, benchmarks/ and
integrations/<name>/. Only files tracked by git count, so local, untracked material never reaches the map.

Outputs docs/architecture/CAPABILITY_MAP.md and ecosystem/registry/capabilities.json.
Pass --check to fail when an annotation is missing, unused or ambiguous, or when the outputs are stale (used in CI).
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANNOTATIONS = ROOT / "docs" / "architecture" / "capability_annotations.toml"
MD_OUT = ROOT / "docs" / "architecture" / "CAPABILITY_MAP.md"
JSON_OUT = ROOT / "ecosystem" / "registry" / "capabilities.json"
OPENAPI = ROOT / "schemas" / "openapi.json"
MATURITY = ROOT / "schemas" / "module_maturity.json"
DECISIONS = ROOT / "docs" / "decisions"
VERBS = {"get", "post", "put", "delete", "patch"}
ADR_RE = re.compile(r"\bADR-(?:([A-Z]+)-)?(\d{2,3})\b")
LEVEL_ORDER = ["Integrated", "Tested", "Exercised", "Prototype"]


# --------------------------------------------------------------------------------------------- introspection


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return sorted(line.strip() for line in out.splitlines() if line.strip())


def tracked_units(files: list[str]) -> list[str]:
    """The files and directory entries that must each belong to one capability."""
    units = set()
    for f in files:
        parts = f.split("/")
        if "__pycache__" in parts or parts[-1] == "__init__.py":
            continue
        if parts[0] == "python" and f.endswith(".py"):
            units.add(f)
        elif parts[0] == "api" and len(parts) == 2 and f.endswith(".py"):
            units.add(f)
        elif parts[0] == "scripts" and len(parts) > 1 and parts[1] != "archive":
            units.add(f)
        elif parts[0] in ("examples", "benchmarks") and len(parts) > 1:
            units.add("/".join(parts[:2]))
        elif parts[0] == "integrations" and len(parts) > 2:
            units.add("/".join(parts[:3]))
    return sorted(units)


def _reexports() -> dict[str, str]:
    """Name -> python/discovery module, from the re-exports in python/discovery/__init__.py."""
    tree = ast.parse((ROOT / "python" / "discovery" / "__init__.py").read_text(encoding="utf-8"))
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            module = node.module.split(".")[-1]
            for alias in node.names:
                names[alias.asname or alias.name] = f"python/discovery/{module}.py"
    return names


def _module_file(dotted: str) -> str | None:
    path = ROOT / (dotted.replace(".", "/") + ".py")
    return str(path.relative_to(ROOT)).replace("\\", "/") if path.exists() else None


def _import_map(tree: ast.Module, reexports: dict[str, str]) -> dict[str, str]:
    """Local name -> repository file of the python/ module it comes from."""
    names = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("python"):
            for alias in node.names:
                local = alias.asname or alias.name
                target = _module_file(f"{node.module}.{alias.name}") or _module_file(node.module)
                if target is None and node.module == "python.discovery":
                    target = reexports.get(alias.name)
                if target:
                    names[local] = target
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("python.") and alias.asname:
                    target = _module_file(alias.name)
                    if target:
                        names[alias.asname] = target
    return names


def endpoints() -> list[dict]:
    """Every route declared in api/, with its summary and the python/ modules its function refers to."""
    reexports = _reexports()
    found = []
    for path in sorted((ROOT / "api").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = _import_map(tree, reexports)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for deco in node.decorator_list:
                if not (isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute)):
                    continue
                if deco.func.attr not in VERBS or not isinstance(deco.func.value, ast.Name):
                    continue
                if deco.func.value.id not in ("router", "app") or not deco.args:
                    continue
                if not (isinstance(deco.args[0], ast.Constant) and isinstance(deco.args[0].value, str)):
                    continue
                hidden = any(
                    k.arg == "include_in_schema" and isinstance(k.value, ast.Constant) and k.value.value is False
                    for k in deco.keywords
                )
                used = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
                doc = (ast.get_docstring(node) or "").strip().split("\n\n")[0]
                found.append(
                    {
                        "method": deco.func.attr.upper(),
                        "path": deco.args[0].value,
                        "summary": " ".join(doc.split()),
                        "source": str(path.relative_to(ROOT)).replace("\\", "/"),
                        "modules": sorted({imports[n] for n in used if n in imports}),
                        "hidden": hidden,
                    }
                )
    return sorted(found, key=lambda e: (e["path"], e["method"]))


def openapi_operations() -> set[tuple[str, str]]:
    spec = json.loads(OPENAPI.read_text(encoding="utf-8"))
    return {(m.upper(), p) for p, ops in spec.get("paths", {}).items() for m in ops if m in VERBS}


def cli_commands() -> dict[str, str]:
    """Leaf subcommand ('formal run') -> help text, from the real argument parser."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from python.cli.main import build_parser

    commands: dict[str, str] = {}

    def walk(parser: argparse.ArgumentParser, prefix: str) -> bool:
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                helps = {choice.dest: choice.help or "" for choice in action._choices_actions}
                for name, sub in action.choices.items():
                    command = f"{prefix} {name}".strip()
                    if not walk(sub, command):
                        commands[command] = helps.get(name, "")
                return True
        return False

    walk(build_parser(), "")
    return dict(sorted(commands.items()))


def maturity() -> dict[str, str]:
    rows = json.loads(MATURITY.read_text(encoding="utf-8"))["modules"]
    return {f"python/discovery/{r['module']}.py": r["level"] for r in rows}


def adr_files() -> dict[str, list[str]]:
    """'ADR-DISCOVERY-085' -> the decision records that carry that identifier."""
    index = defaultdict(list)
    for path in sorted(DECISIONS.glob("ADR-*.md")):
        m = re.match(r"(ADR-[A-Z]+-\d+)", path.name)
        if m:
            index[m.group(1)].append(path.name)
    return index


def cited_adrs(text: str, index: dict[str, list[str]]) -> set[str]:
    out = set()
    for family, number in ADR_RE.findall(text):
        number = number.zfill(3)
        key = f"ADR-{family}-{number}" if family else f"ADR-DISCOVERY-{number}"
        if key in index:
            out.add(key)
    return out


# --------------------------------------------------------------------------------------------- annotations


def load_annotations() -> dict:
    return tomllib.loads(ANNOTATIONS.read_text(encoding="utf-8"))


def _matches(patterns: list[str], value: str) -> bool:
    return any(fnmatch.fnmatchcase(value, p) for p in patterns)


def assign(annotations: dict, units: list[str], eps: list[dict], cli: dict[str, str]) -> tuple[dict, list[str]]:
    """Capability id -> its files, endpoints and commands; plus every problem found."""
    problems = []
    groups = {g["id"] for g in annotations["group"]}
    caps = annotations["capability"]
    seen_ids = set()
    for cap in caps:
        for field in ("id", "title", "group", "what"):
            if not cap.get(field):
                problems.append(f"capability {cap.get('id', '?')}: missing '{field}'")
        if cap.get("group") not in groups:
            problems.append(f"capability {cap.get('id')}: unknown group '{cap.get('group')}'")
        if cap.get("id") in seen_ids:
            problems.append(f"capability {cap.get('id')}: duplicate id")
        seen_ids.add(cap.get("id"))

    owned = {cap["id"]: {"files": [], "endpoints": [], "cli": []} for cap in caps}
    kinds = [
        ("files", "files", units, lambda u: u),
        ("endpoints", "endpoints", eps, lambda e: f"{e['method']} {e['path']}"),
        ("cli", "cli", list(cli), lambda c: c),
    ]
    for kind, field, items, key in kinds:
        used_patterns = set()
        for item in items:
            k = key(item)
            owners = []
            for cap in caps:
                patterns = cap.get(field, [])
                hits = [p for p in patterns if fnmatch.fnmatchcase(k, p)]
                if hits:
                    owners.append(cap["id"])
                    used_patterns.update((cap["id"], p) for p in hits)
            if not owners:
                problems.append(f"{kind}: '{k}' has no capability in {ANNOTATIONS.relative_to(ROOT).as_posix()}")
            elif len(owners) > 1:
                problems.append(f"{kind}: '{k}' is claimed by several capabilities: {', '.join(owners)}")
            else:
                owned[owners[0]][kind].append(item)
        for cap in caps:
            for p in cap.get(field, []):
                if (cap["id"], p) not in used_patterns:
                    problems.append(f"capability {cap['id']}: {field} pattern '{p}' matches nothing")
    return owned, problems


# --------------------------------------------------------------------------------------------- build


def build() -> tuple[dict, list[str]]:
    files = tracked_files()
    units = tracked_units(files)
    eps = endpoints()
    problems = []
    declared = {(e["method"], e["path"]) for e in eps if not e["hidden"]}
    contract = openapi_operations()
    for method, path in sorted(contract - declared):
        problems.append(f"endpoints: {method} {path} is in schemas/openapi.json but the AST scan of api/ missed it")
    for method, path in sorted(declared - contract):
        problems.append(f"endpoints: {method} {path} is in api/ but not in schemas/openapi.json (run export_openapi)")
    cli = cli_commands()
    annotations = load_annotations()
    owned, more = assign(annotations, units, eps, cli)
    problems += more

    levels = maturity()
    index = adr_files()
    test_texts = {f: (ROOT / f).read_text(encoding="utf-8", errors="ignore") for f in files if f.startswith("tests/")}
    test_texts = {f: t for f, t in test_texts.items() if f.endswith((".py", ".mjs", ".js", ".ts"))}
    reach = defaultdict(int)
    for e in eps:
        for m in e["modules"]:
            reach[m] += 1

    caps = []
    for cap in annotations["capability"]:
        own = owned[cap["id"]]
        source_text = ""
        test_patterns = []
        modules = []
        for unit in own["files"]:
            path = ROOT / unit
            if unit.endswith(".py") and path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                try:  # the ADRs a module declares are the ones its docstring names
                    source_text += ast.get_docstring(ast.parse(text)) or text
                except SyntaxError:
                    source_text += text
                stem = path.stem
                if unit.startswith(("python/discovery/", "python/observer/", "python/knowledge/", "scripts/")):
                    test_patterns.append(re.compile(r"\b" + re.escape(stem) + r"\b"))
                else:
                    dotted = unit[:-3].replace("/", ".")
                    test_patterns.append(re.compile(re.escape(dotted) + r"|" + re.escape(unit)))
                if unit.startswith(("python/", "api/")):
                    modules.append(
                        {"file": unit, "maturity": levels.get(unit, "outside register"), "endpoints": reach[unit]}
                    )
            elif not unit.endswith(".py"):
                test_patterns.append(re.compile(re.escape(unit) + r""))
        for e in own["endpoints"]:
            literal = e["path"].split("{")[0].rstrip("/")
            if literal.count("/") >= 2:
                test_patterns.append(re.compile(re.escape(literal) + r"\b"))
        for c in own["cli"]:
            test_patterns.append(re.compile(r"\b" + re.escape(c.split()[0]) + r"\b.{0,40}\b" + re.escape(c.split()[-1])))
        adrs = cited_adrs(source_text, index) | set(cap.get("adrs", []))
        if not source_text:  # an endpoint-only capability: the ADRs its endpoints name
            adrs |= cited_adrs(" ".join(e["summary"] for e in own["endpoints"]), index)
        for a in cap.get("adrs", []):
            if a not in index:
                problems.append(f"capability {cap['id']}: ADR '{a}' has no file in docs/decisions/")
        tests = sorted(f for f, t in test_texts.items() if any(p.search(t) for p in test_patterns))
        counts = defaultdict(int)
        for m in modules:
            counts[m["maturity"]] += 1
        caps.append(
            {
                "id": cap["id"],
                "title": cap["title"],
                "group": cap["group"],
                "what": " ".join(cap["what"].split()),
                "verification_chain": " ".join(cap.get("chain", "").split()),
                "caveats": [" ".join(c.split()) for c in cap.get("caveats", [])],
                "status": cap.get("status", ""),
                "maturity": {lvl: counts[lvl] for lvl in LEVEL_ORDER + ["outside register"] if counts[lvl]},
                "modules": modules,
                "endpoints": [
                    {"method": e["method"], "path": e["path"], "summary": e["summary"], "hidden": e["hidden"]}
                    for e in own["endpoints"]
                ],
                "cli": [{"command": f"coresearcher {c}", "help": cli[c]} for c in own["cli"]],
                "files": [u for u in own["files"] if not (u.startswith(("python/", "api/")) and u.endswith(".py"))],
                "adrs": sorted(adrs, key=_adr_key),
                "tests": tests,
            }
        )
    return {"annotations": annotations, "capabilities": caps, "index": index}, problems


def _adr_key(adr: str) -> tuple[str, int]:
    family, number = adr.rsplit("-", 1)
    return family, int(number)


# --------------------------------------------------------------------------------------------- render


def _adr_links(adrs: list[str], index: dict[str, list[str]]) -> str:
    links = []
    for a in adrs:
        short = a.replace("ADR-DISCOVERY-", "ADR-")
        links.extend(f"[{short}](../decisions/{name})" for name in index[a])
    return ", ".join(links) or "none cited"


def _maturity_text(m: dict) -> str:
    return ", ".join(f"{n} {lvl.lower()}" for lvl, n in m.items()) or "no python module"


def render_markdown(model: dict) -> str:
    ann = model["annotations"]
    caps = model["capabilities"]
    index = model["index"]
    total_eps = sum(len(c["endpoints"]) for c in caps)
    total_cli = sum(len(c["cli"]) for c in caps)
    total_mod = sum(len(c["modules"]) for c in caps)
    lines = [
        "# Capability map",
        "",
        "> Generated by [`scripts/generate_capability_map.py`](../../scripts/generate_capability_map.py) from the code",
        "> and from [`capability_annotations.toml`](capability_annotations.toml). Do not edit by hand: edit the",
        "> annotations and rerun the script. CI runs it with `--check`, so a new endpoint, CLI command, module or",
        "> script without an annotation fails the build.",
        "",
        ann["overview"].strip(),
        "",
        f"The map covers **{len(caps)} capabilities** in {len(ann['group'])} groups: {total_eps} REST endpoints,"
        f" {total_cli} CLI commands and {total_mod} Python modules, plus every script, example, benchmark file and"
        " integration in the repository (except `archive/`).",
        "",
        "## How to read an entry",
        "",
        ann["reading_guide"].strip(),
        "",
        "## Capabilities at a glance",
        "",
        "| Capability | Group | Endpoints | CLI | Modules (maturity) | Verification chain | Caveats |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    group_title = {g["id"]: g["title"] for g in ann["group"]}
    for g in ann["group"]:
        for c in (c for c in caps if c["group"] == g["id"]):
            chain = "yes" if c["verification_chain"] else "-"
            lines.append(
                f"| [{c['title']}](#{c['id']}) | {group_title[c['group']]} | {len(c['endpoints'])} | {len(c['cli'])}"
                f" | {_maturity_text(c['maturity'])} | {chain} | {len(c['caveats']) or '-'} |"
            )
    lines.append("")
    for g in ann["group"]:
        members = [c for c in caps if c["group"] == g["id"]]
        lines += [f"## {g['title']}", "", " ".join(g["intro"].split()), ""]
        for c in members:
            lines += [f'<a id="{c["id"]}"></a>', "", f"### {c['title']}", "", c["what"], ""]
            if c["status"]:
                lines += [f"**Status:** {c['status']}", ""]
            if c["verification_chain"]:
                lines += [f"**Verification chain (ADR-085):** {c['verification_chain']}", ""]
            if c["caveats"]:
                lines += ["**Caveats:**", ""] + [f"- {x}" for x in c["caveats"]] + [""]
            if c["modules"]:
                lines += ["| Module | Maturity | Endpoints using it |", "| --- | --- | --- |"]
                for m in c["modules"]:
                    lines.append(f"| [`{m['file']}`](../../{m['file']}) | {m['maturity']} | {m['endpoints'] or '-'} |")
                lines.append("")
            if c["endpoints"]:
                lines += [f"<details><summary>{len(c['endpoints'])} endpoint(s)</summary>", ""]
                lines += ["| Method | Path | Summary |", "| --- | --- | --- |"]
                for e in c["endpoints"]:
                    summary = e["summary"].replace("|", "\\|")
                    if e["hidden"]:
                        summary = f"Not in the OpenAPI contract. {summary}".strip()
                    lines.append(f"| {e['method']} | `{e['path']}` | {summary} |")
                lines += ["", "</details>", ""]
            if c["cli"]:
                lines.append("**CLI:** " + ", ".join(f"`{x['command']}`" for x in c["cli"]))
                lines.append("")
            if c["files"]:
                shown = ", ".join(f"[`{f}`](../../{f})" for f in c["files"][:12])
                more = f" and {len(c['files']) - 12} more" if len(c["files"]) > 12 else ""
                lines += [f"**Scripts, examples and data:** {shown}{more}", ""]
            lines += [f"**ADRs:** {_adr_links(c['adrs'], index)}", ""]
            if c["tests"]:
                lines += ["**Tests:** " + ", ".join(f"`{Path(t).name}`" for t in c["tests"]), ""]
            else:
                lines += ["**Tests:** none found", ""]
    lines += ["## How this map is kept current", "", ann["maintenance"].strip(), ""]
    return "\n".join(lines)


def render_registry(model: dict) -> str:
    groups = [{"id": g["id"], "title": g["title"]} for g in model["annotations"]["group"]]
    caps = []
    for c in model["capabilities"]:
        caps.append(
            {
                "id": c["id"],
                "title": c["title"],
                "group": c["group"],
                "description": c["what"],
                "status": c["status"],
                "verification_chain": c["verification_chain"],
                "caveats": c["caveats"],
                "maturity": {m["file"]: m["maturity"] for m in c["modules"]},
                "endpoints": [f"{e['method']} {e['path']}" for e in c["endpoints"] if not e["hidden"]],
                "hidden_endpoints": [f"{e['method']} {e['path']}" for e in c["endpoints"] if e["hidden"]],
                "cli": [x["command"] for x in c["cli"]],
                "files": c["files"],
                "adrs": c["adrs"],
            }
        )
    doc = {
        "schema": "coresearcher.capability-registry/v2",
        "generated_by": "scripts/generate_capability_map.py",
        "map": "docs/architecture/CAPABILITY_MAP.md",
        "groups": groups,
        "capabilities": caps,
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    model, problems = build()
    if problems:
        for p in problems:
            print(f"capability map: {p}")
        print(f"{len(problems)} problem(s). Edit {ANNOTATIONS.relative_to(ROOT).as_posix()} and rerun.")
        return 1
    outputs = {MD_OUT: render_markdown(model), JSON_OUT: render_registry(model)}
    if "--check" in argv:
        stale = [p for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            for p in stale:
                print(f"{p.relative_to(ROOT).as_posix()} is stale. Run: python scripts/generate_capability_map.py")
            return 1
        print("Capability map is up to date.")
        return 0
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
