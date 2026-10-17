# ADR-DISCOVERY-065: Portable, verifiable research packages

**Status:** Accepted
**Date:** 2026-10-17
**Module:** [`python/discovery/research_package.py`](../../python/discovery/research_package.py)
**CLI:** [`scripts/research_package.py`](../../scripts/research_package.py) (`export`, `inspect`, `fork`)
**API:** `GET /api/lifecycle/projects/{id}/package`, `POST /api/lifecycle/packages/inspect`

## Context

A lifecycle project (ADR-DISCOVERY-063) records how a result was reached, but the record lived in one server's log
and in files spread across the repository. AIPOCH Open-Science packages a finished research session into a single
`.science` file that another machine imports read-only and can fork. We reviewed its implementation
(`aipoch/open-science`, `src/main/session-package/`). Its main rules:

- a gzip tar with a whitelist of fixed paths and content-addressed objects;
- a manifest with an inventory and explicit omissions;
- a version and required-features check that refuses newer packages;
- validation by replaying the package into a disposable store, because "archive checksums alone cannot establish
  these relationships";
- a scan for credentials before export, read-only imports, forks, and RO-Crate metadata.

## Decision

1. **Format.** A `.crpkg` file is a gzip tar with only these entries:
   - `manifest.json`;
   - `events.jsonl`, the project's lifecycle events, unchanged;
   - `README.md`, written from the log;
   - `ro-crate-metadata.json`, RO-Crate 1.1;
   - `objects/<sha256>`, one per artifact.

   Export is deterministic: the same project gives the same bytes.
2. **Nothing silent.** Every artifact a check recorded is either included with the recorded hash, or listed in
   `omissions`. An omission is `missing` (the file is gone) or `changed` (the file no longer has the hash the check
   recorded).
3. **Import verifies three things.**
   - Integrity: listed files only, with their sizes and hashes. Unknown paths, links and duplicates are refused,
     and nothing is extracted to disk.
   - Consistency: the log replays into a fresh lifecycle with the manifest's version, digest, stage and event count.
   - Completeness: no recorded artifact is unaccounted for.
4. **Replay checks every gate.** A log may record a passed gate only if its own results pass it, with exactly those
   results as evidence, and release criteria are read from the hashed gate evidence. This closes a gap that the
   package tests exposed: an outcome could be rewritten in the results without changing any digest.
5. **Read-only and forks.** An imported project cannot be changed. `fork` copies its history under a new id into a
   writable lifecycle, records where it came from (`forked_from`, with the manifest hash), and can write the
   artifacts back to disk.
6. **Credentials.** Export stops when the log or a text artifact looks like it holds a key, a token or a password,
   unless the caller accepts it. The report names the place, never the value.
7. **Benchmark template.** A second checklist, `benchmark`, fits projects that validate a benchmark rather than
   test a hypothesis. The claim is about the benchmark, and the control is the protocol's positive control.
8. **First package.** [`openai-math-lean-oracle.crpkg`](../reference/packages/openai-math-lean-oracle.crpkg),
   built by [`build_oracle_package.py`](../../scripts/packages/build_oracle_package.py) from repository files. It
   includes the protocol as pre-registered in `f89caf7` (2026-10-13), recovered from git. Human checks are recorded
   only when a person signs off; until then the package stops at the open gate and says so.

## Limits

- Verification shows that a package is complete, untampered and consistent with its own history. It does not
  reproduce the results.
- A wholly rebuilt but consistent history passes verification and has a different digest. Trust needs the digest
  published somewhere independent: the claims register, OnTrack or a commit.
- There is no signature yet. Who exported a package is not proven.
