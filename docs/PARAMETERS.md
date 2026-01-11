# Configuration Parameters Guide

This document provides a comprehensive explanation of every configurable parameter in the THz Research Suite. Understanding these parameters is essential for customizing the simulation to match your specific research questions, hardware constraints, or deployment scenarios.

## Table of Contents

- [Physical Constants](#physical-constants)
- [Environmental Parameters](#environmental-parameters)
- [Simulation Configuration](#simulation-configuration)
- [Antenna Array Parameters](#antenna-array-parameters)
- [Frequency and Channel Configuration](#frequency-and-channel-configuration)
- [Link Budget Parameters](#link-budget-parameters)
- [Molecular Absorption Database](#molecular-absorption-database)
- [Beam Alignment Parameters](#beam-alignment-parameters)
- [Near-Field Analysis Parameters](#near-field-analysis-parameters)
- [Visualization Configuration](#visualization-configuration)
- [Predefined Research Scenarios](#predefined-research-scenarios)

---

## Physical Constants

These fundamental constants define the physical universe in which our electromagnetic waves propagate. You should not modify these values unless you are simulating a different physical medium or testing the sensitivity of your results to measurement uncertainties in fundamental constants.

### Speed of Light
**Parameter:** `PhysicalConstants.SPEED_OF_LIGHT`  
**Value:** 3 × 10⁸ meters per second  
**Purpose:** This is the speed at which electromagnetic waves propagate through vacuum and approximately through air at sea level. We use this constant to calculate wavelength from frequency using the relationship lambda equals c divided by f. In dense atmospheric conditions or at high altitudes, the actual propagation speed may differ slightly, but the error is typically less than zero point zero three percent and can be safely ignored for most applications.

### Boltzmann Constant
**Parameter:** `PhysicalConstants.BOLTZMANN_CONSTANT`  
**Value:** 1.38 × 10⁻²³ joules per Kelvin  
**Purpose:** This constant relates temperature to thermal energy and is essential for calculating thermal noise in receivers. The thermal noise power is given by N equals k times T times B times F, where k is Boltzmann's constant, T is absolute temperature, B is bandwidth, and F is the noise figure. This noise sets the fundamental limit on receiver sensitivity in any communication system.

### Standard Temperature
**Parameter:** `PhysicalConstants.STANDARD_TEMPERATURE`  
**Value:** 290 Kelvin (approximately seventeen degrees Celsius)  
**Purpose:** This represents a typical room temperature or mild outdoor temperature and serves as the baseline for noise calculations when environmental variations are not being explicitly modeled. Many communication system specifications assume this temperature as a reference point for comparing performance across different implementations.

---

## Environmental Parameters

The environment through which THz waves propagate has a profound effect on link performance. Unlike lower frequencies where atmospheric effects are minimal, THz systems experience significant absorption from water vapor and oxygen molecules. These parameters let you model different weather conditions, climates, and altitudes.

### Temperature
**Parameter:** `EnvironmentalParams.temperature_k`  
**Default:** 290 Kelvin  
**Typical Range:** 250-320 Kelvin (minus twenty-three to forty-seven degrees Celsius)  
**Physical Meaning:** Ambient air temperature affects two things in THz systems. First, it determines the thermal noise floor in the receiver through the formula N equals k times T times B times F. Higher temperatures mean more thermal noise. Second, temperature affects molecular absorption because it changes the kinetic energy distribution of air molecules, slightly altering their absorption cross-sections. The effect on absorption is relatively small compared to humidity effects, but it becomes significant in very hot or very cold environments.

**When to Adjust:** Use realistic temperature values for your deployment scenario. Indoor environments might stay near 293 Kelvin (twenty degrees Celsius), while outdoor deployments could see 253 Kelvin (minus twenty degrees Celsius) in winter or 313 Kelvin (forty degrees Celsius) in summer. Desert deployments might experience even wider swings. For Monte Carlo simulations, the code adds random variations with standard deviation of five Kelvin to represent thermal fluctuations over time.

### Humidity
**Parameter:** `EnvironmentalParams.humidity_percent`  
**Default:** 50 percent  
**Typical Range:** 10-90 percent relative humidity  
**Physical Meaning:** This is the most critical environmental parameter for THz communications because water vapor is an extremely strong absorber at many THz frequencies. The parameter represents relative humidity, which is the ratio of actual water vapor pressure to saturation vapor pressure at a given temperature. However, what actually determines absorption is absolute humidity, measured in grams of water per cubic meter of air. The code automatically converts relative humidity to absolute humidity using the Magnus formula, which accounts for the fact that warmer air can hold more water vapor even at the same relative humidity.

**Physical Insight:** Why does water matter so much? Water molecules have a permanent electric dipole moment and several rotational resonance frequencies in the THz range, particularly around 183 gigahertz, 380 gigahertz, and higher. When a THz wave passes through humid air, the oscillating electric field tries to rotate the water molecules at the wave's frequency. If the frequency matches a rotational resonance, the molecules absorb energy efficiently, converting electromagnetic energy into molecular rotation and eventually heat.

**When to Adjust:** Dry climates like deserts might have ten to twenty percent humidity, temperate regions typically see forty to sixty percent, and tropical areas can reach eighty to ninety-five percent. Humidity also varies daily, usually being lowest in the afternoon when temperature is highest and highest at night. For link planning, you should use the worst-case humidity expected in your deployment region.

### Pressure
**Parameter:** `EnvironmentalParams.pressure_kpa`  
**Default:** 101.325 kilopascals (sea level)  
**Typical Range:** 85-105 kilopascals  
**Physical Meaning:** Atmospheric pressure determines the density of air molecules, which directly affects oxygen absorption. Oxygen has absorption peaks at 60 gigahertz and 118 gigahertz due to magnetic dipole transitions. Unlike water vapor absorption which depends on absolute humidity, oxygen absorption scales linearly with pressure because the oxygen concentration is proportional to total air density.

**Altitude Effects:** Pressure decreases exponentially with altitude following the barometric formula. At 1500 meters altitude (typical for many cities like Denver or Mexico City), pressure drops to about 85 kilopascals, reducing oxygen absorption by approximately seventeen percent. Conversely, in below-sea-level locations like Death Valley, pressure might reach 103 kilopascals, slightly increasing absorption.

**When to Adjust:** Use local pressure values for your deployment site. Weather systems also cause pressure variations of plus or minus five kilopascals, which is why the Monte Carlo simulation adds random pressure variations with standard deviation of two kilopascals. For aircraft or drone deployments, pressure changes dramatically with altitude and must be accounted for explicitly.

---

## Simulation Configuration

These parameters control how the Monte Carlo simulations run, affecting the trade-off between accuracy and computation time.

### Number of Simulations
**Parameter:** `SimulationConfig.NUM_SIMULATIONS`  
**Default:** 1000 trials  
**Quick Mode:** 200 trials  
**Purpose:** This determines how many Monte Carlo trials to run. Each trial generates random perturbations to system parameters (transmit power, pointing errors, environmental conditions) and computes the resulting capacity. With more trials, you get better statistical estimates of mean, standard deviation, and percentile values, but computation time increases linearly.

**How Many Do You Need?** Statistical theory tells us that the standard error of the mean decreases as one divided by the square root of the number of samples. With one hundred trials, you know the true mean to within about ten percent. With one thousand trials, you know it to within about three percent. With ten thousand trials, you know it to within one percent. For most research purposes, one thousand trials provides a good balance between accuracy and speed, giving you confidence intervals that are tight enough to draw meaningful conclusions without waiting hours for results.

**Computation Time:** On a typical laptop with four cores, one thousand trials take approximately two to three minutes for a single frequency-distance-array configuration. The full suite with fifteen figures takes about thirty to forty minutes because some figures require running Monte Carlo at multiple parameter combinations.

### Confidence Level
**Parameter:** `SimulationConfig.CONFIDENCE_LEVEL`  
**Default:** 0.95 (ninety-five percent)  
**Purpose:** This determines the width of confidence intervals reported for capacity and SNR. A ninety-five percent confidence interval means that if you repeated the entire experiment many times, ninety-five percent of the computed intervals would contain the true mean value. Common alternatives are ninety percent confidence (narrower intervals, less conservative) or ninety-nine percent confidence (wider intervals, more conservative).

**Interpretation:** When you see a result like "capacity equals forty-five plus or minus three gigabits per second at ninety-five percent confidence," this means you can be ninety-five percent certain the true mean capacity lies between forty-two and forty-eight gigabits per second, assuming your models are correct.

### Random Seed
**Parameter:** `SimulationConfig.RANDOM_SEED`  
**Default:** 42  
**Purpose:** Setting a fixed random seed makes the simulations reproducible. Every time you run the code with the same seed, you will get exactly the same sequence of random numbers and therefore exactly the same results. This is essential for scientific reproducibility. If you want to test whether results change with different random sequences, you can either remove the seed (making it truly random) or try several different seed values.

### Uncertainty Parameters
These standard deviations define how much random variation to add in Monte Carlo trials. They represent typical real-world uncertainties:

**TX Power Standard Deviation:** 0.5 decibels  
This represents transmit power variations from amplifier drift, temperature effects, and aging. High-quality power amplifiers can achieve better stability (0.2 decibels), while low-cost designs might see one decibel or more of variation.

**Pointing Error Standard Deviation:** 2.0 degrees  
This represents beam pointing uncertainty from mechanical jitter, vibration, wind loading, and calibration errors. Fixed installations with rigid mounting might achieve one degree or better, while mobile platforms might see five degrees or more. This parameter has a huge impact on link performance because even small pointing errors cause significant gain reduction when beamwidths are narrow.

**Temperature Standard Deviation:** 5 Kelvin  
This represents thermal fluctuations over time. Rapid weather changes, clouds passing over the link, or daily temperature cycles can cause these variations. Indoor links see much smaller variations (one to two Kelvin).

**Humidity Standard Deviation:** 10 percent  
This represents daily and hour-to-hour humidity variations. Morning dew, afternoon heating, and weather fronts all cause humidity to fluctuate substantially.

**Pressure Standard Deviation:** 2 kilopascals  
This represents pressure variations from weather systems. A strong low-pressure system versus a high-pressure system might differ by ten kilopascals, but the Monte Carlo models shorter-term variations around the mean.

---

## Antenna Array Parameters

Antenna arrays are the key enabling technology for THz communications because they provide the high gains needed to overcome path loss. These parameters let you explore different array designs.

### Default Array Size
**Parameter:** `AntennaConfig.DEFAULT_ARRAY_SIZE_CM`  
**Default:** 5 centimeters  
**Typical Range:** 1-30 centimeters  
**Physical Meaning:** This is the physical dimension of the square planar array. For example, a five-centimeter array means five centimeters by five centimeters. The number of elements that fit in this area depends on frequency through the lambda-over-two spacing requirement. At 100 gigahertz with wavelength three millimeters, a five-centimeter array contains roughly sixteen by sixteen equals two hundred fifty-six elements. At 300 gigahertz with wavelength one millimeter, the same five-centimeter array contains one hundred by one hundred equals ten thousand elements.

**Design Trade-offs:** Larger arrays provide higher gain, which improves link budget and allows longer distances or higher data rates. However, they also have narrower beamwidths, making pointing more critical, and they extend the near-field zone to greater distances. Additionally, larger arrays cost more to manufacture and are more affected by mechanical deformation.

### Element Spacing Factor
**Parameter:** `AntennaConfig.ELEMENT_SPACING_FACTOR`  
**Default:** 0.5 (lambda over two)  
**Why This Value?** Lambda-over-two spacing is optimal for maximizing gain while preventing grating lobes. If elements are spaced closer than lambda-over-two, you waste space because mutual coupling becomes too strong and efficiency drops. If elements are spaced farther than lambda-over-two, grating lobes appear in the radiation pattern, meaning energy goes in unwanted directions. These grating lobes are duplicates of the main beam at other angles, reducing the gain in the desired direction and causing interference.

### Antenna Efficiency
**Parameter:** `AntennaConfig.DEFAULT_EFFICIENCY`  
**Default:** 0.8 (eighty percent)  
**Typical Range:** 0.6-0.9  
**Physical Meaning:** Real antennas have losses. Ohmic losses in conductors, dielectric losses in substrates, impedance mismatches, and feed network losses all convert RF power into heat rather than radiated energy. An efficiency of eighty percent means twenty percent of the power is lost, corresponding to approximately one decibel of loss.

**Frequency Dependence:** Losses generally increase with frequency because conductor resistivity has a component that scales with square root of frequency (skin effect), and dielectric loss tangent often increases with frequency. At very high THz frequencies above 500 gigahertz, achieving even sixty percent efficiency becomes challenging.

### Mutual Coupling Loss
**Parameter:** `AntennaConfig.MUTUAL_COUPLING_LOSS_DB`  
**Default:** 0.5 decibels  
**Typical Range:** 0.2-2.0 decibels  
**Physical Meaning:** When antenna elements are placed close together (lambda-over-two spacing), they interact electromagnetically. The current in one element induces currents in nearby elements, which re-radiate and interfere with the desired pattern. This mutual coupling reduces the effective gain and creates scan blindness in certain directions. Half a decibel is typical for well-designed arrays with good isolation between elements. Poorly designed arrays might see two decibels or more of coupling loss.

---

## Frequency and Channel Configuration

These parameters define the frequency bands and channel characteristics for your analysis.

### Frequency Ranges
**Sub-THz:** 100-300 gigahertz  
**THz:** 300-1000 gigahertz  
**Sweet Spot:** 200-300 gigahertz for practical systems

The distinction between sub-THz and THz is somewhat arbitrary, but generally frequencies below 300 gigahertz are considered more practical for near-term deployment because component technology is more mature. The band from 200 to 300 gigahertz is particularly attractive because it offers both quiet windows with low molecular absorption and sufficient bandwidth for hundred-gigabit-per-second links.

### Default Bandwidth
**Parameter:** `FrequencyConfig.DEFAULT_BANDWIDTH_GHZ`  
**Default:** 10 gigahertz  
**Typical Range:** 1-50 gigahertz  
**Purpose:** This is the RF bandwidth available for data transmission. Shannon capacity increases linearly with bandwidth, so wide channels are desirable. However, maintaining coherence over wide bandwidths becomes challenging, and regulatory allocations may limit available spectrum.

**Capacity Impact:** With a ten-gigahertz bandwidth and SNR of 20 decibels (ratio of one hundred), Shannon capacity is approximately sixty gigabits per second. Doubling the bandwidth to twenty gigahertz doubles the capacity to approximately one hundred twenty gigabits per second, assuming SNR remains constant.

---

## Link Budget Parameters

These parameters define the transmitter and receiver characteristics that determine the link budget equation: received power equals transmitted power plus transmit gain plus receive gain minus path loss.

### Transmit Power
**Parameter:** `LinkBudgetConfig.DEFAULT_TX_POWER_DBM`  
**Default:** 10 dBm (ten milliwatts)  
**Typical Range:** 0-30 dBm  
**Physical Meaning:** This is the RF power fed to the transmit antenna. Ten dBm corresponds to ten milliwatts, which is moderate for THz systems. Higher powers improve link budget but require more DC power consumption and may face regulatory limits. Lower powers save energy but require larger antenna arrays to compensate.

**Why Not More Power?** At THz frequencies, generating high RF power is very difficult. Solid-state amplifiers typically produce one to one hundred milliwatts. Vacuum electronics can reach higher powers but are bulky and expensive. Also, at very high powers, nonlinear effects in the atmosphere become significant, and you may face regulatory limits from radiation safety standards.

### Noise Figure
**Parameter:** `LinkBudgetConfig.DEFAULT_NOISE_FIGURE_DB`  
**Default:** 10 decibels  
**Typical Range:** 6-15 decibels  
**Physical Meaning:** The noise figure quantifies how much noise the receiver adds beyond the theoretical thermal noise limit. A noise figure of zero decibels means the receiver adds no noise (impossible in practice). A noise figure of ten decibels means the receiver adds ten times as much noise power as the thermal noise floor, degrading SNR by ten decibels.

**Technology Limits:** At room temperature and low frequencies, noise figures below three decibels are common. At THz frequencies, achieving even six decibels is challenging because transistor speeds approach their limits, and parasitic effects become significant. State-of-the-art THz receivers achieve eight to twelve decibels. Cryogenic cooling can improve noise figure but adds cost and complexity.

### Distance Ranges
The suite analyzes links from one meter (very short range, perhaps inter-chip communication) to one thousand meters (long-range backhaul). The logarithmic spacing in distance ensures adequate sampling across this wide range while keeping computation tractable.

---

## Molecular Absorption Database

This database maps frequency to oxygen and water vapor absorption coefficients. The values are derived from the HITRAN spectroscopic database, which contains line-by-line absorption data for atmospheric molecules based on laboratory measurements and quantum mechanical calculations.

### Database Structure
Each entry maps a frequency in gigahertz to a tuple of (oxygen_absorption, water_vapor_absorption) in decibels per kilometer under reference conditions (twenty degrees Celsius, fifty percent relative humidity, sea-level pressure).

### Key Absorption Features

**60 GHz Band:** Strong oxygen absorption (ten to fifteen decibels per kilometer) makes this unsuitable for long-range communication but attractive for short-range secure links where attenuation provides isolation.

**118 GHz Peak:** Oxygen resonance creating 0.8 decibels per kilometer absorption, manageable for ranges up to a few hundred meters.

**140-150 GHz Quiet Window:** Low absorption (0.1-0.15 decibels per kilometer) excellent for long-range links.

**183 GHz Peak:** Very strong water vapor resonance (fifteen decibels per kilometer) essentially blocking communication in humid conditions.

**200-240 GHz Quiet Window:** Relatively low absorption (one to three decibels per kilometer), the sweet spot for practical THz systems offering a good balance of low absorption and sufficient bandwidth.

**300-400 GHz:** Increasing water vapor absorption (eight to fifteen decibels per kilometer) limiting range but still workable for short links with high gain arrays.

**Above 500 GHz:** Severe absorption (twenty to thirty decibels per kilometer or more) restricting communication to very short ranges under ten meters in typical conditions, or longer ranges in extremely dry environments.

### Environmental Scaling
The code applies two correction factors to the reference absorption values. Oxygen absorption scales linearly with pressure divided by reference pressure because oxygen concentration is proportional to total air density. Water vapor absorption scales linearly with absolute humidity divided by reference absolute humidity because the number of absorbing water molecules is directly proportional to water vapor density.

---

## Beam Alignment Parameters

Beam alignment is one of the most critical challenges in THz systems because the extremely narrow beamwidths (often less than one degree) mean that transmitter and receiver must point very precisely at each other.

### Beamwidth Ranges
**Parameter:** `BeamAlignmentConfig.BEAMWIDTH_RANGE_DEG`  
**Default:** 5-60 degrees  
**Typical THz Beamwidths:** 1-10 degrees for practical arrays

The beamwidth depends inversely on array size in wavelengths. A five-centimeter array at 200 gigahertz has approximately thirty-three wavelengths of aperture, giving a beamwidth around two to three degrees. Larger arrays or higher frequencies produce even narrower beams. The simulation tests a wide range of beamwidths to show how alignment difficulty increases dramatically as beams become narrower.

### Number of Alignment Simulations
**Parameter:** `BeamAlignmentConfig.NUM_ALIGNMENT_SIMULATIONS`  
**Default:** 1000 trials  
**Purpose:** Each Monte Carlo trial starts the transmitter at a random angle and measures how long it takes to find the receiver using a specific search strategy. With one thousand trials, you can reliably estimate the mean alignment time and the full probability distribution, including worst-case scenarios.

### Alignment Detection Time
**Parameter:** `BeamAlignmentConfig.ALIGNMENT_DETECTION_TIME_MS`  
**Default:** 1 millisecond  
**Purpose:** Once beams overlap, the system needs some time to detect alignment by sensing received signal strength or establishing a control channel. One millisecond is realistic for fast digital signal processing. This time is added to the search time to get total alignment time.

---

## Near-Field Analysis Parameters

Near-field effects become dominant when the link distance is comparable to or less than the Fraunhofer distance, defined as twice the array size squared divided by wavelength.

### Array Element Counts
**Parameter:** `NearFieldConfig.ARRAY_ELEMENT_COUNTS`  
**Default:** [4, 8, 16, 32] elements per side  
**Purpose:** These values let you see how near-field region extends with array size. A four-by-four array (sixteen total elements) has a modest near-field, while a thirty-two-by-thirty-two array (one thousand twenty-four elements) has a near-field extending potentially hundreds of meters at THz frequencies.

### Fraunhofer Phase Threshold
**Parameter:** `NearFieldConfig.FRAUNHOFER_PHASE_THRESHOLD_RAD`  
**Default:** π/8 radians (22.5 degrees)  
**Purpose:** This is the criterion for far-field behavior. When the maximum phase deviation across receiving antenna elements is less than π/8 radians, the wavefront can be approximated as planar with less than three percent error in gain. This threshold comes from antenna theory and represents the point where conventional far-field beamforming becomes accurate.

**Why π/8?** This specific value represents a practical compromise. Smaller thresholds like π/16 would define the far-field more conservatively but push the Fraunhofer distance farther out, making more links operate in the near-field. Larger thresholds like π/4 would classify more links as far-field but with larger errors in gain predictions.

---

## Visualization Configuration

These parameters control the appearance of generated figures, ensuring they meet publication standards.

### Figure Resolution
**Parameter:** `SimulationConfig.FIGURE_DPI`  
**Default:** 300 dots per inch  
**Purpose:** This is the standard resolution for journal publication. Images at 300 DPI appear sharp when printed. Lower resolutions like 150 DPI are acceptable for online viewing but may look pixelated when printed. Higher resolutions like 600 DPI are sometimes required for certain journals but produce larger files.

### Font Sizes
The default font sizes (thirteen-point titles, twelve-point labels, ten-point legends) follow typical academic publication style guides. They ensure text is readable both on screen and in print.

### Color Choices
The default color scheme uses distinct, colorblind-friendly colors that reproduce well in both color and grayscale. When figures are photocopied or printed in black and white, different line styles and markers distinguish curves.

---

## Predefined Research Scenarios

The configuration file includes four predefined scenarios representing common deployment cases. Each scenario specifies a complete link configuration including frequency, distance, array size, transmit power, target capacity, and environmental conditions.

### Urban Backhaul
**Target:** Fifty gigabits per second at one hundred meters  
**Frequency:** 200 gigahertz  
**Environment:** Temperate (50% humidity)  
**Application:** Connecting buildings in dense urban areas where fiber installation is difficult or expensive.

### Short-Range High-Capacity
**Target:** One hundred gigabits per second at ten meters  
**Frequency:** 300 gigahertz  
**Environment:** Low humidity (40%)  
**Application:** Data center interconnects, kiosk downloads, device-to-device communication.

### Long-Range Moderate
**Target:** Ten gigabits per second at five hundred meters  
**Frequency:** 140 gigahertz (quiet window)  
**Environment:** Higher humidity (60%)  
**Application:** Rural connectivity, temporary event networks, emergency communications.

### Extreme Weather
**Target:** Thirty gigabits per second at one hundred meters  
**Frequency:** 200 gigahertz  
**Environment:** Hot and humid (85% humidity, 32°C)  
**Application:** Testing system robustness under worst-case conditions.

You can use these scenarios as templates, modifying them for your specific needs, or create entirely new scenarios with different parameter combinations.

---

## Parameter Sensitivity

Understanding which parameters matter most helps you focus your analysis. From extensive simulation experience, here is the sensitivity ranking for link capacity:

**Most Sensitive:**
1. Frequency (determines both gain and absorption)
2. Distance (inverse square law for path loss)
3. Array size (quadratic effect on gain)
4. Humidity (strong effect on water vapor absorption above 200 GHz)

**Moderately Sensitive:**
5. Transmit power (linear effect on received power)
6. Noise figure (directly affects SNR)
7. Bandwidth (linear effect on capacity)
8. Pointing errors (catastrophic when beamwidth is narrow)

**Less Sensitive:**
9. Temperature (small effect on both noise and absorption)
10. Pressure (affects only oxygen absorption)
11. Antenna efficiency (one to two decibel effect)
12. Mutual coupling (half to one decibel effect)

This ranking helps you decide where to focus when optimizing a system design or where to tighten tolerances in manufacturing.

---

**Last Updated:** January 2026 | **Version:** 1.0
