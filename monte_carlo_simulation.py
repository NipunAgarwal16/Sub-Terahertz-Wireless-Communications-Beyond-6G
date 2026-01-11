"""
monte_carlo_simulation.py - Monte Carlo simulations

This module performs statistical analysis of THz links using Monte Carlo methods,
accounting for uncertainties in transmit power, pointing errors, environmental
conditions, and other real-world variabilities.

Author: Nipun Agarwal
Version: 1.0
"""

import numpy as np
from typing import Dict, Optional
from scipy.stats import norm

from config import SimulationConfig, PhysicalConstants, EnvironmentalParams
from antenna_models import EnhancedAntennaArray
from channel_models import EnhancedPathLossModel
from capacity_analysis import CapacityAnalyzer


class MonteCarloSimulator:
    """
    Monte Carlo simulator for THz link capacity with uncertainty quantification.

    Real-world THz systems face many sources of uncertainty:
    1. TX power variations (amplifier drift, temperature effects)
    2. Beam pointing errors (mechanical jitter, calibration drift)
    3. Environmental fluctuations (temperature, humidity, pressure changes)
    4. Phase noise in oscillators
    5. Manufacturing tolerances in antennas

    Monte Carlo simulation runs thousands of trials, each with randomly
    perturbed parameters, to provide statistical distributions rather than
    single-point estimates. This gives us:

    - Mean and median capacity (central tendency)
    - Standard deviation (variability)
    - Confidence intervals (reliability bounds)
    - Outage probability (chance of failing to meet requirements)
    - Percentiles (worst-case planning)

    These metrics are essential for system design and capacity planning.
    """

    def __init__(self, base_config: Dict, num_simulations: int = None):
        """
        Initialize Monte Carlo simulator.

        Parameters:
        -----------
        base_config : dict
            Base configuration with mean values for all parameters
        num_simulations : int, optional
            Number of Monte Carlo trials (defaults to configured value)
        """
        self.base_config = base_config
        self.num_sims = (
            num_simulations
            if num_simulations is not None
            else SimulationConfig.NUM_SIMULATIONS
        )

        # Set random seed for reproducibility
        np.random.seed(SimulationConfig.RANDOM_SEED)

    def run_capacity_monte_carlo(
        self, frequency_ghz: float, distance_m: float, array_size_cm: float
    ) -> Dict:
        """
        Run Monte Carlo simulation for link capacity.

        Each trial adds random perturbations to system parameters based on
        their expected variability:

        1. TX power: ±0.5 dB (typical amplifier stability)
        2. Pointing errors: σ = 2° (mechanical jitter)
        3. Temperature: σ = 5 K (weather variations)
        4. Humidity: σ = 10% (typical daily fluctuations)
        5. Pressure: σ = 2 kPa (weather systems)

        Parameters:
        -----------
        frequency_ghz : float
            Operating frequency in GHz
        distance_m : float
            Link distance in meters
        array_size_cm : float
            Antenna array size in cm (assumes TX = RX)

        Returns:
        --------
        results : dict
            Statistical summary including mean, std, percentiles, outage probability
        """
        capacities = []
        snr_values = []
        rx_powers = []

        # Extract base parameters from config
        tx_power_base = self.base_config.get("tx_power_dbm", 10)
        nf_db = self.base_config.get("noise_figure_db", 10)
        bw_ghz = self.base_config.get("bandwidth_ghz", 10)
        env_base = self.base_config.get("env_params", EnvironmentalParams())

        for _ in range(self.num_sims):
            # Add random TX power variation
            tx_power = tx_power_base + np.random.normal(
                0, SimulationConfig.TX_POWER_STD_DB
            )

            # Add random pointing errors (always positive, using absolute value)
            pointing_tx = abs(
                np.random.normal(0, SimulationConfig.POINTING_ERROR_STD_DEG)
            )
            pointing_rx = abs(
                np.random.normal(0, SimulationConfig.POINTING_ERROR_STD_DEG)
            )

            # Add environmental variations
            temp_varied = env_base.temperature_k + np.random.normal(
                0, SimulationConfig.TEMPERATURE_STD_K
            )
            hum_varied = np.clip(
                env_base.humidity_percent
                + np.random.normal(0, SimulationConfig.HUMIDITY_STD_PERCENT),
                0,
                100,
            )  # Humidity must be in [0, 100]
            press_varied = env_base.pressure_kpa + np.random.normal(
                0, SimulationConfig.PRESSURE_STD_KPA
            )

            env_varied = EnvironmentalParams(
                temperature_k=temp_varied,
                humidity_percent=hum_varied,
                pressure_kpa=press_varied,
            )

            # Create capacity analyzer with perturbed parameters
            analyzer = CapacityAnalyzer(
                tx_power_dbm=tx_power,
                noise_figure_db=nf_db,
                bandwidth_ghz=bw_ghz,
                env_params=env_varied,
            )

            # Create antenna arrays with pointing errors
            tx_ant = EnhancedAntennaArray(array_size_cm, frequency_ghz)
            rx_ant = EnhancedAntennaArray(array_size_cm, frequency_ghz)

            tx_gain = tx_ant.compute_gain_dbi(pointing_tx)
            rx_gain = rx_ant.compute_gain_dbi(pointing_rx)

            # Compute path loss with varied environment
            path_model = EnhancedPathLossModel(env_varied)
            loss_dict = path_model.compute_total_loss(frequency_ghz, distance_m)

            # Link budget calculation
            rx_pwr_dbm = tx_power + tx_gain + rx_gain - loss_dict["total"]
            rx_pwr_w = 10 ** (rx_pwr_dbm / 10) / 1000

            # Noise calculation
            noise_w = (
                PhysicalConstants.BOLTZMANN_CONSTANT
                * env_varied.temperature_k
                * (bw_ghz * 1e9)
                * (10 ** (nf_db / 10))
            )

            # SNR and capacity
            snr = rx_pwr_w / noise_w
            snr_db = 10 * np.log10(snr) if snr > 0 else -100

            capacity_gbps = ((bw_ghz * 1e9) * np.log2(1 + snr)) / 1e9

            # Store results
            capacities.append(capacity_gbps)
            snr_values.append(snr_db)
            rx_powers.append(rx_pwr_dbm)

        # Convert to numpy arrays for statistics
        cap_arr = np.array(capacities)
        snr_arr = np.array(snr_values)
        rx_pwr_arr = np.array(rx_powers)

        # Calculate comprehensive statistics
        results = self._compute_statistics(cap_arr, snr_arr, rx_pwr_arr)

        return results

    def _compute_statistics(
        self, capacities: np.ndarray, snr_values: np.ndarray, rx_powers: np.ndarray
    ) -> Dict:
        """
        Compute comprehensive statistics from Monte Carlo results.

        Parameters:
        -----------
        capacities : np.ndarray
            Array of capacity values from simulations
        snr_values : np.ndarray
            Array of SNR values (dB)
        rx_powers : np.ndarray
            Array of received power values (dBm)

        Returns:
        --------
        stats : dict
            Dictionary with all statistical metrics
        """
        # Basic statistics
        cap_mean = np.mean(capacities)
        cap_std = np.std(capacities)
        cap_median = np.median(capacities)

        # Percentiles (useful for worst-case design)
        cap_p5 = np.percentile(capacities, 5)
        cap_p95 = np.percentile(capacities, 95)
        cap_p99 = np.percentile(capacities, 99)

        # Confidence intervals (95% by default)
        alpha = 1 - SimulationConfig.CONFIDENCE_LEVEL
        z_score = norm.ppf(1 - alpha / 2)  # Two-tailed

        # Standard error of the mean
        sem = cap_std / np.sqrt(len(capacities))
        ci_lower = cap_mean - z_score * sem
        ci_upper = cap_mean + z_score * sem

        # Outage probability (probability of capacity < 1 Gbps)
        outage_threshold = 1.0  # Gbps
        outage_prob = np.sum(capacities < outage_threshold) / len(capacities)

        # Coefficient of variation (normalized variability)
        coef_var = cap_std / cap_mean if cap_mean > 0 else 0

        return {
            # Central tendency
            "mean": cap_mean,
            "median": cap_median,
            "std": cap_std,
            # Range
            "min": np.min(capacities),
            "max": np.max(capacities),
            # Percentiles
            "p5": cap_p5,
            "p95": cap_p95,
            "p99": cap_p99,
            # Confidence intervals
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "confidence_level": SimulationConfig.CONFIDENCE_LEVEL,
            # Reliability metrics
            "outage_prob": outage_prob,
            "availability": 1 - outage_prob,
            "coef_variation": coef_var,
            # SNR statistics
            "snr_mean": np.mean(snr_values),
            "snr_std": np.std(snr_values),
            "snr_min": np.min(snr_values),
            # RX power statistics
            "rx_power_mean": np.mean(rx_powers),
            "rx_power_std": np.std(rx_powers),
            # Raw data (for plotting)
            "raw_capacities": capacities,
            "raw_snr": snr_values,
            "raw_rx_power": rx_powers,
            # Metadata
            "num_simulations": len(capacities),
        }

    def sensitivity_analysis(
        self,
        parameter_name: str,
        parameter_range: np.ndarray,
        frequency_ghz: float,
        distance_m: float,
        array_size_cm: float,
    ) -> Dict:
        """
        Perform sensitivity analysis on a single parameter.

        This method varies one parameter while keeping others at their base
        values, then runs Monte Carlo simulation at each parameter value.
        This reveals how sensitive the system is to each parameter.

        Parameters:
        -----------
        parameter_name : str
            Name of parameter to vary ('temperature', 'humidity', 'pressure')
        parameter_range : np.ndarray
            Array of parameter values to test
        frequency_ghz, distance_m, array_size_cm : float
            Fixed link parameters

        Returns:
        --------
        results : dict
            Sensitivity analysis results including mean capacity at each value
        """
        mean_capacities = []
        std_capacities = []
        outage_probs = []

        for value in parameter_range:
            # Create modified environment
            if parameter_name == "temperature":
                env = EnvironmentalParams(temperature_k=value)
            elif parameter_name == "humidity":
                env = EnvironmentalParams(humidity_percent=value)
            elif parameter_name == "pressure":
                env = EnvironmentalParams(pressure_kpa=value)
            else:
                raise ValueError(f"Unknown parameter: {parameter_name}")

            # Run Monte Carlo with this environment
            config = self.base_config.copy()
            config["env_params"] = env

            simulator = MonteCarloSimulator(config, num_simulations=1000000)
            results = simulator.run_capacity_monte_carlo(
                frequency_ghz, distance_m, array_size_cm
            )

            mean_capacities.append(results["mean"])
            std_capacities.append(results["std"])
            outage_probs.append(results["outage_prob"])

        # Calculate sensitivity metric (gradient of capacity vs parameter)
        sensitivity = np.gradient(mean_capacities, parameter_range)

        return {
            "parameter_name": parameter_name,
            "parameter_values": parameter_range,
            "mean_capacities": np.array(mean_capacities),
            "std_capacities": np.array(std_capacities),
            "outage_probs": np.array(outage_probs),
            "sensitivity": sensitivity,
            "max_sensitivity": np.max(np.abs(sensitivity)),
            "mean_sensitivity": np.mean(np.abs(sensitivity)),
        }


def run_environmental_sensitivity_suite(
    frequency_ghz: float, distance_m: float, array_size_cm: float
) -> Dict[str, Dict]:
    """
    Run complete environmental sensitivity analysis.

    This convenience function runs sensitivity analysis for all three
    environmental parameters: temperature, humidity, and pressure.

    Parameters:
    -----------
    frequency_ghz, distance_m, array_size_cm : float
        Link configuration

    Returns:
    --------
    results : dict
        Dictionary mapping parameter names to sensitivity results
    """
    base_config = {
        "tx_power_dbm": 10,
        "noise_figure_db": 10,
        "bandwidth_ghz": 10,
        "env_params": EnvironmentalParams(),
    }

    simulator = MonteCarloSimulator(base_config)

    results = {}

    # Temperature sensitivity
    temps = np.linspace(250, 320, 15)  # -23°C to 47°C
    results["temperature"] = simulator.sensitivity_analysis(
        "temperature", temps, frequency_ghz, distance_m, array_size_cm
    )

    # Humidity sensitivity
    humidities = np.linspace(10, 90, 15)  # 10% to 90% RH
    results["humidity"] = simulator.sensitivity_analysis(
        "humidity", humidities, frequency_ghz, distance_m, array_size_cm
    )

    # Pressure sensitivity
    pressures = np.linspace(85, 105, 15)  # 85 to 105 kPa
    results["pressure"] = simulator.sensitivity_analysis(
        "pressure", pressures, frequency_ghz, distance_m, array_size_cm
    )

    return results


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MONTE CARLO SIMULATION MODULE TEST")
    print("=" * 80)

    # Test 1: Basic Monte Carlo simulation
    print("\nTest 1: Monte Carlo Capacity Analysis")
    print("-" * 80)
    print("Configuration: 200 GHz, 100 m, 5 cm arrays")

    base_config = {
        "tx_power_dbm": 10,
        "noise_figure_db": 10,
        "bandwidth_ghz": 10,
        "env_params": EnvironmentalParams(),
    }

    simulator = MonteCarloSimulator(base_config, num_simulations=1000000)
    results = simulator.run_capacity_monte_carlo(
        frequency_ghz=200, distance_m=100, array_size_cm=5
    )

    print(f"\nCapacity Statistics:")
    print(f"  Mean: {results['mean']:.2f} Gbps")
    print(f"  Median: {results['median']:.2f} Gbps")
    print(f"  Std Dev: {results['std']:.2f} Gbps")
    print(f"  Range: [{results['min']:.2f}, {results['max']:.2f}] Gbps")
    print(f"\nPercentiles:")
    print(f"  5th: {results['p5']:.2f} Gbps")
    print(f"  95th: {results['p95']:.2f} Gbps")
    print(f"  99th: {results['p99']:.2f} Gbps")
    print(f"\nConfidence Interval ({results['confidence_level']*100:.0f}%):")
    print(f"  [{results['ci_lower']:.2f}, {results['ci_upper']:.2f}] Gbps")
    print(f"\nReliability Metrics:")
    print(f"  Outage Probability: {results['outage_prob']*100:.2f}%")
    print(f"  Availability: {results['availability']*100:.2f}%")
    print(f"  Coefficient of Variation: {results['coef_variation']:.3f}")
    print(f"\nSNR Statistics:")
    print(f"  Mean: {results['snr_mean']:.2f} dB")
    print(f"  Std Dev: {results['snr_std']:.2f} dB")
    print(f"  Minimum: {results['snr_min']:.2f} dB")

    # Test 2: Sensitivity analysis
    print("\n" + "-" * 80)
    print("Test 2: Environmental Sensitivity Analysis")
    print("-" * 80)

    # Temperature sensitivity
    temps = np.linspace(270, 310, 5)
    temp_results = simulator.sensitivity_analysis("temperature", temps, 200, 100, 5)

    print(f"\nTemperature Sensitivity:")
    print(f"  Range: {temps[0]-273:.0f}°C to {temps[-1]-273:.0f}°C")
    print(
        f"  Capacity Range: {temp_results['mean_capacities'][0]:.2f} to "
        + f"{temp_results['mean_capacities'][-1]:.2f} Gbps"
    )
    print(f"  Max Sensitivity: {temp_results['max_sensitivity']:.3f} Gbps/K")

    print("\n" + "=" * 80)
    print("✓ Monte Carlo simulation module loaded successfully")
    print("=" * 80 + "\n")
