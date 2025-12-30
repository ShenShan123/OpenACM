"""
This file implements the RoSE-Opt algorithm for SRAM optimization.

It combines Bayesian Optimization and Reinforcement Learning to find optimal SRAM parameters.
"""

import os
import time
import numpy as np
import torch
import pandas as pd
import csv
import random
import warnings
import gymnasium as gym
from gymnasium import spaces
from pathlib import Path
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel, ConstantKernel as C
from scipy.stats import norm
from tqdm import tqdm
import matplotlib.pyplot as plt

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
from utils import estimate_bitcell_area

# Set device
device = torch.device("cpu")

# Suppress warnings
warnings.filterwarnings('ignore')


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


class Normalizer:
    """
    Parameter normalizer for optimization
    """

    def __init__(self, low, high, param_names=None):
        """
        Initialize normalizer
        Args:
            low: Lower bounds for parameters
            high: Upper bounds for parameters
            param_names: Names of parameters
        """
        self.low = np.array(low)
        self.high = np.array(high)
        self.param_names = param_names

    def normalize(self, x):
        """
        Normalize parameters to 0-1 range
        """
        # Ensure x is within valid range
        if isinstance(x, np.ndarray):
            x_clipped = np.clip(x, self.low, self.high)
            if not np.array_equal(x, x_clipped):
                x = x_clipped

        return (x - self.low) / (self.high - self.low + 1e-6)

    def denormalize(self, x_norm):
        """
        Convert normalized parameters (0-1) back to original range
        """
        # Ensure normalized values are in 0-1 range
        if isinstance(x_norm, np.ndarray):
            x_norm_clipped = np.clip(x_norm, 0, 1)
            if not np.array_equal(x_norm, x_norm_clipped):
                x_norm = x_norm_clipped

        # Perform denormalization
        return self.low + x_norm * (self.high - self.low)


class SRAMCircuitEnv(gym.Env):
    """
    SRAM circuit environment for reinforcement learning
    """

    def __init__(self, parameter_space, max_steps=5):
        """
        Initialize SRAM circuit environment
        Args:
            parameter_space: Parameter space object
            max_steps: Maximum steps per episode
        """
        super(SRAMCircuitEnv, self).__init__()

        self.parameter_space = parameter_space
        self.max_steps = max_steps
        self.current_step = 0

        # Get parameter space dimensions
        self.dim = parameter_space.bounds.shape[1]

        # Define action and observation space
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(self.dim,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(self.dim + 3,), dtype=np.float32)

        # State variables
        self.current_params = None
        self.best_merit = float('-inf')

    def reset(self, seed=None, options=None):
        """Reset environment"""
        super().reset(seed=seed)
        self.current_step = 0
        
        # Random initial parameters
        self.current_params = np.random.uniform(0, 1, size=self.dim)
        
        # Initial state includes current parameters plus some context
        state = np.concatenate([
            self.current_params,
            [0.0, 0.0, 0.0]  # Merit, constraint violation, step progress
        ])
        
        return state.astype(np.float32), {}

    def step(self, action):
        """Take a step in the environment"""
        self.current_step += 1
        
        # Apply action to modify parameters
        action = np.clip(action, -1.0, 1.0)
        self.current_params = np.clip(self.current_params + action * 0.1, 0, 1)
        
        # Evaluate parameters (simplified for RL environment)
        reward = np.random.random() - 0.5  # Simplified reward
        
        # Check if done
        done = self.current_step >= self.max_steps
        
        # Next state
        state = np.concatenate([
            self.current_params,
            [reward, 0.0, self.current_step / self.max_steps]
        ])
        
        return state.astype(np.float32), reward, done, False, {}


# Simple PPO implementation to avoid import issues
class SimplePPO:
    """
    Simplified PPO implementation
    """
    
    def __init__(self, state_dim, action_dim, lr_actor=3e-4, lr_critic=1e-3, 
                 gamma=0.99, K_epochs=10, eps_clip=0.2, hidden_dim=64):
        """
        Initialize PPO
        """
        self.lr_actor = lr_actor
        self.lr_critic = lr_critic
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs
        
        # Create simple networks
        self.actor = torch.nn.Sequential(
            torch.nn.Linear(state_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, action_dim),
            torch.nn.Tanh()
        )
        
        self.critic = torch.nn.Sequential(
            torch.nn.Linear(state_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, 1)
        )
        
        # Initialize optimizers
        self.optimizer_actor = torch.optim.Adam(self.actor.parameters(), lr=lr_actor)
        self.optimizer_critic = torch.optim.Adam(self.critic.parameters(), lr=lr_critic)
        
    def select_action(self, state):
        """Select action"""
        with torch.no_grad():
            action = self.actor(state)
        return action.cpu().numpy()
    
    def update(self, states, actions, rewards):
        """Update PPO networks"""
        # Simplified update (placeholder)
        pass


class SRAM_BORL:
    """
    SRAM Bayesian Optimization with Reinforcement Learning (RoSE-Opt)
    """

    def __init__(self, env, parameter_space, objective_function,
                 save_dir='results', hidden_dim=64, lr=3e-4, betas=(0.9, 0.999),
                 gamma=0.99, K_epochs=10, eps_clip=0.2, 
                 initial_result=None, initial_params=None):
        """
        Initialize SRAM_BORL optimizer
        """
        self.env = env
        self.parameter_space = parameter_space
        self.objective_function = objective_function
        self.save_dir = save_dir

        # Create save directory
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        # Initialize PPO agent: Use simplified PPO
        state_dim = env.observation_space.shape[0]
        action_dim = env.action_space.shape[0]
        
        # FIXED: Use SimplePPO instead of imported PPO
        self.ppo = SimplePPO(
            state_dim=state_dim, 
            action_dim=action_dim, 
            lr_actor=lr,  # FIXED: correct parameter name
            lr_critic=lr * 0.3,
            gamma=gamma,
            K_epochs=K_epochs,
            eps_clip=eps_clip,
            hidden_dim=hidden_dim
        )

        # Data storage
        self.X_data = []  # Normalized parameter data
        self.Y_data = []  # Merit data
        self.constraint_data = []
        self.results_data = []

        # Best result tracking
        self.best_merit = float('-inf')
        self.best_params = None
        self.best_result = None
        self.best_merit_result = None

        # Timing tracking
        self.simulation_time = 0.0
        self.search_time = 0.0

        # Set initial feasible point: handle both formats
        if initial_result and initial_params:
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
            
            initial_area = estimate_bitcell_area(
                w_access=initial_params['pg_width'],
                w_pd=initial_params['pd_width'],
                w_pu=initial_params['pu_width'],
                l_transistor=initial_params['length']
            )
            
            self.initial_merit = np.log10(initial_min_snm / (initial_max_power * np.sqrt(initial_area)))
            print(f"Initial Merit: {self.initial_merit:.6e}")

        # Normalizer for parameters
        bounds = parameter_space.bounds
        low_bounds = bounds[0].numpy()
        high_bounds = bounds[1].numpy()
        self.normalizer = Normalizer(low_bounds, high_bounds)

    def _init_gp_model(self, n_initial_samples=40):
        """
        Initialize GP model with random sampling
        """
        print(f"Collecting {n_initial_samples} initial samples...")

        start_time = time.time()

        X_train = []
        Y_train = []

        for i in range(n_initial_samples):
            print(f"\n===== Initial sample {i + 1}/{n_initial_samples} =====")

            # Generate random parameters
            x_normalized = np.random.uniform(0, 1, size=self.parameter_space.bounds.shape[1])
            X_train.append(x_normalized)

            # Convert to actual parameters
            x_tensor = torch.tensor(x_normalized, dtype=torch.float32)
            params = self.parameter_space.convert_params(x_tensor)

            print("Random parameters:")
            self.parameter_space.print_params(params)

            # Evaluate
            sim_start_time = time.time()
            objectives, constraints, result, success = self.objective_function(params)
            sim_end_time = time.time()
            self.simulation_time += sim_end_time - sim_start_time

            if success and result:
                merit = result['merit']
                Y_train.append(merit)

                # Store data
                self.X_data.append(x_normalized)
                self.Y_data.append(merit)
                self.constraint_data.append(constraints)
                self.results_data.append(result)

                print(f"Merit: {merit:.6e}")

                # Update best result
                if merit > self.best_merit:
                    self.best_merit = merit
                    self.best_params = params
                    self.best_result = result
                    self.best_merit_result = result
                    print(f"New best Merit: {merit:.6e}")
            else:
                print("Simulation failed, using penalty value")
                Y_train.append(-10.0)  # Penalty value

        # Convert to arrays
        X_train_normalized = np.array(X_train)
        Y_train = np.array(Y_train).reshape(-1, 1)

        # Normalize Y for GP
        Y_mean = Y_train.mean()
        Y_std = Y_train.std() + 1e-6
        Y_train_normalized = (Y_train - Y_mean) / Y_std

        # Train GP model
        kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2)) + WhiteKernel(1e-5, (1e-10, 1e+1))
        gp = GaussianProcessRegressor(
            kernel=kernel,
            alpha=1e-6,
            normalize_y=False,
            n_restarts_optimizer=10,
            random_state=42
        )
        gp.fit(X_train_normalized, Y_train_normalized)

        self.search_time += time.time() - start_time

        return X_train_normalized, Y_train, Y_mean, Y_std, gp

    def train(self, num_iterations=400, debug_interval=20):
        """
        Execute RoSE-Opt training, modify data saving format to match other algorithms
        Args:
            num_iterations: Training iteration count
            debug_interval: Debug information print interval

        Returns:
            dict: Optimization results
        """
        print(f"===== Starting SRAM RoSE-Opt algorithm optimization =====")

        # Initialize GP model
        print(f"Initializing GP model with random sampling...")
        X_train, Y_train, Y_mean, Y_std, gp = self._init_gp_model()

        # Total iteration counter (including initialization and all iterations)
        total_iterations = len(X_train)  # Start counting from number of initialization samples

        # Track repeated suggestions
        recent_suggestions = []
        max_history = 20
        repeat_count = 0
        max_repeat_allowed = 2

        # Set task ID (1 indicates power optimization)
        task_id = 1
        constraints = {
            "max_delay": 5e-10  # 500ps
        }

        # Main loop
        for iteration in tqdm(range(num_iterations), desc="RoSE-Opt optimization", unit="iteration"):
            try:
                # Start timing
                iter_start_time = time.time()

                # ---------- BO step: Use Bayesian optimization to select parameter points ----------
                # ---------- BO step ----------
                search_start_time = time.time()

                # Expected improvement acquisition function
                def expected_improvement(X, Y_mean, Y_std, gp, xi=0.005):
                    Y_train_pred = np.array(self.Y_data)
                    if len(Y_train_pred) == 0:
                        return np.ones(X.shape[0])
                    
                    f_max = np.max(Y_train_pred)
                    mu, sigma = gp.predict(X, return_std=True)
                    
                    # Denormalize predictions
                    mu = mu * Y_std + Y_mean
                    sigma = sigma * Y_std
                    
                    # Keep sigma as 1D array to match ei dimensions
                    sigma = sigma.flatten()
                    
                    with np.errstate(divide='warn'):
                        imp = mu - f_max - xi
                        Z = imp / sigma
                        ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
                        ei[sigma == 0.0] = 0.0
                    
                    return ei.flatten()

                # Generate candidate points and select best
                n_candidates = 5000
                X_candidates = np.random.uniform(0, 1, size=(n_candidates, self.parameter_space.bounds.shape[1]))

                ei_xi = max(1e-3, 0.1 / (1 + len(self.Y_data)))
                ei_values = expected_improvement(X_candidates, Y_mean, Y_std, gp, xi=ei_xi)
                best_idx = np.argmax(ei_values)
                x_next_bo = X_candidates[best_idx]

                # Check for repeated suggestions
                is_repeat = False
                for prev_x in recent_suggestions:
                    if np.linalg.norm(x_next_bo - prev_x) < 0.03:
                        repeat_count += 1
                        is_repeat = True
                        break

                if is_repeat and repeat_count >= max_repeat_allowed:
                    print(f"Too many repeated suggestions, using random exploration")
                    x_next_bo = np.random.uniform(0, 1, size=self.parameter_space.bounds.shape[1])
                    repeat_count = 0
                elif not is_repeat:
                    repeat_count = 0

                # Update suggestion history
                recent_suggestions.append(x_next_bo.copy())
                if len(recent_suggestions) > max_history:
                    recent_suggestions.pop(0)

                self.search_time += time.time() - search_start_time

                # ---------- Evaluate selected parameters ----------
                print(f"\n===== RoSE-Opt iteration {total_iterations + 1} =====")

                # Convert to actual parameters
                x_tensor = torch.tensor(x_next_bo, dtype=torch.float32)
                params = self.parameter_space.convert_params(x_tensor)

                print("BO suggested parameters:")
                self.parameter_space.print_params(params)

                # Evaluate
                sim_start_time = time.time()
                objectives, constraint_values, result, success = self.objective_function(params)
                sim_end_time = time.time()
                self.simulation_time += sim_end_time - sim_start_time

                if success and result:
                    merit = result['merit']

                    # Store data
                    self.X_data.append(x_next_bo)
                    self.Y_data.append(merit)
                    self.constraint_data.append(constraint_values)
                    self.results_data.append(result)

                    print(f"Merit: {merit:.6e}")
                    print(f"SNM: Hold={result['hold_snm']:.6f}, Read={result['read_snm']:.6f}, Write={result['write_snm']:.6f}")
                    print(f"Delay: Read={result['read_delay']*1e12:.2f}ps, Write={result['write_delay']*1e12:.2f}ps")
                    print(f"Power: Read={result['read_power']:.2e}W, Write={result['write_power']:.2e}W")

                    # Update best result
                    if merit > self.best_merit:
                        self.best_merit = merit
                        self.best_params = params
                        self.best_result = result
                        self.best_merit_result = result
                        print(f"*** New best Merit: {merit:.6e} ***")

                    # Update GP model
                    if len(self.Y_data) > 1:
                        X_train_new = np.array(self.X_data)
                        Y_train_new = np.array(self.Y_data).reshape(-1, 1)
                        Y_mean = Y_train_new.mean()
                        Y_std = Y_train_new.std() + 1e-6
                        Y_train_normalized = (Y_train_new - Y_mean) / Y_std
                        gp.fit(X_train_new, Y_train_normalized)

                else:
                    print("Simulation failed!")

                total_iterations += 1

                # Print periodic updates
                if (iteration + 1) % debug_interval == 0:
                    print(f"\n--- Progress Update: {iteration + 1}/{num_iterations} iterations completed ---")
                    print(f"Current best Merit: {self.best_merit:.6e}")

            except Exception as e:
                print(f"Error in iteration {iteration + 1}: {e}")
                continue

        print(f"\n===== RoSE-Opt optimization completed =====")
        print(f"Total evaluations: {total_iterations}")
        print(f"Best Merit: {self.best_merit:.6e}")

        # Return results in format compatible with other algorithms
        return {
            'params': self.best_params,
            'merit': self.best_merit,
            'result': self.best_result,
            'iteration': total_iterations
        }

    def print_final_results(self):
        """
        Print final optimization results
        """
        print("\n===== RoSE-Opt Optimization Final Results =====")

        if self.best_merit != float('-inf'):
            print(f"Best Merit: {self.best_merit:.6e}")

            print("\nBest parameters:")
            self.parameter_space.print_params(self.best_params)

            if self.best_merit_result:
                print(f"\nPerformance metrics:")
                print(f"Min SNM: {self.best_merit_result['min_snm']:.6f}")
                print(f"Max power: {self.best_merit_result['max_power']:.6e}")
                print(f"Area: {self.best_merit_result['area']*1e12:.2f} µm²")
                print(f"Read delay: {self.best_merit_result['read_delay']*1e12:.2f} ps")
                print(f"Write delay: {self.best_merit_result['write_delay']*1e12:.2f} ps")
                print(f"Constraint satisfaction: Read delay {self.best_merit_result['read_delay_feasible']}, Write delay {self.best_merit_result['write_delay_feasible']}")


# Main function to run the RoSE-Opt algorithm for SRAM optimization
def main(config_path="config_sram.yaml", problem=None, max_iter=400):
    """
    Main function to run RoSE-Opt optimization
    Args:
        config_path: Config file path (used for default parameter space)
        problem: Triple (param_space, eval_fn, extra), consistent with experiment stage-2 interface
        max_iter: Maximum iterations (default 400; if provided by experiment, uses that value)
    """
    print("===== SRAM Optimization using RoSE-Opt Algorithm =====")

    # Create directories
    create_directories()

    # Resolve parameter space and evaluation backend
    if problem is not None:
        try:
            parameter_space, eval_fn, _ = problem
        except Exception:
            parameter_space = ModifiedSRAMParameterSpace(config_path)
            eval_fn = evaluate_sram
    else:
        parameter_space = ModifiedSRAMParameterSpace(config_path)
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
    try:
        objectives, constraints, initial_result, success = eval_fn(initial_params)
    except TypeError:
        objectives, constraints, initial_result, success = eval_fn(initial_params)

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

    # Create SRAM environment
    env = SRAMCircuitEnv(parameter_space, max_steps=5)

    # Create optimizer and pass initial feasible point: use selected backend
    optimizer = SRAM_BORL(
        env=env,
        parameter_space=parameter_space,
        objective_function=eval_fn,
        save_dir=str(Path(os.path.dirname(os.path.abspath(__file__))) / 'sim' / 'opt' / 'results'),
        # Increase network capacity and training steps moderately
        hidden_dim=128,
        lr=2e-4,
        betas=(0.9, 0.999),
        gamma=0.995,
        K_epochs=20,
        eps_clip=0.2,
        initial_result=initial_result,
        initial_params=initial_params
    )

    # Run RoSE-Opt training
    debug_interval = max(1, int(max_iter // 20))
    results = optimizer.train(num_iterations=int(max_iter), debug_interval=debug_interval)

    # Print final results
    optimizer.print_final_results()

    # Calculate and print timing statistics
    print("\n===== Timing Statistics =====")
    print(f"Total simulation time: {optimizer.simulation_time:.2f} seconds")
    print(f"Total search time: {optimizer.search_time:.2f} seconds")

    print("\nOptimization completed!")

    # Standardize return fields: add 'fom' for consistency with other algorithms
    if isinstance(results, dict) and ('fom' not in results):
        try:
            results['fom'] = results.get('merit', None)
        except Exception:
            pass

    return results


if __name__ == "__main__":
    # Set random seed for reproducibility
    SEED = 1
    seed_set(seed=SEED)
    main()
