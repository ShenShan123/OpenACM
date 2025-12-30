"""
SRAM Circuit Optimization using Constrained Bayesian Optimization

This file implements a three-objective constrained Bayesian optimization algorithm 
for SRAM parameter optimization.
"""

import os
import time
import numpy as np
import pandas as pd
import torch
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_model
from botorch.acquisition import ConstrainedExpectedImprovement
from botorch.acquisition.multi_objective.monte_carlo import qExpectedHypervolumeImprovement
from botorch.optim import optimize_acqf
from botorch.utils.multi_objective.box_decompositions.dominated import DominatedPartitioning
from gpytorch.mlls import ExactMarginalLogLikelihood
import matplotlib.pyplot as plt
from matplotlib import ticker
import random
import warnings
import csv

# Import test_sram_array function
import sys
from pathlib import Path

# Get current file directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add project root directory to Python path
project_root = os.path.dirname(current_dir)  # Assume exp_code is directly under project root
sys.path.append(project_root)

# Import utilities from exp_utils
from sram_sizing.exp_utils import (
    seed_set, create_directories, evaluate_sram, ModifiedSRAMParameterSpace,
    OptimizationLogger, save_pareto_front, save_best_result, plot_merit_history,
    plot_pareto_frontier, update_pareto_front, save_optimization_history
)
from utils import estimate_bitcell_area

warnings.filterwarnings('ignore')

# Set environment variables
os.environ['PATH'] = os.path.join(os.path.dirname(sys.executable), 'Library', 'bin') + os.pathsep + os.environ['PATH']


# Define parameter space
class SRAMParameterSpace:
    def __init__(self, config_path="config_sram.yaml"):
        """
        Initialize SRAM parameter space
        """
        try:
            self._modified_space = ModifiedSRAMParameterSpace(config_path)
            self.bounds = self._modified_space.bounds
            self.base_pd_width = self._modified_space.base_pd_width
            self.base_pu_width = self._modified_space.base_pu_width
            self.base_pg_width = self._modified_space.base_pg_width
            self.base_length_nm = self._modified_space.base_length_nm
        except:
            print("Warning: Config loading failed, using default parameters")
            self.base_pd_width = 0.205e-6
            self.base_pu_width = 0.09e-6
            self.base_pg_width = 0.135e-6
            self.base_length_nm = 50

            self.nmos_models = ['NMOS_VTL', 'NMOS_VTG', 'NMOS_VTH']
            self.pmos_models = ['PMOS_VTL', 'PMOS_VTG', 'PMOS_VTH']

            # Width ranges - range coefficients can be modified here
            self.pd_width_coef_min = 0.5
            self.pd_width_coef_max = 1.5
            self.pd_width_min = self.base_pd_width * self.pd_width_coef_min
            self.pd_width_max = self.base_pd_width * self.pd_width_coef_max

            self.pu_width_coef_min = 0.5
            self.pu_width_coef_max = 1.5
            self.pu_width_min = self.base_pu_width * self.pu_width_coef_min
            self.pu_width_max = self.base_pu_width * self.pu_width_coef_max

            self.pg_width_coef_min = 0.5
            self.pg_width_coef_max = 1.5
            self.pg_width_min = self.base_pg_width * self.pg_width_coef_min
            self.pg_width_max = self.base_pg_width * self.pg_width_coef_max

            self.length_coef_min = 0.6
            self.length_coef_max = 2.0
            self.length_min = self.base_length_nm * 1e-9 * self.length_coef_min
            self.length_max = self.base_length_nm * 1e-9 * self.length_coef_max

            # Create optimization bounds
            lower_bounds = [0, 0, 0, 0, 0, 0]
            upper_bounds = [1, 1, 1, 1, 1, 1]
            self.bounds = torch.tensor([lower_bounds, upper_bounds], dtype=torch.float)

    def convert_params(self, x):
        """
        Convert normalized parameters [0,1] to actual parameter values
        """
        if hasattr(self, '_modified_space'):
            return self._modified_space.convert_params(x)

        params = {}

        # Convert model parameters
        nmos_idx = int(x[0].item() * len(self.nmos_models))
        nmos_idx = min(nmos_idx, len(self.nmos_models) - 1)
        params['nmos_model_name'] = self.nmos_models[nmos_idx]

        pmos_idx = int(x[1].item() * len(self.pmos_models))
        pmos_idx = min(pmos_idx, len(self.pmos_models) - 1)
        params['pmos_model_name'] = self.pmos_models[pmos_idx]

        # Convert width parameters
        params['pd_width'] = self.pd_width_min + x[2].item() * (self.pd_width_max - self.pd_width_min)
        params['pu_width'] = self.pu_width_min + x[3].item() * (self.pu_width_max - self.pu_width_min)
        params['pg_width'] = self.pg_width_min + x[4].item() * (self.pg_width_max - self.pg_width_min)

        # Convert length parameter
        params['length'] = self.length_min + x[5].item() * (self.length_max - self.length_min)
        params['length_nm'] = params['length'] * 1e9

        return params

    def print_params(self, params):
        """
        Print parameter information
        """
        if hasattr(self, '_modified_space'):
            return self._modified_space.print_params(params)

        print("Parameters:")
        for key, value in params.items():
            print(f"  {key}: {value}")


# Constrained optimizer
class ConstrainedBayesianOptimizer:
    def __init__(self, parameter_space, num_objectives=3, num_constraints=2, initial_result=None, initial_params=None):
        """
        Initialize constrained Bayesian optimizer
        """
        self.parameter_space = parameter_space
        self.bounds = parameter_space.bounds
        self.dim = self.bounds.shape[1]
        self.num_objectives = num_objectives
        self.num_constraints = num_constraints

        # Initialize training data
        self.train_x = torch.zeros((0, self.dim))
        self.train_obj = torch.zeros((0, self.num_objectives))
        self.train_con = torch.zeros((0, self.num_constraints))

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
            # Extract values from initial result
            initial_min_snm = min(
                initial_result['hold_snm']['snm'],
                initial_result['read_snm']['snm'],
                initial_result['write_snm']['snm']
            )
            initial_max_power = max(
                initial_result['read']['power'],
                initial_result['write']['power']
            )

            # Calculate area using initial parameters
            if initial_params:
                initial_area = estimate_bitcell_area(
                    w_access=initial_params['pg_width'],
                    w_pd=initial_params['pd_width'],
                    w_pu=initial_params['pu_width'],
                    l_transistor=initial_params['length']
                )

                self.initial_merit = np.log10(initial_min_snm / (initial_max_power * np.sqrt(initial_area)))
                print(f"Initial Merit: {self.initial_merit:.6e}")

        # Initialize Merit tracking state
        self.best_merit = float('-inf')
        self.best_params = None
        self.best_result = None

        # Initialize history data
        self.iteration_history = []
        self.best_history = []

    def suggest(self, n_suggestions=1):
        """
        Generate next batch of points to evaluate
        """
        if len(self.train_x) < 30:
            print(f"Training set size: {len(self.train_x)}, using quasi-random sequence")

            soboleng = torch.quasirandom.SobolEngine(dimension=self.dim, scramble=True)

            points = soboleng.draw(n_suggestions)
            print(f"Generated points: {points.tolist()}")

            # Ensure not returning all-zero vector
            if torch.allclose(points, torch.zeros_like(points), atol=1e-3):
                print("Detected all-zero vector, switching to uniform random generation")
                points = torch.rand(n_suggestions, self.dim)

            return points
        else:
            # Use Bayesian optimization
            try:
                # Construct GP model
                gp = SingleTaskGP(self.train_x, self.train_obj.mean(dim=-1, keepdim=True))
                mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
                fit_gpytorch_model(mll)

                # Use Expected Improvement acquisition function
                from botorch.acquisition import ExpectedImprovement
                acq_func = ExpectedImprovement(gp, self.train_obj.mean(dim=-1).max())

                # Optimize acquisition function
                bounds = torch.stack([torch.zeros(self.dim), torch.ones(self.dim)])
                candidate, acq_value = optimize_acqf(
                    acq_func,
                    bounds=bounds,
                    q=1,
                    num_restarts=20,
                    raw_samples=1024,
                )

                print(f"BO suggested point: {candidate.tolist()}")
                print(f"Acquisition value: {acq_value.item():.6e}")

                return candidate

            except Exception as e:
                print(f"BO suggestion failed: {e}, using random generation")
                return torch.rand(n_suggestions, self.dim)

    def observe(self, x, objectives, constraints, result, success, iteration, opt_type="BO"):
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
            merit = result['merit']
            self.all_merit.append(merit)

            # Update training data for BO
            x_tensor = torch.tensor(x, dtype=torch.float).unsqueeze(0)
            obj_tensor = torch.tensor(objectives, dtype=torch.float).unsqueeze(0)
            con_tensor = torch.tensor(constraints, dtype=torch.float).unsqueeze(0)

            self.train_x = torch.cat([self.train_x, x_tensor])
            self.train_obj = torch.cat([self.train_obj, obj_tensor])
            self.train_con = torch.cat([self.train_con, con_tensor])

            # Update best result
            if merit > self.best_merit:
                self.best_merit = merit
                self.best_params = self.parameter_space.convert_params(torch.tensor(x, dtype=torch.float32))
                self.best_result = result

        # Record history
        self.best_history.append(self.best_merit if self.best_merit != float('-inf') else float('-inf'))


# Random search phase
def random_search(parameter_space, eval_fn=evaluate_sram, num_iterations=20):
    """
    Random search phase
    """
    print(f"===== Starting {num_iterations} rounds of random search (RS) =====")

    # Initialize optimizer
    optimizer = ConstrainedBayesianOptimizer(parameter_space)

    for i in range(num_iterations):
        print(f"\n===== RS iteration {i + 1}/{num_iterations} =====")

        # Generate random point
        x = torch.rand(optimizer.dim)

        # Map parameters to actual values
        params = parameter_space.convert_params(x)
        parameter_space.print_params(params)

        # Evaluate parameter performance
        start_time = time.time()
        objectives, constraints, result, success = eval_fn(params)
        end_time = time.time()
        print(f"Evaluation time: {end_time - start_time:.2f} seconds")

        if success:
            print("Simulation successful! Results:")
            print(f"Min SNM = {-objectives[0]:.6f}")
            print(f"Max power = {objectives[1]:.6e}")
            print(f"Area = {objectives[2]*1e12:.2f} µm²")
            print(f"Constraints: {['satisfied' if c <= 0 else 'violated' for c in constraints]}")
            if result:
                print(f"Merit = {result['merit']:.6e}")
        else:
            print("Simulation failed, penalty values assigned")

        # Observe results
        optimizer.observe(x, objectives, constraints, result, success, i, "RS")

    print("\n===== Random search completed =====")
    return optimizer


# Bayesian optimization phase
def bayesian_optimization(optimizer, parameter_space, eval_fn=evaluate_sram, num_iterations=380, iteration_offset=20):
    """
    Bayesian optimization phase
    """
    print(f"===== Starting {num_iterations} rounds of Bayesian optimization (BO) =====")

    # Track repeated suggestions
    recent_suggestions = []
    max_history = 20
    repeat_count = 0
    max_repeat_allowed = 2

    for i in range(num_iterations):
        print(f"\n===== BO iteration {i + 1}/{num_iterations} =====")

        # Get next evaluation point
        next_x = optimizer.suggest()[0]

        # Check if too similar to recent suggestions
        is_repeat = False
        for prev_x in recent_suggestions:
            if torch.norm(next_x - prev_x) < 0.03:  # If Euclidean distance is very small
                repeat_count += 1
                is_repeat = True
                print(f"Warning: Current suggestion very similar to previous suggestions (repeat count: {repeat_count})")
                break

        # If too many repeats, force random exploration
        if is_repeat and repeat_count >= max_repeat_allowed:
            print(f"Consecutive repeats {repeat_count} times, switching to random exploration mode...")
            next_x = torch.rand(optimizer.dim)
            repeat_count = 0
        elif not is_repeat:
            repeat_count = 0

        # Update suggestion history
        recent_suggestions.append(next_x)
        if len(recent_suggestions) > max_history:
            recent_suggestions.pop(0)  # Remove oldest record

        # Map parameters to actual values
        params = parameter_space.convert_params(next_x)
        parameter_space.print_params(params)

        # Evaluate parameter performance
        start_time = time.time()
        objectives, constraints, result, success = eval_fn(params)
        end_time = time.time()
        print(f"Evaluation time: {end_time - start_time:.2f} seconds")

        if success:
            print("Simulation successful! Results:")
            print(f"Min SNM = {-objectives[0]:.6f}")
            print(f"Max power = {objectives[1]:.6e}")
            print(f"Area = {objectives[2]*1e12:.2f} µm²")
            print(f"Constraints: {['satisfied' if c <= 0 else 'violated' for c in constraints]}")
            if result:
                print(f"Merit = {result['merit']:.6e}")
        else:
            print("Simulation failed, penalty values assigned")

        # Observe results (index after RS iterations end)
        iteration = i + iteration_offset
        optimizer.observe(next_x, objectives, constraints, result, success, iteration, "BO")

    print("\n===== Bayesian optimization completed =====")
    return optimizer


# Main function
def main(config_path="config_sram.yaml", problem=None, max_iter=400):
    """
    Main function to run CBO optimization
    """
    print("===== SRAM optimization using CBO =====")

    # Create directories
    create_directories()

    # Resolve parameter space and evaluation backend
    if problem is not None:
        try:
            parameter_space, eval_fn, _ = problem
        except Exception:
            parameter_space = SRAMParameterSpace(config_path)
            eval_fn = evaluate_sram
    else:
        parameter_space = SRAMParameterSpace(config_path)
        eval_fn = evaluate_sram

    # Define initial parameters (same as in main.py)
    initial_params = {
        'nmos_model_name': 'NMOS_VTG',
        'pmos_model_name': 'PMOS_VTG',
        'pd_width': 0.205e-6,
        'pu_width': 0.09e-6,
        'pg_width': 0.135e-6,
        'length': 50e-9,
        'length_nm': 50
    }
    
    print("Running initial point simulation to get baseline performance...")
    
    # Evaluate initial parameters using selected backend
    objectives, constraints, initial_result, success = eval_fn(initial_params)
    
    if not success:
        print("Warning: Initial point simulation failed, using default values as initial point")
        # Use default values as fallback
        initial_result = {
            'hold_snm': {'success': True, 'snm': 0.30173446708423357},
            'read_snm': {'success': True, 'snm': 0.12591724230394877},
            'write_snm': {'success': True, 'snm': 0.3732610863628419},
            'read': {'success': True, 'delay': 2.0883543988703797e-10, 'power': 4.024476625792127e-05},
            'write': {'success': True, 'delay': 6.086260190977158e-11, 'power': 3.975272388991992e-05}
        }
    else:
        print(f"Initial point simulation successful!")
        print(f"SNM: Hold={initial_result['hold_snm']:.4f}, Read={initial_result['read_snm']:.4f}, Write={initial_result['write_snm']:.4f}")
        print(f"Delay: Read={initial_result['read_delay']*1e12:.2f}ps, Write={initial_result['write_delay']*1e12:.2f}ps")
        print(f"Power: Read={initial_result['read_power']:.2e}W, Write={initial_result['write_power']:.2e}W")

    # Split iterations: small RS + remaining BO
    rs_iters = max(10, min(50, int(max_iter * 0.10)))
    bo_iters = max(1, int(max_iter) - rs_iters)

    # Run random search phase
    optimizer = random_search(parameter_space, eval_fn=eval_fn, num_iterations=rs_iters)

    # Run Bayesian optimization phase
    optimizer = bayesian_optimization(optimizer, parameter_space, eval_fn=eval_fn, num_iterations=bo_iters, iteration_offset=rs_iters)

    # Output best results
    print("\n===== CBO Optimization Best Results =====")
    if optimizer.best_merit != float('-inf'):
        print(f"Best Merit: {optimizer.best_merit:.6e}")
        print("Best parameters:")
        parameter_space.print_params(optimizer.best_params)
        if optimizer.best_result:
            print(f"Min SNM: {optimizer.best_result['min_snm']:.6f}")
            print(f"Max power: {optimizer.best_result['max_power']:.6e}")
            print(f"Area: {optimizer.best_result['area']*1e12:.2f} µm²")
        
        # Return result
        ret = {
            'params': optimizer.best_params,
            'merit': optimizer.best_merit,
            'result': optimizer.best_result,
            'iteration': rs_iters + bo_iters
        }
        ret['fom'] = ret.get('merit')
        return ret
    else:
        print("No valid solution found")
        return {
            'params': None,
            'merit': None,
            'result': None,
            'iteration': -1
        }


if __name__ == "__main__":
    # Set random seed for reproducibility
    SEED = 1
    seed_set(seed=SEED)
    main()
