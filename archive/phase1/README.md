# Phase 1 archive

Code from CoResearcher's first phase (July to September 2026): a protocol, observer and coordination project that
predates the formal verification court. It is kept for history and is **not maintained, not tested and not imported**
by anything outside this folder. Archived on 2026-10-15 after checking that no module in `api/`, `python/discovery/`,
`tests/` or `scripts/` imported it.

| Path | What it was |
| --- | --- |
| `python/agents/`, `python/connectors/` | Literature and database agents (PubMed, OpenAlex, Crossref, ChEMBL, UniProt, Neo4j) |
| `python/observer/` | Priority discovery and repository observation (the ledger, git scanner and Zenodo publisher stayed in `python/observer/`) |
| `python/knowledge/` | Claim, finding and contradiction registries (the ontology plan engine stayed in `python/knowledge/`) |
| `python/ecosystem/`, `python/experimental/`, `python/workflows/` | Program and capability registries, workflow definitions |
| `python/evaluation/` | Sprint-22 discovery benchmark; it imports the private Einstein generator and does not run |
| `python/_tiers.py`, `scripts_*_tiers.py` | Security tier list, superseded by `docs/reference/MODULE_MATURITY.md` |
| `typescript/` | npm workspace (MCP server, provenance, types, reviewer and co-scientist agents) and its Docker image, whose Python stage pointed at a module that no longer existed |

To revive a piece, move it back with `git mv`, add tests, and register it in the module maturity table.
