"""
antenna_models.py - Antenna array modeling

This module implements antenna array models with realistic impairments including
efficiency losses, mutual coupling, and beam pointing errors.

Author: Nipun Agarwal
Version: 1.0
"""

import numpy as np
from typing import Tuple
from config import AntennaConfig, PhysicalConstants


class EnhancedAntennaArray:
    """
    Enhanced planar antenna array model with realistic impairments.

    This class models a square planar antenna array with lambda/2 element spacing.
    Unlike idealized models, it includes several real-world effects:

    1. Antenna efficiency (typically 70-85% due to ohmic losses in conductors)
    2. Mutual coupling between elements (reduces gain by 0.5-2 dB)
    3. Beam pointing errors (mechanical jitter, calibration errors)

    The lambda/2 spacing is critical because it:
    - Maximizes gain for a given array size
    - Prevents grating lobes (spurious beams in unwanted directions)
    - Allows dense packing while maintaining acceptable mutual coupling
    """

    def __init__(
        self,
        array_size_cm: float,
        frequency_ghz: float,
        efficiency: float = None,
        coupling_loss_db: float = None,
    ):
        """
        Initialize antenna array model.

        Parameters:
        -----------
        array_size_cm : float
            Physical size of the square array (X cm × X cm)
        frequency_ghz : float
            Operating frequency in gigahertz
        efficiency : float, optional
            Antenna efficiency (0-1). Defaults to configured value (0.8)
        coupling_loss_db : float, optional
            Mutual coupling loss in decibels. Defaults to configured value (0.5)
        """
        self.array_size_cm = array_size_cm
        self.frequency_ghz = frequency_ghz
        self.frequency_hz = frequency_ghz * 1e9

        # Calculate wavelength
        self.wavelength_m = PhysicalConstants.SPEED_OF_LIGHT / self.frequency_hz
        self.wavelength_cm = self.wavelength_m * 100

        # Set impairment parameters (use defaults if not specified)
        self.efficiency = (
            efficiency if efficiency is not None else AntennaConfig.DEFAULT_EFFICIENCY
        )
        self.coupling_loss_db = (
            coupling_loss_db
            if coupling_loss_db is not None
            else AntennaConfig.MUTUAL_COUPLING_LOSS_DB
        )

    def compute_array_elements(self) -> Tuple[int, int]:
        """
        Calculate the number of antenna elements that fit in the array.

        With lambda/2 spacing, as frequency increases, the wavelength decreases,
        so more elements fit in the same physical area. This is why THz arrays
        can achieve very high gains in compact form factors.

        For example:
        - At 100 GHz (λ = 3 mm): A 5 cm array fits approximately 10×10 = 100 elements
        - At 300 GHz (λ = 1 mm): The same 5 cm array fits approximately 30×30 = 900 elements

        Returns:
        --------
        total_elements : int
            Total number of elements in the array (N_side²)
        elements_per_side : int
            Number of elements along one side (N_side)
        """
        element_spacing_cm = self.wavelength_cm / 2
        elements_per_side = int(np.ceil(self.array_size_cm / element_spacing_cm))
        total_elements = elements_per_side**2

        return total_elements, elements_per_side

    def compute_gain_dbi(self, pointing_error_deg: float = 0) -> float:
        """
        Compute the maximum directivity gain in dBi.

        The gain calculation includes multiple factors:

        1. Array gain from N elements: Each element contributes coherently,
           giving a theoretical gain of N (or 10*log10(N) in dB)

        2. Efficiency factor: Accounts for losses in the antenna structure,
           feed network, and dielectric materials

        3. Directivity enhancement: Planar arrays have an additional ~10 dB
           directivity compared to isotropic radiators

        4. Mutual coupling losses: When elements are closely spaced, they
           electromagnetically interact, reducing overall efficiency

        5. Pointing error penalty: If the beam is misaligned, the effective
           gain in the desired direction decreases. The loss is approximately
           12*(θ_error/θ_3dB)² dB for small errors

        Parameters:
        -----------
        pointing_error_deg : float, optional
            Beam pointing misalignment in degrees (default: 0)

        Returns:
        --------
        gain_dbi : float
            Maximum gain in dBi (decibels relative to isotropic radiator)
        """
        N, _ = self.compute_array_elements()

        # Start with theoretical maximum: N elements with efficiency factor
        gain_linear = N * self.efficiency

        # Convert to dB and add directivity factor for planar arrays
        gain_dbi = 10 * np.log10(gain_linear) + 10

        # Subtract mutual coupling losses
        gain_dbi -= self.coupling_loss_db

        # Apply pointing error loss if present
        if pointing_error_deg > 0:
            beamwidth = self.compute_beamwidth()
            # Pointing loss follows a quadratic relationship with error angle
            pointing_loss = 12 * (pointing_error_deg / beamwidth) ** 2
            gain_dbi -= pointing_loss

        return gain_dbi

    def compute_beamwidth(self) -> float:
        """
        Calculate the three-decibel beamwidth in degrees.

        The beamwidth is the angular width where the antenna gain drops to
        half power (-3 dB) from its peak value. For planar arrays, the
        beamwidth is approximately:

            θ_3dB ≈ 70 * λ / D  (in degrees)

        where D is the array physical dimension and λ is wavelength.

        Key insights:
        - Larger arrays produce narrower beams (higher gain but harder to align)
        - Higher frequencies produce narrower beams (for fixed physical size)
        - Typical THz beamwidths are 1-10 degrees, requiring precise alignment

        Returns:
        --------
        beamwidth_deg : float
            Three-decibel beamwidth in degrees
        """
        beamwidth_deg = 70 * self.wavelength_cm / self.array_size_cm
        return beamwidth_deg

    def get_fraunhofer_distance(self) -> float:
        """
        Calculate the Fraunhofer distance (far-field boundary).

        The Fraunhofer distance marks the transition from near-field to far-field
        propagation. It's defined as the distance where the maximum phase deviation
        across the array aperture equals π/8 radians (22.5 degrees).

        The formula is: d_F = 2D² / λ

        where:
        - D is the largest physical dimension of the array
        - λ is the wavelength

        Physical interpretation:
        - In the near-field (d < d_F), the wavefront is curved and standard
          beamforming techniques don't work well
        - In the far-field (d > d_F), the wavefront can be approximated as
          planar, simplifying signal processing

        Critical observation for THz systems:
        With large arrays at high frequencies, d_F can be tens to hundreds
        of meters, meaning many practical links operate in the near-field!

        Example:
        - 10 cm array at 300 GHz: d_F ≈ 60 meters
        - 20 cm array at 500 GHz: d_F ≈ 330 meters

        Returns:
        --------
        fraunhofer_distance_m : float
            Fraunhofer distance in meters
        """
        D_m = self.array_size_cm / 100  # Convert to meters
        d_F = 2 * (D_m**2) / self.wavelength_m
        return d_F

    def get_array_info(self) -> dict:
        """
        Return comprehensive information about the array configuration.

        This method is useful for logging, debugging, and documentation.

        Returns:
        --------
        info : dict
            Dictionary containing all relevant array parameters
        """
        total_elements, elements_per_side = self.compute_array_elements()

        return {
            "physical_size_cm": self.array_size_cm,
            "frequency_ghz": self.frequency_ghz,
            "wavelength_mm": self.wavelength_cm * 10,
            "total_elements": total_elements,
            "elements_per_side": elements_per_side,
            "element_spacing_mm": self.wavelength_cm * 5,  # Lambda/2 in mm
            "gain_dbi": self.compute_gain_dbi(),
            "beamwidth_deg": self.compute_beamwidth(),
            "fraunhofer_distance_m": self.get_fraunhofer_distance(),
            "efficiency": self.efficiency,
            "coupling_loss_db": self.coupling_loss_db,
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def compare_ideal_vs_realistic(array_size_cm: float, frequency_ghz: float) -> dict:
    """
    Compare ideal and realistic antenna array models.

    This function is useful for understanding the impact of real-world
    impairments on antenna performance.

    Parameters:
    -----------
    array_size_cm : float
        Array physical size in centimeters
    frequency_ghz : float
        Operating frequency in gigahertz

    Returns:
    --------
    comparison : dict
        Dictionary with ideal and realistic gains, and the difference
    """
    # Ideal array (100% efficiency, no losses, perfect alignment)
    ideal_array = EnhancedAntennaArray(
        array_size_cm, frequency_ghz, efficiency=1.0, coupling_loss_db=0.0
    )
    ideal_gain = ideal_array.compute_gain_dbi(pointing_error_deg=0)

    # Realistic array (85% efficiency, 0.5 dB coupling loss, 2° pointing error)
    realistic_array = EnhancedAntennaArray(
        array_size_cm, frequency_ghz, efficiency=0.85, coupling_loss_db=0.5
    )
    realistic_gain = realistic_array.compute_gain_dbi(pointing_error_deg=2.0)

    return {
        "ideal_gain_dbi": ideal_gain,
        "realistic_gain_dbi": realistic_gain,
        "total_loss_db": ideal_gain - realistic_gain,
        "efficiency_loss_db": -10 * np.log10(0.8),
        "coupling_loss_db": 0.5,
        "pointing_loss_db": ideal_gain - realistic_gain - (-10 * np.log10(0.8)) - 0.5,
    }


def compute_required_array_size(
    target_gain_dbi: float, frequency_ghz: float, efficiency: float = 0.8
) -> float:
    """
    Calculate the required array size to achieve a target gain.

    This function inverts the gain calculation to determine what physical
    array size is needed to meet a gain requirement.

    Parameters:
    -----------
    target_gain_dbi : float
        Desired antenna gain in dBi
    frequency_ghz : float
        Operating frequency in gigahertz
    efficiency : float, optional
        Antenna efficiency (default: 0.8)

    Returns:
    --------
    required_size_cm : float
        Required array size in centimeters
    """
    # Binary search to find required size
    low, high = 0.1, 100.0  # Search range in cm

    while high - low > 0.01:  # Convergence criterion
        mid = (low + high) / 2
        array = EnhancedAntennaArray(mid, frequency_ghz, efficiency=efficiency)
        gain = array.compute_gain_dbi()

        if gain < target_gain_dbi:
            low = mid
        else:
            high = mid

    return (low + high) / 2


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ANTENNA MODELS MODULE TEST")
    print("=" * 80)

    # Test 1: Create an array and display its properties
    print("\nTest 1: Array Properties")
    print("-" * 80)
    array = EnhancedAntennaArray(array_size_cm=5, frequency_ghz=200)
    info = array.get_array_info()

    print(f"Array Size: {info['physical_size_cm']} cm × {info['physical_size_cm']} cm")
    print(f"Frequency: {info['frequency_ghz']} GHz")
    print(f"Wavelength: {info['wavelength_mm']:.2f} mm")
    print(
        f"Total Elements: {info['total_elements']} ({info['elements_per_side']}×{info['elements_per_side']})"
    )
    print(f"Element Spacing: {info['element_spacing_mm']:.2f} mm (λ/2)")
    print(f"Gain: {info['gain_dbi']:.2f} dBi")
    print(f"Beamwidth: {info['beamwidth_deg']:.2f} degrees")
    print(f"Fraunhofer Distance: {info['fraunhofer_distance_m']:.2f} m")

    # Test 2: Compare ideal vs realistic
    print("\nTest 2: Ideal vs Realistic Comparison")
    print("-" * 80)
    comparison = compare_ideal_vs_realistic(array_size_cm=5, frequency_ghz=200)
    print(f"Ideal Gain: {comparison['ideal_gain_dbi']:.2f} dBi")
    print(f"Realistic Gain: {comparison['realistic_gain_dbi']:.2f} dBi")
    print(f"Total Loss: {comparison['total_loss_db']:.2f} dB")
    print(f"  - Efficiency Loss: {comparison['efficiency_loss_db']:.2f} dB")
    print(f"  - Coupling Loss: {comparison['coupling_loss_db']:.2f} dB")
    print(f"  - Pointing Loss: {comparison['pointing_loss_db']:.2f} dB")

    # Test 3: Required array size calculation
    print("\nTest 3: Required Array Size for Target Gain")
    print("-" * 80)
    target_gain = 40.0  # dBi
    required_size = compute_required_array_size(target_gain, frequency_ghz=200)
    print(f"To achieve {target_gain:.0f} dBi at 200 GHz:")
    print(f"Required Array Size: {required_size:.2f} cm × {required_size:.2f} cm")

    # Verify the result
    verify_array = EnhancedAntennaArray(required_size, 200)
    print(f"Verification: Actual gain = {verify_array.compute_gain_dbi():.2f} dBi")

    print("\n" + "=" * 80)
    print("✓ Antenna models module loaded successfully")
    print("=" * 80 + "\n")
