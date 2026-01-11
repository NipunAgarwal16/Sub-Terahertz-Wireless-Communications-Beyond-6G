"""
data_exporter.py - Data export utilities

This module exports simulation results to CSV files for further analysis.

Author: Nipun Agarwal
Version: 1.0
"""

import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from config import SimulationConfig, DataExportConfig


class DataExporter:
    """Export simulation results to CSV files."""

    def __init__(self, output_dir: str = None):
        """Initialize data exporter."""
        self.output_dir = Path(output_dir or SimulationConfig.OUTPUT_DIRECTORY)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime(DataExportConfig.TIMESTAMP_FORMAT)

    def export_monte_carlo_results(self, results: Dict, label: str):
        """Export Monte Carlo simulation results."""
        filename = f"{DataExportConfig.CSV_PREFIX}mc_{label}_{self.timestamp}.csv"
        filepath = self.output_dir / filename

        # Create DataFrame from raw data
        df = pd.DataFrame(
            {
                "capacity_gbps": results["raw_capacities"],
                "snr_db": results["raw_snr"],
                "rx_power_dbm": results["raw_rx_power"],
            }
        )

        # Save to CSV
        df.to_csv(
            filepath, index=False, float_format=f"%.{DataExportConfig.FLOAT_PRECISION}f"
        )
        print(f"  ✓ Exported: {filename}")

        # Export statistics
        stats_filename = (
            f"{DataExportConfig.CSV_PREFIX}mc_stats_{label}_{self.timestamp}.csv"
        )
        stats_filepath = self.output_dir / stats_filename

        stats_df = pd.DataFrame(
            {
                "metric": [
                    "mean",
                    "median",
                    "std",
                    "min",
                    "max",
                    "p5",
                    "p95",
                    "outage_prob",
                    "snr_mean",
                ],
                "value": [
                    results["mean"],
                    results["median"],
                    results["std"],
                    results["min"],
                    results["max"],
                    results["p5"],
                    results["p95"],
                    results["outage_prob"],
                    results["snr_mean"],
                ],
            }
        )

        stats_df.to_csv(
            stats_filepath,
            index=False,
            float_format=f"%.{DataExportConfig.FLOAT_PRECISION}f",
        )
        print(f"  ✓ Exported: {stats_filename}")

    def export_link_budget(self, results: Dict, label: str):
        """Export link budget results."""
        filename = (
            f"{DataExportConfig.CSV_PREFIX}linkbudget_{label}_{self.timestamp}.csv"
        )
        filepath = self.output_dir / filename

        df = pd.DataFrame([results])
        df.to_csv(
            filepath, index=False, float_format=f"%.{DataExportConfig.FLOAT_PRECISION}f"
        )
        print(f"  ✓ Exported: {filename}")

    def export_beam_alignment(self, times: np.ndarray, strategy: str, beamwidth: float):
        """Export beam alignment results."""
        filename = f"{DataExportConfig.CSV_PREFIX}alignment_{strategy}_bw{beamwidth}_{self.timestamp}.csv"
        filepath = self.output_dir / filename

        df = pd.DataFrame({"alignment_time_ms": times})
        df.to_csv(
            filepath, index=False, float_format=f"%.{DataExportConfig.FLOAT_PRECISION}f"
        )
        print(f"  ✓ Exported: {filename}")


if __name__ == "__main__":
    print("\n✓ Data exporter module loaded successfully\n")
