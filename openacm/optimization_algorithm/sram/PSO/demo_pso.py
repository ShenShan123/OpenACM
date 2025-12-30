"""
SRAM Circuit Optimization using PSO Algorithm

This file implements a Particle Swarm Optimization algorithm for SRAM parameter optimization.
"""

import os
import time
import numpy as np
import torch
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# Import path handling
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import utilities from exp_utils
from sram_sizing.exp_utils import (
    seed_set, create_directories, evaluate_sram, ModifiedSRAMParameterSpace,
    OptimizationLogger, save_pareto_front, save_best_result, plot_merit_history,
    plot_pareto_frontier, update_pareto_front, save_optimization_history
)
from sram_sizing.utils import estimate_bitcell_area


def format_initial_result(result):
    """
    Convert evaluate_sram result format to expected format
    """
    if result is None:
        return None
    
    formatted_result = {
        'hold_snm': {'success': True, 'snm': result['hold_snm']},
        'read_snm': {'success': True, 'snm': result['read_snm']},
        'write_snm': {'success': True, 'snm': result['write_snm']},
        'read': {'success': True, 'delay': result['read_delay'], 
                 'power': abs(result['read_power'])},
        'write': {'success': True, 'delay': result['write_delay'], 
                  'power': abs(result['write_power'])}
    }
    return formatted_result


# PSO optimizer class
class PSOOptimizer:
    def __init__(self, parameter_space, num_objectives=3, num_constraints=2, initial_result=None, initial_params=None, evaluate_backend=None):
        """
        Initialize PSO optimizer
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
            # Extract values from initial result
            if isinstance(initial_result.get('hold_snm'), dict):
                # New format: {'hold_snm': {'snm': value}}
                initial_min_snm = min(
                    initial_result['hold_snm']['snm'],
                    initial_result['read_snm']['snm'],
                    initial_result['write_snm']['snm']
                )
                initial_max_power = max(
                    initial_result['read']['power'],
                    initial_result['write']['power']
                )
            else:
                # Direct format: {'hold_snm': value}
                initial_min_snm = min(
                    initial_result['hold_snm'],
                    initial_result['read_snm'],
                    initial_result['write_snm']
                )
                initial_max_power = max(
                    abs(initial_result['read_power']),
                    abs(initial_result['write_power'])
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

        # Initialize history data
        self.iteration_history = []  # Record evaluation results for each iteration
        self.best_history = []  # Record best Merit for each iteration

    def evaluate(self, x):
        """
        Evaluate single parameter setting for PSO optimization
        """
        # Ensure x is numpy array type
        x = np.array(x) if not isinstance(x, np.ndarray) else x

        # Convert to torch.Tensor
        x_tensor = torch.tensor(x, dtype=torch.float32)

        # Convert parameters
        params = self.parameter_space.convert_params(x_tensor)

        # Evaluate SRAM performance
        eval_func = self.evaluate_backend if self.evaluate_backend is not None else evaluate_sram
        objectives, constraints, result, success = eval_func(params)

        # Calculate optimization objective: Merit = log10(min_snm / (max_power * (area**0.5)))
        if success and result:
            merit = result['merit']

            # Return negative Merit, because PSO is a minimization problem
            return -merit
        else:
            # If evaluation fails, return a large penalty value
            return 1e9

    def run_optimization(self, max_iter=100, population_size=30):
        """
        Run PSO optimization
        """
        print(f"===== Starting PSO optimization, maximum simulations: {max_iter} =====")

        # Parameter ranges
        lb = np.zeros(self.dim)
        ub = np.ones(self.dim)

        # PSO parameters
        w = 0.8  # Inertia weight
        c1 = 0.5  # Individual learning factor
        c2 = 0.5  # Social learning factor

        # Initialize particle swarm
        particles = np.random.uniform(lb, ub, (population_size, self.dim))
        velocities = np.random.uniform(-0.5, 0.5, (population_size, self.dim))

        # Initialize fitness
        p_best = particles.copy()
        p_best_fitness = np.ones(population_size) * 1e9
        g_best = particles[0].copy()
        g_best_fitness = 1e9

        # Best merit tracking
        best_merit = float('-inf')
        best_params = None
        best_result = None

        # Counter
        sim_counter = 0

        # Each particle computes one simulation, each simulation counts as one iteration
        while sim_counter < max_iter:
            # Randomly select a particle
            particle_idx = sim_counter % population_size

            # Update particle position and velocity
            if sim_counter >= population_size:
                r1 = np.random.random(self.dim)
                r2 = np.random.random(self.dim)

                velocities[particle_idx] = (w * velocities[particle_idx] +
                                            c1 * r1 * (p_best[particle_idx] - particles[particle_idx]) +
                                            c2 * r2 * (g_best - particles[particle_idx]))

                particles[particle_idx] = particles[particle_idx] + velocities[particle_idx]
                particles[particle_idx] = np.clip(particles[particle_idx], lb, ub)

            # Evaluate current particle
            print(f"\n===== PSO simulation {sim_counter + 1}/{max_iter} =====")
            print(f"Evaluating particle {particle_idx + 1}/{population_size}")

            x_tensor = torch.tensor(particles[particle_idx], dtype=torch.float32)
            params = self.parameter_space.convert_params(x_tensor)

            print("Current parameters:")
            self.parameter_space.print_params(params)

            # Detailed evaluation, get complete results
            start_time = time.time()
            eval_func = self.evaluate_backend if self.evaluate_backend is not None else evaluate_sram
            objectives, constraints, result, success = eval_func(params)
            end_time = time.time()
            print(f"Evaluation time: {end_time - start_time:.2f} seconds")

            # Calculate fitness
            if success and result:
                # Updated to use Merit
                merit = result['merit']
                fitness = -merit  # Negative Merit as fitness (minimization problem)

                # Update individual best
                if fitness < p_best_fitness[particle_idx]:
                    p_best[particle_idx] = particles[particle_idx].copy()
                    p_best_fitness[particle_idx] = fitness

                    # Update global best
                    if fitness < g_best_fitness:
                        g_best = particles[particle_idx].copy()
                        g_best_fitness = fitness
                        print(f"Found new global best: {-g_best_fitness:.6e}")

                # Update overall best tracking
                if merit > best_merit:
                    best_merit = merit
                    best_params = params
                    best_result = result

                # Record results
                self.all_x.append(particles[particle_idx])
                self.all_objectives.append(objectives)
                self.all_constraints.append(constraints)
                self.all_results.append(result)
                self.all_success.append(success)
                self.all_merit.append(merit)

                print(f"Current Merit: {merit:.6e}")
                print(f"Best Merit: {-g_best_fitness:.6e}")
            else:
                # Failed simulations also count towards iteration count, but don't update optimal solutions
                self.all_x.append(particles[particle_idx])
                self.all_objectives.append(objectives)
                self.all_constraints.append(constraints)
                self.all_results.append(result)
                self.all_success.append(success)
                print("Evaluation failed")

            # Record current iteration
            sim_counter += 1

        print("\n===== PSO optimization completed =====")

        # Return best result
        if best_merit != float('-inf'):
            return {
                'params': best_params,
                'merit': best_merit,
                'result': best_result,
                'iteration': max_iter
            }
        else:
            return {
                'params': None,
                'merit': None,
                'result': None,
                'iteration': -1
            }


# Main function
def main(config_path=os.path.join(project_root, "config/config_sram.yaml"), problem=None, max_iter=None):
    """
    Main function to run PSO optimization
    """
    print("===== SRAM optimization using PSO =====")

    # Create directories
    create_directories()

    # Create parameter space - use modified parameter space class
    if problem is not None and isinstance(problem, (tuple, list)) and len(problem) >= 2:
        parameter_space = problem[0]
        external_eval_fn = problem[1]
    else:
        parameter_space = ModifiedSRAMParameterSpace(config_path)
        external_eval_fn = None

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
    
    # Evaluate initial parameters
    if external_eval_fn is not None:
        objectives, constraints, initial_result, success = external_eval_fn(initial_params)
    else:
        objectives, constraints, initial_result, success = evaluate_sram(initial_params)
    
    if not success:
        print("Warning: Initial point simulation failed, using default values as initial point")
        # Use default values as fallback
        initial_result = {
            'hold_snm': 0.30173446708423357,
            'read_snm': 0.12591724230394877,
            'write_snm': 0.3732610863628419,
            'read_delay': 2.0883543988703797e-10,
            'read_power': 4.024476625792127e-05,
            'write_delay': 6.086260190977158e-11,
            'write_power': 3.975272388991992e-05
        }
    else:
        print(f"Initial point simulation successful!")
        print(f"SNM: Hold={initial_result['hold_snm']:.4f}, Read={initial_result['read_snm']:.4f}, Write={initial_result['write_snm']:.4f}")
        print(f"Delay: Read={initial_result['read_delay']*1e12:.2f}ps, Write={initial_result['write_delay']*1e12:.2f}ps")
        print(f"Power: Read={initial_result['read_power']:.2e}W, Write={initial_result['write_power']:.2e}W")

    # Create PSO optimizer, pass initial parameters and results
    optimizer = PSOOptimizer(
        parameter_space,
        initial_result=initial_result,  # Use direct format
        initial_params=initial_params,
        evaluate_backend=external_eval_fn
    )

    # Run PSO optimization
    _max_iter = max_iter if isinstance(max_iter, int) and max_iter > 0 else 5
    best_result = optimizer.run_optimization(max_iter=_max_iter, population_size=3)

    # Output best results
    print("\n===== PSO Optimization Best Results =====")
    if best_result['params'] is not None:
        print(f"Best Merit: {best_result['merit']:.6e}")
        print(f"Iteration count: {best_result['iteration']}")
        print("Best parameters:")
        parameter_space.print_params(best_result['params'])
        if best_result['result']:
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
