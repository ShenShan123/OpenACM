# **SRAM-OPT: Variation-Aware SRAM Transistor-Level Optimization Framework**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-Apache--2.0-green.svg)
![PDK](https://img.shields.io/badge/PDK-FreePDK45-orange.svg)

This repository contains the implementation of:

**SRAM-OPT: A Variation-Aware Multi-Objective Optimization Framework for 6T SRAM Transistor Sizing**

SRAM-OPT provides comprehensive SPICE-based Monte Carlo simulation and multi-objective optimization for 6T SRAM bit-cells and peripheral circuits. It serves as the **Level-II (Transistor-Level)** optimization engine in the OpenACMv2 framework.

---

## 📌 Overview

Static Random Access Memory (SRAM) is a critical component in modern SoCs, dominating on-chip area and significantly impacting power consumption. Process variations at advanced technology nodes pose severe challenges to SRAM reliability and yield.

SRAM-OPT addresses these challenges through:

- **Monte Carlo Simulation**: PVT-aware SPICE simulation with threshold voltage variations
- **Multi-Objective Optimization**: Simultaneous optimization of SNM, delay, power, and area
- **Comprehensive Metrics**: Hold/Read/Write SNM, read/write delay, static/dynamic power
- **Multiple Algorithms**: Eight optimization algorithms (including a random baseline)
- **Full Peripheral Support**: Word-line driver, precharge, sense amplifier, write driver, decoder, column mux

---

## ✨ Highlights

### ✔️ Complete 6T SRAM Simulation Framework

- Full SRAM array with configurable rows and columns
- All peripheral circuits (WL driver, precharge, SA, write driver, decoder, mux)
- RC parasitic modeling with π-network
- Process corner support (TT/FF/SS/FS/SF)
- Monte Carlo variation analysis with configurable Vth standard deviation

### ✔️ Multi-Objective Optimization

- **SNM Metrics**: Hold SNM, Read SNM, Write SNM
- **Timing Metrics**: Read delay, Write delay
- **Power Metrics**: Read power, Write power, Static power, Dynamic power
- **Area Metric**: Bit-cell area estimation based on design rules

### ✔️ Rich Algorithm Library

| Algorithm | Type | Description |
|-----------|------|-------------|
| NSGA-II | Multi-objective | Non-dominated Sorting Genetic Algorithm II |
| MOEA/D | Multi-objective | Multi-objective Evolutionary Algorithm based on Decomposition |
| MOBO | Multi-objective | Multi-objective Bayesian Optimization with EHVI |
| CBO | Constrained | Constrained Bayesian Optimization with GP surrogate |
| SMAC | Model-based | Sequential Model-based Algorithm Configuration |
| PSO | Swarm | Particle Swarm Optimization |
| SA | Metaheuristic | Simulated Annealing with exponential cooling |
| Random | Baseline | Random search for comparison |

### ✔️ Flexible Configuration System

- YAML-based parameter space definition
- Support for continuous and categorical parameters
- Configurable optimization objectives and constraints
- Easy integration with external evaluation functions

---

## 📁 Repository Structure

```
SRAM-OPT/
├── sram_compiler/
│   ├── subcircuits/                    # Circuit building blocks
│   │   ├── base_subcircuit.py          # Base class for all subcircuits
│   │   ├── sram_6t_core_for_yield.py   # 6T SRAM cell and array generator
│   │   ├── wordline_driver.py          # Word-line driver (NAND + INV)
│   │   ├── precharge_and_write_driver.py  # Precharge & write driver
│   │   ├── mux_and_sa.py               # Column mux & sense amplifier
│   │   ├── decoder.py                  # Address decoder
│   │   └── standard_cell.py            # Standard cells (NAND, INV)
│   ├── testbenches/
│   │   ├── base_testbench.py           # Base testbench with timing setup
│   │   ├── sram_6t_core_testbench.py   # Single-run testbench
│   │   └── sram_6t_core_MC_testbench.py  # Monte Carlo testbench
│   └── config_yaml/                    # Circuit configuration files
│       ├── global.yaml                 # Global simulation parameters
│       ├── sram_6t_cell.yaml           # 6T cell transistor sizing
│       ├── wordline_driver.yaml        # WL driver parameters
│       ├── precharge.yaml              # Precharge circuit parameters
│       ├── write_driver.yaml           # Write driver parameters
│       ├── sa.yaml                     # Sense amplifier parameters
│       ├── mux.yaml                    # Column mux parameters
│       └── decoder.yaml                # Decoder parameters
├── size_optimization/                  # Optimization algorithms
│   ├── exp_utils.py                    # Common utilities and base classes
│   ├── config_sram.yaml                # Optimization configuration
│   ├── demo_nsgaii.py                  # NSGA-II optimizer
│   ├── demo_moead.py                   # MOEA/D optimizer
│   ├── demo_mobo.py                    # Multi-objective Bayesian Optimization
│   ├── demo_cbo.py                     # Constrained Bayesian Optimization
│   ├── demo_smac.py                    # SMAC optimizer
│   ├── demo_pso.py                     # Particle Swarm Optimization
│   ├── demo_sa.py                      # Simulated Annealing
│   ├── demo_roseopt.py                 # RoSE-Opt integration
│   ├── demo_random.py                  # Random search baseline
│   ├── sram_lef_generator.py           # LEF file generator for P&R
│   └── NSGA-II/                        # NSGA-II core implementation
│       ├── problem.py                  # Problem definition
│       ├── individual.py               # Individual representation
│       ├── population.py               # Population management
│       ├── evolution.py                # Evolution main loop
│       └── nsga2_utils.py              # Non-dominated sort, crowding distance
├── tran_models/                        # FreePDK45 transistor models
│   ├── models_TT.spice                 # Typical-Typical corner
│   ├── models_FF.spice                 # Fast-Fast corner
│   ├── models_SS.spice                 # Slow-Slow corner
│   ├── models_FS.spice                 # Fast-Slow corner
│   └── models_SF.spice                 # Slow-Fast corner
├── sim/                                # Simulation output directory
├── environment.yml                     # Conda environment definition
├── config.py                           # Configuration loader
├── utils.py                            # Utility functions
├── main_sram.py                        # Main simulation entry
├── plot_data.py                        # Visualization utilities
├── experiment.py                       # Joint optimization entry
└── SRAM_OPT_README.md                  # This document
```

---

## ⚙️ Installation

SRAM-OPT is a subfolder inside OpenACM. Follow the OpenACM repository setup for cloning and Python environment, then enter this folder:

```bash
git clone https://github.com/ShenShan123/OpenACM.git
cd OpenACM
cd SRAM-OPT
```

### External Tools

- **ngspice** or **Xyce**: SPICE simulator backend
- **FreePDK45**: Transistor models (included in `tran_models/`)

```bash
# Ubuntu/Debian
sudo apt-get install ngspice

# macOS
brew install ngspice

# Verify
ngspice --version
```

---

## 🚀 Quick Start

### 1. Run Basic Monte Carlo Simulation

```bash
python main_sram.py
```

This performs Monte Carlo simulation and outputs:
- Hold SNM, Read SNM, Write SNM
- Read/Write delay
- Read/Write power (average, static, dynamic)

### 2. Run Joint Optimization

```bash
python experiment.py
```

You will be prompted to select:
- Circuit mode: real cell or equivalent cell
- Maximum iterations
- Optimization algorithm (SA/PSO/SMAC/CBO/RoSE_Opt/MOEAD/MOBO/NSGA-II)

### 3. Configure Simulation Parameters

Edit `sram_compiler/config_yaml/global.yaml`:

```yaml
vdd: 1.0                    # Supply voltage (V)
temperature: 45             # Temperature (°C)
num_rows: 32                # SRAM array rows
num_cols: 16                # SRAM array columns
monte_carlo_runs: 30        # Number of MC iterations
pdk_path_TT: "tran_models/models_TT.spice"
```

### 4. Configure Transistor Sizing

Edit `sram_compiler/config_yaml/sram_6t_cell.yaml`:

```yaml
SRAM_6T_CELL:
  parameters:
    pmos_width:
      type: "continuous scalar"
      names: "pu"
      upper: 9e-08
      lower: 9e-08
      value: 9e-08               # Pull-up: 90nm
    nmos_width:
      type: "continuous list"
      names: ['pd', 'pg']
      upper: [2.05e-07, 1.35e-07]
      lower: [2.05e-07, 1.35e-07]
      value: [2.05e-07, 1.35e-07]  # PD: 205nm, PG: 135nm
    length:
      value: 5e-08               # Channel length: 50nm
    nmos_model:
      type: "categorical list"
      names: ['pd', 'pg']
      choices: ["NMOS_VTL", "NMOS_VTG", "NMOS_VTH"]
      value: ["NMOS_VTH", "NMOS_VTH"]
```

### 5. Run Optimization Algorithms (Standalone Demos)

```bash
# Multi-objective: NSGA-II
python size_optimization/demo_nsgaii.py

# Multi-objective: MOEA/D
python size_optimization/demo_moead.py

# Single-objective: SMAC
python size_optimization/demo_smac.py

# Constrained: CBO
python size_optimization/demo_cbo.py
```

---

## 📊 Optimization Framework

### Design Parameter Space

The framework supports a mixed design space combining architecture and device parameters:

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| Rows | Discrete | 16–512 | SRAM rows (power-of-two set) |
| Cols | Discrete | 16–512 | SRAM columns (power-of-two set) |
| Num Arrays | Derived | total_bits / (rows × cols) | Ensures 262,144 total bits |
| W_PD | Continuous | 45nm - 135nm | Pull-down NMOS width |
| W_PU | Continuous | 45nm - 135nm | Pull-up PMOS width |
| W_PG | Continuous | 67.5nm - 202.5nm | Pass-gate NMOS width |
| L | Continuous | 30nm - 100nm | Channel length |
| NMOS_model | Categorical | VTL/VTG/VTH | NMOS threshold type |
| PMOS_model | Categorical | VTL/VTG/VTH | PMOS threshold type |

### Figure of Merit (FoM)

The default optimization objective combines multiple metrics:

```
FoM = log₁₀(min_SNM / (max_power × max_delay × √total_area))
```

Where:
- `min_SNM = min(Hold_SNM, Read_SNM, Write_SNM)`
- `max_power = max(P_read, P_write)`
- `max_delay = max(T_read, T_write)`

### Algorithm Configurations

All algorithms use the runtime budget specified by `experiment.py` (max iterations).

| Algorithm | Notes |
|-----------|-------|
| SA | Single-objective joint optimization |
| PSO | Particle swarm over joint space |
| SMAC | Model-based optimization |
| CBO | Constrained Bayesian optimization |
| RoSE-Opt | RL-assisted Bayesian optimization |
| MOEA/D | Multi-objective decomposition |
| MOBO | Multi-objective Bayesian optimization |
| NSGA-II | Non-dominated sorting GA |

---

## 🔧 Advanced Usage

### Process Corner Analysis

```python
from config import SRAM_CONFIG
from sram_compiler.testbenches.sram_6t_core_MC_testbench import Sram6TCoreMcTestbench

sram_config = SRAM_CONFIG()
sram_config.load_all_configs(
    global_file="sram_compiler/config_yaml/global.yaml",
    circuit_configs={
        "SRAM_6T_CELL": "sram_compiler/config_yaml/sram_6t_cell.yaml",
        # ... other configs
    }
)

# Run across all corners
for corner in ["TT", "FF", "SS", "FS", "SF"]:
    mc_testbench = Sram6TCoreMcTestbench(
        sram_config,
        coner=corner,
        use_mc=True,
        vth_std=0.05,
        sim_path=f"sim/{corner}"
    )
    result = mc_testbench.run_mc_simulation(
        operation="read_snm",
        target_row=31, target_col=15,
        mc_runs=30
    )
    print(f"{corner}: Read SNM = {result}")
```

### Custom Optimization Run

```python
from size_optimization.exp_utils import (
    ModifiedSRAMParameterSpace, evaluate_sram, seed_set
)

seed_set(42)

# Create parameter space
param_space = ModifiedSRAMParameterSpace("config_sram.yaml")

# Define custom parameters
params = {
    'pd_width': 0.09e-6,
    'pu_width': 0.072e-6,
    'pg_width': 0.162e-6,
    'length': 50e-9,
    'nmos_model': 'NMOS_VTG',
    'pmos_model': 'PMOS_VTH'
}

# Evaluate
objectives, constraints, result, success = evaluate_sram(params)
if success:
    print(f"FoM: {result['merit']:.4f}")
    print(f"SNM: H={result['hold_snm']:.3f}, R={result['read_snm']:.3f}, W={result['write_snm']:.3f}")
```

## 🔗 Integration with OpenACMv2

SRAM-OPT serves as the transistor-level optimization engine in the OpenACMv2 ACCO framework:

```
OpenACMv2 ACCO Framework
├── Level-I (Architecture-Level)
│   └── GNN-based multiplier and SRAM macro configuration
└── Level-II (Transistor-Level)
    ├── Compressor sizing (compressor_sizing/)
    └── SRAM bit-cell sizing (SRAM-OPT)  ← This module
```

### Integration Command

```bash
# In OpenACMv2
python DCIM_OPT/run_optimization.py \
    --stage width \
    --component sram \
    --algo MOEAD
```

### Output Files

SRAM-OPT generates optimized configurations that feed into the OpenROAD backend:
- `config_yaml/*.yaml`: Optimized transistor parameters
- `lef/*.lef`: LEF macro definition for place & route

---

## 📈 Benchmarking Results

### Optimization Algorithm Comparison (32KB SRAM, FreePDK45)

The table below shows example results from a past evaluation run and may not match your current environment.

| Measure | Baseline | MOEA/D | NSGA-II | SMAC | CBO | PSO |
|---------|----------|--------|---------|------|-----|-----|
| Array Size | 16×16 | 64×32 | 64×32 | 64×32 | 32×32 | 32×32 |
| W_PD (µm) | 0.205 | 0.072 | 0.075 | 0.108 | 0.045 | 0.045 |
| W_PU (µm) | 0.090 | 0.072 | 0.080 | 0.072 | 0.048 | 0.049 |
| W_PG (µm) | 0.135 | 0.162 | 0.158 | 0.108 | 0.107 | 0.156 |
| T_read (ns) | 2.564 | 2.274 | 2.271 | 2.394 | 2.448 | 2.430 |
| T_write (ns) | 0.750 | 0.638 | 0.637 | 0.626 | 0.721 | 0.679 |
| P_max (mW) | 3.331 | 1.923 | 1.889 | 1.787 | 1.658 | 1.847 |
| min SNM (V) | 0.174 | **0.290** | 0.276 | 0.270 | 0.315 | 0.365 |
| Area (mm²) | 0.4773 | **0.1253** | 0.1262 | 0.1211 | 0.2042 | 0.2270 |
| **FoM** | 7.4689 | **8.2721** | 8.2577 | 8.2591 | 8.2356 | 8.2316 |

**Key Improvements (MOEA/D vs Baseline):**
- SNM: +66.7% (0.174V → 0.290V)
- Area: -73.6%
- Read Delay: -11.3%
- Peak Power: -42.3%
- Overall FoM: +10.8%

---

## 📚 API Reference

### Core Classes

| Class | Description |
|-------|-------------|
| `SRAM_CONFIG` | Configuration loader from YAML files |
| `Sram6TCoreMcTestbench` | Monte Carlo simulation testbench |
| `ModifiedSRAMParameterSpace` | Optimization parameter space handler |
| `BaseOptimizer` | Abstract base class for all optimizers |

### Key Functions

| Function | Description |
|----------|-------------|
| `evaluate_sram(params)` | Evaluate SRAM with given parameters |
| `estimate_bitcell_area(...)` | Estimate bit-cell area from W/L |
| `run_mc_simulation(...)` | Run Monte Carlo simulation |
---

## 📜 License

This project is licensed under Apache-2.0. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

SRAM-OPT builds on:

- **OpenACM** - Approximate CiM compiler framework
- **OpenYield** - Variation-aware SRAM simulation
- **PySpice** - Python interface to SPICE simulators
- **FreePDK45** - Open-source 45nm PDK
- **SMAC3** - Sequential Model-based Algorithm Configuration
- **BoTorch** - Bayesian Optimization in PyTorch

---
