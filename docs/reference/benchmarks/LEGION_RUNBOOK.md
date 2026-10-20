# Runbook for the Lenovo Legion

Everything in CoResearcher that needs a local model or a Lean toolchain runs on the Lenovo Legion (Linux). The
development laptop has neither. This runbook lists the four jobs in the order they should run, with the exact
commands. Each job writes raw outputs first and scores them offline, so a run can be audited and re-scored without
repeating it.

## 0. Setup (once)

1. Clone the repository and install it with the formal back end:

   ```bash
   git clone https://github.com/Fundacion-de-Neurociencias/coresearcher.git && cd coresearcher
   python3 -m venv .venv && . .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   python -m pytest -q
   ```

2. **Local model server.** Install Ollama (or LM Studio with its OpenAI-compatible server) and pull the candidate
   models. Record each exact tag; results are only comparable for the same tag. Example:

   ```bash
   ollama pull qwen2.5:14b-instruct-q4_K_M
   export FORMALIZER_BASE_URL=http://localhost:11434/v1
   export FORMALIZER_MODEL=qwen2.5:14b-instruct-q4_K_M
   ```

   If Laya is served through an OpenAI-compatible endpoint, point the same variables at it. Put the variables in a
   git-ignored `.env`, never in a committed file. If the endpoint needs a key, set `FORMALIZER_API_KEY` there too.

3. **Lean and Mathlib** (jobs 3 and 4). Install `elan`, then create a Lake project that depends on Mathlib and fetch
   the cache (`lake exe cache get`). Check free disk space first: the Mathlib cache needs several gigabytes.

## 1. Formalizer benchmark (ADR-DISCOVERY-061)

Protocol: [FORMALIZER_BENCH_PROTOCOL.md](FORMALIZER_BENCH_PROTOCOL.md). Freeze the dataset after the scientists'
review, then run each candidate model with and without the variable schema:

```bash
python scripts/benchmarks/formalizer_bench.py gold-check
python scripts/benchmarks/formalizer_bench.py run --out runs/formalizer_<tag>.jsonl
python scripts/benchmarks/formalizer_bench.py run --out runs/formalizer_<tag>_noschema.jsonl --no-schema
python scripts/benchmarks/formalizer_bench.py score --responses runs/formalizer_<tag>.jsonl \
    --out docs/reference/benchmarks/FORMALIZER_BENCH_REPORT_<tag>.md
```

Report the parse rate, the vacuous, unfalsifiable and self-contradictory rates, spurious and missed defects, and
equivalence to gold. Update row 24 of the claims register with the result, whatever it is.

## 2. Concordance pilot, LLM arm (protocol section 7a)

Run only after the 20 pilot tasks are frozen, and before any judgment is opened:

```bash
python scripts/benchmarks/concordance_score.py validate --tasks tasks/round1
python scripts/benchmarks/concordance_score.py seal --tasks tasks/round1 --out sealed/coresearcher_round1.json
python scripts/benchmarks/concordance_llm_arm.py run --tasks tasks/round1 --out sealed/llm_round1.json
```

Record both printed SHA-256 hashes in the ledger and in the freeze table of
[CONCORDANCE_PILOT_ROUND1.md](CONCORDANCE_PILOT_ROUND1.md). Confidential tasks never leave this machine.

## 3. Lean oracle for the openai/math pilot

Protocol: section 4 of [LEAN_ORACLE_PROTOCOL.md](LEAN_ORACLE_PROTOCOL.md) (Comparator with `landrun`, non-root
user, pinned openai/math commit). It runs the 19 original challenges and 52 mutants (71 challenges). An agent can do
all of it from [LEGION_AGENT_PROMPT.md](LEGION_AGENT_PROMPT.md).

**Requirements**, checked by the preflight: Linux with Landlock in the kernel, a non-root user, a systemd user
session (`systemd-run --user`), at least 30 GB free. No sudo is needed.

**1. Toolchain.** The script installs elan, clones openai/math at the pinned commit, fetches the Mathlib cache,
installs Go under `~/go-sdk`, builds `landrun` (main) and builds `lean4export` and `comparator` for the pinned Lean
version, all under `~/oracle`. It is idempotent and resumable:

```bash
PREFLIGHT_ONLY=1 bash scripts/benchmarks/legion/oracle_setup.sh
bash scripts/benchmarks/legion/oracle_setup.sh
export PATH="$HOME/oracle/bin:$HOME/.elan/bin:$PATH"
```

**2. Prepare, build, run, report:**

```bash
M=~/oracle/openai-math
python scripts/benchmarks/openai_math_lean_oracle.py preflight --math-root $M
python scripts/benchmarks/openai_math_lean_oracle.py prepare --math-root $M
# build the 19 solutions it lists, from $M/lean:  lake build OAI...
python scripts/benchmarks/openai_math_lean_oracle.py preflight --math-root $M   # must pass
python scripts/benchmarks/openai_math_lean_oracle.py run --math-root $M
python scripts/benchmarks/openai_math_lean_oracle.py report --math-root $M
```

`prepare` and `report` need no Lean toolchain. `run` is resumable; `--timeout` (seconds per challenge) defaults to
the protocol's 3,600. `report` writes `docs/reference/benchmarks/openai_math_lean_oracle_results.json`; the agent
then writes `LEAN_ORACLE_REPORT.md` and updates the claims register.

**Notes from the trial** (Ubuntu 24.04 under WSL2, 4 cores, 7 GB RAM; stopped during the cache download
to leave the run to the Legion):

- WSL2 kernel 5.15 has Landlock, and a user-level install works without sudo.
- WSLg sets `XDG_RUNTIME_DIR` to its own directory; the script switches to `/run/user/UID` when the user bus is
  there. Without a lingering user manager, `systemctl --user` fails: `loginctl enable-linger $USER` fixes it.
- The Mathlib cache (about 9,000 files) downloaded at 10 to 200 KB/s on that link: plan an hour or more on a slow
  connection. Re-running the script resumes.
- With 7 GB of RAM the run is expected to take many hours; the Legion's memory and cores shorten it.
- If the kernel's Landlock ABI is below v9, the systemd user session is the only guard against UNIX sockets (protocol, step 1), so do not bypass it.

## 4. Lean kernel check of z3 entailments (ADR-DISCOVERY-060)

```bash
python scripts/benchmarks/formal_lean_check.py export --out-dir runs/lean_checks
python scripts/benchmarks/formal_lean_check.py run --out-dir runs/lean_checks --project ~/mathlib-project \
    --out runs/lean_checks/results.json
```

Expected with the current default tactic: 12 of the 12 entailed checks PROVED and the 4 others NOT_PROVED (the
result on a Linux container with Mathlib modules built from source; see section 2b of the round 0 results).
A theorem that z3 rejects and Lean proves is a soundness discrepancy: the command exits with status 1, and neither
back end should be trusted until it is explained. A theorem z3 accepts but the default tactic cannot prove is not a
contradiction; it is reported as `NOT_PROVED`.

## 5. Unknown-mechanism v3, PySR arm

Protocol: [UNKNOWN_MECHANISM_V3_PROTOCOL.md](UNKNOWN_MECHANISM_V3_PROTOCOL.md). The library (L) and ridge (R) arms
have no Julia dependency and may already have run elsewhere. They are kept in the same raw file. This job runs the
PySR arm, on real and null data:

```bash
pip install pysr==2.7.0          # the first import installs Julia and SymbolicRegression.jl ~2.7.0
python -c "import pysr"          # one-off download and precompilation; needs internet access
python scripts/benchmarks/run_unknown_mechanism_v3.py run --arm P
python scripts/benchmarks/run_unknown_mechanism_v3.py run --arm P --null
python scripts/benchmarks/run_unknown_mechanism_v3.py score
```

Both `run` commands are resumable. Expect several hours for the 200 searches. Commit
`unknown_mechanism_v3_raw.jsonl` and `unknown_mechanism_v3_results.json`, then update row 18 of the claims
register with the criteria as they came out.

## 6. Unknown-mechanism v4, PySR and language-model arms

Protocol: [UNKNOWN_MECHANISM_V4_PROTOCOL.md](UNKNOWN_MECHANISM_V4_PROTOCOL.md). The oracle (O), library (L) and ridge
(R) arms need only numpy and scipy and may already have run elsewhere. This job runs the PySR arm (P) and the local
language-model arm (E), on real and null data. E uses `qwen2.5:14b-instruct-q4_K_M` from setup step 2.

```bash
python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm P
python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm P --null
FORMALIZER_BASE_URL=http://localhost:11434/v1 python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm E
FORMALIZER_BASE_URL=http://localhost:11434/v1 python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm E --null
python scripts/benchmarks/run_unknown_mechanism_v4.py score
```

Every `run` command is resumable. Commit `unknown_mechanism_v4_raw.jsonl` and `unknown_mechanism_v4_results.json`,
then update the claims-register row for v4 with the criteria as they came out.

## 7. Counterexample search, proposer arm (P)

Protocol: [COUNTEREXAMPLE_SEARCH_PROTOCOL.md](COUNTEREXAMPLE_SEARCH_PROTOCOL.md). Arms E (exact evaluator) and R (random
search) have already run here, and their raw records are committed. This job runs only arm P, the local language model
proposing states. It does not change the protocol, the corpus or the scoring. If anything in this section conflicts
with the protocol, the protocol wins, and the session stops and reports the conflict.

```bash
git pull origin claude/stoic-turing-eb2nk2
. .venv/bin/activate                            # the venv from section 0
export FORMALIZER_BASE_URL=http://localhost:11434/v1
export FORMALIZER_MODEL=qwen2.5:14b-instruct-q4_K_M
ollama pull qwen2.5:14b-instruct-q4_K_M        # the same tag as the formalizer benchmark
python scripts/benchmarks/run_counterexample_search.py run --arm P
python scripts/benchmarks/run_counterexample_search.py score
```

- This job cannot run from the cloud sandbox: it has no access to `ollama.com` or `huggingface.co`, so the model must be
  pulled on the Legion, which has network access. If `ollama list` does not show the tag above, run `ollama pull` first.
- `run` is resumable. It skips items already recorded under the same protocol hash, so an interrupted job can simply be
  restarted with the same command.
- Check first that the corpus and the protocol are unchanged: `python scripts/benchmarks/run_counterexample_search.py
  score` must print the validity block for E and R before the P run starts. Its protocol hash must match the one in the
  committed results file.
- Expect about 200 items × 5 model calls. Each call should take well under a minute on this machine; if one call
  takes longer, let it finish, do not change timeouts or prompts.
- Do not edit the prompt, the seeds or the budget. Do not drop items. A failed call is recorded as no candidates for that
  call, which the script already does; report the count of failed calls, do not retry them by hand.

Commit `counterexample_raw.jsonl` (the P rows are appended to the same file) and `counterexample_results.json`, then
update the claims-register row for this benchmark with the criteria as they came out. Report the four numbers the
scoring prints: detection on planted items for P, R and E, the false detections on correct items (must be 0), and the
criteria A and S with their intervals. Do not report a result that the scoring does not produce.

## 8. Hypothesis inspiration and falsifiability pilot (not yet runnable)

Protocols: [HYPOTHESIS_INSPIRATION_PROTOCOL.md](HYPOTHESIS_INSPIRATION_PROTOCOL.md) and
[FALSIFIABILITY_PILOT_PROTOCOL.md](FALSIFIABILITY_PILOT_PROTOCOL.md). Both are drafts, and nothing in them has run.
This section says what the Legion session can do now and what must be decided first. Do not start a run from this
section alone.

### 8.1 Model configuration (decided 2026-10-20, recorded in both protocols)

Only Ollama with Qwen 2.5 is available, so:

1. **Formalizer** (falsifiability pilot): `qwen2.5:14b-instruct-q4_K_M`. Not installed on the Legion yet: pull it.
2. **Generator for C1** (inspiration protocol): `qwen2.5:14b-instruct-q4_K_M`.
3. **Rubric judge** (falsifiability pilot) and **judge** (inspiration protocol): `qwen2.5-coder:32b`. Pull it if absent.
4. **Frontier comparators F1 and F2: removed.** The inspiration protocol therefore supports only an exploratory C1
   rate against its random-reference floor. It cannot test the DiscoveryRSI comparison.

Record the exact tags and digests (`ollama show <tag>`) in the first raw record of each run.

**Host and status (2026-10-20).** The Ollama host is a Mac Studio, not the Legion machine. Run every command in this
section on that machine with `FORMALIZER_BASE_URL=http://localhost:11434/v1`. Network addresses of the host are kept
out of this repository; set them only in the local `.env`.

- Pulled: `qwen2.5-coder:32b` (judge and rubric judge).
- Not yet pulled: `qwen2.5:14b-instruct-q4_K_M` (formalizer and C1 generator). Pull it before section 8.3.
- **Never use `manuel-sovereign:32b` in any arm.** It is a derived model with a personal system prompt injected from
  a private vault. Using it as a judge, generator or formalizer would put those criteria into the measurement.
  Every arm uses an unmodified base tag.
- Optional judge: a 30B Nemotron model is present on the host. It belongs to a different model family from the Qwen
  generator, which would reduce the family correlation reported in both protocols. Adopting it needs its exact tag
  (`ollama list`) and a protocol revision committed before any run. Until then, `qwen2.5-coder:32b` stays the judge.

### 8.2 Required code that does not exist yet

- A **question-bank generator** for the inspiration protocol (200 questions, seed `61000`, four domains).
- The **citation-traversal reference corpus** (section 5.3) and its date rule.
- The **hypothesis generator** for the falsifiability pilot, which must produce up to 300 hypotheses from a frozen
  question bank (seed `62000`).
- **Self-improvement arms C2 to C4**: CoResearcher has no per-hypothesis credit assignment or harness replay. The
  primary and mechanism contrasts of the inspiration protocol are therefore not runnable.

### 8.3 Falsifiability pilot, what can run once 8.1 and 8.2 are done

Model prerequisites are the same as in section 0, step 2:

```bash
ollama pull qwen2.5:14b-instruct-q4_K_M
export FORMALIZER_BASE_URL=http://localhost:11434/v1
export FORMALIZER_MODEL=qwen2.5:14b-instruct-q4_K_M
```

Then, in order, and each step recorded with its hash:

1. Freeze the question bank and the generator prompt. Commit them.
2. Generate the hypotheses, then formalize each with the pinned formalizer. Keep only those that pass the
   self-consistency gate (ADR-DISCOVERY-064). Record every exclusion with its reason.
3. Compute the exact measure with the formal evaluator: content verdict and forbidden fraction (protocol section 4).
4. Score each hypothesis with the rubric judge, three reviews, median (protocol section 3.3).
5. Analyse Q1 and Q2 as written. Q3 is not run.

Report, for each arm: the exclusion rate, kappa with its interval, the informative share, and the exact model
versions and prompt hashes. Do not report Q3, and do not change the threshold of 0.05 after seeing any result.

### 8.4 Inspiration protocol

Nothing in 8.4 can run until 8.2 is complete. With the configuration in 8.1, only the exploratory C1 analysis is
possible. Once they are, the Legion session follows section 5 of the
protocol in order: question bank, reference corpus, retrieval with the whole-proposal query, judge with the random
identifier, human validation sample, random-reference control, then cluster-bootstrap analysis. Report every arm
with its denominator, and report the human-validation gate result before any judged rate.

## What comes back to the repository

Run files (`runs/`) stay on the Legion unless they contain no confidential text. Reports, hashes and claims-register
updates are committed through a pull request.
