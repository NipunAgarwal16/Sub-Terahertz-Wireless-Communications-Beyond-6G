"""
channel_models.py - Channel modeling

This module implements path loss models including free-space path loss,
molecular absorption (with environmental dependencies), and rain attenuation.

Author: Nipun Agarwal
Version: 1.0
"""

import numpy as np
from scipy.interpolate import interp1d
from typing import Dict, Optional
from config import EnvironmentalParams, MolecularAbsorptionData, PhysicalConstants


class EnhancedPathLossModel:
    """
    Comprehensive path loss model for THz frequencies.

    THz propagation differs fundamentally from microwave frequencies due to
    significant molecular absorption. This model accounts for:

    1. Free-space path loss (geometric spreading)
    2. Molecular absorption by O2 and H2O
    3. Environmental parameter dependencies
    4. Optional rain attenuation

    The molecular absorption is particularly important because it creates
    "absorption peaks" at specific frequencies (60, 118, 183, 380 GHz) where
    propagation is very lossy, and "quiet windows" between peaks where
    long-range communication is feasible.
    """

    def __init__(self, env_params: Optional[EnvironmentalParams] = None):
        """
        Initialize path loss model with environmental parameters.

        Parameters:
        -----------
        env_params : EnvironmentalParams, optional
            Environmental conditions (temperature, humidity, pressure).
            If None, uses standard atmospheric conditions.
        """
        self.env_params = (
            env_params if env_params is not None else EnvironmentalParams()
        )
        self.absorption_db = MolecularAbsorptionData.ABSORPTION_DATABASE

    def get_absorption(self, freq_ghz: float) -> float:
        """
        Calculate total molecular absorption coefficient with environmental corrections.

        This method:
        1. Interpolates O2 and H2O absorption from the database
        2. Applies pressure correction to O2 (scales linearly with pressure)
        3. Applies humidity correction to H2O (scales with water vapor density)

        The corrections are important because:
        - O2 concentration is proportional to atmospheric pressure
        - H2O absorption depends on absolute humidity, not relative humidity

        Parameters:
        -----------
        freq_ghz : float
            Frequency in gigahertz

        Returns:
        --------
        absorption_db_per_km : float
            Total absorption coefficient in dB per kilometer
        """
        # Extract frequency points and absorption values
        freqs = sorted(self.absorption_db.keys())
        o2_vals = [self.absorption_db[f][0] for f in freqs]
        h2o_vals = [self.absorption_db[f][1] for f in freqs]

        # Create interpolation functions (cubic for smoothness)
        f_o2 = interp1d(
            freqs, o2_vals, kind="cubic", fill_value="extrapolate", bounds_error=False
        )
        f_h2o = interp1d(
            freqs, h2o_vals, kind="cubic", fill_value="extrapolate", bounds_error=False
        )

        # Apply environmental corrections
        pressure_factor = (
            self.env_params.pressure_kpa / MolecularAbsorptionData.REFERENCE_PRESSURE
        )
        humidity_factor = (
            self.env_params.get_water_vapor_density()
            / MolecularAbsorptionData.REFERENCE_WATER_VAPOR_DENSITY
        )

        # Calculate corrected absorption
        o2_absorption = float(f_o2(freq_ghz)) * pressure_factor
        h2o_absorption = float(f_h2o(freq_ghz)) * humidity_factor

        total_absorption = o2_absorption + h2o_absorption

        return max(0, total_absorption)  # Ensure non-negative

    def compute_fspl(self, freq_ghz: float, dist_m: float) -> float:
        """
        Calculate Free-Space Path Loss using the Friis equation.

        FSPL represents the geometric spreading loss as electromagnetic waves
        propagate through space. The power density decreases with the square
        of distance (inverse square law).

        Formula: FSPL(dB) = 20·log10(f) + 20·log10(d) + 20·log10(4π/c)
                          ≈ 20·log10(f_GHz) + 20·log10(d_m) + 92.45 dB

        Parameters:
        -----------
        freq_ghz : float
            Frequency in gigahertz
        dist_m : float
            Distance in meters

        Returns:
        --------
        fspl_db : float
            Free-space path loss in decibels
        """
        freq_hz = freq_ghz * 1e9
        fspl = (
            20 * np.log10(freq_hz)
            + 20 * np.log10(dist_m)
            + 20 * np.log10(4 * np.pi / PhysicalConstants.SPEED_OF_LIGHT)
        )
        return fspl

    def compute_rain_attenuation(
        self, freq_ghz: float, rain_mm_hr: float, dist_m: float
    ) -> float:
        """
        Calculate rain attenuation using simplified ITU-R P.838 model.

        Rain droplets scatter and absorb THz waves, with attenuation increasing
        rapidly with both frequency and rain rate. The specific attenuation
        (dB/km) follows an empirical power law.

        Simplified model: γ_R = k · R^α
        where:
        - γ_R is specific attenuation (dB/km)
        - R is rain rate (mm/hr)
        - k and α are frequency-dependent coefficients

        Parameters:
        -----------
        freq_ghz : float
            Frequency in gigahertz
        rain_mm_hr : float
            Rain rate in millimeters per hour (0 = no rain)
        dist_m : float
            Path length in meters

        Returns:
        --------
        rain_loss_db : float
            Total rain attenuation in decibels
        """
        if rain_mm_hr <= 0:
            return 0.0

        # Simplified coefficients (more accurate models use lookup tables)
        if freq_ghz < 100:
            k = 0.0001 * freq_ghz**2.5
            alpha = 1.0
        else:
            k = 0.001 * (freq_ghz / 100) ** 2
            alpha = 1.1

        # Specific attenuation (dB/km)
        gamma_rain = k * (rain_mm_hr**alpha)

        # Total attenuation over distance
        rain_loss = gamma_rain * (dist_m / 1000)

        return rain_loss

    def compute_total_loss(
        self, freq_ghz: float, dist_m: float, rain_mm_hr: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate total path loss including all components.

        This is the master function that combines all loss mechanisms.
        It returns a dictionary so you can see the contribution of each
        component separately, which is crucial for understanding which
        factors dominate at different frequencies and distances.

        Parameters:
        -----------
        freq_ghz : float
            Frequency in gigahertz
        dist_m : float
            Distance in meters
        rain_mm_hr : float, optional
            Rain rate in mm/hr (default: 0)

        Returns:
        --------
        losses : dict
            Dictionary containing:
            - 'total': Total path loss (dB)
            - 'fspl': Free-space path loss component (dB)
            - 'absorption': Molecular absorption component (dB)
            - 'rain': Rain attenuation component (dB)
            - 'absorption_coeff': Absorption coefficient (dB/km)
        """
        # Calculate each component
        fspl = self.compute_fspl(freq_ghz, dist_m)

        absorption_coeff = self.get_absorption(freq_ghz)
        absorption_loss = absorption_coeff * (dist_m / 1000)  # Convert distance to km

        rain_loss = self.compute_rain_attenuation(freq_ghz, rain_mm_hr, dist_m)

        # Sum all components
        total_loss = fspl + absorption_loss + rain_loss

        return {
            "total": total_loss,
            "fspl": fspl,
            "absorption": absorption_loss,
            "rain": rain_loss,
            "absorption_coeff": absorption_coeff,
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def find_quiet_windows(
    freq_range_ghz: np.ndarray, max_absorption_db_km: float = 2.0
) -> list:
    """
    Identify frequency ranges with low molecular absorption ("quiet windows").

    These windows are preferred for long-range THz communication because
    they minimize propagation losses.

    Parameters:
    -----------
    freq_range_ghz : np.ndarray
        Array of frequencies to analyze
    max_absorption_db_km : float
        Maximum acceptable absorption (dB/km) to qualify as a quiet window

    Returns:
    --------
    windows : list
        List of (start_freq, end_freq) tuples representing quiet windows
    """
    model = EnhancedPathLossModel()
    windows = []
    in_window = False
    window_start = None

    for freq in freq_range_ghz:
        absorption = model.get_absorption(freq)

        if absorption <= max_absorption_db_km and not in_window:
            # Entering a quiet window
            window_start = freq
            in_window = True
        elif absorption > max_absorption_db_km and in_window:
            # Exiting a quiet window
            windows.append(
                (
                    window_start,
                    freq_range_ghz[np.where(freq_range_ghz == freq)[0][0] - 1],
                )
            )
            in_window = False

    # Close final window if still open
    if in_window:
        windows.append((window_start, freq_range_ghz[-1]))

    return windows


def compare_environmental_conditions(freq_ghz: float, dist_m: float) -> dict:
    """
    Compare path loss under different environmental conditions.

    This function illustrates how weather significantly affects THz propagation.

    Parameters:
    -----------
    freq_ghz : float
        Frequency in gigahertz
    dist_m : float
        Distance in meters

    Returns:
    --------
    comparison : dict
        Path losses under various conditions
    """
    # Standard conditions
    standard = EnhancedPathLossModel(EnvironmentalParams())
    loss_standard = standard.compute_total_loss(freq_ghz, dist_m)

    # Hot and humid (tropical)
    tropical = EnhancedPathLossModel(
        EnvironmentalParams(temperature_k=305, humidity_percent=85, pressure_kpa=101.3)
    )
    loss_tropical = tropical.compute_total_loss(freq_ghz, dist_m)

    # Cold and dry (arctic)
    arctic = EnhancedPathLossModel(
        EnvironmentalParams(temperature_k=253, humidity_percent=20, pressure_kpa=101.3)
    )
    loss_arctic = arctic.compute_total_loss(freq_ghz, dist_m)

    return {
        "standard": loss_standard["total"],
        "tropical": loss_tropical["total"],
        "arctic": loss_arctic["total"],
        "tropical_excess_db": loss_tropical["total"] - loss_standard["total"],
        "arctic_advantage_db": loss_standard["total"] - loss_arctic["total"],
    }


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CHANNEL MODELS MODULE TEST")
    print("=" * 80)

    # Test 1: Path loss components at 200 GHz
    print("\nTest 1: Path Loss Components at 200 GHz, 100 m")
    print("-" * 80)
    model = EnhancedPathLossModel()
    losses = model.compute_total_loss(freq_ghz=200, dist_m=100)

    print(f"Free-Space Path Loss: {losses['fspl']:.2f} dB")
    print(
        f"Molecular Absorption: {losses['absorption']:.2f} dB ({losses['absorption_coeff']:.2f} dB/km)"
    )
    print(f"Rain Attenuation: {losses['rain']:.2f} dB (no rain)")
    print(f"Total Path Loss: {losses['total']:.2f} dB")

    # Test 2: Environmental sensitivity
    print("\nTest 2: Environmental Sensitivity at 300 GHz, 100 m")
    print("-" * 80)
    comparison = compare_environmental_conditions(freq_ghz=300, dist_m=100)
    print(f"Standard Atmosphere: {comparison['standard']:.2f} dB")
    print(
        f"Tropical (hot/humid): {comparison['tropical']:.2f} dB ({comparison['tropical_excess_db']:+.2f} dB)"
    )
    print(
        f"Arctic (cold/dry): {comparison['arctic']:.2f} dB ({comparison['arctic_advantage_db']:+.2f} dB)"
    )

    # Test 3: Rain impact
    print("\nTest 3: Rain Attenuation at 200 GHz, 100 m")
    print("-" * 80)
    for rain_rate in [0, 5, 10, 25]:
        loss_dict = model.compute_total_loss(
            freq_ghz=200, dist_m=100, rain_mm_hr=rain_rate
        )
        print(
            f"Rain Rate {rain_rate:2d} mm/hr: Total loss = {loss_dict['total']:.2f} dB "
            + f"(rain contrib: {loss_dict['rain']:.2f} dB)"
        )

    print("\n" + "=" * 80)
    print("✓ Channel models module loaded successfully")
    print("=" * 80 + "\n")
