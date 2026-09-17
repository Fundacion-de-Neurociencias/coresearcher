"""TRACES Epistemic Meta-Evaluation Benchmark CLI Runner.

Executes CoResearcher's TRACES Epistemic Adapter across 3 difficulty tiers:
1. Dry Substrate (Synthetic World with Hidden Invariants)
2. Damp Substrate (Historical Clinical & Astrophysical Cohorts)
3. Wet Substrate (Physical Lab-in-the-Loop Microfluidics)

Computes the 5 Epistemic Meta-Metrics:
- DV: Discovery Value
- RCS: Reality Contact Score (0 to 4)
- FRI: Failure Recovery Index
- SG: Bayesian Surprise Gain (bits)
- CSR: Constraint Survival Rate
"""

import sys
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from python.discovery.traces_epistemic_adapter import TracesEpistemicAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
console = Console(force_terminal=True, legacy_windows=False)

def run_traces_epistemic_suite():
    console.print(Panel.fit(
        "[bold cyan]CORESEARCHER EPISTEMIC TRACES ADAPTER & META-BENCHMARK[/bold cyan]\n"
        "[dim]Elevating TRACES from Surface Tool-Use Capabilities to Rigorous Epistemological Meta-Metrics[/dim]",
        box=box.DOUBLE_EDGE
    ))

    # Benchmark run on 3 tiers
    cases = [
        {
            "id": "CASE-DRY-BROADBOX",
            "title": "Hidden Invariant Gene Repression Rule (Synthetic Dry Oracle)",
            "tier": "DRY_SYNTHETIC",
            "traces": {"Tools": 0.90, "Repair": 0.85, "Alternatives": 0.80, "Coherence": 0.95, "Evidence": 0.70, "Scope": 0.80},
            "falsifications": 3,
            "revisions": 3,
            "invariants": 2,
            "survived": 2,
            "prior": 0.05,
            "p_val": 0.0001,
            "pruned": 0.4200
        },
        {
            "id": "CASE-DAMP-METABOAD",
            "title": "Tauopathy Connectome Spreading vs Metabolic Gating (MetaboAD Cohort)",
            "tier": "DAMP_HISTORICAL",
            "traces": {"Tools": 0.88, "Repair": 0.75, "Alternatives": 0.85, "Coherence": 0.90, "Evidence": 0.82, "Scope": 0.78},
            "falsifications": 4,
            "revisions": 3,
            "invariants": 2,
            "survived": 2,
            "prior": 0.15,
            "p_val": 0.0005,
            "pruned": 0.3958
        },
        {
            "id": "CASE-WET-MICROFLUIDICS",
            "title": "Closed-Loop Microfluidic Tau Clearance Protocol (Physical Instrumentation)",
            "tier": "WET_PHYSICAL",
            "traces": {"Tools": 0.95, "Repair": 0.80, "Alternatives": 0.88, "Coherence": 0.92, "Evidence": 0.95, "Scope": 0.85},
            "falsifications": 2,
            "revisions": 2,
            "invariants": 1,
            "survived": 1,
            "prior": 0.10,
            "p_val": 0.00001,
            "pruned": 0.4500
        }
    ]

    table = Table(
        title="CoResearcher Epistemic Meta-Evaluation of TRACES Benchmark Runs",
        box=box.ROUNDED,
        header_style="bold magenta",
        show_lines=True
    )

    table.add_column("Benchmark Case", style="bold yellow", width=20)
    table.add_column("Substrate Tier", style="cyan", width=16)
    table.add_column("TRACES Score", justify="center", style="dim", width=12)
    table.add_column("Discovery Value (DV)", justify="right", style="bold white", width=16)
    table.add_column("Reality Contact (RCS)", justify="center", style="bold yellow", width=14)
    table.add_column("Failure Recovery (FRI)", justify="right", style="bold green", width=16)
    table.add_column("Surprise Gain (SG)", justify="right", style="bold magenta", width=14)
    table.add_column("Constraint Survival (CSR)", justify="right", style="bold cyan", width=16)
    table.add_column("Epistemic Verdict", style="bold", width=22)

    for c in cases:
        report = TracesEpistemicAdapter.evaluate_benchmark_run(
            instance_id=c["id"],
            problem_title=c["title"],
            substrate_tier=c["tier"],
            raw_traces_results=c["traces"],
            falsifications_count=c["falsifications"],
            successful_revisions_count=c["revisions"],
            promoted_invariants_count=c["invariants"],
            surviving_invariants_after_k_campaigns=c["survived"],
            prior_p=c["prior"],
            empirical_p_val=c["p_val"],
            state_space_pruned_fraction=c["pruned"]
        )

        table.add_row(
            f"{report.benchmark_instance_id}\n[dim]{report.target_problem_title[:35]}...[/dim]",
            report.substrate_tier,
            f"{report.traces_overall_score:.1%}",
            f"DV = {report.discovery_value_dv:.3f}",
            f"Level {report.reality_contact_score_rcs}/4",
            f"{report.failure_recovery_index_fri:.1%}",
            f"{report.surprise_gain_sg_bits:.2f} bits",
            f"{report.constraint_survival_rate_csr:.1%}",
            f"[green]{report.epistemic_verdict}[/green]"
        )

    console.print(table)

    console.print("\n[bold cyan]Key Strategic Differentiation:[/bold cyan]")
    console.print("[dim]• TRACES measures execution capabilities: 'Did the LLM call a tool and format output?'[/dim]")
    console.print("[dim]• CoResearcher measures discovery epistemology: 'Did the hypothesis earn reality, survive Duhem-Quine falsification, prune impossible state space, and maintain invariant stability over time?'[/dim]\n")

if __name__ == "__main__":
    run_traces_epistemic_suite()
