# Kernel records

Records written by the `Lean kernel checks` workflow (`.github/workflows/lean-kernel.yml`, ADR-DISCOVERY-092). Each run
adds a directory `<date>-run<id>/` with one `<target>.json` record and its `<target>.log` per check.

- A record's `result` is PASS, FAIL or BLOCKED, computed from its log by `python/discovery/kernel_records.py`.
- Only a PASS record that still matches its log lets a claim climb to KERNEL_CHECKED.
- `tests/test_kernel_records.py` re-verifies every record here against its log. Do not edit records or logs by hand.

Verify a run's records with `python scripts/lean/kernel_check.py verify records/kernel/<dir>`.

`2026-11-03-probe-lenovo/` is different: it holds the trivial-witness probe records (docs/reference/cases/OPENAI_MATH_COVERAGE_MAP.md §5.1), written by `scripts/cases/trivial_witness_probe_report.py` on the Lenovo WSL machine (`checked_by: local:…`). Their theorems are probe declarations, not claims. A PASS on a `trivial` or `inconsistent` probe would be a vacuity finding. None occurred.
