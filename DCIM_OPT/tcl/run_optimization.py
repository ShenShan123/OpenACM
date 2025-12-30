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
import common_metrics

# ==========================================
# Configuration & Defaults
# ==========================================

DEFAULT_CONFIG = {
    "8bit": {
        "dim": 9,
        "base_path": "8bit-multiplier",
        "paths": {
            "NSGA": "NSGA_GNN-8bit-revised/NSGA",
            "MOSMAC": "MOSMAC-8bit",
            "MOBO": "MOBO - 8bit-revised",
            "SMAC": "MOSMAC-8bit"
        },
        "min_max": {
            'MRED': (0.00086214, 0.15909895),
            'NMED': (0.00009676, 0.00313291),
            'Area': (435.97400000, 480.92800000),
            'Delay': (1.30000000, 1.34000000),
            'Power': (0.00014600, 0.00018400)
        }
    },
    "16bit": {
        "dim": 49,
        "base_path": "16bit-multiplier",
        "paths": {
            "NSGA": "NSGA_GNN-16bit-revised/NSGA",
            "MOSMAC": "MOSMAC-16bit",
            "MOBO": "MOBO - 16bit-revised",
            "SMAC": "MOSMAC-16bit"
        },
        "min_max": {
            'MRED': (0.00000533, 0.00375792),
            'NMED': (0.00000012, 0.00002442),
            'Delay': (1.70, 1.94),
            'Area': (1573.12400000, 1693.35600000),
            'Power': (0.00060700, 0.00088600)
        }
    }
}

# Transistor Sizing Info (Reference)
TRANSISTOR_INFO = {
    "Akbar1": {"gates": ["XNOR2_X1_NMOS1", "XNOR2_X1_NMOS2", "XNOR2_X1_PMOS1", "XNOR2_X1_PMOS2", "NAND2_X1_NMOS1", "NAND2_X1_PMOS1", "BUF_X1_NMOS1", "BUF_X1_NMOS2", "BUF_X1_PMOS1", "BUF_X1_PMOS2"], "range": (0.145, 2.7), "step": 0.045},
    "Akbar2": {"gates": ["XNOR2_X1_NMOS1", "XNOR2_X1_NMOS2", "XNOR2_X1_PMOS1", "XNOR2_X1_PMOS2", "NAND2_X1_NMOS1", "NAND2_X1_PMOS1", "AOI22_X1_NMOS1", "AOI22_X1_PMOS1", "INV_X1_NMOS1", "INV_X1_PMOS1"], "range": (0.145, 2.7), "step": 0.045},
    # ... (Other types can be added here)
}

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

def setup_environment(circuit_type, algo_type):
    """
    Setup sys.path and load necessary modules
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config = DEFAULT_CONFIG[circuit_type]
    rel_path = config["paths"][algo_type]
    full_path = os.path.join(root_dir, config["base_path"], rel_path)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Path not found: {full_path}")
        
    print(f"Loading modules from: {full_path}")
    sys.path.insert(0, full_path)
    
    return full_path

def run_optimization(args):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_dir_name = f"{args.circuit}_{args.algo}_{timestamp}"
    result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", result_dir_name)
    os.makedirs(result_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Starting Optimization: {args.circuit} - {args.algo}")
    print(f"Output Directory: {result_dir}")
    print(f"{'='*60}\n")

    # Save configuration
    with open(os.path.join(result_dir, "config.json"), "w") as f:
        json.dump(vars(args), f, indent=4)

    module_path = setup_environment(args.circuit, args.algo)
    
    try:
        # Import common modules
        import problem
        importlib.reload(problem)
        
        # Define Objectives (Wrapper to handle normalization if needed, or use default)
        # We rely on the Problem class defined in the subfolder
        
        def get_val(x):
            return x.item() if hasattr(x, 'item') else x
        
        # Instantiate Problem
        # Note: We assume the Problem class in subfolders accepts these arguments
        # If not, we might need to adjust based on specific implementation
        
        # Check Problem signature
        # Most implementations: Problem(num_of_variables, objectives, variables_range, same_range, expand, variables_type)
        
        # Load objectives from the local script if possible, or define generic ones
        # Since objectives depend on gnn_predictor which is local to the folder, we should import them from the local 'multiplier.py' or similar if possible
        # Or better, we define them here but using the imported 'gnn_predictor'
        
        from gnn_predictor import predict_metrics
        from my_io import state_to_graph
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Get min_max (User defined or Default)
        min_max = args.min_max if args.min_max else DEFAULT_CONFIG[args.circuit]["min_max"]
        
        # Update common_metrics global to ensure consistency if used elsewhere
        if args.circuit == '8bit':
            common_metrics.MIN_MAX_8BIT = min_max
        else:
            common_metrics.MIN_MAX_16BIT = min_max

        # Define Objectives (Normalized)
        # Note: We use common_metrics.denormalize with DEFAULT config to get raw values from GNN (assuming GNN is fixed),
        # and then normalize with USER config.
        # However, for simplicity and assuming user wants to override the "Operating Range", we use user's min_max for both.
        
        def f1_mred(state):
            """Objective 1: MRED (Normalized)"""
            T = state_to_graph(state, device)
            reward = predict_metrics(T)
            # GNN output is usually normalized to training data range.
            # We denormalize it to get raw value, then normalize it to current min_max.
            # If min_max matches training data, this is redundant but safe.
            mred_raw = common_metrics.denormalize(reward[0], 'MRED', min_max)
            return common_metrics.normalize(mred_raw, 'MRED', min_max)

        def f2_pdp(state):
            """Objective 2: PDP (Normalized)"""
            T = state_to_graph(state, device)
            reward = predict_metrics(T)
            
            delay_raw = common_metrics.denormalize(reward[2], 'Delay', min_max)
            power_raw = common_metrics.denormalize(reward[4], 'Power', min_max)
            
            return common_metrics.normalize_pdp(delay_raw, power_raw, min_max)
        
        # Variables Type
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

        # ==================== 算法执行 ====================
        if args.algo == "NSGA":
            from evolution import Evolution
            importlib.reload(sys.modules['evolution'])
            
            optimizer = Evolution(
                prob,
                num_of_generations=args.gen,
                num_of_individuals=args.pop_size,
                num_of_tour_particips=3,
                tournament_prob=0.25,
                crossover_param=args.crossover,
                mutation_param=args.mutation
            )
            print("Running NSGA-II...")
            population = optimizer.evolve()
            for ind in population:
                results.append({"state": ind.features, "objs": ind.objectives})
                
        elif args.algo == "MOSMAC":
            from mosmac_optimizer import MOSMAC
            importlib.reload(sys.modules['mosmac_optimizer'])
            
            optimizer = MOSMAC(
                problem=prob,
                h=args.pop_size, 
                max_gen=args.gen,
                T_size=20,
                name='multiplier'
            )
            print("Running MOSMAC...")
            optimizer.run()
            states, objs = optimizer.get_pareto_front()
            for s, o in zip(states, objs):
                results.append({"state": s, "objs": o})

        elif args.algo == "MOBO":
            from bayesian_optimizer import BayesianOptimizer
            importlib.reload(sys.modules['bayesian_optimizer'])
            
            optimizer = BayesianOptimizer(
                prob,
                n_initial=min(args.pop_size, 50),
                n_iterations=args.gen,
                n_candidates_per_iter=100,
                mc_samples=50
            )
            print("Running MOBO...")
            pareto_front = optimizer.optimize()
            for ind in pareto_front:
                results.append({"state": ind.features, "objs": ind.objectives})

        elif args.algo == "SMAC":
            try:
                from smac_multiplier import MultiplierSMACOptimizer
            except ImportError:
                # 尝试直接从文件加载
                spec = importlib.util.spec_from_file_location("MultiplierSMACOptimizer", os.path.join(module_path, "smac_multiplier.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                MultiplierSMACOptimizer = mod.MultiplierSMACOptimizer
            
            optimizer = MultiplierSMACOptimizer(prob, max_trials=args.gen)
            print("Running SMAC...")
            best_state, best_obj, history = optimizer.run(result_dir)
            for entry in history:
                results.append({"state": entry['state'], "objs": entry['objectives']})

        # ==========================================
        # Post-Processing & Saving
        # ==========================================
        
        print(f"Saving results to {result_dir}...")
        
        # Filter results based on constraints
        filtered_results = []
        
        pdp_min, pdp_max = common_metrics.get_pdp_range(min_max)
        
        for res in results:
            # Objectives are Normalized [0,1]
            mred_norm = res['objs'][0]
            pdp_norm = res['objs'][1]
            
            # Denormalize to get Raw values for saving/checking constraints
            mred_raw = common_metrics.denormalize(mred_norm, 'MRED', min_max)
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
            plt.xlabel("PDP (Approx)", fontsize=12)
            plt.ylabel("MRED (Normalized/Raw)", fontsize=12)
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

if __name__ == "__main__":
    print("==========================================")
    print("Select Configuration Mode:")
    print("1. Manual Configuration (Edit script parameters)")
    print("2. Interactive Input (Enter parameters in terminal)")
    print("==========================================")
    mode = input("Enter choice (1 or 2) [default: 1]: ").strip()

    class Config:
        def __init__(self):
            # Default values
            self.circuit = "8bit"
            self.algo = "NSGA"
            self.dim = None
            self.step = 1.0
            self.pop_size = 100
            self.gen = 50
            self.crossover = 20.0
            self.mutation = 20.0
            self.max_mred = None
            self.max_pdp = None
            self.min_max = None

    args = Config()

    if mode == "2":
        print("\n--- Interactive Configuration ---")
        print("(Press Enter to use default values)")
        
        # Circuit
        c = input(f"Circuit type (8bit/16bit) [default: {args.circuit}]: ").strip()
        if c: args.circuit = c
        
        # Algo
        a = input(f"Algorithm (NSGA/MOSMAC/MOBO/SMAC) [default: {args.algo}]: ").strip()
        if a: args.algo = a
        
        # Dim
        d = input(f"Dimension (int, optional) [default: Auto]: ").strip()
        if d: args.dim = int(d)
        
        # Step
        s = input(f"Step size [default: {args.step}]: ").strip()
        if s: args.step = float(s)
        
        # Pop size
        p = input(f"Population size [default: {args.pop_size}]: ").strip()
        if p: args.pop_size = int(p)
        
        # Gen
        g = input(f"Generations/Iterations [default: {args.gen}]: ").strip()
        if g: args.gen = int(g)
        
        # Crossover
        co = input(f"Crossover param [default: {args.crossover}]: ").strip()
        if co: args.crossover = float(co)
        
        # Mutation
        mu = input(f"Mutation param [default: {args.mutation}]: ").strip()
        if mu: args.mutation = float(mu)
        
        # Constraints
        mm = input(f"Max MRED (float, optional) [default: None]: ").strip()
        if mm: args.max_mred = float(mm)
        
        mp = input(f"Max PDP (float, optional) [default: None]: ").strip()
        if mp: args.max_pdp = float(mp)
        
        # Note: Interactive mode does not support detailed min_max editing to keep it simple.
        # Use Manual mode for that.

    else:
        print("\n--- Manual Configuration Mode ---")
        print("Using parameters defined in the script.")
        # ==========================================
        # MANUAL CONFIGURATION SECTION (EDIT HERE)
        # ==========================================
        args.circuit = "8bit"      # Options: "8bit", "16bit"
        args.algo = "SMAC"         # Options: "NSGA", "MOBO", "SMAC"
        
        args.dim = None            # None = auto-detect (9 for 8bit, 49 for 16bit)
        args.step = 1.0            # Step size
        
        args.pop_size = 100        # Population size
        args.gen = 10              # Generations / Iterations
        args.crossover = 20.0      # Crossover parameter
        args.mutation = 20.0       # Mutation parameter
        
        args.max_mred = None       # e.g., 0.005
        args.max_pdp = None        # e.g., 1500.0
        
        # Parameter Ranges (Min, Max) for Normalization
        # Modify these to change the optimization bounds/normalization
        if args.circuit == "8bit":
            args.min_max = {
                'MRED': (0.00086214, 0.15909895),
                'NMED': (0.00009676, 0.00313291),
                'Area': (435.97400000, 480.92800000),
                'Delay': (1.30000000, 1.34000000),
                'Power': (0.00014600, 0.00018400)
            }
        elif args.circuit == "16bit":
            args.min_max = {
                'MRED': (0.00000533, 0.00375792),
                'NMED': (0.00000012, 0.00002442),
                'Delay': (1.70, 1.94),
                'Area': (1573.12400000, 1693.35600000),
                'Power': (0.00060700, 0.00088600)
            }
        # ==========================================

    # Set default dim if not provided
    if args.dim is None:
        args.dim = DEFAULT_CONFIG[args.circuit]["dim"]
        
    run_optimization(args)
