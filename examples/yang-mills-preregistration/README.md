# Yang–Mills existence pre-registration

Inputs and outputs of the case described in
[`docs/reference/cases/YANG_MILLS_PREREGISTRATION.md`](../../docs/reference/cases/YANG_MILLS_PREREGISTRATION.md)
(ADR-DISCOVERY-077).

| File | What it is |
|---|---|
| `ym4_existence_checklist.v1.json` | The frozen acceptance checklist: vocabulary, obligations with sources, trivial-witness catalogue |
| `ym4_existence_checklist.v1.lock.json` | SHA-256 of its canonical JSON and the freeze date (2026-10-30). Never edit v1; make a new version |
| `ym_claim_record.json` | Trust-ladder record of the claim: CLAIMED, statement not public |
| `preregistration_report.json` | Self-probe, barriers per witness, single barriers, scenarios; regenerate with `python scripts/cases/ym_preregistration_report.py` |

No third-party file is vendored. The committee statement and the Jaffe–Witten problem description are pinned by
SHA-256 in the checklist's `references`.
