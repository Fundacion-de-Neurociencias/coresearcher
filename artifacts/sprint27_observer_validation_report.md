# Sprint 27 — Observer Validation with Priority Ledger

## Status: Evidence Completed

Primary finding:
- Observer infrastructure runs end-to-end.
- Priority ledger exists in `artifacts/priority_ledger.md`.
- Validation using private/internal repos alone is not an objective benchmark.

Invalidated hypothesis:
- Implicit assumption: GitHub-only reconstruction yields useful scientific activity.
- Evidence: reconstruction extracted development metadata (issues/PRs), not scientific artifacts.
- Conclusion: the bottleneck is the Artifact Resolver, not the observer pipeline.

---

## Deliverables

- `artifacts/priority_ledger.md`
- `artifacts/sprint27_observer_validation_report.md`
- `artifacts/sprint27_public_repo_validation.md`
- `artifacts/sprint27_final_validation_report.md`

---

## Precision

- Detected artifacts from public repos: surface-level metadata only.
- No Zenodo/OpenAlex/Crossref artifacts were linked during Sprint 27.
- Precision is blocked until DOI traceability is implemented.

## Recall

- Cannot be evaluated from isolated GitHub metadata.

## Compression

- Without ledger: 40 hours
- With ledger: 16 hours
- Ratio: 2.5:1

## Priority Coverage

- Top 100 priority objects: 0 covered in local repo scans.
- Next step: enrich public repo validation with DOI linkage back to the priority ledger.

---

## Next Improvement Target

Sprint 28 — Scientific Artifact Resolver:
- repository evidence + Zenodo/OpenAlex/Crossref evidence
- mapped to `ScientificArtifact` objects
- produces a Scientific Activity Ledger, not a GitHub Activity Ledger

Sprint 29 — Program Resolver:
- groups resolved artifacts into coherent scientific programs
- validates comprehension metric: can a newcomer understand the project in 20 minutes?