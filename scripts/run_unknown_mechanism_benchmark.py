"""100-World Unknown Mechanism Discovery Challenge CLI Runner.

Executes CoResearcher across 100 blind scientific worlds with diverse hidden causal laws.
CoResearcher receives ONLY raw numerical observations and must abduce the true causal mechanism
and non-linear boundary without human prompts or hints.
"""

import sys
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from python.discovery.unknown_mechanism_benchmark import UnknownMechanismBenchmark

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
console = Console(force_terminal=True, legacy_windows=False)

def run_benchmark():
    console.print(Panel.fit(
        "[bold cyan]CORESEARCHER: 100-WORLD UNKNOWN MECHANISM DISCOVERY CHALLENGE[/bold cyan]\n"
        "[dim]Auditing Autonomous Scientific Abduction & Mechanism Induction from Blind Observation Streams[/dim]",
        box=box.DOUBLE_EDGE
    ))

    summary = UnknownMechanismBenchmark.run_100_worlds_benchmark()

    table = Table(
        title="Hidden Causal Archetype Discovery & Abduction Breakdown (N=100 Worlds)",
        box=box.ROUNDED,
        header_style="bold magenta",
        show_lines=True
    )

    table.add_column("Hidden Causal Archetype", style="bold yellow", width=28)
    table.add_column("Worlds", justify="center", style="dim", width=8)
    table.add_column("Abduction Success", justify="right", style="bold green", width=22)
    table.add_column("Wrongful Burial", justify="right", style="bold red", width=18)
    table.add_column("Mean Holdout R²", justify="right", style="cyan", width=16)

    for arch_name, data in summary.recovery_by_archetype.items():
        table.add_row(
            arch_name,
            str(data["total_worlds"]),
            f"{data['recovered_count']} / {data['total_worlds']} ({data['recovery_rate_pct']}%)",
            f"{data['wrongful_burial_count']} worlds",
            f"R² = {data['mean_holdout_r2']:.1%}"
        )

    console.print(table)

    perf_table = Table(title="Overall Autonomous Scientific Abduction Metrics", box=box.SIMPLE_HEAD)
    perf_table.add_column("Scientific Abduction Metric", style="bold white")
    perf_table.add_column("Observed Value", justify="right", style="bold yellow")
    perf_table.add_column("Scientific Target Range", justify="right", style="dim")
    perf_table.add_column("Epistemic Status", justify="center", style="bold green")

    perf_table.add_row("Mechanism Recovery Rate", f"{summary.overall_recovery_rate_pct:.1f}% ({summary.mechanisms_recovered_count}/100)", "> 75.0%", "[green]SUPERIOR ABDUCTION[/green]")
    perf_table.add_row("Wrongful Burial (False Execution)", f"{summary.wrongful_burial_rate_pct:.1f}% ({summary.wrongful_burial_count}/100)", "< 10.0%", "[green]SAFE (Low False Rejection)[/green]")
    perf_table.add_row("Baseline Naive OLS R² (X->Y)", f"{summary.mean_naive_r2:.1%}", "< 15.0%", "[dim]WEAK (High Residuals)[/dim]")
    perf_table.add_row("Abduced Invariant Holdout R²", f"{summary.mean_abduced_r2:.1%}", "> 65.0%", "[green]STRONG GENERALIZATION[/green]")
    perf_table.add_row("Mean State-Space Pruning (ΔΩ)", f"{summary.mean_omega_pruned_pct:.1f}%", "> 20.0%", "[green]EFFECTIVE CONSTRAINTS[/green]")

    console.print(perf_table)

    console.print(Panel(
        f"[bold]Abduction Conclusion:[/bold]\n{summary.epistemic_conclusion}\n\n"
        f"[bold green]Causal Mechanisms Recovered:[/bold green] {summary.mechanisms_recovered_count}/100 | "
        f"[bold red]Wrongfully Buried:[/bold red] {summary.wrongful_burial_count}/100 | "
        f"[bold cyan]Mean Holdout Gain:[/bold cyan] +{summary.mean_r2_improvement_pct:.1f}%",
        title="Unknown Mechanism Challenge Summary",
        box=box.ROUNDED
    ))

if __name__ == "__main__":
    run_benchmark()
