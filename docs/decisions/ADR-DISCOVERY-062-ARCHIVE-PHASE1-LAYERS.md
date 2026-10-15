# ADR-DISCOVERY-062: Archive the phase-1 layers and the TypeScript workspace

**Status:** Accepted
**Date:** 2026-10-15

## Context

The repository still carried the layers of CoResearcher's first phase (a protocol, observer and coordination
project): literature agents, connectors, knowledge registries, ecosystem and workflow registries, an evaluation
package, and an npm workspace with an MCP server and TypeScript agents. A dependency check on 2026-10-15 found that no
module in `api/`, `python/discovery/`, `tests/` or `scripts/` imported any of it, except four modules: the scientific
ledger, the git scanner, the Zenodo publisher (with its ledger normalizer) and the ontology plan engine.

The Dockerfile built that workspace, and its Python stage ran `python -m python.agents`, a module with no entry point,
so the image could not have served the API.

## Decision

- Move the unused layers to `archive/phase1/` with `git mv`, keeping their history. The four used modules stay where
  they are.
- Move the npm workspace and its Dockerfile to `archive/phase1/typescript/`. The new `Dockerfile` serves the FastAPI
  API, runs as a non-root user and takes secrets only from the runtime environment.
- The private Einstein generator, which used the knowledge registries, now carries its own copy of them in the private
  package, so the public archive is not a dependency of private code. Its output goes through the formalizer and the
  exact evaluator before anything is forwarded (ADR-DISCOVERY-002, ADR-DISCOVERY-061).
- Remove the npm workspace check from `check_repo_consistency.py`; declare `uvicorn`, which `serve` needs.

## Consequences

- The maintained surface is the API, the discovery engines, the formal hypothesis stack, the ledger and the CLI.
- Anything archived can be revived with `git mv`, tests and a module maturity entry.
- Any deployment that built the old Dockerfile must switch to the new one; the old image could not run the API.
