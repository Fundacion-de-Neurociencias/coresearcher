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

Steps 2 to 4 are scripted: as the non-root user, run
`bash scripts/benchmarks/legion_lean_oracle_setup.sh [TOOLS_DIR] [MATH_ROOT]` (defaults `~/oracle-tools` and
`~/openai-math`), then `python scripts/benchmarks/openai_math_lean_oracle.py preflight --math-root MATH_ROOT`.
The preflight checks every item below and exits 1 while a required one is missing.

1. **System.** Recent Linux with Landlock support, a systemd user session, a non-root user, and enough disk
   for Mathlib's cache plus the project's dependencies. Check free space before downloading.
   - **Landlock ABI and the systemd guard.** `landrun` from `main` asks for Landlock ABI v9. Comparator calls it
     with `--best-effort`, so on an older kernel (Linux 6.18 reports ABI v7) it falls back to a sandbox that does
     not restrict UNIX sockets, without any error. The `systemd-run --property=RestrictAddressFamilies=~AF_UNIX
     --user` wrapper then is the only guard against that, so a working systemd user session is required, not
     optional. The preflight reports the ABI and tests the wrapper. `COMPARATOR_CMD` bypasses the wrapper and is
     for local tests only.
2. **Lean.** Install `elan`. The project pins `leanprover/lean4:v4.34.1` through `lean/lean-toolchain`, and
   `elan` picks it up automatically.
3. **openai/math at the pinned commit.**
   ```bash
   git clone https://github.com/openai/math.git openai-math
   cd openai-math && git checkout 1581d4cbdd69a0faf34b2089614fe2a814316a6a
   cd lean && lake exe cache get
   ```
   Do not run `lake update` (the openai/math challenge README does): the manifest is part of the pinned
   commit, and updating would move the dependencies.
   *(official)* If compiling fails with memory-map errors, raise `vm.max_map_count` or set
   `GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.arena_max=1` (openai/math `lean/README.md`).
4. **Comparator tools** *(official)*: build `landrun` from its `main` branch, `lean4export` at a version
   compatible with Lean v4.34.1, and `comparator` from `leanprover/comparator`. Put all three on `PATH`, or
   set `COMPARATOR_LANDRUN` and `COMPARATOR_LEAN4EXPORT`.
   - Pinned versions: `lean4export` and `comparator` at their `v4.34.0` tags (`076e8e5` and `d03acab`; the
     Comparator tag pins that same `lean4export`), both built with the project toolchain `v4.34.1` by overriding
     their `lean-toolchain`. `.olean` files record the Lean version that wrote them, and both tools read the
     project's files. No `v4.34.1` tags exist upstream. The setup script records the exact commits in
     `TOOLS_DIR/tools.txt`; copy that file into the results commit.
   - Standalone Comparator is deprecated upstream: from Lean v4.35.0 it ships in core as `lake comparator` and
     `lake check`. openai/math pins v4.34.1, so this protocol keeps the standalone tool. Moving to v4.35 would
     change the pinned commit and is out of scope for this pilot.
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

## 5b. Linux runs

### Lenovo Legion, full run (2026-10-17)

**Environment.** The Legion runs Windows 11 Pro; the oracle ran in **WSL2** (Ubuntu 26.04 LTS, kernel
`6.6.114.1-microsoft-standard-WSL2`, Landlock ABI **v3**), on an Intel Core Ultra 9 275HX with 24 threads and
31 GB of RAM assigned to WSL, on the Linux file system (not `/mnt/c`). Systemd was enabled in WSL, the user
manager kept alive with `loginctl enable-linger`, and every step ran as an unprivileged user (uid 1000).
Tool commits, as written by the setup script, are in
[`openai_math_lean_oracle_tools.txt`](openai_math_lean_oracle_tools.txt): openai/math `1581d4c`, Lean v4.34.1,
`landrun` `ec104f6` (`main`), `lean4export` `076e8e5` and `comparator` `d03acab` (both `v4.34.0` tags).

**Sandbox.** Landlock ABI v3 is below v9, so `landrun --best-effort` does not restrict UNIX sockets. Every run went
through the `systemd-run --property=RestrictAddressFamilies=~AF_UNIX --user` guard (step 8); `COMPARATOR_CMD` was
not set. The final `preflight` passed with only the expected ABI warning.

**Setup deviation (build only, no change to the procedure).** The openai/math lakefile applies its compatibility
patches for 12 dependencies (`rellich-kondrachov`, `carleson`, `PrimeNumberTheoremAnd` and 9 more) only in its
`post_update` hook, which runs on `lake update` alone. Step 3 forbids `lake update`, so the first build of the 19
solution modules failed in `rellich-kondrachov`. The 12 patches from the pinned commit's `patches/` directory were
applied with `git apply`, with the same forward and reverse checks as the hook; no dependency commit moved. The
setup script now does this, and `tools.txt` lists the patched packages. The 19 modules then built without errors
(14,454 jobs, 23 minutes).

**Result** ([`openai_math_lean_oracle_results.json`](openai_math_lean_oracle_results.json)). 71 runs, no timeouts,
78 minutes in total. The longest run was F275_ORIGINAL (12.7 minutes, about 21 GB of memory in use).

| | Result | 95% Wilson interval |
| --- | --- | --- |
| Originals accepted | 19/19 | 0.832–1.000 |
| Mutants rejected | 52/52 | 0.931–1.000 |
| M1 numeric literal | 9/9 | 0.701–1.000 |
| M2 order relation | 9/9 | 0.701–1.000 |
| M3 quantifier | 10/10 | 0.722–1.000 |
| M4 hypothesis removed | 5/5 | 0.566–1.000 |
| M5 negation | 19/19 | 0.832–1.000 |

- **Pipeline sound: met.** Every original copy was accepted.
- **Labels valid: met.** The lower bound 0.931 is at least 0.9.
- **Label noise: none.** No mutant was accepted.
- **Sensitivity analysis** ([`openai_math_oracle_sensitivity.json`](openai_math_oracle_sensitivity.json), script
  [`openai_math_oracle_sensitivity.py`](../../../scripts/benchmarks/openai_math_oracle_sensitivity.py)). With no
  noisy labels to remove, the S1/B0/B1 figures are unchanged: S1 8/52 flagged, 17/19 passed, AUROC 0.524
  (0.500–0.561); B0 0/52, 19/19, 0.500; B1 14/52, 16/19, 0.553 (0.519–0.588). The script first reproduces the
  published pilot figures exactly, then recomputes them.

**How the mutants were rejected.** 45 runs ended with Comparator's "challenge and solution theorem statement do
not match". The other 7 failed earlier, because the mutated challenge file did not compile:

- 4 are real changes of meaning. In families 115 and 275 the pilot extracted a helper lemma that is proved inside
  the challenge file, and the mutation breaks that proof (F115_M2, F115_M4, F115_M5, F275_M5).
- 3 are **ill-formed mutants**, a defect of the mutation operators: M3 turned `∀` into `∃` over instance binders
  such as `[Fintype F]`, which `∃` does not accept (F231_M3, F243_M3), and M5 left a parenthesis unclosed in a
  multi-line statement (F277_M5). Their rejection says nothing about the labels.

Supplementary, not pre-registered: without the 3 ill-formed mutants, 49/49 are rejected (lower bound 0.927); S1
flags 8/49 (AUROC 0.529) and B1 13/49 (AUROC 0.550). Without all 7 build failures, 45/45 (lower bound 0.921). The
conclusions do not change.

**What this does and does not show.** Comparator compares the challenge statement with the one the solution proves.
A mutant is accepted only if it leaves that statement unchanged, so this oracle can find mutants that changed
nothing, but not mutants that changed the text into a logically equivalent statement. Within that limit, the
pilot labels hold, and the null result for S1 (claims register, row 19) is not an artefact of label noise.

### Cloud container, before the Legion (2026-10-15)

On a Linux cloud container (kernel 6.18, Landlock ABI v7, no systemd user session):

- `prepare` on a real checkout of openai/math at the pinned commit: 71 challenges from 19 pairs, no problems.
- `landrun` (`main`, `811cfff`), `lean4export` and `comparator` (both `v4.34.0` tags) built with Lean
  v4.34.1 as described in step 4.
- Comparator, with the real `landrun` and as a non-root user, accepted its `simple_match` test project and
  rejected `simple_mismatch`. This was run without the systemd guard, which needs a user session the container
  does not have.
- `preflight` reported the expected failures there: no systemd user session, no Mathlib cache, 0 of 19
  solution modules built. The Mathlib cache host was not reachable from the container, so nothing in openai/math
  was compiled and no oracle result exists yet.

## 6. Next step (design only): a Lean-based fidelity auditor

Answering the prose-fidelity question with Lean needs one more component:

1. **Autoformalize** the scope prose with a local model on the Legion, producing a Lean statement `S_p`.
2. **Check equivalence** with the reference statement `S_ref` by trying to prove `S_p ↔ S_ref` with a bounded
   tactic search and a fixed time limit. Outcome: equivalent, not shown, or a refuted direction.
3. **Evaluate** on the same originals and validated mutants. An original should come out equivalent; a mutant
   should not.

The main risk is autoformalization errors, which produce false alarms on originals. Model choice, prompt and
time limits must be fixed in a protocol before the first run.
