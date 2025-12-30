"""
SRAM Circuit Optimization using Simulated Annealing Algorithm

This file implements a Simulated Annealing optimization algorithm for SRAM parameter optimization.
"""

import os
import time
import numpy as np
import torch
import random
import warnings
from pathlib import Path
import traceback

warnings.filterwarnings("ignore")

# Import path handling
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import utilities from exp_utils
from sram_sizing.exp_utils import seed_set, create_directories, evaluate_sram, ModifiedSRAMParameterSpace, OptimizationLogger, save_pareto_front, save_best_result, plot_merit_history, plot_pareto_frontier, update_pareto_front, save_optimization_history
from utils import estimate_bitcell_area


def format_initial_result(result):
    """
    Convert evaluate_sram result format to expected format
    """
    if result is None:
        return None

    formatted_result = {"hold_snm": {"success": True, "snm": result["hold_snm"]}, "read_snm": {"success": True, "snm": result["read_snm"]}, "write_snm": {"success": True, "snm": result["write_snm"]}, "read": {"success": True, "delay": result["read_delay"], "power": abs(result["read_power"])}, "write": {"success": True, "delay": result["write_delay"], "power": abs(result["write_power"])}}
    return formatted_result


# SA optimizer class
class SAOptimizer:
    def __init__(self, parameter_space, num_objectives=3, num_constraints=2, initial_result=None, initial_params=None, evaluate_backend=None):
        """
        Initialize SA optimizer
        """
        self.parameter_space = parameter_space
        self.bounds = parameter_space.bounds
        self.dim = self.bounds.shape[1]
        self.num_objectives = num_objectives
        self.num_constraints = num_constraints
        # Optional external evaluation function (e.g., Stage 2)
        self.evaluate_backend = evaluate_backend

        # Record all evaluation results
        self.all_x = []
        self.all_objectives = []
        self.all_constraints = []
        self.all_results = []
        self.all_success = []
        self.pareto_front = []

        # Initialize Merit tracking
        self.all_merit = []

        # Set initial feasible point Merit and results
        if initial_result:
            # Extract values from initial results: handle both formats
            if isinstance(initial_result.get("hold_snm"), dict):
                # New format: {'hold_snm': {'snm': value}}
                initial_min_snm = min(initial_result["hold_snm"]["snm"], initial_result["read_snm"]["snm"], initial_result["write_snm"]["snm"])
                initial_max_power = max(initial_result["read"]["power"], initial_result["write"]["power"])
            else:
                # Direct format: {'hold_snm': value}
                initial_min_snm = min(initial_result["hold_snm"], initial_result["read_snm"], initial_result["write_snm"])
                initial_max_power = max(abs(initial_result["read_power"]), abs(initial_result["write_power"]))

            # Calculate area using initial parameters
            if initial_params:
                initial_area = estimate_bitcell_area(w_access=initial_params["pg_width"], w_pd=initial_params["pd_width"], w_pu=initial_params["pu_width"], l_transistor=initial_params["length"])

                self.initial_merit = np.log10(initial_min_snm / (initial_max_power * np.sqrt(initial_area)))
                print(f"Initial Merit: {self.initial_merit:.6e}")

        # Initialize Merit tracking state
        self.best_merit = float("-inf")
        self.best_x = None
        self.best_result = None

        # Initialize history data
        self.iteration_history = []  # Record evaluation results for each iteration
        self.best_history = []  # Record best Merit for each iteration

    def evaluate(self, x):
        """
        Evaluate single parameter setting for SA optimization
        """
        # Ensure x is numpy array type
        x = np.array(x) if not isinstance(x, np.ndarray) else x

        # Constrain x to [0,1] range
        x = np.clip(x, 0, 1)

        # Convert to torch.Tensor (if needed)
        x_tensor = torch.tensor(x, dtype=torch.float32)

        # Convert parameters
        params = self.parameter_space.convert_params(x_tensor)

        # Evaluate SRAM performance
        eval_func = self.evaluate_backend if self.evaluate_backend is not None else evaluate_sram
        objectives, constraints, result, success = eval_func(params)

        # Calculate optimization objective: Merit = log10(min_snm / (max_power * (area**0.5)))
        if success and result:
            merit = result["merit"]

            # Return negative Merit, because SA is a minimization problem
            return -merit
        else:
            # If evaluation fails, return a large penalty value
            return 1e9

    def run_optimization(self, max_iter=10, T_max=1000, T_min=1e-7):
        """
        Run SA optimization - modified to count one simulation as one iteration
        """
        print(f"===== Starting SA optimization, maximum simulations: {max_iter} =====")

        # Parameter ranges
        lb = np.zeros(self.dim)
        ub = np.ones(self.dim)

        # Optimized temperature settings
        T = T_max  # Higher initial temperature
        alpha = 0.98  # Slower cooling rate

        # Find better initial point
        print("Searching for valid initial point...")
        best_init_x = None
        best_init_merit = float("-inf")
        best_init_success = False

        # Try to find a good starting point (try at most 10 initial points)
        for i in range(min(10, max_iter // 10)):
            init_x = np.random.uniform(lb, ub)
            x_tensor = torch.tensor(init_x, dtype=torch.float32)
            params = self.parameter_space.convert_params(x_tensor)

            print(f"Evaluating initial point {i + 1}/10:")
            self.parameter_space.print_params(params)

            objectives, constraints, result, success = evaluate_sram(params)

            # If it's a successful simulation, check if it's the best initial point
            if success and result:
                init_merit = result["merit"]
                if init_merit > best_init_merit:
                    best_init_x = init_x.copy()
                    best_init_merit = init_merit
                    best_init_success = True
                    print(f"Found better initial point, Merit = {init_merit:.6e}")

                    # If a valid point is found, record it first
                    self.observe(init_x, objectives, constraints, result, success, i, "SA_init")

        # Determine starting point
        if best_init_success:
            current_x = best_init_x.copy()
            print(f"Using found best initial point, Merit = {best_init_merit:.6e}")
        else:
            current_x = np.random.uniform(lb, ub)
            print("No valid initial point found, using random initial point")

        # Set current best solution
        best_x = current_x.copy()

        # Counter and state variables
        sim_counter = 10 if best_init_success else 0  # Consider simulations used for initial point search
        no_improve_count = 0  # Track consecutive non-improvement count

        # Main loop - each simulation counts as one iteration
        while sim_counter < max_iter:
            print(f"\n===== SA simulation {sim_counter + 1}/{max_iter} =====")
            print(f"Current temperature: {T:.6e}, No improvement count: {no_improve_count}")

            # Generate new solution randomly near current solution
            new_x = current_x + np.random.normal(0, max(0.1, T / T_max), size=self.dim)  # Higher temperature means larger perturbation
            new_x = np.clip(new_x, lb, ub)  # Ensure within parameter range

            # Evaluate new solution
            x_tensor = torch.tensor(new_x, dtype=torch.float32)
            params = self.parameter_space.convert_params(x_tensor)

            print("Evaluating new solution:")
            self.parameter_space.print_params(params)

            start_time = time.time()
            eval_func = self.evaluate_backend if self.evaluate_backend is not None else evaluate_sram
            objectives, constraints, result, success = eval_func(params)
            end_time = time.time()
            print(f"Evaluation time: {end_time - start_time:.2f} seconds")

            # Record results
            self.observe(new_x, objectives, constraints, result, success, sim_counter, "SA")

            # Metropolis criterion to decide whether to accept new solution
            accepted = False

            if success and result:
                new_merit = result["merit"]
                current_merit = self.best_merit if self.best_merit != float("-inf") else 0.0

                print(f"New solution Merit: {new_merit:.6e}")

                # Metropolis acceptance criterion
                if new_merit > current_merit:
                    # Accept better solution
                    accepted = True
                    current_x = new_x.copy()
                    no_improve_count = 0
                    print(f"Accept better solution: {new_merit:.6e}")
                else:
                    # Accept worse solution with probability
                    delta = current_merit - new_merit  # Energy difference (Merit difference)
                    if T > 0:
                        prob = np.exp(-delta / T)
                        if np.random.random() < prob:
                            accepted = True
                            current_x = new_x.copy()
                            print(f"Accept worse solution with probability {prob:.6f}: {new_merit:.6e}")

                if not accepted:
                    no_improve_count += 1
                    print(f"Reject solution: {new_merit:.6e}")

            else:
                print("Simulation failed!")
                no_improve_count += 1

            # Decrease temperature - cool down every 5 simulations, slower cooling
            if sim_counter % 5 == 0:
                T = max(T * alpha, T_min)

            # Early stopping condition
            if T < T_min:
                print(f"Temperature reached minimum {T_min}, stopping optimization")
                break

            # Restart mechanism: if no improvement for long time, reset state
            if no_improve_count >= 50:
                print("No improvement for long time, restarting search...")
                current_x = np.random.uniform(lb, ub)  # Re-initialize randomly
                T = T_max * 0.5  # Lower initial temperature, but keep it high to promote exploration
                no_improve_count = 0

            # Update counter
            sim_counter += 1

        print("\n===== SA optimization completed =====")

        # Return best result
        if self.best_merit != float("-inf"):
            best_params = self.parameter_space.convert_params(torch.tensor(self.best_x, dtype=torch.float32))
            return {"params": best_params, "merit": self.best_merit, "result": self.best_result, "iteration": max_iter}
        else:
            return {"params": None, "merit": None, "result": None, "iteration": -1}

    def observe(self, x, objectives, constraints, result, success, iteration, opt_type="SA"):
        """
        Record observation results and update model
        """
        # Record all evaluation results
        self.all_x.append(x)
        self.all_objectives.append(objectives)
        self.all_constraints.append(constraints)
        self.all_results.append(result)
        self.all_success.append(success)

        if success and result:
            merit = result["merit"]
            self.all_merit.append(merit)

            # Update best result
            if merit > self.best_merit:
                self.best_merit = merit
                self.best_x = x.copy()
                self.best_result = result

        # Record history
        self.best_history.append(self.best_merit if self.best_merit != float("-inf") else float("-inf"))


# Main function
def main(config_path="config_sram.yaml", problem=None, max_iter=None):
    """
    Main function to run SA optimization
    """
    print("===== SRAM optimization using SA =====")

    # Create directories
    create_directories()

    # Create parameter space
    if problem is not None and isinstance(problem, (tuple, list)) and len(problem) >= 2:
        parameter_space = problem[0]
        external_eval_fn = problem[1]
    else:
        parameter_space = ModifiedSRAMParameterSpace(config_path)
        external_eval_fn = None

    # Define initial parameters (same as in main.py)
    initial_params = {"nmos_model_name": "NMOS_VTG", "pmos_model_name": "PMOS_VTG", "pd_width": 0.205e-6, "pu_width": 0.09e-6, "pg_width": 0.135e-6, "length": 50e-9, "length_nm": 50}

    print("Running initial point simulation to get baseline performance...")

    # Evaluate initial parameters
    eval_func = external_eval_fn if external_eval_fn is not None else evaluate_sram
    try:
        objectives, constraints, initial_result, success = eval_func(initial_params)
    except TypeError as e:
        try:
            objectives, constraints, initial_result, success = eval_func(initial_params, timeout=None)
        except Exception:
            raise

    if not success:
        print("Warning: Initial point simulation failed, using default values as initial point")
        # Use default values as fallback
        initial_result = {"hold_snm": 0.30173446708423357, "read_snm": 0.12591724230394877, "write_snm": 0.3732610863628419, "read_delay": 2.0883543988703797e-10, "read_power": 4.024476625792127e-05, "write_delay": 6.086260190977158e-11, "write_power": 3.975272388991992e-05}
    else:
        print(f"Initial point simulation successful!")
        print(f"SNM: Hold={initial_result['hold_snm']:.4f}, Read={initial_result['read_snm']:.4f}, Write={initial_result['write_snm']:.4f}")
        print(f"Delay: Read={initial_result['read_delay']*1e12:.2f}ps, Write={initial_result['write_delay']*1e12:.2f}ps")
        print(f"Power: Read={initial_result['read_power']:.2e}W, Write={initial_result['write_power']:.2e}W")

    # Create SA optimizer, pass initial parameters and results
    optimizer = SAOptimizer(parameter_space, initial_result=initial_result, initial_params=initial_params, evaluate_backend=external_eval_fn)

    # Run SA optimization
    # Use provided max_iter if available
    _max_iter = max_iter if isinstance(max_iter, int) and max_iter > 0 else 5
    best_result = optimizer.run_optimization(max_iter=_max_iter, T_max=100, T_min=1e-3)

    # Output best results
    print("\n===== SA Optimization Best Results =====")
    if best_result["params"] is not None:
        print(f"Best Merit: {best_result['merit']:.6e}")
        print(f"Iteration count: {best_result['iteration']}")
        print("Best parameters:")
        parameter_space.print_params(best_result["params"])
        if best_result["result"]:
            print(f"Min SNM: {best_result['result']['min_snm']:.6f}")
            print(f"Max power: {best_result['result']['max_power']:.6e}")
            print(f"Area: {best_result['result']['area']*1e12:.2f} µm²")
    else:
        print("No valid solution found")

    return best_result


if __name__ == "__main__":
    # Set random seed for reproducibility
    SEED = 1
    seed_set(seed=SEED)
    main()
