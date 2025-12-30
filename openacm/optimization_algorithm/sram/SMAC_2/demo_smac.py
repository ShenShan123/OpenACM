"""
SRAM Circuit Optimization using SMAC Algorithm

This file implements a SMAC (Sequential Model-based Algorithm Configuration) optimization algorithm 
for SRAM parameter optimization.
"""

import os
import sys
import time
import numpy as np
import torch
import random
import warnings
import csv
from pathlib import Path
from smac import HyperparameterOptimizationFacade, Scenario
from smac.runhistory.dataclasses import TrialValue, TrialInfo
from ConfigSpace import Configuration, ConfigurationSpace
import ConfigSpace.hyperparameters as CSH

warnings.filterwarnings('ignore')

# Setup paths first - before importing from sram_optimization
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import utilities from exp_utils
from sram_sizing.exp_utils import (
    seed_set, create_directories, evaluate_sram, ModifiedSRAMParameterSpace,
    BaseOptimizer, get_default_initial_params, run_initial_evaluation
)


class SMACOptimizer(BaseOptimizer):
    """
    SMAC optimizer class
    """
    
    def __init__(self, parameter_space, num_objectives=3, num_constraints=2, 
                 initial_result=None, initial_params=None, evaluate_backend=None):
        """
        Initialize SMAC optimizer
        """
        super().__init__(parameter_space, "SMAC", num_objectives, num_constraints, 
                         initial_result, initial_params)
        # Optional external evaluation function
        self.evaluate_backend = evaluate_backend

        # Initialize configuration space
        self.cs = self._create_config_space()
        
        # Initialize SMAC state
        self.evaluation_count = 0

    def _create_config_space(self):
        """
        Create configuration space for SMAC
        """
        cs = ConfigurationSpace()
        
        # Add hyperparameters for each dimension
        for i in range(self.dim):
            hp = CSH.UniformFloatHyperparameter(f"x_{i:03d}", 0.0, 1.0, default_value=0.5)
            cs.add_hyperparameter(hp)
        
        return cs

    def smac_objective(self, config: Configuration, seed: int = 0) -> float:
        """
        Objective function for SMAC
        """
        # Convert configuration to parameter vector
        x = torch.tensor([config[f"x_{i:03d}"] for i in range(self.dim)], dtype=torch.float32)
        
        # Convert parameters
        params = self.parameter_space.convert_params(x)
        
        print(f"\n===== SMAC Evaluation {self.evaluation_count + 1} =====")
        print("Current parameters:")
        self.parameter_space.print_params(params)
        
        start_time = time.time()
        eval_func = self.evaluate_backend if self.evaluate_backend is not None else evaluate_sram
        objectives, constraints, result, success = eval_func(params)
        end_time = time.time()
        print(f"Evaluation time: {end_time - start_time:.2f} seconds")
        
        if success and result:
            merit = result['merit']
            
            # Record results
            self.observe(x.numpy(), objectives, constraints, result, success, self.evaluation_count, "SMAC")
            
            print(f"Merit: {merit:.6e}")
            print(f"SNM: Hold={result['hold_snm']:.6f}, Read={result['read_snm']:.6f}, Write={result['write_snm']:.6f}")
            print(f"Delay: Read={result['read_delay']*1e12:.2f}ps, Write={result['write_delay']*1e12:.2f}ps")
            print(f"Power: Read={result['read_power']:.2e}W, Write={result['write_power']:.2e}W")
            print(f"Area: {result['area']*1e12:.2f} µm²")
            
            if merit > self.best_merit:
                print(f"Found new best merit: {merit:.6e}")
            
            # SMAC minimizes, so return negative Merit
            self.evaluation_count += 1
            return -merit
        else:
            print("Simulation failed!")
            self.evaluation_count += 1
            return 1e6  # Large penalty for failed simulations

    def run_optimization(self, max_iter=400):
        """
        Run SMAC optimization
        """
        print(f"===== Starting SMAC optimization, maximum simulations: {max_iter} =====")

        # Create SMAC scenario
        scenario = Scenario(
            configspace=self.cs,
            deterministic=True,
            n_trials=max_iter,
            seed=1,
        )

        # Initialize SMAC
        smac = HyperparameterOptimizationFacade(
            scenario,
            self.smac_objective,
            dask_client=None,  # No parallel execution
        )

        # Run optimization
        print("Starting SMAC optimization loop...")
        incumbent = smac.optimize()

        print(f"\nSMAC optimization completed, total evaluations: {self.evaluation_count}")
        print(f"Final configuration: {incumbent}")

        # Return best results
        if self.best_merit != float('-inf'):
            return {
                'params': self.best_params,
                'merit': self.best_merit,
                'result': self.best_result,
                'iteration': self.evaluation_count
            }
        else:
            return {
                'params': None,
                'merit': None,
                'result': None,
                'iteration': -1
            }


def main(config_path="config_sram.yaml", problem=None, max_iter=None):
    """
    Main function to run SMAC optimization
    """
    print("===== SRAM optimization using SMAC =====")

    # Create directories
    create_directories()

    # Create parameter space - use modified parameter space class with config support
    if problem is not None and isinstance(problem, (tuple, list)) and len(problem) >= 2:
        parameter_space = problem[0]
        external_eval_fn = problem[1]
    else:
        parameter_space = ModifiedSRAMParameterSpace(config_path)
        external_eval_fn = None

    # Define initial parameters
    initial_params = get_default_initial_params()
    
    print("Running initial point simulation to get baseline performance...")
    
    # Run initial evaluation
    if external_eval_fn is None:
        initial_result, initial_params = run_initial_evaluation(initial_params)
    else:
        # When external eval is provided, evaluate initial params using it
        objectives, constraints, direct_result, success = external_eval_fn(initial_params)
        # Convert to formatted result expected by BaseOptimizer
        if success and direct_result:
            formatted_result = {
                'hold_snm': {'success': True, 'snm': direct_result['hold_snm']},
                'read_snm': {'success': True, 'snm': direct_result['read_snm']},
                'write_snm': {'success': True, 'snm': direct_result['write_snm']},
                'read': {'success': True, 'delay': direct_result['read_delay'], 'power': abs(direct_result['read_power'])},
                'write': {'success': True, 'delay': direct_result['write_delay'], 'power': abs(direct_result['write_power'])}
            }
            initial_result = formatted_result
        else:
            initial_result = None
    
    if initial_result:
        print(f"Initial point simulation successful!")
        print(f"SNM: Hold={initial_result['hold_snm']['snm']:.4f}, Read={initial_result['read_snm']['snm']:.4f}, Write={initial_result['write_snm']['snm']:.4f}")
        print(f"Delay: Read={initial_result['read']['delay']*1e12:.2f}ps, Write={initial_result['write']['delay']*1e12:.2f}ps")
        print(f"Power: Read={initial_result['read']['power']:.2e}W, Write={initial_result['write']['power']:.2e}W")

    # Create SMAC optimizer
    optimizer = SMACOptimizer(
        parameter_space,
        initial_result=initial_result,
        initial_params=initial_params,
        evaluate_backend=external_eval_fn
    )

    # Run SMAC optimization
    _max_iter = max_iter if isinstance(max_iter, int) and max_iter > 0 else 5
    best_result = optimizer.run_optimization(max_iter=_max_iter)

    # Output best results
    print("\n===== SMAC Optimization Best Results =====")
    if best_result['params'] is not None:
        print(f"Best Merit: {best_result['merit']:.6e}")
        print(f"Evaluation count: {best_result['iteration']}")
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
    # Set random seed for reproducibility
    SEED = 1
    seed_set(seed=SEED)
    main()
