"""
visualization.py - Figure generation

Author: Nipun Agarwal
Version: 1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

from config import *
from antenna_models import EnhancedAntennaArray
from channel_models import EnhancedPathLossModel
from capacity_analysis import CapacityAnalyzer, compute_capacity_vs_parameter
from beam_alignment import BeamAlignment2D, BeamAlignment3D
from nearfield_analysis import NearFieldAnalyzer, compare_near_field_at_frequencies
from monte_carlo_simulation import (
    MonteCarloSimulator,
    run_environmental_sensitivity_suite,
)


class FigureGenerator:
    """Generate all 15 figures."""

    def __init__(self):
        """Initialize figure generator with configuration."""
        plt.style.use(VisualizationConfig.PLOT_STYLE)
        self.dpi = SimulationConfig.FIGURE_DPI
        self.fmt = SimulationConfig.FIGURE_FORMAT

    def _save_figure(self, fig_num: int, name: str):
        """Save figure with standard naming."""
        filename = f"fig{fig_num:02d}_{name}.{self.fmt}"
        plt.savefig(filename, dpi=self.dpi, bbox_inches="tight")
        print(f"  ✓ Saved: {filename}")
        plt.close()

    # BASIC ANALYSIS FIGURES (1-9)

    def fig01_gain_vs_frequency(self):
        """Figure 1: Antenna gain vs frequency"""
        print("[1/15] Generating gain vs frequency...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        freqs = FrequencyConfig.GAIN_FREQ_RANGE_GHZ
        for size in AntennaConfig.ARRAY_SIZES_CM:
            gains = [EnhancedAntennaArray(size, f).compute_gain_dbi() for f in freqs]
            ax.plot(
                freqs,
                gains,
                label=f"{size}cm × {size}cm",
                linewidth=VisualizationConfig.LINEWIDTH_STANDARD,
            )

        ax.set_xlabel(
            "Frequency (GHz)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_ylabel(
            "Gain (dBi)", fontsize=VisualizationConfig.LABEL_FONTSIZE, fontweight="bold"
        )
        ax.set_title(
            "Antenna Array Gain vs Frequency",
            fontsize=VisualizationConfig.TITLE_FONTSIZE,
            fontweight="bold",
        )
        ax.grid(True, alpha=VisualizationConfig.GRID_ALPHA)
        ax.legend(fontsize=VisualizationConfig.LEGEND_FONTSIZE)

        self._save_figure(1, "gain_frequency")

    def fig02_gain_vs_size(self):
        """Figure 2: Antenna gain vs array size"""
        print("[2/15] Generating gain vs array size...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        sizes = AntennaConfig.ARRAY_SIZE_RANGE_CM
        for freq in FrequencyConfig.ANALYSIS_FREQUENCIES_GHZ:
            gains = [EnhancedAntennaArray(s, freq).compute_gain_dbi() for s in sizes]
            ax.plot(
                sizes,
                gains,
                label=f"{freq}GHz",
                linewidth=VisualizationConfig.LINEWIDTH_STANDARD,
            )

        ax.set_xlabel(
            "Array Size (cm)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_ylabel(
            "Gain (dBi)", fontsize=VisualizationConfig.LABEL_FONTSIZE, fontweight="bold"
        )
        ax.set_title(
            "Antenna Array Gain vs Array Size",
            fontsize=VisualizationConfig.TITLE_FONTSIZE,
            fontweight="bold",
        )
        ax.grid(True, alpha=VisualizationConfig.GRID_ALPHA)
        ax.legend(fontsize=VisualizationConfig.LEGEND_FONTSIZE)

        self._save_figure(2, "gain_size")

    def fig03_pathloss_vs_frequency(self):
        """Figure 3: Path loss vs frequency"""
        print("[3/15] Generating path loss vs frequency...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        freqs = FrequencyConfig.LOSS_FREQ_RANGE_GHZ
        model = EnhancedPathLossModel()

        for dist in LinkBudgetConfig.ANALYSIS_DISTANCES_M:
            losses = [model.compute_total_loss(f, dist)["total"] for f in freqs]
            ax.plot(
                freqs,
                losses,
                label=f"d={dist}m",
                linewidth=VisualizationConfig.LINEWIDTH_STANDARD,
            )

        ax.set_xlabel(
            "Frequency (GHz)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_ylabel(
            "Path Loss (dB)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_title(
            "Total Path Loss vs Frequency",
            fontsize=VisualizationConfig.TITLE_FONTSIZE,
            fontweight="bold",
        )
        ax.grid(True, alpha=VisualizationConfig.GRID_ALPHA)
        ax.legend(fontsize=VisualizationConfig.LEGEND_FONTSIZE)

        self._save_figure(3, "pathloss_frequency")

    def fig04_pathloss_vs_distance(self):
        """Figure 4: Path loss vs distance"""
        print("[4/15] Generating path loss vs distance...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        dists = LinkBudgetConfig.DISTANCE_RANGE_M
        model = EnhancedPathLossModel()

        for freq in FrequencyConfig.ANALYSIS_FREQUENCIES_GHZ:
            losses = [model.compute_total_loss(freq, d)["total"] for d in dists]
            ax.semilogx(
                dists,
                losses,
                label=f"f={freq}GHz",
                linewidth=VisualizationConfig.LINEWIDTH_STANDARD,
            )

        ax.set_xlabel(
            "Distance (m)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_ylabel(
            "Path Loss (dB)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_title(
            "Total Path Loss vs Distance",
            fontsize=VisualizationConfig.TITLE_FONTSIZE,
            fontweight="bold",
        )
        ax.grid(True, alpha=VisualizationConfig.GRID_ALPHA, which="both")
        ax.legend(fontsize=VisualizationConfig.LEGEND_FONTSIZE)

        self._save_figure(4, "pathloss_distance")

    def fig05_capacity_vs_frequency(self):
        """Figure 5: Shannon capacity vs frequency"""
        print("[5/15] Generating capacity vs frequency...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        analyzer = CapacityAnalyzer()
        freqs = FrequencyConfig.CAPACITY_FREQ_RANGE_GHZ

        for dist in [10, 50, 100]:
            caps = [
                analyzer.compute_link_budget(f, dist, 5, 5)["capacity_gbps"]
                for f in freqs
            ]
            ax.plot(
                freqs,
                caps,
                "o-",
                label=f"d={dist}m",
                linewidth=VisualizationConfig.LINEWIDTH_STANDARD,
                markersize=VisualizationConfig.MARKERSIZE_STANDARD,
            )

        ax.set_xlabel(
            "Frequency (GHz)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_ylabel(
            "Capacity (Gbps)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_title(
            "Shannon Capacity vs Frequency (5cm arrays)",
            fontsize=VisualizationConfig.TITLE_FONTSIZE,
            fontweight="bold",
        )
        ax.grid(True, alpha=VisualizationConfig.GRID_ALPHA)
        ax.legend(fontsize=VisualizationConfig.LEGEND_FONTSIZE)
        ax.set_yscale("log")

        self._save_figure(5, "capacity_frequency")

    def fig06_capacity_vs_distance(self):
        """Figure 6: Shannon capacity vs distance"""
        print("[6/15] Generating capacity vs distance...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        analyzer = CapacityAnalyzer()
        dists = np.logspace(0, 2.5, 50)

        for size in [2, 5, 10]:
            caps = [
                analyzer.compute_link_budget(200, d, size, size)["capacity_gbps"]
                for d in dists
            ]
            ax.loglog(
                dists,
                caps,
                label=f"{size}cm arrays",
                linewidth=VisualizationConfig.LINEWIDTH_STANDARD,
            )

        ax.set_xlabel(
            "Distance (m)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_ylabel(
            "Capacity (Gbps)",
            fontsize=VisualizationConfig.LABEL_FONTSIZE,
            fontweight="bold",
        )
        ax.set_title(
            "Shannon Capacity vs Distance (200GHz)",
            fontsize=VisualizationConfig.TITLE_FONTSIZE,
            fontweight="bold",
        )
        ax.grid(True, alpha=VisualizationConfig.GRID_ALPHA, which="both")
        ax.legend(fontsize=VisualizationConfig.LEGEND_FONTSIZE)

        self._save_figure(6, "capacity_distance")

    def fig07_beam_alignment_2d(self):
        """Figure 7: 2D beam alignment strategies"""
        print("[7/15] Generating 2D beam alignment...")
        fig, (ax1, ax2) = plt.subplots(
            1, 2, figsize=VisualizationConfig.FIGURE_SIZE_WIDE
        )

        bws = BeamAlignmentConfig.BEAMWIDTH_RANGE_DEG
        m_cw, m_rand, m_bin, m_adap = [], [], [], []

        for bw in bws:
            ba = BeamAlignment2D(bw, 500)
            m_cw.append(np.mean(ba.strategy_clockwise()))
            m_rand.append(np.mean(ba.strategy_random()))
            m_bin.append(np.mean(ba.strategy_binary_search()))
            m_adap.append(np.mean(ba.strategy_adaptive_step()))

        ax1.plot(bws, m_cw, "o-", label="Clockwise", linewidth=2)
        ax1.plot(bws, m_rand, "s-", label="Random", linewidth=2)
        ax1.plot(bws, m_bin, "d-", label="Binary", linewidth=2)
        ax1.plot(bws, m_adap, "^-", label="Adaptive", linewidth=2)
        ax1.set_xlabel("Beamwidth (°)", fontweight="bold")
        ax1.set_ylabel("Time (ms)", fontweight="bold")
        ax1.set_title("2D Alignment Time", fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ba = BeamAlignment2D(20, 1000)
        t_cw, t_bin = ba.strategy_clockwise(), ba.strategy_binary_search()
        ax2.hist(t_cw, bins=30, alpha=0.5, label="Clockwise")
        ax2.hist(t_bin, bins=30, alpha=0.5, label="Binary")
        ax2.set_xlabel("Time (ms)", fontweight="bold")
        ax2.set_ylabel("Frequency", fontweight="bold")
        ax2.set_title("PDF (20°)", fontweight="bold")
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis="y")

        self._save_figure(7, "beam_alignment_2d")

    def fig08_nearfield(self):
        """Figure 8: Near-field analysis"""
        print("[8/15] Generating near-field analysis...")
        fig, (ax1, ax2) = plt.subplots(
            1, 2, figsize=VisualizationConfig.FIGURE_SIZE_WIDE
        )

        dists = NearFieldConfig.NEAR_FIELD_DISTANCE_RANGE_M
        for n in [4, 8, 16]:
            devs = [
                np.degrees(NearFieldAnalyzer(n, n, 200).compute_max_phase_deviation(d))
                for d in dists
            ]
            ax1.loglog(dists, devs, "o-", label=f"N={n}×{n}", linewidth=2)

        ax1.axhline(y=22.5, color="red", linestyle="--", linewidth=2, label="π/8")
        ax1.set_xlabel("Distance (m)", fontweight="bold")
        ax1.set_ylabel("Phase Dev (°)", fontweight="bold")
        ax1.set_title("Near-Field Phase Deviation", fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        freqs = np.linspace(100, 500, 20)
        df_vals = [NearFieldAnalyzer(8, 8, f).find_fraunhofer_distance() for f in freqs]
        ax2.plot(freqs, df_vals, "o-", linewidth=2, color="darkblue", markersize=8)
        ax2.fill_between(freqs, 0, df_vals, alpha=0.2)
        ax2.set_xlabel("Frequency (GHz)", fontweight="bold")
        ax2.set_ylabel("Fraunhofer Dist (m)", fontweight="bold")
        ax2.set_title("Fraunhofer Distance (8×8)", fontweight="bold")
        ax2.grid(True, alpha=0.3)

        self._save_figure(8, "nearfield")

    def fig09_2d_vs_3d(self):
        """Figure 9: 2D vs 3D comparison"""
        print("[9/15] Generating 2D vs 3D comparison...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        bws = BeamAlignmentConfig.BEAMWIDTH_RANGE_DEG
        m_2d = [np.mean(BeamAlignment2D(bw, 300).strategy_clockwise()) for bw in bws]
        m_3d = [
            np.mean(BeamAlignment3D(bw, 300).strategy_3d_hierarchical()) for bw in bws
        ]

        ax.plot(bws, m_2d, "o-", label="2D", linewidth=2, markersize=8, color="blue")
        ax.plot(bws, m_3d, "s-", label="3D", linewidth=2, markersize=8, color="red")
        ax.set_xlabel("Beamwidth (°)", fontweight="bold")
        ax.set_ylabel("Time (ms)", fontweight="bold")
        ax.set_title("2D vs 3D Beam Alignment", fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_yscale("log")

        self._save_figure(9, "2d_vs_3d")

    # MONTE CARLO FIGURES (10-15)

    def fig10_monte_carlo_capacity(self):
        """Figure 10: Monte Carlo capacity distributions"""
        print("[10/15] Generating Monte Carlo capacity (may take 1-2 min)...")
        fig, axes = plt.subplots(2, 2, figsize=VisualizationConfig.FIGURE_SIZE_TALL)

        base_cfg = {
            "tx_power_dbm": 10,
            "noise_figure_db": 10,
            "bandwidth_ghz": 10,
            "env_params": EnvironmentalParams(),
        }

        for idx, freq in enumerate([150, 200, 250, 300]):
            mc = MonteCarloSimulator(base_cfg, 1000)
            res = mc.run_capacity_monte_carlo(freq, 100, 5)

            ax = axes[idx // 2, idx % 2]
            ax.hist(res["raw_capacities"], bins=40, alpha=0.7, edgecolor="black")
            ax.axvline(
                res["mean"],
                color="red",
                linestyle="--",
                linewidth=2,
                label=f"μ={res['mean']:.2f}",
            )
            ax.axvspan(res["p5"], res["p95"], alpha=0.2, color="green", label="90% CI")
            ax.set_xlabel("Capacity (Gbps)", fontweight="bold")
            ax.set_ylabel("Frequency", fontweight="bold")
            ax.set_title(
                f'{freq}GHz | σ={res["std"]:.2f} | Pout={res["outage_prob"]*100:.1f}%',
                fontweight="bold",
            )
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self._save_figure(10, "monte_carlo_capacity")

    def fig11_environmental_sensitivity(self):
        """Figure 11: Environmental sensitivity"""
        print("[11/15] Generating environmental sensitivity...")
        results = run_environmental_sensitivity_suite(200, 100, 5)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Temperature
        temp_res = results["temperature"]
        axes[0].plot(
            temp_res["parameter_values"] - 273.15,
            temp_res["mean_capacities"],
            "o-",
            linewidth=2,
            markersize=7,
            color="orangered",
        )
        axes[0].set_xlabel("Temperature (°C)", fontweight="bold")
        axes[0].set_ylabel("Capacity (Gbps)", fontweight="bold")
        axes[0].set_title("Temperature Sensitivity", fontweight="bold")
        axes[0].grid(True, alpha=0.3)

        # Humidity
        hum_res = results["humidity"]
        axes[1].plot(
            hum_res["parameter_values"],
            hum_res["mean_capacities"],
            "s-",
            linewidth=2,
            markersize=7,
            color="dodgerblue",
        )
        axes[1].set_xlabel("Humidity (%)", fontweight="bold")
        axes[1].set_ylabel("Capacity (Gbps)", fontweight="bold")
        axes[1].set_title("Humidity Sensitivity", fontweight="bold")
        axes[1].grid(True, alpha=0.3)

        # Pressure
        press_res = results["pressure"]
        axes[2].plot(
            press_res["parameter_values"],
            press_res["mean_capacities"],
            "^-",
            linewidth=2,
            markersize=7,
            color="forestgreen",
        )
        axes[2].set_xlabel("Pressure (kPa)", fontweight="bold")
        axes[2].set_ylabel("Capacity (Gbps)", fontweight="bold")
        axes[2].set_title("Pressure Sensitivity", fontweight="bold")
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        self._save_figure(11, "environmental_sensitivity")

    def fig12_capacity_distance_mc(self):
        """Figure 12: Capacity vs distance with Monte Carlo"""
        print("[12/15] Generating capacity vs distance (Monte Carlo)...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        dists = np.logspace(1, 2.5, 15)
        base_cfg = {
            "tx_power_dbm": 10,
            "noise_figure_db": 10,
            "bandwidth_ghz": 10,
            "env_params": EnvironmentalParams(),
        }

        for size in [2, 5, 10]:
            means, p5s, p95s = [], [], []
            for d in dists:
                mc = MonteCarloSimulator(base_cfg, 500)
                res = mc.run_capacity_monte_carlo(200, d, size)
                means.append(res["mean"])
                p5s.append(res["p5"])
                p95s.append(res["p95"])

            ax.loglog(dists, means, "o-", linewidth=2, label=f"{size}cm", markersize=6)
            ax.fill_between(dists, p5s, p95s, alpha=0.2)

        ax.set_xlabel("Distance (m)", fontweight="bold")
        ax.set_ylabel("Capacity (Gbps)", fontweight="bold")
        ax.set_title("Capacity vs Distance (MC, 90% CI)", fontweight="bold")
        ax.grid(True, alpha=0.3, which="both")
        ax.legend()

        self._save_figure(12, "capacity_distance_mc")

    def fig13_advanced_alignment(self):
        """Figure 13: Advanced alignment strategies"""
        print("[13/15] Generating advanced alignment...")
        fig, (ax1, ax2) = plt.subplots(
            1, 2, figsize=VisualizationConfig.FIGURE_SIZE_WIDE
        )

        bws = BeamAlignmentConfig.BEAMWIDTH_RANGE_DEG
        m_bin = [
            np.mean(BeamAlignment2D(bw, 500).strategy_binary_search()) for bw in bws
        ]
        m_adap = [
            np.mean(BeamAlignment2D(bw, 500).strategy_adaptive_step()) for bw in bws
        ]

        ax1.plot(
            bws, m_bin, "s-", linewidth=2, label="Binary", color="teal", markersize=7
        )
        ax1.plot(
            bws,
            m_adap,
            "o-",
            linewidth=2,
            label="Adaptive",
            color="purple",
            markersize=7,
        )
        ax1.set_xlabel("Beamwidth (°)", fontweight="bold")
        ax1.set_ylabel("Time (ms)", fontweight="bold")
        ax1.set_title("Advanced Strategies", fontweight="bold")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ba = BeamAlignment2D(20, 1000)
        t_bin, t_adap = ba.strategy_binary_search(), ba.strategy_adaptive_step()
        ax2.hist(
            t_bin, bins=30, alpha=0.6, label="Binary", edgecolor="black", color="teal"
        )
        ax2.hist(
            t_adap,
            bins=30,
            alpha=0.6,
            label="Adaptive",
            edgecolor="black",
            color="purple",
        )
        ax2.set_xlabel("Time (ms)", fontweight="bold")
        ax2.set_ylabel("Frequency", fontweight="bold")
        ax2.set_title("Time Distribution (20°)", fontweight="bold")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        self._save_figure(13, "advanced_alignment")

    def fig14_gain_impairments(self):
        """Figure 14: Gain with impairments"""
        print("[14/15] Generating gain with impairments...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        freqs = np.linspace(100, 500, 50)
        g_ideal = [
            EnhancedAntennaArray(5, f, 1.0, 0).compute_gain_dbi(0) for f in freqs
        ]
        g_real = [
            EnhancedAntennaArray(5, f, 0.8, 0.5).compute_gain_dbi(2) for f in freqs
        ]

        ax.plot(freqs, g_ideal, linewidth=2, label="Ideal", color="blue")
        ax.plot(
            freqs, g_real, linewidth=2, label="Realistic", color="red", linestyle="--"
        )
        ax.fill_between(freqs, g_real, g_ideal, alpha=0.2, color="orange", label="Loss")
        ax.set_xlabel("Frequency (GHz)", fontweight="bold")
        ax.set_ylabel("Gain (dBi)", fontweight="bold")
        ax.set_title("Antenna Gain: Ideal vs Realistic (5cm)", fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.legend()

        self._save_figure(14, "gain_impairments")

    def fig15_rain_impact(self):
        """Figure 15: Rain attenuation impact"""
        print("[15/15] Generating rain impact...")
        fig, ax = plt.subplots(figsize=VisualizationConfig.FIGURE_SIZE_STANDARD)

        dists = np.logspace(1, 2.5, 20)
        for rain in [0, 5, 10, 25]:
            caps = []
            for d in dists:
                loss = EnhancedPathLossModel().compute_total_loss(200, d, rain)["total"]
                tx_g = EnhancedAntennaArray(5, 200).compute_gain_dbi()
                rx_pwr = 10 + 2 * tx_g - loss
                snr = 10 ** ((rx_pwr + 90) / 10)
                caps.append((10e9 * np.log2(1 + snr)) / 1e9)
            ax.loglog(
                dists, caps, "o-", linewidth=2, label=f"Rain: {rain}mm/hr", markersize=6
            )

        ax.set_xlabel("Distance (m)", fontweight="bold")
        ax.set_ylabel("Capacity (Gbps)", fontweight="bold")
        ax.set_title("Rain Attenuation Impact (200GHz, 5cm)", fontweight="bold")
        ax.grid(True, alpha=0.3, which="both")
        ax.legend()

        self._save_figure(15, "rain_impact")

    def generate_all_figures(self):
        """Generate all 15 figures."""
        print("\n" + "=" * 80)
        print("GENERATING ALL 15 FIGURES")
        print("=" * 80 + "\n")

        # Basic figures (1-9)
        self.fig01_gain_vs_frequency()
        self.fig02_gain_vs_size()
        self.fig03_pathloss_vs_frequency()
        self.fig04_pathloss_vs_distance()
        self.fig05_capacity_vs_frequency()
        self.fig06_capacity_vs_distance()
        self.fig07_beam_alignment_2d()
        self.fig08_nearfield()
        self.fig09_2d_vs_3d()

        # Monte Carlo figures (10-15)
        self.fig10_monte_carlo_capacity()
        self.fig11_environmental_sensitivity()
        self.fig12_capacity_distance_mc()
        self.fig13_advanced_alignment()
        self.fig14_gain_impairments()
        self.fig15_rain_impact()

        print("\n" + "=" * 80)
        print("✓ ALL 15 FIGURES GENERATED SUCCESSFULLY")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    generator = FigureGenerator()
    generator.generate_all_figures()
