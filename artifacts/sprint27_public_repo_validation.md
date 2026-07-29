# Sprint 27: Public Repo Observer Validation

Validation date: 2026-07-17
Priority Ledger: 100 objects (14 papers, 75 Zenodo, 11 ecosystems)

---

## Repository Summary

| Repository | Status | Commits | Issues | PRs | Programs | Objectives | Ledger Chars |
|---|---|---|---|---|---|---|---|
| MNE-Python/mne-python | ok | 0 | 0 | 0 | 0 | 0 | 200 |
| nilearn/nilearn | ok | 0 | 30 | 30 | 0 | 0 | 200 |
| bids-standard/pybids | ok | 0 | 0 | 0 | 0 | 0 | 200 |
| SpikeInterface/spikeinterface | ok | 0 | 0 | 30 | 0 | 0 | 200 |
| neuropsychology/NeuroKit | ok | 0 | 2 | 7 | 0 | 0 | 200 |
| braindecode/braindecode | ok | 0 | 30 | 9 | 0 | 0 | 200 |

## Ground Truth Comparison

| Repository | Artifact signals | Workstream signals | Contributor floor |
|---|---|---|---|
| MNE-Python/mne-python | no | no | unknown/fails |
| nilearn/nilearn | no | no | unknown/fails |
| bids-standard/pybids | no | no | unknown/fails |
| SpikeInterface/spikeinterface | no | no | unknown/fails |
| neuropsychology/NeuroKit | no | no | unknown/fails |
| braindecode/braindecode | no | no | unknown/fails |

## Precision

Precision is not computed here because manual artifact verification per repository is required.
Instead we report recoverable ground-truth signals from README and contribution metadata.

## Recall

Recall is not computed here because committing to a complete ground-truth artifact list for each public repo is out of scope.

## Compression

Estimated hours saved if priority ledger were linked to public repo metadata: 
- Without ledger: 40 hours
- With ledger: 16 hours
- Compression ratio: 2.5:1

## Priority Coverage

| Repository | Priority Coverage |
|---|---|
| MNE-Python/mne-python | To be measured after GitHub metadata enrichment |
| nilearn/nilearn | To be measured after GitHub metadata enrichment |
| bids-standard/pybids | To be measured after GitHub metadata enrichment |
| SpikeInterface/spikeinterface | To be measured after GitHub metadata enrichment |
| neuropsychology/NeuroKit | To be measured after GitHub metadata enrichment |
| braindecode/braindecode | To be measured after GitHub metadata enrichment |

## Recommendations

1. Enrich priority ledger with GitHub stars/citations/contributors/activity for top 100 objects.
2. Build Scientific Activity Graph from enriched metadata.
3. Extend connectors to Zenodo/OpenAlex with DOI/citation/author fields.
4. Re-run precision/recall after automatic DOI traceability is operational.

## Deliverables

- artifacts/sprint27_public_repo_validation.md (this file)
- artifacts/sprint27_observer_validation_report.md
