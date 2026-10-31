# Proof pipeline: reproducible obligation proofs

Status: in use for the Mahler scalar input (ADR-DISCOVERY-076). Module: `python/discovery/proof_pipeline.py`.

## 1. What it is for

CoResearcher checks a claimed mathematical result by splitting it into obligations (identities and inequalities)
and discharging each one independently of the authors' code. The Mahler pilot showed that the discharges are
long computations: from seconds up to about two hours, about 3.5 hours in all with 8 workers. Such a computation
counts as evidence only if three things hold:

1. anyone can rerun it with one command;
2. anyone can check in seconds that the stored results belong to the current code;
3. the ledger's verdict follows mechanically from the stored results.

The pipeline provides all three.

## 2. How it works

A case is a list of `ProofStep`s. Each step has:

- a script that writes one JSON report;
- the dotted keys of that report that must be `true`, such as `window.verified`;
- the source files the result depends on.

The manifest (`manifest.json` next to the reports) stores:

- the SHA-256 of every source and every report;
- the Python, mpmath, SymPy and NumPy versions;
- the git commit.

| Command | Cost | What it does |
| --- | --- | --- |
| `python scripts/cases/mahler_reproduce.py` | seconds | Audit: reports exist and are verified, hashes match, no STALE proof, ledger roll-up consistent |
| `... --run all` | about 3.5 h | Rerun every proof in dependency order, then rewrite the manifest and audit |
| `... --run segment_box ledger` | about 25 min | Rerun selected steps |
| `... --write-manifest` | seconds | Record the current reports and sources |

A proof is **STALE** when a file it depends on changed after the proof ran. The audit then fails until that step
is rerun. This blocks the most common silent error in computer-assisted proofs: a certificate that was valid for
an earlier version of the code.

Hashes ignore CRLF versus LF and the `seconds` fields of the reports. A rerun on another machine therefore
reproduces the same report hashes whenever the results agree. Float interval arithmetic with outward rounding is
deterministic under IEEE 754, and the worker pools return results in order.

## 3. Reproduction record (Mahler, 2026-10-30)

Four proofs were rerun from scratch into a separate folder and compared with the committed reports:

- `interval`, `twovar` and `segment_box` reproduced bit for bit (equal report hashes);
- `tail` differed. Its verification results were identical, but the committed report came from an earlier version
  of `mahler_tail.py` and lacked four entries of model metadata. The report was regenerated from the current code.
  This is the stale-certificate case the audit is designed for. The first manifest had been built from the current
  code, so only a rerun could reveal it;
- `ranges` (about 2.2 hours) was not rerun in this pass.

## 4. Reusable techniques from the Mahler pilot

Each technique is a module that a new case can reuse or copy.

| Technique | Module | Use it when |
| --- | --- | --- |
| Exact identities by CAS | `mahler_segment`, `mahler_obligations` | algebraic reductions, closed forms |
| Stable closed forms + mean-value / Taylor branch and bound | `mahler_interval`, `mahler_ranges` | one-variable inequalities on a bounded window |
| Laurent–Taylor models in t = 1/x with exact rational coefficients | `mahler_tail` | the same inequalities as x → ∞, where cancellations defeat plain intervals |
| Vectorized float intervals with one-ulp outward rounding | `mahler_twovar`, `mahler_segment_box` | millions of boxes or pairs |
| Cell integrals + prefix sums + partial end cells | `mahler_segment_box` | inequalities on averages over segments |
| Adaptive refinement of only the failing boxes | `mahler_twovar`, `mahler_segment_box` | thin regions where the margin is small |

## 5. Adding a new case

1. Write the claim as obligations in a ledger builder, as in `mahler_obligations.build_ledger`. Split every
   obligation that is proved on part of its domain into a proved part and the rest.
2. For each obligation, write a module that discharges it and a `scripts/cases/<case>_<step>_report.py` that writes
   its JSON report.
3. Declare the steps in a `scripts/cases/<case>_reproduce.py` like `mahler_reproduce.py`. List every source file a
   step imports from the case.
4. Run `--run all`, commit the reports and the manifest, and add a test that audits the committed manifest
   (`tests/test_proof_pipeline.py`).

## 6. Next steps

- **Rerun `ranges`** to close the reproduction record.
- **Generic engines.** Extract the branch-and-bound driver, the Laurent–Taylor model class and the vectorized
  interval operations into case-independent modules. Today each Mahler module carries its own copy of the
  vectorized operations.
- **Audit in CI.** Run the fast audit in the test suite. This is already done for Mahler through
  `test_committed_mahler_manifest_audits_clean`. Rerun the long proofs on a schedule on a work machine, never with
  personal data.
- **Lean export.** Interval certificates can be replayed in Lean through a verified interval library. Doing so
  would raise DISCHARGED_INTERVAL obligations to DISCHARGED_FORMAL.
- **API.** Expose the ledger and the audit result next to the existing verification endpoints, so that a claim's
  status always comes with its audit.
