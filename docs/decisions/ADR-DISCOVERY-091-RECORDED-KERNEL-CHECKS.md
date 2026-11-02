# ADR-DISCOVERY-091: Recorded Lean kernel checks, the only way into KERNEL_CHECKED

**Status:** Accepted
**Date:** 2026-11-02

**Modules:**
- [`python/discovery/kernel_records.py`](../../python/discovery/kernel_records.py) (record schema, verification, ladder evidence)
- [`python/discovery/trust_ladder.py`](../../python/discovery/trust_ladder.py) (KERNEL_CHECKED step)
- [`python/discovery/cited_registry.py`](../../python/discovery/cited_registry.py) (`kernel_evidence`, `record_kernel_check`)
- [`api/routers/registry.py`](../../api/routers/registry.py) (`POST /api/registry/entries/{id}/kernel-check`)
- [`scripts/lean/kernel_check.py`](../../scripts/lean/kernel_check.py), [`scripts/lean/comparator_preflight.sh`](../../scripts/lean/comparator_preflight.sh)
- [`.github/workflows/lean-kernel.yml`](../../.github/workflows/lean-kernel.yml), [`lean/kernel-check/`](../../lean/kernel-check/)
- [`records/kernel/`](../../records/kernel/) (committed records and logs)

**Builds on:** ADR-068 (formal statuses), ADR-080 (trust ladder), ADR-081 (claim records), ADR-083 (cited registry).

## Context

The trust ladder has a KERNEL_CHECKED rung, but until now no Lean kernel had run in our environment:

- openai/math's Comparator needs Linux and landrun (Landlock).
- The Windows development machine cannot run them.
- The Linux machine was offline.
- The Mac Studio has Lean but no Landlock.

The rung's evidence was a set of hand-typed fields (toolchain, axioms, log digest, checker). Nothing tied those fields
to a run that happened. A claim could therefore reach KERNEL_CHECKED on assertion alone, and a registry entry could be
registered at that rung with no evidence at all.

## Decision

1. **A Linux CI job runs the kernel.**
   - The `Lean kernel checks` workflow runs on GitHub-hosted Ubuntu runners.
   - It runs on demand (`workflow_dispatch`), weekly (Mondays 03:17 UTC), and on pushes to `lean-kernel/*`
     branches, which are used to try a change to the workflow.
   - It never runs on pull requests, so PR CI stays fast.
   - It checks two kinds of target.
     - **Our files**, with `lake env lean` and `#print axioms` for every theorem. The project is
       `lean/kernel-check`, at Lean v4.35.0 and Mathlib tag v4.35.0, with `lake exe cache get`. The files are
       `examples/sakana-ed-polarity/EdPolarity.lean`, `examples/ptau217-cutoff/Ptau217Cutoff.lean` and
       `examples/local-smoothing-fidelity/LocalSmoothing.lean`.
     - **Three openai/math Comparator challenges**: LocalSmoothing, SubexponentialSAT (ETH, family 378) and
       ClassicalON. They run at the pinned commit `4eaee875…` with comparator and lean4export at tag v4.34.0 and
       landrun from main at `811cfff5…`, as the Comparator README requires.
   - Before Comparator runs, a preflight checks that the kernel lists Landlock. It also checks that landrun, given
     Comparator's own flags, refuses a write outside its rules.
   - If any preparation step fails, the check is recorded as BLOCKED with the reason. A BLOCKED check is never
     recorded as a pass.
   - Comparator runs under `systemd-run --user` when the runner allows it. Whether it did is recorded.
2. **Every check writes a kernel record and its log.**
   - The record (`coresearcher.kernel-record/v1`) contains:
     - toolchain, `lean --version` and Mathlib commit;
     - SHA-256 of the checked file;
     - the theorems and the axioms of each, from `#print axioms`;
     - wall time and exit code;
     - `kernel_log` and `kernel_log_sha256`;
     - `checked_by`, the URL of the Actions run;
     - `result`: PASS, FAIL or BLOCKED.
   - The record carries the four fields of the trust-ladder rung: `toolchain`, `axioms`, `kernel_log_sha256` and
     `checked_by`.
3. **The result is computed from the log, never trusted from the record.**
   - The runner ends each log with an exit-code footer.
   - PASS needs:
     - exit code 0;
     - no Lean error line;
     - at least one theorem, each with an axioms line;
     - only `propext`, `Quot.sound` and `Classical.choice` (never `sorryAx`);
     - for Comparator, its success line.
   - BLOCKED means the kernel did not run or did not finish. It is a non-verdict.
   - Verification rehashes the stored log. It also recomputes the result, the axioms and the exit code, and
     compares them with the record.
4. **Only a verified PASS record climbs.**
   - `trust_ladder.ClaimRecord` refuses a KERNEL_CHECKED step unless its evidence does three things:
     - it embeds a PASS record;
     - it cites that record's digest and path;
     - it repeats the record's four ladder fields.
   - When the step is taken, the record is re-read from its path and verified against its log. On replay from
     JSON, the embedded record is re-checked.
   - `kernel_records.climb` takes the step from a record path.
   - In the registry, an entry at KERNEL_CHECKED or above needs `kernel_evidence` that passes the same check.
     `Registry.record_kernel_check`, and its API endpoint, climb an entry from STATEMENT_AUDITED. The endpoint
     accepts only records under `records/kernel/`.
   - FAIL and BLOCKED records are refused. So is a record whose log or digest does not match, and so is
     hand-written evidence.
5. **Records are published as artifacts and proposed by pull request.**
   - The `publish` job collects the records and writes a BLOCKED record for any expected check that left none
     (for example, a job cut off by its time limit).
   - It verifies every record. A record that does not match its log fails the job, and nothing is published.
   - It pushes the records to `records/kernel/<date>-run<id>/` on a new branch, based on the default branch, and
     opens a pull request.
   - A test re-verifies every committed record against its log.

## Consequences

- A claim can reach KERNEL_CHECKED, but only on a record a real run wrote. Claims that had hand-typed kernel
  evidence must be re-climbed from a record. The only one was the synthetic fixture in `tests/test_preregistration.py`.
- A Comparator check depends on the hosted runner: Landlock, disk, and a build that must finish within the
  job's time limit. When one of these fails, the record says BLOCKED and why. That is a statement about the
  environment, not about the proof.
- `LocalSmoothing.lean` in our examples is the challenge file: its theorems end in `sorry`. Its record is FAIL by
  design. The record shows that the statements elaborate, and that `sorryAx` keeps them off the KERNEL_CHECKED rung.
  The proofs are checked by the Comparator target for LocalSmoothing.
- INDEPENDENTLY_REPRODUCED still needs a second check by another party. A CI run of ours is not independent of us.
- The `examples/*/lean_check.txt` notes stay as history. The records in `records/kernel/` are the evidence.
