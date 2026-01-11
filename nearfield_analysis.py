"""
nearfield_analysis.py - Near-field analysis for Sub-THz

This module analyzes near-field effects in THz antenna arrays, particularly
the Fraunhofer distance where plane-wave assumptions become valid.

Author: Nipun Agarwal
Version: 1.0
"""

import numpy as np
from typing import Optional, Tuple
from config import PhysicalConstants, NearFieldConfig


class NearFieldAnalyzer:
    """
    Analyze near-field propagation effects for antenna arrays.

    In the near-field (Fresnel zone), the wavefront curvature is significant
    and traditional beamforming techniques don't work well. The Fraunhofer
    distance marks the transition to far-field where plane-wave assumptions
    are valid.

    The Fraunhofer criterion: Maximum phase deviation ≤ π/8 (22.5°)

    For THz frequencies with large arrays, this distance can be surprisingly
    large - tens to hundreds of meters - meaning many practical links operate
    in the near-field!

    This has profound implications:
    - Standard beamforming may fail
    - Need near-field focusing techniques
    - Link budget calculations must account for phase coherence
    - Beam patterns differ from far-field predictions
    """

    def __init__(self, n1: int, n2: int, frequency_ghz: float):
        """
        Initialize near-field analyzer for two arrays.

        Parameters:
        -----------
        n1 : int
            Number of TX antenna elements per side (N1 × N1 array)
        n2 : int
            Number of RX antenna elements per side (N2 × N2 array)
        frequency_ghz : float
            Operating frequency in GHz
        """
        self.n1 = n1
        self.n2 = n2
        self.frequency_hz = frequency_ghz * 1e9
        self.wavelength = PhysicalConstants.SPEED_OF_LIGHT / self.frequency_hz
        self.element_spacing = self.wavelength / 2  # Lambda/2 spacing

    def compute_array_dimensions(self) -> Tuple[float, float]:
        """
        Calculate physical dimensions of TX and RX arrays.

        Returns:
        --------
        tx_size_m : float
            TX array size in meters
        rx_size_m : float
            RX array size in meters
        """
        tx_size = (self.n1 - 1) * self.element_spacing
        rx_size = (self.n2 - 1) * self.element_spacing

        return tx_size, rx_size

    def compute_max_phase_deviation(self, distance_m: float) -> float:
        """
        Calculate maximum phase deviation between different paths.

        When TX and RX arrays are separated by distance d, different TX-RX
        element pairs have different path lengths. The shortest path is
        center-to-center. The longest paths are corner-to-corner.

        This path length difference creates a phase difference that increases
        as distance decreases. The phase deviation is:

            Δφ = 2π × Δpath / λ

        where Δpath is the difference between longest and shortest paths.

        For small angles (d >> D), the path difference approximates to:

            Δpath ≈ D² / (2d)

        where D is the array size.

        Parameters:
        -----------
        distance_m : float
            Separation between array centers in meters

        Returns:
        --------
        phase_deviation_rad : float
            Maximum phase deviation in radians (normalized to [0, 2π])
        """
        tx_size, rx_size = self.compute_array_dimensions()

        # Maximum physical dimension
        max_size = max(tx_size, rx_size)

        # Simplified formula for small angles
        # More accurate: would need to compute all paths explicitly
        max_path_diff = (max_size**2) / (2 * distance_m)

        # Convert path difference to phase (in radians)
        phase_deviation = (2 * np.pi * max_path_diff) / self.wavelength

        # Normalize to [0, 2π] since phase is periodic
        phase_deviation = phase_deviation % (2 * np.pi)

        return phase_deviation

    def find_fraunhofer_distance(self) -> Optional[float]:
        """
        Find the Fraunhofer distance where phase deviation equals π/8.

        The Fraunhofer distance is defined as the minimum distance where the
        maximum phase deviation across the array is ≤ π/8 (22.5 degrees).
        Beyond this distance, plane-wave assumptions are valid with less than
        3% error in the far-field pattern.

        Analytical formula: d_F = 2D²/λ

        where D is the largest array dimension.

        We also verify this numerically by searching for the distance where
        our computed phase deviation equals π/8.

        Returns:
        --------
        fraunhofer_distance_m : float
            Fraunhofer distance in meters, or None if not found
        """
        # Analytical formula
        tx_size, rx_size = self.compute_array_dimensions()
        max_size = max(tx_size, rx_size)
        d_F_analytical = 2 * (max_size**2) / self.wavelength

        # Numerical verification
        distances = np.logspace(
            np.log10(NearFieldConfig.FRAUNHOFER_SEARCH_MIN_M),
            np.log10(NearFieldConfig.FRAUNHOFER_SEARCH_MAX_M),
            NearFieldConfig.FRAUNHOFER_SEARCH_POINTS,
        )

        for d in distances:
            phase_dev = self.compute_max_phase_deviation(d)

            if phase_dev <= NearFieldConfig.FRAUNHOFER_PHASE_THRESHOLD_RAD:
                # Found the transition distance
                return d

        # If numerical search fails, return analytical formula
        return d_F_analytical

    def compute_all_path_lengths(self, distance_m: float) -> np.ndarray:
        """
        Compute path lengths for all TX-RX element pairs.

        This provides a complete picture of the near-field geometry.
        Each TX element at (x_tx, y_tx, 0) connects to each RX element
        at (x_rx, y_rx, distance_m).

        Path length = √[(x_tx - x_rx)² + (y_tx - y_rx)² + distance_m²]

        Parameters:
        -----------
        distance_m : float
            Array separation distance in meters

        Returns:
        --------
        path_lengths : np.ndarray
            Array of shape (N1², N2²) with all path lengths
        """
        tx_size, rx_size = self.compute_array_dimensions()

        # TX element positions (centered at origin)
        tx_positions = []
        for i in range(self.n1):
            for j in range(self.n1):
                x = (i - (self.n1 - 1) / 2) * self.element_spacing
                y = (j - (self.n1 - 1) / 2) * self.element_spacing
                tx_positions.append((x, y, 0))

        # RX element positions (centered at (0, 0, distance_m))
        rx_positions = []
        for i in range(self.n2):
            for j in range(self.n2):
                x = (i - (self.n2 - 1) / 2) * self.element_spacing
                y = (j - (self.n2 - 1) / 2) * self.element_spacing
                rx_positions.append((x, y, distance_m))

        # Compute all path lengths
        path_lengths = []
        for tx_pos in tx_positions:
            for rx_pos in rx_positions:
                dx = tx_pos[0] - rx_pos[0]
                dy = tx_pos[1] - rx_pos[1]
                dz = tx_pos[2] - rx_pos[2]

                path_length = np.sqrt(dx**2 + dy**2 + dz**2)
                path_lengths.append(path_length)

        return np.array(path_lengths)

    def get_near_field_info(self) -> dict:
        """
        Return comprehensive near-field information.

        Returns:
        --------
        info : dict
            Dictionary with array sizes, wavelength, Fraunhofer distance, etc.
        """
        tx_size, rx_size = self.compute_array_dimensions()
        d_F = self.find_fraunhofer_distance()

        return {
            "tx_elements": self.n1**2,
            "rx_elements": self.n2**2,
            "tx_size_m": tx_size,
            "rx_size_m": rx_size,
            "tx_size_cm": tx_size * 100,
            "rx_size_cm": rx_size * 100,
            "wavelength_mm": self.wavelength * 1000,
            "element_spacing_mm": self.element_spacing * 1000,
            "fraunhofer_distance_m": d_F,
            "fraunhofer_distance_km": d_F / 1000 if d_F else None,
        }


def compare_near_field_at_frequencies(
    array_size_n: int, frequencies_ghz: np.ndarray
) -> dict:
    """
    Compare Fraunhofer distances at different frequencies.

    This shows how the near-field region extends further at higher frequencies
    (for fixed physical array size) because more elements fit in the array.

    Parameters:
    -----------
    array_size_n : int
        Number of elements per side (N × N)
    frequencies_ghz : np.ndarray
        Array of frequencies to analyze

    Returns:
    --------
    results : dict
        Dictionary mapping frequency to Fraunhofer distance
    """
    results = {}

    for freq in frequencies_ghz:
        analyzer = NearFieldAnalyzer(array_size_n, array_size_n, freq)
        d_F = analyzer.find_fraunhofer_distance()
        results[freq] = d_F

    return results


def estimate_near_field_gain_penalty(
    distance_m: float, fraunhofer_distance_m: float
) -> float:
    """
    Estimate the gain penalty when operating in the near-field.

    In the near-field, the actual gain is lower than the far-field
    prediction due to phase decoherence. This function provides a
    rough estimate of the penalty.

    Parameters:
    -----------
    distance_m : float
        Actual link distance
    fraunhofer_distance_m : float
        Fraunhofer distance for the arrays

    Returns:
    --------
    penalty_db : float
        Estimated gain penalty in dB (positive value = loss)
    """
    if distance_m >= fraunhofer_distance_m:
        # Far-field: no penalty
        return 0.0

    # Near-field: penalty increases as we get closer
    # Empirical model: penalty ∝ (d_F / d)^0.5
    ratio = fraunhofer_distance_m / distance_m
    penalty_db = 3 * np.sqrt(ratio - 1)  # 3 dB per doubling

    return min(penalty_db, 10.0)  # Cap at 10 dB


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("NEAR-FIELD ANALYSIS MODULE TEST")
    print("=" * 80)

    # Test 1: Basic near-field analysis
    print("\nTest 1: Near-Field Analysis for 8×8 Array at 200 GHz")
    print("-" * 80)

    analyzer = NearFieldAnalyzer(n1=8, n2=8, frequency_ghz=200)
    info = analyzer.get_near_field_info()

    print(f"Array Configuration:")
    print(f"  TX: {info['tx_elements']} elements ({analyzer.n1}×{analyzer.n1})")
    print(f"  RX: {info['rx_elements']} elements ({analyzer.n2}×{analyzer.n2})")
    print(f"  Physical Size: {info['tx_size_cm']:.2f} cm")
    print(f"  Wavelength: {info['wavelength_mm']:.2f} mm")
    print(f"  Element Spacing: {info['element_spacing_mm']:.2f} mm (λ/2)")
    print(f"\nFraunhofer Distance: {info['fraunhofer_distance_m']:.2f} m")

    # Test phase deviation at different distances
    print(f"\nPhase Deviation at Various Distances:")
    for dist in [10, 25, 50, 100, 200]:
        phase_dev_rad = analyzer.compute_max_phase_deviation(dist)
        phase_dev_deg = np.degrees(phase_dev_rad)
        status = "NEAR-FIELD" if dist < info["fraunhofer_distance_m"] else "FAR-FIELD"
        print(f"  {dist:3d} m: {phase_dev_deg:5.1f}° ({status})")

    # Test 2: Frequency scaling
    print("\n" + "-" * 80)
    print("Test 2: Fraunhofer Distance vs Frequency (8×8 array)")
    print("-" * 80)

    # frequencies = np.array([100, 150, 200, 300, 500])
    frequencies = np.array([100, 150, 200, 250, 300, 500, 700, 800, 900, 1000])
    freq_results = compare_near_field_at_frequencies(8, frequencies)

    print(
        f"{'Frequency (GHz)':>15} {'Fraunhofer Dist (m)':>20} {'Physical Size (cm)':>20}"
    )
    for freq in frequencies:
        analyzer_temp = NearFieldAnalyzer(8, 8, freq)
        size_cm = analyzer_temp.compute_array_dimensions()[0] * 100
        print(f"{freq:>15.0f} {freq_results[freq]:>20.1f} {size_cm:>20.2f}")

    # Test 3: Array size scaling
    print("\n" + "-" * 80)
    print("Test 3: Fraunhofer Distance vs Array Size (200 GHz)")
    print("-" * 80)

    # array_sizes = [4, 8, 16, 32]
    array_sizes = [4, 8, 16, 32, 64, 128, 256]
    print(
        f"{'Array Size':>12} {'Elements':>10} {'Phys Size (cm)':>15} {'Fraunhofer (m)':>15}"
    )

    for n in array_sizes:
        analyzer_temp = NearFieldAnalyzer(n, n, 200)
        info_temp = analyzer_temp.get_near_field_info()
        print(
            f"{n:>4}×{n:<4} {info_temp['tx_elements']:>10} "
            + f"{info_temp['tx_size_cm']:>15.2f} {info_temp['fraunhofer_distance_m']:>15.1f}"
        )

    # Test 4: Near-field gain penalty
    print("\n" + "-" * 80)
    print("Test 4: Near-Field Gain Penalty")
    print("-" * 80)

    analyzer = NearFieldAnalyzer(8, 8, 200)
    d_F = analyzer.find_fraunhofer_distance()

    print(f"Fraunhofer Distance: {d_F:.1f} m\n")
    print(f"{'Distance (m)':>15} {'Region':>15} {'Gain Penalty (dB)':>20}")

    for dist in [10, 25, 50, 75, 100]:
        penalty = estimate_near_field_gain_penalty(dist, d_F)
        region = "Near-field" if dist < d_F else "Far-field"
        print(f"{dist:>15} {region:>15} {penalty:>20.2f}")

    print("\n" + "=" * 80)
    print("✓ Near-field analysis module loaded successfully")
    print("=" * 80 + "\n")
