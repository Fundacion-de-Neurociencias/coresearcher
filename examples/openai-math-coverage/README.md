# openai/math claim-vs-formal coverage map

Data for [docs/reference/cases/OPENAI_MATH_COVERAGE_MAP.md](../../docs/reference/cases/OPENAI_MATH_COVERAGE_MAP.md).
Source: [github.com/openai/math](https://github.com/openai/math) (Apache-2.0), commit
`4eaee87548250b2682affda7d05d947c05554bae`. No upstream file is copied here; the dataset quotes headline sentences and
Comparator theorem names.

| File | Content |
|---|---|
| `judgements.json` | Input. One reading judgement per headline claim of the 245 families with a Lean scope note (570 claims), each tagged `[inferred]`. |
| `coverage_map.json` | Output. Source pin and hashes, summary by discipline, calibration paper items, per-family parse, one row per headline claim (844). |
| `lint_open.json` | Output. OPEN junk-value findings (`lean_junk_lint`) of the 546 Comparator targets. |
| `vacuity_probe.json` | Output. Trivial-witness probe: stage 1 (z3) results per target, the Lean probes with their outcome (NOT_RUN until run on a Lean machine), the degenerate-witness cases. |

Rebuild: `python scripts/cases/openai_math_coverage_report.py --corpus <checkout>` (or `--fetch <empty dir>`).
Probe: `python scripts/cases/trivial_witness_probe_report.py static --corpus <checkout>`; the Lean stages use `prepare`, `run`, `report` on a built checkout.
