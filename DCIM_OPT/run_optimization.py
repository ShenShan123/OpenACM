import os
import sys
import time
import argparse
import json
import importlib
import shutil
import matplotlib.pyplot as plt
import torch
from datetime import datetime

# ==========================================
# Configuration & Defaults
# ==========================================
# Delay in ns, Power in uW, Area in um^2
DEFAULT_CONFIG = {
    "8bit": {
        "dim": 9,
        "min_max": {
            'MRED': (0.00086214, 0.15909895),
            'NMED': (0.00009676, 0.00313291),
            'Area': (435.97400000, 480.92800000),
            'Delay': (1.30000000, 1.34000000),
            'Power': (146.00000000, 184.00000000)
        }
    },
    "16bit": {
        "dim": 49,
        "min_max": {
            'MRED': (0.00000533, 0.00375792),
            'NMED': (0.00000012, 0.00002442),
            'Delay': (1.70, 1.94),
            'Area': (1573.12400000, 1693.35600000),
            'Power': (607.00000000, 886.00000000)
        }
    }
}

# ==========================================
# Metrics Helpers (inline from common_metrics.py)
# ==========================================

def safe_get(value):
    """Safely convert tensor/numpy/float to python float."""
    if hasattr(value, 'item'):
        return float(value.item())
    try:
        return float(value)
    except Exception:
        return value


def normalize(value, key, min_max_dict):
    min_val, max_val = min_max_dict[key]
    if max_val == min_val:
        return 0.0
    val = safe_get(value)
    return (val - min_val) / (max_val - min_val)


def denormalize(value, key, min_max_dict):
    min_val, max_val = min_max_dict[key]
    val = safe_get(value)
    return val * (max_val - min_val) + min_val


def get_pdp_range(min_max_dict):
    """Calculate PDP min/max based on Delay and Power ranges (PDP in fJ)."""
    d_min, d_max = min_max_dict['Delay']
    p_min, p_max = min_max_dict['Power']
    # PDP = Delay(ns) * Power(uW) => fJ
    pdp_min = d_min * p_min
    pdp_max = d_max * p_max
    return pdp_min, pdp_max


def normalize_pdp(delay_raw, power_raw, min_max_dict):
    # PDP = Delay(ns) * Power(uW) => fJ
    pdp_raw = safe_get(delay_raw) * safe_get(power_raw)
    pdp_min, pdp_max = get_pdp_range(min_max_dict)
    return (pdp_raw - pdp_min) / (pdp_max - pdp_min)

# Transistor sizing info (from compressor_sizing/readme.md)
TRANSISTOR_INFO = {
    "AKbar1": {
        "gates": [
            "XNOR2_X1_NMOS1", "XNOR2_X1_NMOS2", "XNOR2_X1_PMOS1", "XNOR2_X1_PMOS2",
            "NAND2_X1_NMOS1", "NAND2_X1_PMOS1",
            "BUF_X1_NMOS1", "BUF_X1_NMOS2", "BUF_X1_PMOS1", "BUF_X1_PMOS2",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
    "AKbar2": {
        "gates": [
            "XNOR2_X1_NMOS1", "XNOR2_X1_NMOS2", "XNOR2_X1_PMOS1", "XNOR2_X1_PMOS2",
            "NAND2_X1_NMOS1", "NAND2_X1_PMOS1",
            "AOI22_X1_NMOS1", "AOI22_X1_PMOS1",
            "INV_X1_NMOS1", "INV_X1_PMOS1",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
    "antonio": {
        "gates": [
            "OR2_X1_NMOS1", "OR2_X1_NMOS2", "OR2_X1_PMOS1", "OR2_X1_PMOS2",
            "AOI22_X1_NMOS1", "AOI22_X1_PMOS1",
            "INV_X1_NMOS1", "INV_X1_PMOS1",
            "NAND2_X1_NMOS1", "NAND2_X1_PMOS1",
            "XNOR2_X1_NMOS1", "XNOR2_X1_NMOS2", "XNOR2_X1_PMOS1", "XNOR2_X1_PMOS2",
            "OAI21_X1_NMOS1", "OAI21_X1_PMOS1",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
    "AP1": {
        "gates": [
            "OAI22_X1_NMOS1", "OAI22_X1_PMOS1",
            "NAND2_X1_NMOS1", "NAND2_X1_PMOS1",
            "NAND3_X1_NMOS1", "NAND3_X1_PMOS1",
            "XOR2_X1_NMOS1", "XOR2_X1_NMOS2", "XOR2_X1_PMOS1", "XOR2_X1_PMOS2",
            "XNOR2_X1_NMOS1", "XNOR2_X1_NMOS2", "XNOR2_X1_PMOS1", "XNOR2_X1_PMOS2",
            "OAI21_X1_NMOS1", "OAI21_X1_PMOS1",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
    "ha": {
        "gates": [
            "NOR2_X1_NMOS1", "NOR2_X1_PMOS1",
            "NAND2_X1_NMOS1", "NAND2_X1_PMOS1",
            "XOR2_X1_NMOS1", "XOR2_X1_NMOS2", "XOR2_X1_PMOS1", "XOR2_X1_PMOS2",
            "XNOR2_X1_NMOS1", "XNOR2_X1_NMOS2", "XNOR2_X1_PMOS1", "XNOR2_X1_PMOS2",
            "OAI21_X1_NMOS1", "OAI21_X1_PMOS1",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
    "kong2": {
        "gates": [
            "OAI22_X1_NMOS1", "OAI22_X1_PMOS1",
            "INV_X1_NMOS1", "INV_X1_PMOS1",
            "AOI22_X1_NMOS1", "AOI22_X1_PMOS1",
            "NAND2_X1_NMOS1", "NAND2_X1_PMOS1",
            "XOR2_X1_NMOS1", "XOR2_X1_NMOS2", "XOR2_X1_PMOS1", "XOR2_X1_PMOS2",
            "NOR3_X1_NMOS1", "NOR3_X1_PMOS1",
            "AOI21_X1_NMOS1", "AOI21_X1_PMOS1",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
    "momeni": {
        "gates": [
            "OAI22_X1_NMOS1", "OAI22_X1_PMOS1",
            "INV_X1_NMOS1", "INV_X1_PMOS1",
            "AND2_X1_NMOS1", "AND2_X1_NMOS2", "AND2_X1_PMOS1", "AND2_X1_PMOS2",
            "OR3_X1_NMOS1", "OR3_X1_NMOS2", "OR3_X1_PMOS1", "OR3_X1_PMOS2",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
    "sabetz": {
        "gates": [
            "NAND2_X1_NMOS1", "NAND2_X1_PMOS1",
            "OAI21_X1_NMOS1", "OAI21_X1_PMOS1",
        ],
        "range": (0.145, 2.7),
        "step": 0.045,
    },
}

# Compressor sizing configuration (from compressor_sizing/readme.md)
COMPRESSOR_DIMENSIONS = {
    "AKbar1": 10,
    "AKbar2": 10,
    "antonio": 16,
    "AP1": 16,
    "ha": 14,
    "kong2": 16,
    "momeni": 12,
    "sabetz": 4,
}

WIDTH_RANGE = (0.145, 2.7)
WIDTH_STEP = 0.045

# Compressor PPA ranges (Delay/Power/Area) for width-stage normalization
COMPRESSOR_PPA_RANGE = {
    # Delay in ns, Power in uW, Area in um^2
    "AKbar1": {"Delay": (0.38400, 1.70357), "Power": (0.494, 1.595), "Area": (1.421, 26.46)},
    "AKbar2": {"Delay": (0.93865, 1.65838), "Power": (0.5865, 1.411), "Area": (2.6827, 24.1447)},
    "antonio": {"Delay": (0.99986, 1.84911), "Power": (0.7687, 2.1647), "Area": (2.436, 45.36)},
    "AP1": {"Delay": (0.27159, 30.49830), "Power": (1.1426, 4.3819), "Area": (2.9435, 54.81)},
    "ha": {"Delay": (0.12069, 1.44647), "Power": (0.6488, 1.807), "Area": (1.9285, 35.91)},
    "kong2": {"Delay": (0.40548, 1.76231), "Power": (0.7025, 2.4466), "Area": (2.233, 41.58)},
    "momeni": {"Delay": (0.26048, 2.18843), "Power": (0.3469, 2.078), "Area": (1.5225, 28.35)},
    "sabetz": {"Delay": (0.28882, 1.70986), "Power": (0.1998, 0.5592), "Area": (0.7105, 13.23)},
}


def build_width_values(min_width, max_width, step):
    values = []
    v = min_width
    while v <= max_width + 1e-12:
        values.append(round(v, 6))
        v += step
    if values and abs(values[-1] - max_width) > 1e-6:
        values.append(round(max_width, 6))
    return values


def normalize_value(value, min_val, max_val):
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

def clean_sys_modules(path_to_remove):
    """
    Remove modules loaded from a specific path to allow reloading
    """
    modules_to_remove = []
    for name, module in sys.modules.items():
        if hasattr(module, '__file__') and module.__file__ and path_to_remove in os.path.abspath(module.__file__):
            modules_to_remove.append(name)
    
    for name in modules_to_remove:
        del sys.modules[name]
    
    if path_to_remove in sys.path:
        sys.path.remove(path_to_remove)

def setup_environment(algo_type):
    """
    Setup sys.path and load algorithm modules
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(root_dir, "algorithms", algo_type)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Path not found: {full_path}")
        
    print(f"Loading modules from: {full_path}")
    sys.path.insert(0, full_path)
    
    return full_path

def run_optimization(args):
    if hasattr(args, "stage") and args.stage:
        args.stage = args.stage.lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if args.stage == "width":
        result_dir_name = f"width_{args.compressor}_{args.algo}_{timestamp}"
    else:
        result_dir_name = f"{args.circuit}_{args.algo}_{timestamp}"
    result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", result_dir_name)
    os.makedirs(result_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    if args.stage == "width":
        print(f"Starting Optimization: width - {args.compressor} - {args.algo}")
    else:
        print(f"Starting Optimization: config - {args.circuit} - {args.algo}")
    print(f"Output Directory: {result_dir}")
    print(f"{'='*60}\n")

    # Save configuration
    with open(os.path.join(result_dir, "config.json"), "w") as f:
        json.dump(vars(args), f, indent=4)

    module_path = setup_environment(args.algo)
    extra_paths = []
    compressor_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compressor_sizing")
    gnn_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "multiplier_gnn")
    if args.stage == "width":
        if compressor_root not in sys.path:
            sys.path.insert(0, compressor_root)
            extra_paths.append(compressor_root)
    else:
        gnn_dir = "8-bitGNN" if args.circuit == "8bit" else "16-bitGNN"
        gnn_path = os.path.join(gnn_root, gnn_dir)
        if not os.path.exists(gnn_path):
            raise FileNotFoundError(f"GNN path not found: {gnn_path}")
        if gnn_path not in sys.path:
            sys.path.insert(0, gnn_path)
            extra_paths.append(gnn_path)
    
    try:
        # Import common modules
        import problem
        importlib.reload(problem)
        
        eval_cache = None
        width_values = None
        compressor_key = None
        comp_ranges = None
        pdp_min = None
        pdp_max = None

        if args.stage == "width":
            # Compressor transistor width optimization
            comp_map = {k.lower(): k for k in COMPRESSOR_DIMENSIONS.keys()}
            compressor_key = comp_map.get(args.compressor.lower(), args.compressor)
            if compressor_key not in COMPRESSOR_DIMENSIONS:
                raise ValueError(f"Unknown compressor type: {args.compressor}")

            if args.dim is None:
                args.dim = COMPRESSOR_DIMENSIONS[compressor_key]

            if compressor_key not in COMPRESSOR_PPA_RANGE:
                raise ValueError(f"PPA range not found for compressor: {compressor_key}")
            comp_ranges = COMPRESSOR_PPA_RANGE[compressor_key]

            delay_min, delay_max = comp_ranges['Delay']
            power_min, power_max = comp_ranges['Power']
            area_min, area_max = comp_ranges['Area']
            pdp_min = delay_min * power_min
            pdp_max = delay_max * power_max

            width_values = build_width_values(WIDTH_RANGE[0], WIDTH_RANGE[1], WIDTH_STEP)
            index_min = 0
            index_max = len(width_values) - 1

            from run_ppa import run_ppa_vector

            eval_cache = {}

            def _evaluate_state(state):
                key = tuple(state)
                if key in eval_cache:
                    return eval_cache[key]

                widths = [width_values[int(x)] for x in state]
                try:
                    ppa = run_ppa_vector(os.path.join(compressor_root, compressor_key), widths, verbose=False)
                except Exception:
                    ppa = None
                
                if ppa is None:
                    result = {
                        "area_norm": 1e9,
                        "pdp_norm": 1e9,
                        "raw": None,
                        "widths": widths,
                    }
                    eval_cache[key] = result
                    return result

                delay_raw, power_raw, area_raw = ppa
                # Convert delay from ps to ns for unified units
                delay_raw = delay_raw / 1000.0
                pdp_raw = delay_raw * power_raw
                area_norm = normalize_value(area_raw, area_min, area_max)
                pdp_norm = normalize_value(pdp_raw, pdp_min, pdp_max)

                result = {
                    "area_norm": area_norm,
                    "pdp_norm": pdp_norm,
                    "raw": {
                        "delay": delay_raw,
                        "power": power_raw,
                        "area": area_raw,
                        "pdp": pdp_raw,
                    },
                    "widths": widths,
                }
                eval_cache[key] = result
                return result

            def f1_area(state):
                """Objective 1: Area (Normalized)"""
                return _evaluate_state(state)["area_norm"]

            def f2_pdp(state):
                """Objective 2: PDP (Normalized)"""
                return _evaluate_state(state)["pdp_norm"]

            variables_type = ['int'] * args.dim
            prob = problem.Problem(
                num_of_variables=args.dim,
                objectives=[f1_area, f2_pdp],
                variables_range=[(index_min, index_max)],
                same_range=True,
                expand=False,
                variables_type=variables_type
            )

        else:
            # Compressor configuration optimization (GNN-based)
            from gnn_predictor import predict_metrics
            from my_io import state_to_graph

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # Get min_max (Default config)
            min_max = DEFAULT_CONFIG[args.circuit]["min_max"]

            # Define Objectives (Normalized)
            # Note: We use denormalize with DEFAULT config to get raw values from GNN (assuming GNN is fixed),
            # and then normalize with USER config.
            # Use default min_max for both denormalize/normalize.

            def f1_mred(state):
                """Objective 1: MRED (Normalized)"""
                T = state_to_graph(state, device)
                reward = predict_metrics(T)
                mred_raw = denormalize(reward[0], 'MRED', min_max)
                return normalize(mred_raw, 'MRED', min_max)

            def f2_pdp(state):
                """Objective 2: PDP (Normalized)"""
                T = state_to_graph(state, device)
                reward = predict_metrics(T)

                delay_raw = denormalize(reward[2], 'Delay', min_max)
                power_raw = denormalize(reward[4], 'Power', min_max)

                return normalize_pdp(delay_raw, power_raw, min_max)

            variables_type = ['int'] * args.dim
            prob = problem.Problem(
                num_of_variables=args.dim,
                objectives=[f1_mred, f2_pdp],
                variables_range=[(0, 7)],
                same_range=True,
                expand=False,
                variables_type=variables_type
            )
        
        results = []

        # ==================== Algorithm Execution ====================
        if args.algo == "NSGA":
            from evolution import Evolution
            importlib.reload(sys.modules['evolution'])
            
            nsga_generations = args.nsga_generations
            nsga_individuals = args.nsga_individuals
            nsga_tour = args.nsga_tour
            nsga_tournament_prob = args.nsga_tournament_prob
            nsga_crossover = args.nsga_crossover
            nsga_mutation = args.nsga_mutation

            optimizer = Evolution(
                prob,
                num_of_generations=nsga_generations,
                num_of_individuals=nsga_individuals,
                num_of_tour_particips=nsga_tour,
                tournament_prob=nsga_tournament_prob,
                crossover_param=nsga_crossover,
                mutation_param=nsga_mutation
            )
            print("Running NSGA-II...")
            population = optimizer.evolve()
            for ind in population:
                results.append({"state": ind.features, "objs": ind.objectives})
                
        elif args.algo == "MOEAD":
            from moead_optimizer import MOEAD
            importlib.reload(sys.modules['moead_optimizer'])
            moead_h = args.moead_h
            moead_generations = args.moead_generations
            moead_t_size = args.moead_t_size
            moead_name = args.moead_name

            optimizer = MOEAD(
                problem=prob,
                h=moead_h,
                max_gen=moead_generations,
                T_size=moead_t_size,
                name=moead_name
            )
            print("Running MOEAD...")
            optimizer.run()
            states, objs = optimizer.get_pareto_front()
            for s, o in zip(states, objs):
                results.append({"state": s, "objs": o})

        elif args.algo == "MOBO":
            from bayesian_optimizer import BayesianOptimizer
            importlib.reload(sys.modules['bayesian_optimizer'])
            n_initial = args.mobo_initial
            n_iterations = args.mobo_iterations
            n_candidates_per_iter = args.mobo_candidates
            mc_samples = args.mobo_mc_samples

            optimizer = BayesianOptimizer(
                prob,
                n_initial=n_initial,
                n_iterations=n_iterations,
                n_candidates_per_iter=n_candidates_per_iter,
                mc_samples=mc_samples,
                ref_point=args.mobo_ref_point
            )
            print("Running MOBO...")
            pareto_front = optimizer.optimize()
            for ind in pareto_front:
                results.append({"state": ind.features, "objs": ind.objectives})

        elif args.algo == "SMAC":
            from smac_multiplier import MultiplierSMACOptimizer
            smac_trials = args.smac_trials
            smac_seed = args.smac_seed
            optimizer = MultiplierSMACOptimizer(prob, max_trials=smac_trials, seed=smac_seed)
            print("Running SMAC...")
            best_state, best_obj, history = optimizer.run(result_dir)
            for entry in history:
                results.append({"state": entry["state"], "objs": entry["objectives"]})

        # ==========================================
        # Post-Processing & Saving
        # ==========================================
        
        print(f"Saving results to {result_dir}...")
        
        # Filter results based on constraints
        filtered_results = []

        if args.stage == "width":
            for res in results:
                state = res['state']
                cache = eval_cache.get(tuple(state)) if eval_cache is not None else None
                if cache is None:
                    cache = _evaluate_state(state)

                raw = cache.get("raw") if cache else None
                if raw is None:
                    continue

                area_raw = raw["area"]
                pdp_raw = raw["pdp"]

                # Apply constraints (on Raw values)
                if args.max_mred is not None and area_raw > args.max_mred:
                    continue
                if args.max_pdp is not None and pdp_raw > args.max_pdp:
                    continue

                filtered_results.append({
                    "state": cache["widths"],
                    "objs": [area_raw, pdp_raw],
                    "raw": raw,
                })

            # Save to file
            output_file = os.path.join(result_dir, "solutions.txt")
            with open(output_file, "w") as f:
                f.write("widths\tArea\tPDP\tDelay\tPower\n")
                for res in filtered_results:
                    state_str = ','.join([f"{x:.6f}" for x in res['state']])
                    f.write(
                        f"{state_str}\t{res['objs'][0]:.6f}\t{res['objs'][1]:.6f}\t"
                        f"{res['raw']['delay']:.6f}\t{res['raw']['power']:.6f}\n"
                    )

            # Plot
            if filtered_results:
                areas = [r['objs'][0] for r in filtered_results]
                pdps = [r['objs'][1] for r in filtered_results]

                plt.figure(figsize=(10, 8))
                plt.scatter(pdps, areas, alpha=0.6, edgecolor='k', s=50)
                plt.xlabel("PDP (fJ)", fontsize=12)
                plt.ylabel("Area (um^2)", fontsize=12)
                plt.title(f"Pareto Front - width {compressor_key} {args.algo}", fontsize=14)
                plt.grid(True, alpha=0.3)
                plt.savefig(os.path.join(result_dir, "pareto_front.png"), dpi=300)
                plt.close()

        else:
            pdp_min, pdp_max = get_pdp_range(min_max)

            for res in results:
                # Objectives are Normalized [0,1]
                mred_norm = res['objs'][0]
                pdp_norm = res['objs'][1]

                # Denormalize to get Raw values for saving/checking constraints
                mred_raw = denormalize(mred_norm, 'MRED', min_max)
                pdp_raw = pdp_norm * (pdp_max - pdp_min) + pdp_min

                # Apply constraints (on Raw values)
                if args.max_mred is not None and mred_raw > args.max_mred:
                    continue
                if args.max_pdp is not None and pdp_raw > args.max_pdp:
                    continue

                # Store raw values for output
                filtered_results.append({
                    "state": res['state'],
                    "objs": [mred_raw, pdp_raw]
                })

            # Save to file
            output_file = os.path.join(result_dir, "solutions.txt")
            with open(output_file, "w") as f:
                f.write("state\tMRED\tPDP\n")
                for res in filtered_results:
                    state_str = ','.join(map(str, res['state']))
                    f.write(f"{state_str}\t{res['objs'][0]:.6f}\t{res['objs'][1]:.6f}\n")

            # Plot
            if filtered_results:
                mreds = [r['objs'][0] for r in filtered_results]
                pdps = [r['objs'][1] for r in filtered_results]

                plt.figure(figsize=(10, 8))
                plt.scatter(pdps, mreds, alpha=0.6, edgecolor='k', s=50)
                plt.xlabel("PDP (fJ)", fontsize=12)
                plt.ylabel("MRED", fontsize=12)
                plt.title(f"Pareto Front - {args.circuit} {args.algo}", fontsize=14)
                plt.grid(True, alpha=0.3)
                plt.savefig(os.path.join(result_dir, "pareto_front.png"), dpi=300)
                plt.close()
            
        print(f"Done. Found {len(filtered_results)} solutions satisfying constraints.")

    except Exception as e:
        print(f"Error during optimization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup sys.path
        clean_sys_modules(module_path)
        for p in extra_paths:
            clean_sys_modules(p)
        # Remove empty ppa_results directory if present (width stage)
        if hasattr(args, "stage") and args.stage == "width":
            ppa_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ppa_results")
            try:
                if os.path.isdir(ppa_dir) and not os.listdir(ppa_dir):
                    os.rmdir(ppa_dir)
            except Exception:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimization runner (config/width stages).")
    parser.add_argument("--stage", choices=["config", "width"], default="config",
                        help="Optimization stage: config or width")
    parser.add_argument("--circuit", choices=["8bit", "16bit"], default="8bit",
                        help="Circuit type for config stage")
    parser.add_argument("--compressor", default="sabetz",
                        help="Compressor type for width stage")
    parser.add_argument("--algo", choices=["NSGA", "MOEAD", "MOBO", "SMAC"], default="NSGA",
                        help="Optimization algorithm")
    parser.add_argument("--dim", type=int, default=None, help="Dimension (optional)")
    parser.add_argument("--max_mred", type=float, default=None,
                        help="Max MRED (config) or Max Area (width)")
    parser.add_argument("--max_pdp", type=float, default=None,
                        help="Max PDP (config/width)")
    # NSGA-specific overrides (optional)
    parser.add_argument("--nsga_generations", type=int, default=1200,
                        help="NSGA: generations (num_of_generations)")
    parser.add_argument("--nsga_individuals", type=int, default=800,
                        help="NSGA: population size (num_of_individuals)")
    parser.add_argument("--nsga_tour", type=int, default=3,
                        help="NSGA: tournament participants (num_of_tour_particips)")
    parser.add_argument("--nsga_tournament_prob", type=float, default=0.25,
                        help="NSGA: tournament probability")
    parser.add_argument("--nsga_crossover", type=float, default=12.0,
                        help="NSGA: crossover parameter")
    parser.add_argument("--nsga_mutation", type=float, default=45.0,
                        help="NSGA: mutation parameter")
    # MOEAD-specific overrides (optional)
    parser.add_argument("--moead_h", type=int, default=799,
                        help="MOEAD: weight divisions (h)")
    parser.add_argument("--moead_generations", type=int, default=1200,
                        help="MOEAD: generations (max_gen)")
    parser.add_argument("--moead_t_size", type=int, default=20,
                        help="MOEAD: neighborhood size (T_size)")
    parser.add_argument("--moead_name", type=str, default="multiplier",
                        help="MOEAD: problem name (weights file prefix)")
    # MOBO-specific overrides (optional)
    parser.add_argument("--mobo_initial", type=int, default=200,
                        help="MOBO: initial samples (n_initial)")
    parser.add_argument("--mobo_iterations", type=int, default=1000,
                        help="MOBO: Bayesian iterations (n_iterations)")
    parser.add_argument("--mobo_candidates", type=int, default=2000,
                        help="MOBO: candidates per iteration (n_candidates_per_iter)")
    parser.add_argument("--mobo_mc_samples", type=int, default=100,
                        help="MOBO: Monte Carlo samples (mc_samples)")
    parser.add_argument("--mobo_ref_point", type=float, nargs=2, default=None,
                        help="MOBO: reference point (2 floats, e.g. --mobo_ref_point 0.1 0.2)")
    # SMAC-specific overrides (optional)
    parser.add_argument("--smac_trials", type=int, default=400,
                        help="SMAC: number of trials (max_trials)")
    parser.add_argument("--smac_seed", type=int, default=42,
                        help="SMAC: random seed")

    args = parser.parse_args()


    # Set default dim if not provided
    if args.dim is None:
        if args.stage == "width":
            comp_map = {k.lower(): k for k in COMPRESSOR_DIMENSIONS.keys()}
            compressor_key = comp_map.get(args.compressor.lower(), args.compressor)
            if compressor_key not in COMPRESSOR_DIMENSIONS:
                raise ValueError(f"Unknown compressor type: {args.compressor}")
            args.dim = COMPRESSOR_DIMENSIONS[compressor_key]
        else:
            args.dim = DEFAULT_CONFIG[args.circuit]["dim"]
        
    run_optimization(args)
