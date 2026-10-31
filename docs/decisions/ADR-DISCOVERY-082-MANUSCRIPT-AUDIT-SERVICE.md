# ADR-DISCOVERY-082: Manuscript audit as an integrated capability

**Status:** Accepted
**Date:** 2026-10-31

**Modules:**
- [`python/discovery/manuscript_audit.py`](../../python/discovery/manuscript_audit.py)
- [`python/discovery/formal_pipeline.py`](../../python/discovery/formal_pipeline.py) (request kind `manuscript_audit`)
- [`python/discovery/formal_trust.py`](../../python/discovery/formal_trust.py) (trust view of a manuscript claim)
- [`python/cli/formal.py`](../../python/cli/formal.py) (`formal manuscript`)
- [`api/routers/manuscripts.py`](../../api/routers/manuscripts.py) (`POST /api/manuscripts/audit`)

**Builds on:**
- ADR-DISCOVERY-077: import obligations and the citation gate;
- ADR-DISCOVERY-076: obligation ledger;
- ADR-DISCOVERY-068: status, relays, provenance, two-phase CLI;
- ADR-DISCOVERY-080: trust ladder, statement checks as services.

**Numbering:** 080 and 081 are taken on master, so this record is 082.

## Context

ADR-077 built two mechanisms from the openai/math time-travel benchmark:
- the citation gate;
- import obligations: convention transfer, hypothesis match against a cited-result registry, dependency on a
  withdrawn or corrected companion, and effective constant.

They existed only as library functions and a benchmark script. Methodology M6 ("errors live at the seams") and M9
("measure on real errors") in [`VERIFICATION_METHODOLOGY.md`](../architecture/VERIFICATION_METHODOLOGY.md) call
for them to be product capabilities: reachable from the API and the CLI, with the same non-verdict statuses,
relays and provenance as every other formal report. This record does that, following the pattern ADR-080 set for
statement fidelity.

## Decision

1. **One sealed report.** `manuscript_audit.audit(files, registry, manuscript_status, collection, claim)` returns:
   - `citation_gate`:
     - `status`: PASS, FAIL, or NO_BIBLIOGRAPHY;
     - the unresolved citations, each with file and line;
     - counts of citations, bibliography entries and collection links.
   - `imports`: every ADR-077 obligation with file, line, key, locator, context and outcome.
   - `import_counts` and `hypothesis_outcomes` (MATCHED, UNMATCHED, NO_ENTRY).
   - `ledger_status`: the ADR-076 weakest-link roll-up, which is OPEN whenever any import exists.
   - `formal_status`, `mandatory_relays` and an ADR-068 provenance block (operation `manuscript_audit`).
   - The digest covers the full sources, so the same sources always give the same `output_sha256`.
2. **Non-verdicts stay non-verdicts (M8).**
   - Sources without a bibliography cannot be judged by the gate. The report says NO_BIBLIOGRAPHY with
     `formal_status` UNDECIDED (CLI exit 10), never PASS.
   - Obligations are never discharged by the audit.
   - Three new relays are registered in `formal_status`:
     - `IMPORTS_ARE_LEXICAL`, always;
     - `IMPORT_OBLIGATIONS_OPEN`, when there is any import;
     - `CITATIONS_UNRESOLVED`, when the gate fails.
3. **Trust ladder (ADR-080).**
   - A manuscript's prose claim has no pinned formal statement, so `formal_trust.for_response` keeps it at
     CLAIMED. The audit never lifts it, and the relay `CLAIM_BELOW_KERNEL_CHECKED` applies.
   - The trust view sits beside the report: in the API response (`claim_trust`, `trust_relays`) and in the CLI
     sidecar and analysis. It is never inside the digested report.
4. **The registry takes literal phrases, not regular expressions.**
   - A cited result is `{key, locator, statement, hypotheses: [{text, phrases}], conventions}`.
   - A hypothesis counts as stated where the result is used when any of its phrases occurs in the citing statement
     or proof (case-insensitive).
   - Phrases are escaped before matching. A caller's registry can therefore never make the server run a
     catastrophic regular expression.
5. **Interfaces.**
   - **API:** `POST /api/manuscripts/audit` takes `{files: {path: text}, registry, manuscript_status, collection,
     claim}`. It is catalogued READ_ONLY and DETERMINISTIC, and malformed input gets 422.
   - **CLI:** `coresearcher formal manuscript --dir D [--registry R.json] [--manuscript-status S.json]
     [--collection C] [--claim TEXT]` reads every `.tex`, `.bib` and `.bbl` under D. It is phase 1 of the ADR-068
     convention: it writes the request (with the full sources), the response and the checksummed sidecar.
     `formal analyze` re-derives the report offline and compares digests. The sidecar leaves out the sources and
     the registry.
6. **Scope is unchanged.** The audit checks the formal structure of a manuscript's imports and references. It
   does not judge evidence, sources' quality, credit or announcements, and it generates nothing.

## Consequences

- Any manuscript CoResearcher is asked to check now gets, in one call, the check that found the one real defect of
  the time-travel benchmark (an unresolved citation). It also gets the OPEN imports that sat at the defect sites
  of the three withdrawals and of the taming corollary.
- The registry is the shared place where reviewer effort accumulates. Each encoded cited result is matched at
  every later use, through the API or the CLI.
- The registry stores `conventions` as typed fields, but no comparison of conventions is automated yet. A
  CONVENTION_TRANSFER obligation is discharged by a reviewer. Comparing typed conventions is the next M6 step
  (block B of the roadmap).
- **Known limitation, kept on purpose.** The ADR-077 sentence window stops at a paragraph break, not at
  `\end{proof}`. Two proofs written back to back without a blank line therefore share a window, and a citation in
  the first can pick up a CONVENTION_TRANSFER from sign words in the second. The fix belongs in
  `cited_import_ledger`, which ADR-077 froze for its prospective test, so it is not changed here. It will be made
  as a recorded deviation once that test has run.
- The prospective test of ADR-077 is unaffected. The mechanisms it froze (`cited_import_ledger`,
  `manuscript_checks`, `citation_gate`) are called, not changed.
- **Beyond mathematics (M6).** A biomedical manuscript imports cutoffs, scales and units from cited validation
  studies. The same request kinds apply once the registry holds those cited results with their validated
  conditions as phrases.

## Alternatives considered

- **Regular-expression hypotheses in the registry.** Rejected for the API: Python's `re` has no timeout, and a
  caller-supplied pattern could stall the server. Literal phrases keep the check linear.
- **Fail the gate when there is no bibliography.** Rejected: absence of evidence is a non-verdict (M8), not a
  defect. Some manuscripts keep their references in a compiled `.bbl` that the caller may not have sent.
- **Put the trust view inside the report.** Rejected for the same reason as in ADR-080: it would make the report
  digest depend on evidence outside the manuscript.
