"""Checks that documentation, configuration and code agree with each other.

Run locally with ``python scripts/check_repo_consistency.py``. CI runs it on every
push so that README claims, package metadata and the API contract cannot drift.
"""

import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def check_python_version() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    required = re.search(r'requires-python\s*=\s*">=\s*([\d.]+)"', pyproject)
    documented = re.search(r"Python\s+([\d.]+)\+", readme)
    if not required or not documented:
        fail("Python version: could not find requires-python in pyproject.toml or 'Python X+' in README.md")
    elif required.group(1) != documented.group(1):
        fail(f"Python version: pyproject requires {required.group(1)} but README says {documented.group(1)}+")


def check_workspaces() -> None:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    for pattern in package.get("workspaces", []):
        if not glob.glob(str(ROOT / pattern)):
            fail(f"package.json workspace '{pattern}' matches no directory")


def check_env_example() -> None:
    documented = set(re.findall(r"^([A-Z_]+)=", (ROOT / ".env.example").read_text(encoding="utf-8"), re.M))
    read = set()
    for path in glob.glob(str(ROOT / "api" / "**" / "*.py"), recursive=True):
        read |= set(re.findall(r'environ(?:\.get)?\(\s*"([A-Z_]+)"', Path(path).read_text(encoding="utf-8")))
    for name in sorted(n for n in read if n.startswith("CORESEARCHER_")):
        if name not in documented:
            fail(f".env.example does not document {name}")


def check_readme_webhook_route() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    spec = json.loads((ROOT / "schemas" / "openapi.json").read_text(encoding="utf-8"))
    for route in set(re.findall(r"(/api/[a-z/_-]+)", readme)):
        if route not in spec["paths"] and not any(p.startswith(route) for p in spec["paths"]):
            fail(f"README references route {route} which is not in the API contract")


def check_readme_scripts() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for script in set(re.findall(r"`?(scripts/[\w./-]+\.py)`?", readme)):
        if not (ROOT / script).exists():
            fail(f"README references missing script {script}")


def check_markdown_links() -> None:
    for doc in [
        ROOT / "README.md",
        *sorted(path for path in (ROOT / "docs").rglob("*.md") if "private" not in path.parts),
    ]:
        # Inline code and fenced code blocks are not links, so they are removed before scanning.
        text = re.sub(r"```.*?```", "", doc.read_text(encoding="utf-8"), flags=re.S)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path = target.split("#")[0]
            if path and not (doc.parent / path).resolve().exists():
                fail(f"{doc.relative_to(ROOT)} links to missing file {path}")


CHECKS = [
    check_python_version,
    check_workspaces,
    check_env_example,
    check_readme_webhook_route,
    check_readme_scripts,
    check_markdown_links,
]

if __name__ == "__main__":
    for check in CHECKS:
        check()
    for message in errors:
        print(f"[FAIL] {message}")
    print(f"{len(CHECKS)} checks run, {len(errors)} problem(s) found.")
    sys.exit(1 if errors else 0)
