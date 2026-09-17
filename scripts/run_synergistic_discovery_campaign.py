"""Synergistic Long-Horizon Scientific Discovery Suite CLI Runner.

Executes a complete 4-cycle Test-Time Science campaign combining:
1. Economic Research Budget Scarcity
2. Multi-Substrate Validation (Dry -> Damp -> Wet)
3. Unsupervised High-Dimensional Latent Factor Discovery
4. Bayesian Surprise & Information Gain (EIG)
5. State Space Omega Pruning & Constraint Ledger Promotion
"""

import sys
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from python.discovery.long_horizon_campaign_engine import LongHorizonCampaignEngine
from python.discovery.latent_factor_discovery import LatentFactorDiscoveryEngine
from python.discovery.bayesian_surprise_engine import BayesianSurpriseEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
console = Console(force_terminal=True, legacy_windows=False)

def run_synergistic_suite():
    console.print(Panel.fit(
        "[bold cyan]CORESEARCHER: LONG-HORIZON TEST-TIME SCIENCE CAMPAIGN[/bold cyan]\n"
        "[dim]Synergistic Epistemic Circuit: Economic Budget + Bayesian Surprise + Dry/Damp/Wet Substrates + Latent Manifolds[/dim]",
        box=box.DOUBLE_EDGE
    ))

    campaign_state = LongHorizonCampaignEngine.run_multi_cycle_campaign(
        research_question="How do connectome topological hubs buffer against cortical tau pathology?",
        target_cycles=4
    )

    table = Table(
        title="Long-Horizon Iterative Research Cycles (Closed-Loop Test-Time Science)",
        box=box.ROUNDED,
        header_style="bold magenta",
        show_lines=True
    )

    table.add_column("Cycle", justify="center", style="bold yellow", width=8)
    table.add_column("Substrate Tier", style="cyan", width=22)
    table.add_column("Active Hypothesis", style="white", width=32)
    table.add_column("Prior -> Post P(H)", justify="center", style="dim", width=18)
    table.add_column("Info Gain (KL)", justify="right", style="bold green", width=16)
    table.add_column("Epistemic Outcome", style="bold", width=20)
    table.add_column("State Pruned (ΔΩ)", justify="right", style="bold cyan", width=16)

    for c in campaign_state.cycle_history:
        color = "red" if "FALSIFIED" in c.outcome else "green"
        table.add_row(
            f"Cycle {c.cycle_number}",
            c.substrate_tested,
            c.active_hypothesis[:60] + ("..." if len(c.active_hypothesis) > 60 else ""),
            f"{c.prior_probability:.0%} -> {c.posterior_probability:.0%}",
            f"{c.information_gain_bits:.2f} bits\n[dim]{c.surprise_tier}[/dim]",
            f"[{color}]{c.outcome}[/{color}]",
            f"{c.pruned_omega_delta:.1%}" if c.pruned_omega_delta > 0 else "-"
        )

    console.print(table)

    b = campaign_state.budget
    budget_table = Table(title="Research Budget & Scarcity Ledger Status", box=box.SIMPLE_HEAD)
    budget_table.add_column("Resource Axis", style="bold white")
    budget_table.add_column("Consumed", justify="right", style="yellow")
    budget_table.add_column("Remaining", justify="right", style="bold green")
    budget_table.add_column("Total Quota", justify="right", style="dim")
    budget_table.add_column("Utilization", justify="right", style="cyan")

    budget_table.add_row("Compute Tokens", f"{b.consumed_compute_tokens:,}", f"{b.remaining_compute_tokens:,}", f"{b.total_compute_tokens:,}", f"{(b.consumed_compute_tokens/b.total_compute_tokens):.1%}")
    budget_table.add_row("Clinical Samples (N)", f"{b.consumed_patient_samples}", f"{b.remaining_patient_samples}", f"{b.total_patient_samples_quota}", f"{(b.consumed_patient_samples/b.total_patient_samples_quota):.1%}")
    budget_table.add_row("Wet-Lab Assays (€)", f"€{b.consumed_wet_lab_euros:,.2f}", f"€{b.remaining_wet_lab_euros:,.2f}", f"€{b.total_wet_lab_budget_euros:,.2f}", f"{(b.consumed_wet_lab_euros/b.total_wet_lab_budget_euros):.1%}")
    budget_table.add_row("Campaign Timeline (h)", f"{b.consumed_time_units_hours}h", f"{b.total_time_units_hours - b.consumed_time_units_hours}h", f"{b.total_time_units_hours}h", f"{(b.consumed_time_units_hours/b.total_time_units_hours):.1%}")

    console.print(budget_table)

    console.print(Panel(
        f"[bold]Campaign Synthesis:[/bold]\n{campaign_state.final_synthesis}\n\n"
        f"[bold cyan]Total Information Gain:[/bold cyan] {campaign_state.total_information_gain_bits:.2f} bits | "
        f"[bold cyan]Total Ω Excluded:[/bold cyan] {campaign_state.total_omega_pruned_fraction:.1%} | "
        f"[bold cyan]Promoted Invariants:[/bold cyan] {campaign_state.promoted_invariants_count}",
        title="Epistemic Closure",
        box=box.ROUNDED
    ))

if __name__ == "__main__":
    run_synergistic_suite()
