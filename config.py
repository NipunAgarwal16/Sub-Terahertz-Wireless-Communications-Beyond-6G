"""
config.py - Configuration file

This file contains all simulation parameters, physical constants, and configuration
settings. By centralizing these values, you can easily adjust the simulation
characteristics without modifying the core implementation code.

Author: Nipun Agarwal
Version: 1.0
"""

from dataclasses import dataclass
from typing import Dict, List
import numpy as np

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================


class PhysicalConstants:
    """
    Fundamental physical constants used throughout the simulations.
    These values are based on international standards (SI units).
    """

    SPEED_OF_LIGHT = 3e8  # meters per second
    BOLTZMANN_CONSTANT = 1.38e-23  # Joules per Kelvin
    STANDARD_TEMPERATURE = 290.0  # Kelvin (approximately 17°C)
    STANDARD_PRESSURE = 101.325  # kilopascals (sea level)
    STANDARD_HUMIDITY = 50.0  # percent relative humidity


# ============================================================================
# ENVIRONMENTAL PARAMETERS
# ============================================================================


@dataclass
class EnvironmentalParams:
    """
    Environmental conditions that affect THz wave propagation.

    These parameters are critical because molecular absorption varies significantly
    with atmospheric conditions. Water vapor and oxygen are the primary absorbers
    at THz frequencies, and their concentrations depend on temperature, humidity,
    and pressure.
    """

    temperature_k: float = 290.0
    humidity_percent: float = 50.0
    pressure_kpa: float = 101.325

    def get_water_vapor_density(self) -> float:
        """
        Calculate water vapor density using the Magnus formula.

        This converts relative humidity to absolute humidity (grams per cubic meter),
        which is what actually determines water vapor absorption. The Magnus-Tetens
        approximation is accurate to within one percent for typical atmospheric
        conditions.
        """
        T_celsius = self.temperature_k - 273.15

        # Saturation vapor pressure using Magnus-Tetens formula (in hectopascals)
        saturation_pressure = 6.1078 * np.exp((17.27 * T_celsius) / (T_celsius + 237.3))

        # Actual vapor pressure based on relative humidity
        actual_pressure = (self.humidity_percent / 100.0) * saturation_pressure

        # Convert to water vapor density using ideal gas law
        # R_v = 461.5 J/(kg·K) is the specific gas constant for water vapor
        density = (actual_pressure * 100) / (461.5 * self.temperature_k)

        return density * 1000  # Convert from kg/m³ to g/m³


# ============================================================================
# SIMULATION CONFIGURATION
# ============================================================================


class SimulationConfig:
    """
    Configuration for Monte Carlo simulations and analysis parameters.
    """

    # Monte Carlo settings
    NUM_SIMULATIONS = 1000000  # Number of Monte Carlo trials
    CONFIDENCE_LEVEL = 0.95  # For confidence intervals (95%)

    # Random seed for reproducibility
    RANDOM_SEED = 11012026

    # Uncertainty parameters (standard deviations)
    TX_POWER_STD_DB = 0.5  # Transmit power variation in dB
    POINTING_ERROR_STD_DEG = 2.0  # Beam pointing error in degrees
    TEMPERATURE_STD_K = 5.0  # Temperature fluctuation in Kelvin
    HUMIDITY_STD_PERCENT = 10.0  # Humidity variation in percent
    PRESSURE_STD_KPA = 2.0  # Pressure variation in kilopascals

    # Output settings
    OUTPUT_DIRECTORY = "results"
    FIGURE_DPI = 400  # Dots per inch for publication quality
    FIGURE_FORMAT = "png"  # Output format (png, pdf, svg)
    SAVE_INTERMEDIATE_DATA = True  # Save CSV files of results


# ============================================================================
# ANTENNA ARRAY PARAMETERS
# ============================================================================


class AntennaConfig:
    """
    Default parameters for antenna array modeling.
    """

    # Physical parameters
    DEFAULT_ARRAY_SIZE_CM = 5.0  # Five centimeter square array
    ELEMENT_SPACING_FACTOR = 0.5  # Lambda over two spacing

    # Realistic impairments
    DEFAULT_EFFICIENCY = 0.9  # Ninty percent efficiency (typical for THz)
    MUTUAL_COUPLING_LOSS_DB = 0.5  # Half decibel loss from element coupling

    # Ideal parameters (for comparison)
    IDEAL_EFFICIENCY = 1.0
    IDEAL_COUPLING_LOSS_DB = 0.0

    # Array size ranges for analysis
    ARRAY_SIZES_CM = [1, 2, 5, 10, 20, 30, 50, 75, 100]  # Array sizes to analyze
    ARRAY_SIZE_RANGE_CM = np.linspace(1, 100, 1000)  # Continuous range


# ============================================================================
# FREQUENCY AND CHANNEL PARAMETERS
# ============================================================================


class FrequencyConfig:
    """
    Frequency ranges and channel configuration for THz analysis.
    """

    # Frequency bands
    MIN_FREQUENCY_GHZ = 50  # Lower bound (quasi-THz)
    MAX_FREQUENCY_GHZ = 1100  # Upper bound (deep THz)

    # Standard analysis frequencies
    ANALYSIS_FREQUENCIES_GHZ = [100, 150, 200, 250, 300, 500, 700, 800, 900, 1000]

    # Frequency ranges for different plots
    GAIN_FREQ_RANGE_GHZ = np.linspace(100, 1200, 100)
    LOSS_FREQ_RANGE_GHZ = np.linspace(100, 1200, 100)
    CAPACITY_FREQ_RANGE_GHZ = np.linspace(100, 1000, 200)

    # Channel bandwidth
    DEFAULT_BANDWIDTH_GHZ = 10.0  # Ten gigahertz (typical for backhaul)


# ============================================================================
# LINK BUDGET PARAMETERS
# ============================================================================


class LinkBudgetConfig:
    """
    Default parameters for link budget calculations.
    """

    # Transmitter parameters
    DEFAULT_TX_POWER_DBM = 10.0  # Ten dBm (10 milliwatts)
    TX_POWER_RANGE_DBM = [0, 10, 20, 30]  # Range for analysis

    # Receiver parameters
    DEFAULT_NOISE_FIGURE_DB = 10.0  # Ten dB noise figure (typical)
    NOISE_FIGURE_RANGE_DB = [6, 8, 10, 12, 15]

    # Distance parameters
    MIN_DISTANCE_M = 1.0  # One meter minimum
    MAX_DISTANCE_M = 1000.0  # One kilometer maximum
    DISTANCE_RANGE_M = np.logspace(0, 3, 100)  # Logarithmic spacing

    # Standard distances for analysis
    ANALYSIS_DISTANCES_M = [10, 50, 100, 500, 600, 700, 800, 900, 1000]


# ============================================================================
# MOLECULAR ABSORPTION DATABASE
# ============================================================================


class MolecularAbsorptionData:
    """
    Molecular absorption coefficients based on HITRAN database.

    This dictionary maps frequency in gigahertz to a tuple of
    (oxygen_absorption_db_per_km, water_vapor_absorption_db_per_km).

    The data includes major absorption peaks:
    - 60 GHz, 118 GHz: Oxygen (O2) resonances
    - 183 GHz, 380 GHz: Water vapor (H2O) resonances

    The "quiet windows" between these peaks (such as 140-150 GHz, 200-240 GHz)
    are preferred for long-range communication because they have lower absorption.
    """

    ABSORPTION_DATABASE: Dict[float, tuple] = {
        50: (0.01, 0.002),  # Sub-THz, very low absorption
        100: (0.05, 0.01),  # Lower THz boundary
        118: (0.8, 0.01),  # O2 absorption peak
        140: (0.1, 0.02),  # Quiet window
        150: (0.15, 2.5),  # Moderate absorption
        183: (0.05, 15.0),  # H2O absorption peak (strong)
        200: (0.2, 1.0),  # Good window for communication
        250: (0.3, 3.0),  # Moderate
        300: (0.5, 7.5),  # Increasing absorption
        325: (12.0, 2.0),  # O2 peak
        380: (15.0, 5.0),  # Major O2 peak
        400: (8.0, 10.0),  # High absorption
        450: (3.0, 12.0),  # Very high H2O absorption
        500: (2.0, 18.0),  # Severe H2O absorption
        600: (1.5, 23.0),  # Extreme absorption
        700: (1.2, 28.0),  # Extremely high absorption
    }

    # Reference conditions for absorption data
    REFERENCE_WATER_VAPOR_DENSITY = 7.5  # grams per cubic meter
    REFERENCE_PRESSURE = 101.325  # kilopascals


# ============================================================================
# BEAM ALIGNMENT PARAMETERS
# ============================================================================


class BeamAlignmentConfig:
    """
    Configuration for beam alignment simulations.
    """

    # Beamwidth ranges
    MIN_BEAMWIDTH_DEG = 5.0
    MAX_BEAMWIDTH_DEG = 100.0
    BEAMWIDTH_RANGE_DEG = np.linspace(5, 100, 20)

    # Standard beamwidths for analysis
    ANALYSIS_BEAMWIDTHS_DEG = [10, 20, 30, 45]

    # Number of simulations for beam alignment
    NUM_ALIGNMENT_SIMULATIONS = 1000000
    NUM_ALIGNMENT_SIMULATIONS_QUICK = 1000000

    # Alignment detection time
    ALIGNMENT_DETECTION_TIME_MS = 1.0  # One millisecond to detect alignment

    # Search strategy parameters
    BINARY_SEARCH_MAX_ITERATIONS = 20  # log2(360) ≈ 9, with margin
    ADAPTIVE_COARSE_STEP_FACTOR = 0.2  # Fine step = beamwidth × factor


# ============================================================================
# NEAR-FIELD ANALYSIS PARAMETERS
# ============================================================================


class NearFieldConfig:
    """
    Configuration for near-field and Fraunhofer distance analysis.
    """

    # Array sizes to analyze (N×N elements)
    ARRAY_ELEMENT_COUNTS = [4, 8, 16, 32, 64, 128, 256]

    # Phase deviation threshold (Fraunhofer criterion)
    FRAUNHOFER_PHASE_THRESHOLD_RAD = np.pi / 8  # 22.5 degrees

    # Distance range for near-field analysis
    NEAR_FIELD_DISTANCE_RANGE_M = np.logspace(0, 3, 100)  # One meter to one kilometer

    # Search range for Fraunhofer distance calculation
    FRAUNHOFER_SEARCH_MIN_M = 0.1
    FRAUNHOFER_SEARCH_MAX_M = 1000.0
    FRAUNHOFER_SEARCH_POINTS = 1000000


# ============================================================================
# VISUALIZATION PARAMETERS
# ============================================================================


class VisualizationConfig:
    """
    Parameters for generating publication-quality figures.
    """

    # Figure sizes (width, height in inches)
    FIGURE_SIZE_STANDARD = (10, 6)
    FIGURE_SIZE_WIDE = (14, 5)
    FIGURE_SIZE_SQUARE = (10, 10)
    FIGURE_SIZE_TALL = (10, 12)

    # Font sizes
    TITLE_FONTSIZE = 13
    LABEL_FONTSIZE = 12
    LEGEND_FONTSIZE = 10
    TICK_FONTSIZE = 10

    # Line properties
    LINEWIDTH_STANDARD = 2
    MARKERSIZE_STANDARD = 6
    MARKERSIZE_LARGE = 8

    # Colors for consistency
    COLOR_PRIMARY = "steelblue"
    COLOR_SECONDARY = "orangered"
    COLOR_TERTIARY = "forestgreen"
    COLOR_QUATERNARY = "purple"

    # Grid and transparency
    GRID_ALPHA = 0.3
    FILL_ALPHA = 0.2
    HISTOGRAM_ALPHA = 0.7

    # Plot style
    PLOT_STYLE = "default"  # Can be 'seaborn', 'ggplot', etc.


# ============================================================================
# DATA EXPORT PARAMETERS
# ============================================================================


class DataExportConfig:
    """
    Configuration for exporting simulation results to CSV files.
    """

    # CSV format settings
    CSV_DELIMITER = ","
    CSV_DECIMAL = "."
    FLOAT_PRECISION = 6  # Number of decimal places

    # File naming convention
    CSV_PREFIX = "thz_data_"
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

    # What to export
    EXPORT_RAW_DATA = True  # Export all Monte Carlo samples
    EXPORT_STATISTICS = True  # Export mean, std, percentiles
    EXPORT_PARAMETERS = True  # Export simulation parameters


# ============================================================================
# RESEARCH SCENARIOS
# ============================================================================


class ResearchScenarios:
    """
    Predefined scenarios for specific research questions.
    These can be easily modified or extended for different analyses.
    """

    # Scenario 1: Urban backhaul link
    URBAN_BACKHAUL = {
        "name": "Urban Backhaul",
        "frequency_ghz": 200,
        "distance_m": 100,
        "array_size_cm": 5,
        "tx_power_dbm": 10,
        "bandwidth_ghz": 10,
        "target_capacity_gbps": 50,
        "environment": EnvironmentalParams(temperature_k=290, humidity_percent=50),
    }

    # Scenario 2: Short-range high-capacity link
    SHORT_RANGE_HIGH_CAPACITY = {
        "name": "Short-Range High-Capacity",
        "frequency_ghz": 300,
        "distance_m": 10,
        "array_size_cm": 2,
        "tx_power_dbm": 10,
        "bandwidth_ghz": 10,
        "target_capacity_gbps": 100,
        "environment": EnvironmentalParams(temperature_k=290, humidity_percent=40),
    }

    # Scenario 3: Long-range moderate capacity
    LONG_RANGE_MODERATE = {
        "name": "Long-Range Moderate",
        "frequency_ghz": 140,
        "distance_m": 500,
        "array_size_cm": 10,
        "tx_power_dbm": 20,
        "bandwidth_ghz": 10,
        "target_capacity_gbps": 10,
        "environment": EnvironmentalParams(temperature_k=290, humidity_percent=60),
    }

    # Scenario 4: Extreme weather conditions
    EXTREME_WEATHER = {
        "name": "Extreme Weather",
        "frequency_ghz": 200,
        "distance_m": 100,
        "array_size_cm": 8,
        "tx_power_dbm": 15,
        "bandwidth_ghz": 10,
        "target_capacity_gbps": 30,
        "environment": EnvironmentalParams(temperature_k=305, humidity_percent=85),
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_default_config() -> dict:
    """
    Return a dictionary with all default configuration parameters.
    This is useful for saving configuration snapshots with results.
    """
    return {
        "physical_constants": {
            "speed_of_light": PhysicalConstants.SPEED_OF_LIGHT,
            "boltzmann_constant": PhysicalConstants.BOLTZMANN_CONSTANT,
        },
        "simulation": {
            "num_simulations": SimulationConfig.NUM_SIMULATIONS,
            "confidence_level": SimulationConfig.CONFIDENCE_LEVEL,
            "random_seed": SimulationConfig.RANDOM_SEED,
        },
        "antenna": {
            "default_size_cm": AntennaConfig.DEFAULT_ARRAY_SIZE_CM,
            "efficiency": AntennaConfig.DEFAULT_EFFICIENCY,
            "coupling_loss_db": AntennaConfig.MUTUAL_COUPLING_LOSS_DB,
        },
        "link_budget": {
            "tx_power_dbm": LinkBudgetConfig.DEFAULT_TX_POWER_DBM,
            "noise_figure_db": LinkBudgetConfig.DEFAULT_NOISE_FIGURE_DB,
            "bandwidth_ghz": FrequencyConfig.DEFAULT_BANDWIDTH_GHZ,
        },
    }


def print_configuration_summary():
    """
    Human-readable summary of the current configuration.
    Useful for documentation and debugging.
    """
    print("\n" + "=" * 80)
    print("CONFIGURATION SUMMARY")
    print("=" * 80)
    print(f"\nMonte Carlo Simulations: {SimulationConfig.NUM_SIMULATIONS:,} trials")
    print(f"Confidence Level: {SimulationConfig.CONFIDENCE_LEVEL*100:.0f}%")
    print(f"Random Seed: {SimulationConfig.RANDOM_SEED}")
    print(
        f"\nFrequency Range: {FrequencyConfig.MIN_FREQUENCY_GHZ}-{FrequencyConfig.MAX_FREQUENCY_GHZ} GHz"
    )
    print(f"Default Bandwidth: {FrequencyConfig.DEFAULT_BANDWIDTH_GHZ} GHz")
    print(f"\nDefault Array Size: {AntennaConfig.DEFAULT_ARRAY_SIZE_CM} cm")
    print(f"Antenna Efficiency: {AntennaConfig.DEFAULT_EFFICIENCY*100:.0f}%")
    print(f"\nTX Power: {LinkBudgetConfig.DEFAULT_TX_POWER_DBM} dBm")
    print(f"Noise Figure: {LinkBudgetConfig.DEFAULT_NOISE_FIGURE_DB} dB")
    print(
        f"\nOutput Format: {SimulationConfig.FIGURE_FORMAT.upper()} at {SimulationConfig.FIGURE_DPI} DPI"
    )
    print(f"Output Directory: {SimulationConfig.OUTPUT_DIRECTORY}/")
    print("=" * 80 + "\n")


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    # Test the configuration module
    print_configuration_summary()

    # Test environmental parameter calculations
    env = EnvironmentalParams()
    print(
        f"Standard atmosphere water vapor density: {env.get_water_vapor_density():.2f} g/m³"
    )

    # Test configuration export
    config_dict = get_default_config()
    print(f"\nConfiguration dictionary contains {len(config_dict)} top-level keys")

    print("\n✓ Configuration module loaded successfully\n")
