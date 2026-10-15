# Prompt for the coding agent on the Lenovo Legion

Paste the block below into the IDE agent running on the Legion. It is self-contained: the agent needs only this
repository and internet access. The owner does not run commands manually, so the agent does every step.

```text
You are working on the Lenovo Legion (Linux) for the CoResearcher repository
(https://github.com/Fundacion-de-Neurociencias/coresearcher). Do every step yourself; the owner does not run
commands manually. Never print or commit secrets. Never push to master: work on a branch and open a pull request.

Goal 1 (required): run the Lean/Comparator label oracle for the openai/math pilot (71 challenges: 19 originals +
52 mutants) and record the result.

1. Clone the repo (or pull master), create a venv, `pip install -r requirements.txt -r requirements-dev.txt`,
   and check `python -m pytest -q` passes.
2. Read docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md (sections 2-4) and LEGION_RUNBOOK.md section 3. Follow
   them exactly; the procedure and criteria are pre-registered and must not be changed.
3. Check the machine, then install the toolchain (no sudo needed; everything goes under ~/oracle):
     PREFLIGHT_ONLY=1 bash scripts/benchmarks/legion/oracle_setup.sh
     bash scripts/benchmarks/legion/oracle_setup.sh
   If preflight fails, fix only what it names (for a missing systemd user session: `loginctl enable-linger $USER`
   and a new shell). The Mathlib cache download is slow; re-running the script resumes it.
4. With PATH="$HOME/oracle/bin:$HOME/.elan/bin:$PATH", follow LEGION_RUNBOOK.md section 3: `prepare`, build the
   19 solutions it lists, `run` (resumable, up to 3,600 s per challenge; timeouts are excluded, never counted as
   accept or reject), then `report`.
5. Interpret with the pre-registered criteria: the pipeline is sound only if every original copy is accepted;
   labels are valid if the lower 95% Wilson bound of "mutants rejected" is >= 0.9; every accepted mutant is label
   noise, listed by mutation type; recompute the pilot S1/B0/B1 figures without noisy labels as a sensitivity
   analysis.
6. Write docs/reference/benchmarks/LEAN_ORACLE_REPORT.md with the results, whatever they are, plus exact tool
   versions (Lean, landrun, lean4export, comparator commits). Update the related row of
   docs/reference/CLAIMS_REGISTER.md. Run `python scripts/check_repo_consistency.py`, `ruff check tests/ api/`,
   `black --check tests/ api/` and `python scripts/enforce_english_policy.py` (all repo text in English). Commit on
   branch `bench/lean-oracle`, push, open a PR, wait for CI to pass, and merge it.

Goal 2 (optional, only after Goal 1, if the GPU allows it): run the formalizer benchmark with the largest
instruction model that fits in GPU memory (for example qwen2.5:32b-instruct via Ollama), following
LEGION_RUNBOOK.md section 1. Do not change the prompt or the dataset. Add the results as a new column in
docs/reference/benchmarks/ROUND0_EXPLORATORY_RESULTS.md, in the same PR flow.

If something blocks you (missing permissions, Landlock unsupported by the kernel, no disk), stop and report
exactly what blocked and what you tried; do not work around safety checks.
```

## What the owner gets back

- A merged pull request with `LEAN_ORACLE_REPORT.md` and the updated claims register.
- If Goal 2 ran, a new model column in the round 0 formalizer results.
