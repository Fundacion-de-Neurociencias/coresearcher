# ADR-DISCOVERY-067: EvidenceRequest and EvidenceGraph v1, and the capability catalogue

**Status:** Accepted
**Date:** 2026-10-18
**Modules:** [`python/discovery/evidence_service.py`](../../python/discovery/evidence_service.py),
[`api/routers/evidence.py`](../../api/routers/evidence.py)
**Schemas:** [`schemas/evidence/v1/`](../../schemas/evidence/v1)

## Context

CoResearcher has no user interface of its own. EdiTXT is the shared frontend of the ecosystem
([ARCH-003](../architecture/ARCH-003_ECOSYSTEM_FULL_INTEGRATION_AND_EDITXT_FRONTEND.md)): its Epistemic Inspector is
meant to show CoResearcher's EvidenceGraph next to each claim of a manuscript. Until now that link did not exist:

- [BOUNDARY_WITH_EDITXT.md](../architecture/BOUNDARY_WITH_EDITXT.md) said CoResearcher answers EvidenceRequests with
  EvidenceGraphs, but no endpoint did.
- Two incompatible drafts described the contract: the boundary document (`target_claim`, `evidence_scope`,
  `minimum_confidence`) and `schemas/evidence_request.schema.json` / `schemas/evidence_graph.schema.json` (`ER-` and
  `EG-` ids with six digits, and targets such as `DOI` and `REPOSITORY` that CoResearcher cannot resolve).
- Several results had no route to a user at all: the pTau217 two-cutoff case, the ED polarity case, the published
  research packages, and the claims register. Lifecycle projects and the `formal-claim` template were reachable only
  as raw JSON.

## Decision

### 1. One contract, `coresearcher.evidence/v1`

`POST /api/evidence/requests` takes an EvidenceRequest and returns an EvidenceGraph. Both have JSON Schemas in
`schemas/evidence/v1/`, served at `GET /api/evidence/schema`. A request names one **target** that CoResearcher
actually holds:

| Target type | Built from |
| --- | --- |
| `LIFECYCLE_PROJECT` | gates, check results by kind, artifacts with their live hash status, releases, criteria, findings (ADR-063) |
| `RESEARCH_PACKAGE` | a published `.crpkg`, verified on import, with its digests checked against the package index (ADR-065) |
| `REGISTERED_CLAIM` | a row of the claims register, its status and its scripts |
| `FORMAL_HYPOTHESIS` | the content verdict, up to 10 consequences and up to 5 rivals with discriminating states (ADR-059, ADR-060) |
| `FORMAL_CASE` | `ptau217_two_cutoff`, `alzheimer_rivals` or `ed_polarity` |
| `QUESTION` | free text; the graph contains the question and a `no_linked_evidence` gap, nothing else |

`claim_ids` lets the client attach its own claim ids (EdiTXT's `CLM-001`), which appear as `claim` nodes linked to
the target. `GET /api/evidence/targets` lists every valid target, so a client offers choices instead of guessing ids.

### 2. What a graph says

- **Nodes** have a kind (for example `verification`, `review`, `artifact`, `criterion`, `assumption`, `rival`).
  **Edges** have a relation from a closed list (`verified_by`, `supports`, `contradicts`, `requires`,
  `discriminates`, ...) and a justification.
- A **verifier result is reported as what the named tool decided**: z3, enumeration, Comparator, the Lean kernel.
  It is not CoResearcher's opinion. No node carries a confidence score: CoResearcher has no calibrated method that
  would produce one, so the boundary document's `confidence_distribution` is not implemented.
- **Gaps are never hidden.** Open checks, failed checks, unmet criteria, artifacts changed, missing or omitted since
  their gate, packages that do not verify or whose digest is not published, register rows that are not PASS,
  unfalsifiable or vacuous hypotheses, consequences not entailed, entailments no proof kernel has checked, live
  rivals, and the scope limits of formal cases are all gaps.
- **No manuscript grading.** Nothing in the graph judges prose, assigns severity or recommends an edit.

### 3. Content addressing

`provenance.digest` is the SHA-256 of the canonical target, nodes, edges and gaps; `graph_id` is `EG-` plus its first
16 hex digits. The same evidence gives the same id, and changed evidence (an edited artifact, a new release) gives a
new one. EdiTXT stores the digest in its `EvidenceTraceArtifact.artifactHash`; a later request that returns a
different digest tells the editor that the evidence behind a claim has changed. `generated_at` is outside the digest.
`GET /api/evidence/graphs/{graph_id}` serves recently produced graphs from a bounded in-memory store (512 graphs);
a graph that is no longer stored is recomputed by sending the request again.

### 4. Capability catalogue

`GET /api/capabilities` lists every endpoint in the shape of OnTrack's `CapabilityContract`: name, description,
method, path, group, input and output schemas, `determinism`, `operationClass`, whether the API key is needed, and
the maturity level of the discovery modules behind it (from `schemas/module_maturity.json`). It is built from the
running application, so it cannot drift from the API.

- `determinism` is `NON_DETERMINISTIC` unless the endpoint is on a short reviewed list of pure computations.
- `operationClass` is `READ_ONLY` for GET and for a reviewed list of POST endpoints that compute without changing
  state (evidence requests, formal evaluation, comparison, entailment, formalization, package inspection);
  every other POST is `STATE_MODIFYING`.

EdiTXT uses the catalogue to show every capability with its maturity, so no module stays hidden, and its proxy
forwards only `READ_ONLY` POST endpoints unless writes are enabled explicitly.

### 5. Published packages

`GET /api/lifecycle/packages` lists the packages in `docs/reference/packages/` with their SHA-256 and the digests
from the package index; `GET /api/lifecycle/packages/{name}` returns one byte for byte. Published packages are
public, so neither needs the API key. Exporting a live project still does.

### 6. Ports and existing consumers

DataAILab keeps port 8000 and calls CoResearcher on **port 8001** (`CORESEARCHER_URL`). The quick start now uses
8001. The three endpoints DataAILab consumes (`GET /api/health`, `POST /api/discovery/inference-scaling/search`,
`POST /api/discovery/lab-in-the-loop/ground-recipe`) are pinned by consumer contract tests in
`tests/test_evidence_service.py`.

## Consequences

- EdiTXT can show, for each claim, the evidence CoResearcher holds and every gap in it, with a digest that detects
  stale evidence.
- The old draft schemas stay in `schemas/` for the documents that cite them. They are not implemented; v1 replaces
  them.
- The ED polarity case takes about 20 seconds the first time; its report is then cached for the life of the
  process.
- Evidence requests need the API key, like every POST, because formal checks can be expensive. EdiTXT holds the key
  on its server and never sends it to the browser.

## Amendment (2026-10-18): premise origin

A formal result is only as good as its premises. The pTau217 case shows it: the rule is PROVED but UNFALSIFIABLE,
because the claims follow from the assumptions alone. Its empirical content therefore lies entirely in the premises,
which is the abductive part of the work. Graphs now say where each premise came from:

- Every premise is an `assumption` node, linked to its hypothesis or formal case by `requires`. Each node carries:
  - `origin`: `SUPPLIED` (given in the input), `LITERATURE`, `PERSON`, `SYSTEM` (introduced by CoResearcher or an
    agent) or `UNDECLARED`;
  - `tested_against_data`;
  - `source`.
- A hypothesis object can declare these in `premise_provenance`. Undeclared premises are reported as `UNDECLARED` and
  untested, never guessed. The premises of the pTau217 and ED polarity cases come from the cited literature and have
  not been tested against data by CoResearcher.
- Each untested premise is a `premise_untested` gap. The focus node summarises the origins (`premise_origins`).
- **Origin never changes a verdict.** Validity does not depend on who proposed a premise. What origin does show is
  how much a result says about the system's own ability to propose premises; this follows ADR-DISCOVERY-066.
  `SYSTEM` premises confirmed by data are the evidence that a system made what Zahavy (ICML 2026) calls the "jump".
  The unknown-mechanism v4 benchmark measures that directly.

The `formal-claim` template gains the matching optional check `report.premise_origin`
([ADR-DISCOVERY-066](ADR-DISCOVERY-066-FORMAL-CLAIM-AUDIT.md), amendment).

## Verification

`tests/test_evidence_service.py` validates every target type against both JSON Schemas, checks that edges and gaps
point at existing nodes, recomputes the digest, checks that an edited artifact changes the graph id, that tampered
and unlisted packages are reported, that malformed requests are refused, that the capability catalogue covers every
OpenAPI operation, and pins the DataAILab contract. Claims register, row 30.
