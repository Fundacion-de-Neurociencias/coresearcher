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

## What comes back to the repository

Run files (`runs/`) stay on the Legion unless they contain no confidential text. Reports, hashes and claims-register
updates are committed through a pull request.
