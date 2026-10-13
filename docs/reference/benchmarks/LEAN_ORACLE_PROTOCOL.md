# Lean oracle for the openai/math pilot: protocol and runbook

Status: written before any Lean run. Script:
[`scripts/benchmarks/openai_math_lean_oracle.py`](../../../scripts/benchmarks/openai_math_lean_oracle.py).

## 1. What this measures, and what it does not

Comparator checks that a Lean proof establishes a given formal statement. This step uses it as an
**oracle for the pilot labels**: each mutant should no longer be provable with the paper's own proof.

It does **not** measure whether a formal statement matches its prose. A Lean-based check of prose fidelity
needs an extra step (section 6).

## 2. Procedure (pre-registered)

- Source: openai/math at commit `1581d4cbdd69a0faf34b2089614fe2a814316a6a`, the same commit as the pilot.
- Inputs: the 19 pairs and 52 mutants of
  [`openai_math_pilot_dataset.json`](openai_math_pilot_dataset.json), unchanged.
- For each pair: one copy of the original Comparator challenge (control) and one challenge per mutant, each
  checked by Comparator against the paper's existing solution module, with the original `permitted_axioms`.
- One Comparator run per challenge. A run that exceeds the timeout (default 3,600 s) is recorded as a timeout
  and excluded from the rates. It is not counted as an acceptance or a rejection.

## 3. Pre-registered criteria

- **Pipeline sound:** every completed original-copy run is accepted. If not, the setup is broken and no label
  conclusion is drawn.
- **Labels valid:** the lower bound of the 95% Wilson interval for "mutants rejected" is at least 0.9.
- Every accepted mutant is listed as **label noise**, by mutation type. Such a mutant did not change what the
  proof establishes, so the pilot's "mismatch" label for it was wrong.
- The pilot's S1/B0/B1 figures are then recomputed **without** the noisy labels, as a sensitivity analysis,
  and reported next to the originals.

## 4. Runbook for the Linux machine (Lenovo Legion)

Comparator needs Linux: it sandboxes the build with `landrun` (Landlock) and must not run as root. Steps
marked *(official)* follow the Comparator or openai/math READMEs; the others are ordinary setup.

1. **System.** Recent Linux with Landlock support, a systemd user session, a non-root user, and enough disk
   for Mathlib's cache plus the project's dependencies. Check free space before downloading.
2. **Lean.** Install `elan`. The project pins `leanprover/lean4:v4.34.1` through `lean/lean-toolchain`, and
   `elan` picks it up automatically.
3. **openai/math at the pinned commit.**
   ```bash
   git clone https://github.com/openai/math.git openai-math
   cd openai-math && git checkout 1581d4cbdd69a0faf34b2089614fe2a814316a6a
   cd lean && lake exe cache get
   ```
   *(official)* If compiling fails with memory-map errors, raise `vm.max_map_count` or set
   `GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.arena_max=1` (openai/math `lean/README.md`).
4. **Comparator tools** *(official)*: build `landrun` from its `main` branch, `lean4export` at a version
   compatible with Lean v4.34.1, and `comparator` from `leanprover/comparator`. Put all three on `PATH`, or
   set `COMPARATOR_LANDRUN` and `COMPARATOR_LEAN4EXPORT`.
5. **CoResearcher.** Check out the branch that contains this script and the pilot dataset.
6. **Prepare** (writes 71 challenges into `lean/ComparatorChallenges/OracleMutants/` of the openai/math
   checkout, plus a manifest; no Lean needed):
   ```bash
   python scripts/benchmarks/openai_math_lean_oracle.py prepare --math-root ../openai-math
   ```
7. **Build the solutions** it lists (19 `lake build OAI...` commands), from `openai-math/lean`. Build them
   before any challenge is compiled (Comparator README, assumption 2).
8. **Run**, resumable (it can be interrupted and restarted):
   ```bash
   python scripts/benchmarks/openai_math_lean_oracle.py run --math-root ../openai-math
   ```
   Each run uses `systemd-run --property=RestrictAddressFamilies=~AF_UNIX --user` *(official)*.
9. **Report** and commit the output:
   ```bash
   python scripts/benchmarks/openai_math_lean_oracle.py report --math-root ../openai-math
   ```
   This writes `docs/reference/benchmarks/openai_math_lean_oracle_results.json`.

## 5. Already verified on Windows (without Lean)

`prepare` was run against a minimal mirror of the pinned commit: 71 challenges from 19 pairs, no problems.
The generated mutants were checked by hand. `report` was checked with synthetic outcomes, and `run` refuses
to start outside Linux. No Comparator result exists yet.

## 6. Next step (design only): a Lean-based fidelity auditor

Answering the prose-fidelity question with Lean needs one more component:

1. **Autoformalize** the scope prose with a local model on the Legion, producing a Lean statement `S_p`.
2. **Check equivalence** with the reference statement `S_ref` by trying to prove `S_p ↔ S_ref` with a bounded
   tactic search and a fixed time limit. Outcome: equivalent, not shown, or a refuted direction.
3. **Evaluate** on the same originals and validated mutants. An original should come out equivalent; a mutant
   should not.

The main risk is autoformalization errors, which produce false alarms on originals. Model choice, prompt and
time limits must be fixed in a protocol before the first run.
