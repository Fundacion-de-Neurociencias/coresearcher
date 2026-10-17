"""Export, verify and fork research packages (ADR-DISCOVERY-065).

    python scripts/research_package.py export --log LIFECYCLE.jsonl --project ID --out FILE.crpkg [--root .]
    python scripts/research_package.py inspect FILE.crpkg
    python scripts/research_package.py fork FILE.crpkg --log MY_LIFECYCLE.jsonl --project NEW_ID [--materialize DIR]

`export` reads artifact paths relative to --root (default: the repository) and refuses possible credentials unless
--allow-sensitive is given. `inspect` verifies the package and prints a JSON summary; it exits 1 if verification
fails. `fork` copies the package's project into a writable lifecycle log under a new id.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.research_lifecycle import LifecycleService  # noqa: E402
from python.discovery.research_package import PackageError, export_package, fork_package, import_package  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--log", required=True, help="Lifecycle event log (JSON Lines).")
    e.add_argument("--project", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--root", default=str(ROOT), help="Folder that artifact paths are relative to.")
    e.add_argument("--allow-sensitive", action="store_true")
    i = sub.add_parser("inspect")
    i.add_argument("package")
    f = sub.add_parser("fork")
    f.add_argument("package")
    f.add_argument("--log", required=True, help="Writable lifecycle event log that receives the fork.")
    f.add_argument("--project", required=True, help="Id of the forked project.")
    f.add_argument("--materialize", help="Also write the included artifacts under this folder.")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "export":
            service = LifecycleService(Path(args.log))
            _, manifest = export_package(
                service, args.project, Path(args.root), Path(args.out), allow_sensitive=args.allow_sensitive
            )
            print(json.dumps({"written": args.out, "source": manifest["source"], "omissions": manifest["omissions"]}))
            return 0
        package = import_package(Path(args.package).read_bytes())
        if args.cmd == "inspect":
            print(json.dumps(package.summary(), indent=2))
            return 0
        project = fork_package(
            package,
            LifecycleService(Path(args.log)),
            args.project,
            Path(args.materialize) if args.materialize else None,
        )
        print(json.dumps({"forked": project.project_id, "from": project.forked_from}))
        return 0
    except PackageError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
