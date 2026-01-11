"""
main.py - Main execution script

Run this file to execute the complete research suite and generate all outputs.

Usage: python main.py

Author: Nipun Agarwal
Version: 1.0
"""

import time
from pathlib import Path

from config import *
from visualization import FigureGenerator
from data_exporter import DataExporter
from monte_carlo_simulation import MonteCarloSimulator


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("Sub-THz WIRELESS COMMUNICATIONS")
    print("=" * 80)

    start_time = time.time()

    # Print configuration summary
    print_configuration_summary()

    # Create output directory
    output_dir = Path(SimulationConfig.OUTPUT_DIRECTORY)
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}\n")

    # Generate all figures
    print("PHASE 1: Figure Generation")
    print("-" * 80)
    generator = FigureGenerator()
    generator.generate_all_figures()

    # Export sample data
    if SimulationConfig.SAVE_INTERMEDIATE_DATA:
        print("\nPHASE 2: Data Export")
        print("-" * 80)
        exporter = DataExporter()

        # Export sample Monte Carlo results
        base_config = {
            "tx_power_dbm": 10,
            "noise_figure_db": 10,
            "bandwidth_ghz": 10,
            "env_params": EnvironmentalParams(),
        }

        simulator = MonteCarloSimulator(base_config, num_simulations=1000000)
        mc_results = simulator.run_capacity_monte_carlo(200, 100, 5)
        exporter.export_monte_carlo_results(mc_results, "example_200ghz_100m")

    # Calculate execution time
    elapsed_time = time.time() - start_time

    # Final summary
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETE")
    print("=" * 80)
    print(
        f"\nExecution Time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)"
    )
    print(f"\nGenerated Outputs:")
    print("  • 15 figures (300 DPI)")
    print("  • CSV data files with simulation results")
    print(f"  • All files saved to: {output_dir.absolute()}")
    print("\nFigure Summary:")
    print(
        "  [1-9]   Basic Analysis (antenna gains, path loss, capacity, beam alignment)"
    )
    print(
        "  [10-15] Advanced Monte Carlo Analysis (uncertainty, sensitivity, impairments)"
    )
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
