# Models and Theory Documentation

This document explains the mathematical models and physical theory underlying the THz Research Suite. Each section builds from fundamental principles through to the implementation, helping you understand not just what the code calculates, but why these calculations correctly represent THz wireless systems.

## Table of Contents

- [Antenna Array Model](#antenna-array-model)
- [Channel Propagation Model](#channel-propagation-model)
- [Link Budget and Capacity](#link-budget-and-capacity)
- [Beam Alignment Theory](#beam-alignment-theory)
- [Near-Field Propagation](#near-field-propagation)
- [Statistical Analysis Methods](#statistical-analysis-methods)

---

## Antenna Array Model

### Fundamental Principles

An antenna converts guided electromagnetic waves (traveling in coaxial cables or waveguides) into free-space electromagnetic radiation. A single antenna element might be a dipole, a patch, or a slot, but at THz frequencies we almost always use arrays of many elements working together coherently to achieve high gain.

The gain of an antenna array comes from constructive interference. When multiple elements transmit the same signal with appropriate phase relationships, their radiated fields add up constructively in certain directions (the main beam) and destructively in others (nulls). This focusing of energy into a narrow beam is exactly analogous to how a flashlight's parabolic reflector focuses light into a spotlight.

### Array Gain Formula

For a planar array of N identical elements arranged in a regular grid with proper phase excitation, the maximum directivity gain can be approximated as:

```
G = η × N × D_element
```

where η is the antenna efficiency (accounting for ohmic losses, typically 0.6 to 0.9), N is the total number of elements, and D_element is the directivity of a single element. For isotropic elements, D_element equals one, but practical elements have some inherent directivity.

For a square planar array, we add an additional factor that accounts for the directivity pattern:

```
G_dBi = 10 × log₁₀(η × N) + 10 dB
```

The ten-decibel term represents the directivity enhancement from the planar geometry. This formula gives the maximum gain in the boresight direction (perpendicular to the array plane).

### Element Spacing and Grating Lobes

Why do we always use lambda-over-two spacing? This choice represents a fundamental trade-off in array design. If we space elements closer than lambda-over-two, they fit too tightly and mutual coupling becomes severe, reducing efficiency. If we space them farther than lambda-over-two, something worse happens: grating lobes appear.

Grating lobes are duplicate main beams appearing at angles other than the desired direction. They occur when the spacing between elements equals or exceeds one wavelength, because then the radiation from adjacent elements can constructively interfere not only in the main direction but also at certain other angles determined by the array geometry. These grating lobes steal energy from the main beam and cause interference to other systems.

With lambda-over-two spacing, grating lobes are theoretically pushed to ninety degrees off axis where they cannot occur for a planar array, leaving all the energy in the desired main beam and

 controlled side lobes.

### Beamwidth Calculation

The three-decibel beamwidth (where gain drops to half its peak value) can be estimated from the array physical size D and wavelength λ:

```
θ_3dB ≈ 70° × (λ / D)
```

This formula comes from Fourier optics and represents the fundamental diffraction limit. A larger aperture (measured in wavelengths) produces a narrower beam. At THz frequencies where wavelengths are sub-millimeter, even modest physical sizes correspond to many wavelengths, producing extremely narrow beams.

For example, at two hundred gigahertz where wavelength is one point five millimeters, a five-centimeter array spans about thirty-three wavelengths, giving a beamwidth around two degrees. This narrow beam provides high gain but makes pointing critical.

### Pointing Error Loss

When the antenna beam is misaligned from the intended direction by an angle θ_error, the gain in the desired direction decreases approximately as:

```
Loss_dB ≈ 12 × (θ_error / θ_3dB)²
```

This quadratic relationship means that small pointing errors have relatively minor effects, but errors approaching the beamwidth cause severe gain loss. For a two-degree beamwidth, a one-degree pointing error causes three-decibel loss (reducing power by half), while a two-degree error causes twelve-decibel loss (reducing power to one-sixteenth).

This sensitivity to pointing errors is one of the biggest practical challenges in THz systems. Mechanical structures must be extremely rigid, and active tracking may be required for mobile scenarios.

### Fraunhofer Distance

The Fraunhofer distance marks the boundary between near-field and far-field regions. It is given by:

```
d_F = 2 × D² / λ
```

where D is the largest physical dimension of the antenna array. In the far-field (distances greater than d_F), the wavefront can be approximated as planar and conventional beamforming works correctly. In the near-field (distances less than d_F), the wavefront curvature becomes significant and special techniques are needed.

At THz frequencies with large arrays, the Fraunhofer distance can be surprisingly large. A ten-centimeter array at three hundred gigahertz has d_F equal to sixty meters. This means many practical links operate in the near-field, requiring modified analysis.

---

## Channel Propagation Model

### Free-Space Path Loss

When electromagnetic waves propagate through free space, their power density decreases with distance squared due to geometric spreading. The Friis transmission equation quantifies this for a link between two antennas:

```
P_rx = P_tx × (G_tx / (4πR)²) × G_rx × λ²
```

where P_rx is received power, P_tx is transmitted power, G_tx and G_rx are antenna gains (as linear ratios), R is distance, and λ is wavelength. Converting to logarithmic form in decibels:

```
P_rx(dBm) = P_tx(dBm) + G_tx(dBi) + G_rx(dBi) - PL_FSPL(dB)
```

The free-space path loss term is:

```
PL_FSPL(dB) = 20×log₁₀(f_Hz) + 20×log₁₀(d_m) + 20×log₁₀(4π/c)
            ≈ 20×log₁₀(f_GHz) + 20×log₁₀(d_m) + 92.45 dB
```

Notice that path loss increases with both frequency and distance, with a twenty-decibel-per-decade slope for each. Doubling the frequency or doubling the distance increases path loss by six decibels (a factor of four in linear terms).

### Molecular Absorption

At THz frequencies, atmospheric molecules absorb electromagnetic energy and re-emit it as thermal radiation in random directions, effectively removing power from the directed beam. This absorption is negligible at microwave frequencies but becomes the dominant loss mechanism at THz.

The absorption follows Beer's Law:

```
P(d) = P(0) × exp(-α × d)
```

where α is the absorption coefficient in nepers per meter, and d is distance. Converting to decibels:

```
L_absorption(dB) = α_dB/km × (d / 1000)
```

where α_dB/km is the specific absorption in decibels per kilometer.

### Why Molecules Absorb

Molecules absorb electromagnetic waves when the wave frequency matches one of their resonant transition frequencies. For rotational transitions in water vapor and magnetic transitions in oxygen, these resonances fall right in the THz range.

Water (H₂O) is particularly problematic because its bent molecular geometry creates a permanent electric dipole moment. The molecule has quantized rotational energy levels, and transitions between these levels occur at specific frequencies determined by quantum mechanics. The strong resonance near 183 gigahertz corresponds to a transition between the ground rotational state and a low-lying excited state.

Oxygen (O₂) has resonances at 60 gigahertz and 118 gigahertz from magnetic dipole transitions associated with unpaired electron spins. These are somewhat weaker than water resonances but still significant.

Between these resonant peaks lie "quiet windows" where absorption is relatively low. The bands from 140 to 150 gigahertz and 200 to 240 gigahertz are particularly attractive for communication because they offer both low absorption and reasonable bandwidth.

### Environmental Dependence

The absorption coefficient depends on atmospheric conditions:

**Oxygen absorption** scales linearly with pressure because the number density of oxygen molecules is proportional to total air density. At higher altitudes where pressure is lower, oxygen absorption decreases proportionally.

**Water vapor absorption** scales with absolute humidity (mass of water per volume of air), not relative humidity. The code converts relative humidity to absolute humidity using temperature, accounting for the fact that warmer air can hold more water vapor. This is why THz links often work better in winter (cold, dry) than summer (warm, humid) even if relative humidity is similar.

### Rain Attenuation

Rain adds additional attenuation through scattering and absorption by water droplets. The specific attenuation from rain can be estimated using the ITU-R P.838 model:

```
γ_rain = k × R^α
```

where R is rain rate in millimeters per hour, and k and α are frequency-dependent coefficients. At THz frequencies, even moderate rain (five millimeters per hour, light rain) can cause several decibels per kilometer of additional loss.

Rain is fundamentally different from water vapor because raindrops are much larger than wavelengths (millimeters versus microns). This means Mie scattering becomes important, where droplets scatter energy out of the beam. The combination of absorption and scattering makes rain a serious impairment for outdoor THz links.

---

## Link Budget and Capacity

### Complete Link Budget

The received power in a realistic THz link includes all gains and losses:

```
P_rx(dBm) = P_tx(dBm) + G_tx(dBi) + G_rx(dBi) - PL_FSPL(dB) 
            - L_absorption(dB) - L_rain(dB) - L_pointing(dB) - L_other(dB)
```

Each term must be carefully calculated:
- Transmit power from amplifier specifications
- Antenna gains from array design (accounting for efficiency and mutual coupling)
- Free-space path loss from Friis equation
- Molecular absorption from HITRAN data with environmental corrections
- Rain attenuation if applicable
- Pointing loss if beams are misaligned
- Other losses (polarization mismatch, connector losses, etc.)

### Thermal Noise

The receiver thermal noise power sets the fundamental limit on sensitivity. It arises from random thermal motion of electrons in resistive components and is given by:

```
N = k × T × B × F
```

where k is Boltzmann's constant, T is absolute temperature, B is bandwidth, and F is the noise figure (linear, not decibels). Converting to dBm:

```
N(dBm) = 10×log₁₀(k × T × B × F) + 30
```

For example, at room temperature (290 K) with ten-gigahertz bandwidth and ten-decibel noise figure:

```
N(dBm) = 10×log₁₀(1.38×10⁻²³ × 290 × 10×10⁹ × 10) + 30 ≈ -64 dBm
```

This means the receiver cannot reliably detect signals below about negative sixty-four dBm. This noise floor is one reason why THz systems need high-gain antennas.

### Signal-to-Noise Ratio

The signal-to-noise ratio determines how reliably we can detect the transmitted information:

```
SNR = P_rx / N
```

In decibels:

```
SNR(dB) = P_rx(dBm) - N(dBm)
```

For digital communication, we need a minimum SNR to achieve acceptable bit error rates. The exact requirement depends on the modulation scheme. Simple schemes like BPSK need about ten decibels SNR for bit error rate of ten to the minus six, while sophisticated schemes like 64-QAM need closer to twenty-five decibels SNR.

### Shannon Capacity

Claude Shannon proved in 1948 that the maximum rate at which information can be transmitted reliably over a noisy channel is:

```
C = B × log₂(1 + SNR)
```

where C is capacity in bits per second, B is bandwidth in hertz, and SNR is the signal-to-noise ratio (linear, not decibels). This fundamental limit applies regardless of how clever your coding or modulation scheme is.

Converting SNR from decibels and expressing capacity in gigabits per second:

```
C(Gbps) = (B_GHz × 10⁹) × log₂(1 + 10^(SNR_dB/10)) / 10⁹
        = B_GHz × log₂(1 + 10^(SNR_dB/10))
```

The logarithm means that capacity increases slowly with SNR at high SNR values. Doubling SNR (adding three decibels) increases capacity by one bit per second per hertz. This diminishing return means there is little benefit to excessively high SNR; it is usually better to improve bandwidth than to push SNR higher.

For example, with ten-gigahertz bandwidth and twenty-decibel SNR (ratio of one hundred):

```
C = 10 × log₂(1 + 100) = 10 × log₂(101) ≈ 10 × 6.66 = 66.6 Gbps
```

This is close to the theoretical maximum; real systems might achieve sixty to seventy percent of this due to imperfect coding and modulation.

---

## Beam Alignment Theory

### The Initial Alignment Problem

When a THz transmitter and receiver are first powered on, they do not know where to point their beams. The transmitter must search through the angular space (zero to 360 degrees in azimuth, possibly also minus ninety to plus ninety degrees in elevation) until its beam overlaps with the receiver's beam. This is the initial alignment problem.

The difficulty of this problem scales dramatically with beamwidth. For a ten-degree beamwidth, there are thirty-six possible pointing directions in a full circle. For a one-degree beamwidth, there are three hundred sixty directions. The narrower the beam, the longer it takes to find the receiver using naive search strategies.

### Search Strategies Analyzed

**Systematic Sweep (Clockwise or Counterclockwise):** The simplest approach is to start at a random angle and rotate step-by-step in one direction. This guarantees finding the receiver eventually, with expected time proportional to 180/beamwidth. For a one-degree beam, this averages ninety steps or ninety milliseconds if each step takes one millisecond. The worst case is twice as long if the receiver happens to be in the opposite direction from where we start.

**Random Search:** Randomly select untried angles until hitting the receiver. This has the same expected time as systematic sweep (the mathematics of random search in a finite space gives this result), but with much higher variance. Sometimes you get lucky and find the receiver quickly; other times you might test almost the entire space before succeeding. The high variability makes this unattractive for systems with latency requirements.

**Binary Search:** This is where innovation enters. Instead of testing angles sequentially, we can use a divide-and-conquer approach. Test the midpoint of the current search range; based on whether alignment occurs, eliminate half the remaining space. This gives logarithmic complexity: log₂(360) equals about nine steps for one-degree resolution, compared to ninety steps for systematic sweep. This ten-times speedup is significant for narrow-beam systems.

The key insight is that binary search performance is nearly independent of beamwidth, whereas systematic and random search get linearly worse as beams narrow. This makes binary search increasingly superior as we move to higher frequencies and larger arrays with narrower beams.

**Adaptive Two-Phase:** A practical hybrid approach uses coarse steps (say, twice the beamwidth) to quickly narrow down the region, then fine steps to precisely locate the receiver. This reduces the constant factor compared to pure systematic sweep while maintaining simple implementation.

### Three-Dimensional Extension

In 3D, both azimuth and elevation must be searched. The naive approach of exhaustively testing all azimuth-elevation combinations takes the product of 1D times, making it prohibitively slow. A hierarchical strategy works better: first perform coarse azimuth search, then fine elevation search at the best azimuth, then refinement. This sequential approach takes the sum of 1D times rather than the product, a huge improvement.

---

## Near-Field Propagation

### Far-Field Approximation and Its Limits

In the far-field, we assume plane waves: the wavefront arriving at the receiver is flat, with all path lengths approximately equal. This simplifies beamforming because we can add signals from different antenna elements using simple phase shifts proportional to element position.

But this approximation breaks down when the transmit-receive distance is comparable to the Fraunhofer distance. In the near-field, the wavefront is curved like ripples on a pond, and path lengths from transmitter elements to receiver elements differ significantly.

### Phase Deviation Analysis

Consider a transmit array of size D_tx and a receive array of size D_rx separated by distance d. The shortest path is center-to-center with length d. The longest paths are corner-to-corner with approximate length:

```
d_max ≈ sqrt(d² + (D_tx/2)² + (D_rx/2)²)
```

The path length difference is:

```
Δpath = d_max - d ≈ (D_tx² + D_rx²) / (4d)
```

where the approximation holds for d much larger than D. This path difference translates to a phase difference:

```
Δφ = 2π × Δpath / λ
```

The Fraunhofer criterion requires this maximum phase deviation to be less than π/8 radians:

```
Δφ ≤ π/8

2π × (D_tx² + D_rx²) / (4d × λ) ≤ π/8

d ≥ 2 × (D_tx² + D_rx²) / λ
```

For equal-sized arrays (D_tx equals D_rx equals D), this simplifies to:

```
d_F = 2D² / λ
```

This is the Fraunhofer distance. Links operating at d less than d_F are in the near-field and require special handling.

### Implications for THz Systems

At THz frequencies with large arrays, the near-field extends remarkably far. A ten-centimeter array at 300 gigahertz (wavelength one millimeter) has:

```
d_F = 2 × (0.1 m)² / (0.001 m) = 20 meters
```

Many practical deployments fall within this range, meaning near-field effects cannot be ignored. Fortunately, near-field operation is not necessarily bad; it just requires different signal processing. Near-field focusing can actually provide additional spatial selectivity and may help with interference mitigation.

---

## Statistical Analysis Methods

### Why Monte Carlo?

Deterministic calculations give you one answer: "The capacity is forty-five gigabits per second." But real systems face numerous uncertainties: transmit power varies by plus or minus half a decibel, pointing errors fluctuate, weather changes. Monte Carlo simulation quantifies these uncertainties by running thousands of trials with randomly perturbed parameters.

### Statistical Metrics

**Mean and Median:** The mean (average) tells you the central tendency, but for skewed distributions, the median (fiftieth percentile) may be more representative. In communication systems, distributions are often slightly skewed with a long tail toward low capacity when multiple impairments align unfavorably.

**Standard Deviation:** This measures spread or variability. A high standard deviation means capacity is unpredictable; a low standard deviation means it is relatively stable. For system design, you often care more about worst-case performance than average, so high variability is concerning.

**Percentiles:** The fifth percentile tells you the capacity that you exceed ninety-five percent of the time. This is often more useful for quality-of-service guarantees than the mean. If your fifth percentile is forty gigabits per second, you can be confident of at least that capacity in almost all conditions.

**Confidence Intervals:** A ninety-five percent confidence interval on the mean, say [43, 47] gigabits per second, means that if you repeated the entire experiment many times, ninety-five percent of the computed confidence intervals would contain the true mean. This quantifies your uncertainty about the mean value itself.

**Outage Probability:** The fraction of trials where capacity falls below some threshold. If your target is fifty gigabits per second and outage probability is five percent, the link fails to meet requirements five percent of the time. This metric directly translates to service level agreements.

### Environmental Sensitivity

By varying one parameter while holding others constant and running Monte Carlo at each value, we can measure sensitivity: how much does capacity change per unit change in that parameter? Parameters with high sensitivity deserve careful attention in system design, while those with low sensitivity can be treated more casually.

For THz systems, humidity typically shows the highest sensitivity above 200 gigahertz due to strong water vapor absorption. Temperature has moderate sensitivity through both noise and absorption effects. Pressure has relatively low sensitivity, mainly affecting oxygen absorption.

---

**Last Updated:** January 2026 | **Version:** 1.0
