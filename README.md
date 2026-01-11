# Sub-THz/THz Wireless Communications Research

A comprehensive, patent-ready research framework for analyzing terahertz wireless communication systems, with focus on 6G and beyond-6G networks (100-1000 GHz).

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![IEEE](https://img.shields.io/badge/Standard-IEEE%20802.15.3--2023-orange)](https://standards.ieee.org/)

## Overview

This research suite provides a complete framework for analyzing wireless communication systems operating in the sub-terahertz and terahertz frequency bands. The project addresses fundamental challenges in next-generation wireless networks, including antenna array design, molecular absorption effects, beam alignment strategies, and near-field propagation phenomena.

![Alt text](docs/project_overview.png)

### What Makes THz Communication Different?

Traditional microwave and millimeter-wave systems operate below 100 gigahertz, where propagation is relatively straightforward. However, when we move into the terahertz spectrum, several new phenomena emerge that fundamentally change how we design wireless systems. Water vapor and oxygen molecules in the atmosphere strongly absorb electromagnetic waves at specific frequencies, creating "absorption peaks" where communication becomes very difficult and "quiet windows" where longer-range links are feasible. Additionally, the very high frequencies allow us to pack thousands of antenna elements into compact arrays, creating extremely high gains but also extending the near-field zone to distances of tens or even hundreds of meters.

This research suite models all these effects with realistic impairments, statistical uncertainty quantification, and multiple optimization strategies to help you design practical THz communication systems.

## Key Features

### Comprehensive Physical Modeling
The suite implements accurate models for every component of a THz wireless link, from the antenna arrays through the propagation channel to the receiver. Each model accounts for realistic impairments such as antenna efficiency losses, mutual coupling between array elements, beam pointing errors from mechanical jitter, and environmental variations in temperature, humidity, and atmospheric pressure.

### Statistical Analysis with Monte Carlo
Real-world systems face numerous sources of uncertainty that single-point calculations cannot capture. The Monte Carlo simulation engine runs thousands of trials with randomly perturbed parameters to provide statistical distributions, confidence intervals, and outage probabilities rather than just mean values. This tells you not only what performance to expect on average, but also how much variability you might see and what the worst-case scenarios look like.

### Multiple Beam Alignment Strategies
One of the biggest challenges in THz systems is the initial alignment problem. With beamwidths often less than one degree, how do transmitter and receiver find each other when they start at random orientations? The suite implements and compares five different search strategies, from simple systematic sweeps to novel hierarchical algorithms, showing you the trade-offs between complexity, speed, and reliability.

## Research Outputs

### Fifteen Publication-Quality Figures
The suite generates a complete set of figures suitable for journal papers, conference presentations, and patent applications. The figures are organized into two groups: basic analysis figures that establish fundamental relationships, and advanced Monte Carlo figures that quantify uncertainty and sensitivity.

**Basic Analysis (Figures 1-9):**
- Antenna array gain as a function of frequency and physical size
- Total path loss including free-space spreading and molecular absorption
- Shannon capacity calculations showing achievable data rates
- Beam alignment performance comparing different search strategies
- Near-field phase analysis identifying the Fraunhofer distance boundary
- Two-dimensional versus three-dimensional alignment complexity

**Advanced Monte Carlo Analysis (Figures 10-15):**
- Capacity distributions showing mean, standard deviation, and percentiles
- Environmental sensitivity to temperature, humidity, and pressure variations
- Capacity versus distance with ninety-percent confidence intervals
- Advanced beam alignment strategies with probability density functions
- Antenna gain degradation from realistic impairments
- Rain attenuation impact on link capacity

### Exportable Data in CSV Format
All simulation results are automatically exported to comma-separated value files for further analysis in Excel, MATLAB, Python, or other tools. The exported data includes raw Monte Carlo samples, statistical summaries, link budget breakdowns, and beam alignment timing distributions.

## Quick Start

### Installation

The research suite requires Python three point eight or later along with three scientific computing libraries. You can install everything with a single pip command:

```bash
pip install numpy scipy matplotlib pandas
```

For optimal performance on large Monte Carlo simulations, we recommend installing on a system with at least four gigabytes of RAM and a modern multi-core processor.

### Basic Usage

Running the complete research suite is straightforward. Simply execute the main script from your terminal:

```bash
python main.py
```

This will automatically generate all fifteen figures, run Monte Carlo simulations, export data to CSV files, and provide a comprehensive summary of execution time and outputs.

If you want to run just a specific analysis module to test it independently, you can execute any of the component files directly:

```bash
python antenna_models.py      # Test antenna array calculations
python channel_models.py       # Test path loss models
python monte_carlo_simulation.py  # Run statistical analysis
```

Each module includes self-test code that demonstrates its functionality and verifies correct operation.

### Customizing Parameters

All simulation parameters are centralized in the configuration file, making it easy to adjust the analysis without modifying the core implementation. For example, to change the number of Monte Carlo trials, the frequency range, or the array sizes being analyzed, simply edit the relevant values in `config.py`:

```python
# Increase Monte Carlo trials for higher statistical confidence
SimulationConfig.NUM_SIMULATIONS = 5000

# Analyze different frequency range
FrequencyConfig.MIN_FREQUENCY_GHZ = 200
FrequencyConfig.MAX_FREQUENCY_GHZ = 500

# Test larger antenna arrays
AntennaConfig.ARRAY_SIZES_CM = [5, 10, 15, 20, 30]
```

The configuration file is extensively commented to explain what each parameter controls and what values are reasonable for different types of analysis.

## Project Structure

Understanding the modular architecture helps you navigate the codebase and extend it for your specific research needs. Each module has a well-defined purpose and clear interfaces to other modules.

```
thz-research-suite/
├── main.py                      # Main execution script
├── config.py                    # All parameters and constants
├── antenna_models.py            # Antenna array calculations
├── channel_models.py            # Path loss and absorption
├── capacity_analysis.py         # Shannon capacity
├── beam_alignment.py            # Alignment strategies
├── nearfield_analysis.py        # Fraunhofer distance
├── monte_carlo_simulation.py    # Statistical analysis
├── visualization.py             # Figure generation
├── data_exporter.py            # CSV export utilities
├── results/                     # Output directory
│   ├── fig01_gain_frequency.png
│   ├── fig02_gain_size.png
│   └── ...                      # All 15 figures
└── docs/                        # Documentation
    ├── PARAMETERS.md            # Parameter guide
    ├── MODELS_AND_THEORY.md     # Technical documentation
    └── RESULTS_INTERPRETATION.md # Figure explanation
```

## Documentation

We have created comprehensive documentation that explains the research from multiple perspectives, suitable for readers with different backgrounds and interests.

### [Parameter Guide](docs/PARAMETERS.md)
This document provides a detailed explanation of every configuration parameter in the system. For each parameter, you will find its physical meaning, typical values, acceptable ranges, and how it affects the simulation results. This is your reference when customizing the analysis for your specific research questions.

### [Models and Theory](docs/MODELS_AND_THEORY.md)
This technical documentation explains the mathematical models underlying each component of the simulation. You will understand the antenna array gain formulas, the path loss equations including molecular absorption, the Shannon capacity theorem, the beam alignment algorithms, and the near-field phase analysis. Each section includes the relevant physics, mathematical derivations, and implementation details.

### [Results Interpretation](docs/RESULTS_INTERPRETATION.md)
This guide walks you through all fifteen figures, explaining what each one shows, how to interpret the curves and distributions, what the key insights are, and how the results relate to practical system design. This is essential reading for understanding the research outputs and using them in your own work.

### [Presentation](docs/presentation.pdf)
This document serves as a technical blueprint for 6G engineers, providing the analytical tools and empirical insights needed to move terahertz technology from the laboratory to commercial reality.

## Research Applications

### Academic Research
The suite provides a solid foundation for graduate-level research in wireless communications. You can use it to explore trade-offs in THz system design, validate theoretical predictions, generate figures for papers, and develop new optimization algorithms. The modular architecture makes it easy to add new features or modify existing models.

### Standards Contributions
The analysis aligns with IEEE 802.15.3-2023 specifications for THz wireless networks, making it relevant for standards development work. You can use the simulation results to propose new physical layer features, evaluate different design choices, or demonstrate the feasibility of new capabilities.

### System Design and Planning
For engineers designing real THz communication systems, the suite helps answer practical questions like what antenna array size you need for a given link distance and capacity, how environmental conditions will affect your link budget, and how long it will take to establish initial beam alignment. The Monte Carlo analysis provides the statistical confidence needed for system planning.

## Citation

If you use this research suite in your work, please cite it appropriately:

```
@software{thz_research_suite_2026,
  title = {Sub-THz/THz Wireless Communications Research Suite v3.0},
  author = {Nipun Agarwal},
  year = {2026},
  version = {1.0},
  url = {https://github.com/NipunAgarwal16/Sub-Terahertz-Wireless-Communications-Beyond-6G.git}
}
```

## Key References

The research builds upon foundational work in terahertz communications:

**IEEE Standard 802.15.3-2023:** Wireless Multimedia Networks, Chapter 14 on THz Physical Layer

**Jornet and Akyildiz (2011):** "Channel Modeling and Capacity Analysis for Electromagnetic Wireless Nanonetworks in the Terahertz Band," IEEE Transactions on Wireless Communications

**Petrov et al. (2024):** "Accurate Channel Model for Near Field Terahertz Communications Beyond 6G," IEEE SPAWC

**Singh et al. (2024):** "Wavefront Engineering: Realising Efficient Terahertz Band Communications in 6G and Beyond," IEEE Wireless Communications

## License

This project is released under the MIT License, allowing you to freely use, modify, and distribute the code for both academic and commercial purposes. See the LICENSE file for full details.

## Contributing

We welcome contributions from the research community. If you have improvements to suggest, bugs to report, or new features to add, please open an issue or submit a pull request. Areas where contributions would be particularly valuable include additional beam alignment strategies, more sophisticated channel models, integration with measurement data, and optimization algorithms for specific deployment scenarios.

## Support

For questions about using the research suite, interpreting results, or extending the codebase, please open an issue on GitHub. For academic collaborations or commercial applications, contact the research team directly.

## Acknowledgments

This research suite was developed to support next-generation wireless communication research and to facilitate the transition of terahertz technology from laboratory demonstrations to practical deployments. We gratefully acknowledge the pioneering work of researchers who have established the foundations of THz communications, particularly the teams at Northeastern University, Aalto University, and other institutions advancing this field.

---

**Version:** 1.0 | **Last Updated:** January 2026 | **Status:** Production-Ready | **Contributor & Maintainer:** Nipun Agarwal
