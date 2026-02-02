import itertools
import time

import numpy as np
# import warnings  # To disable ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from acquisition import (
    extract_pareto_front,
    monte_carlo_ehvi,
    create_individuals_from_front,
)


class BayesianOptimizer:
    """
    Multi-objective Bayesian optimizer.
    """

    def __init__(
        self,
        problem,
        n_initial=200,
        n_iterations=1000,
        n_candidates_per_iter=3000,
        mc_samples=100,
        ref_point=None,
    ):
        """
        Args:
            problem: Problem object
            n_initial: number of initial random samples
            n_iterations: Bayesian optimization iterations
            n_candidates_per_iter: candidates per iteration (lower for speed)
            mc_samples: Monte Carlo samples (lower for speed)
            ref_point: reference point
        """
        self.problem = problem
        self.n_initial = n_initial
        self.n_iterations = n_iterations
        self.n_candidates_per_iter = n_candidates_per_iter
        self.mc_samples = mc_samples
        self.ref_point = ref_point

        self.scaler_X = StandardScaler()  # Input feature scaling
        self.scaler_obj1 = StandardScaler()
        self.scaler_obj2 = StandardScaler()

        # Use wider kernel bounds and stronger regularization
        # Lower length_scale bound: 1e-3 -> 1e-4 (fewer ConvergenceWarnings)
        kernel = C(1.0, (1e-4, 1e4)) * RBF(1.0, (1e-4, 1e3))
        self.gp_obj1 = GaussianProcessRegressor(
            kernel=kernel,
            alpha=1e-3,  # Stronger regularization for numerical stability
            n_restarts_optimizer=1,  # Fewer restarts to avoid over-optimization
            normalize_y=True,  # Must be on to handle scale differences
            optimizer="fmin_l_bfgs_b",
        )
        self.gp_obj2 = GaussianProcessRegressor(
            kernel=C(1.0, (1e-4, 1e4)) * RBF(1.0, (1e-4, 1e3)),
            alpha=1e-3,
            n_restarts_optimizer=1,
            normalize_y=True,
            optimizer="fmin_l_bfgs_b",
        )

    def optimize(self):
        """Run Bayesian optimization."""
        print(f"\n{'=' * 60}")
        print("Starting Bayesian optimization (performance-tuned)")
        print(f"Initial samples: {self.n_initial}")
        print(f"BO iterations: {self.n_iterations}")
        print(f"Candidates per iteration: {self.n_candidates_per_iter}")
        print(f"MC samples: {self.mc_samples}")
        print(f"Total evaluations: {self.n_initial + self.n_iterations}")
        print(f"{'=' * 60}\n")

        # Initial sampling
        print("Step 1: Initial random sampling...")
        X_train, Y_train = self._initial_sampling()

        # Set reference point
        if self.ref_point is None:
            self.ref_point = [
                np.max(Y_train[:, 0]) * 1.2,
                np.max(Y_train[:, 1]) * 1.2,
            ]
            print(
                f"Auto reference point: "
                f"[{self.ref_point[0]:.4f}, {self.ref_point[1]:.2f}]"
            )

        # Bayesian iterations
        print(f"\nStep 2: BO iterations ({self.n_iterations})...")

        for iteration in tqdm(range(self.n_iterations), desc="Optimization progress"):
            iter_start_time = time.time()

            # Data selection: Pareto front + random samples
            max_train_size = 600

            if len(X_train) > max_train_size:
                # Current Pareto front indices
                pareto_indices_temp = extract_pareto_front(Y_train)
                n_pareto = len(pareto_indices_temp)

                # Number of random samples needed
                n_random = max_train_size - n_pareto

                if n_random > 0:
                    # Randomly select non-Pareto points
                    non_pareto_indices = [
                        i for i in range(len(X_train)) if i not in pareto_indices_temp
                    ]
                    if len(non_pareto_indices) > n_random:
                        random_indices = np.random.choice(
                            non_pareto_indices,
                            size=n_random,
                            replace=False,
                        )
                        selected_indices = list(pareto_indices_temp) + list(random_indices)
                    else:
                        selected_indices = list(range(len(X_train)))
                else:
                    # If Pareto points exceed max_train_size, keep only Pareto points
                    selected_indices = pareto_indices_temp

                X_train_selected = X_train[selected_indices]
                Y_train_selected = Y_train[selected_indices]
            else:
                X_train_selected = X_train
                Y_train_selected = Y_train

            # Standardize input features
            X_train_scaled = self.scaler_X.fit_transform(X_train_selected)

            # Standardize targets (GP also normalizes, but external scaling helps)
            Y_obj1_scaled = self.scaler_obj1.fit_transform(
                Y_train_selected[:, 0].reshape(-1, 1)
            ).flatten()
            Y_obj2_scaled = self.scaler_obj2.fit_transform(
                Y_train_selected[:, 1].reshape(-1, 1)
            ).flatten()

            # Train GP (with error handling)
            gp_start = time.time()
            try:
                self.gp_obj1.fit(X_train_scaled, Y_obj1_scaled)
                self.gp_obj2.fit(X_train_scaled, Y_obj2_scaled)
            except Exception as e:
                tqdm.write(
                    f"Warning: GP training failed - {str(e)}; using previous model"
                )
            gp_time = time.time() - gp_start

            # Current Pareto front
            pareto_indices = extract_pareto_front(Y_train)
            pareto_front = Y_train[pareto_indices].tolist()

            # Find best candidate
            acq_start = time.time()
            best_candidate = self._find_best_candidate(X_train, pareto_front)
            acq_time = time.time() - acq_start

            # Evaluate new point
            eval_start = time.time()
            y_new = self._evaluate(best_candidate)
            eval_time = time.time() - eval_start

            # Append to training data
            X_train = np.vstack([X_train, best_candidate])
            Y_train = np.vstack([Y_train, y_new])

            iter_time = time.time() - iter_start_time

            # Log every 10 iterations
            if (iteration + 1) % 10 == 0:
                current_pareto = extract_pareto_front(Y_train)
                pareto_change = len(current_pareto) - len(pareto_indices)
                change_symbol = "+" if pareto_change > 0 else ""

                tqdm.write(
                    f"\nIter {iteration + 1}/{self.n_iterations}: "
                    f"Pareto front {len(current_pareto)} solutions "
                    f"({change_symbol}{pareto_change}) | "
                    f"Time: {iter_time:.1f}s "
                    f"(GP:{gp_time:.1f}s, ACQ:{acq_time:.1f}s, EVAL:{eval_time:.1f}s)"
                )

        # Final Pareto front
        print("\nStep 3: Extracting final Pareto front...")
        pareto_indices = extract_pareto_front(Y_train)
        X_pareto = X_train[pareto_indices]
        Y_pareto = Y_train[pareto_indices]

        print(
            f"Optimization complete! Pareto front has {len(pareto_indices)} solutions"
        )
        print("Objective ranges:")

        pareto_individuals = create_individuals_from_front(X_pareto, Y_pareto)
        return pareto_individuals

    def _initial_sampling(self):
        """Initial random sampling."""
        X_train = []
        Y_train = []

        for _ in tqdm(range(self.n_initial), desc="Initial sampling"):
            individual = self.problem.generate_individual()
            x = individual.features
            y = self._evaluate(x)
            X_train.append(x)
            Y_train.append(y)

        return np.array(X_train), np.array(Y_train)

    def _evaluate(self, x):
        """Evaluate objective values."""
        if self.problem.expand:
            obj_values = [f(*x) for f in self.problem.objectives]
        else:
            obj_values = [f(x) for f in self.problem.objectives]
        return obj_values

    def _find_best_candidate(self, X_train, pareto_front):
        """Find candidate with maximum EHVI (with verbose progress)."""
        evaluated_set = set(map(tuple, X_train))

        # Sample candidate points
        candidates = self._sample_candidates(evaluated_set)

        if len(candidates) == 0:
            print("Warning: no unevaluated candidates; selecting a random one")
            return self.problem.generate_individual().features

        candidates = np.array(candidates)

        # Standardize candidates (use same scaling as training)
        candidates_scaled = self.scaler_X.transform(candidates)

        # Batch GP prediction
        mu_obj1_scaled, sigma_obj1_scaled = self.gp_obj1.predict(
            candidates_scaled, return_std=True
        )
        mu_obj2_scaled, sigma_obj2_scaled = self.gp_obj2.predict(
            candidates_scaled, return_std=True
        )

        # Inverse transform
        mu_obj1 = self.scaler_obj1.inverse_transform(
            mu_obj1_scaled.reshape(-1, 1)
        ).flatten()
        mu_obj2 = self.scaler_obj2.inverse_transform(
            mu_obj2_scaled.reshape(-1, 1)
        ).flatten()

        sigma_obj1 = sigma_obj1_scaled * self.scaler_obj1.scale_[0]
        sigma_obj2 = sigma_obj2_scaled * self.scaler_obj2.scale_[0]

        # Compute EHVI
        best_ehvi = -np.inf
        best_idx = 0

        for i in range(len(candidates)):
            ehvi = monte_carlo_ehvi(
                mu_obj1[i],
                sigma_obj1[i],
                mu_obj2[i],
                sigma_obj2[i],
                pareto_front,
                self.ref_point,
                n_samples=self.mc_samples,
            )

            if ehvi > best_ehvi:
                best_ehvi = ehvi
                best_idx = i

        return candidates[best_idx]

    def _sample_candidates(self, evaluated_set):
        """Dynamically sample candidates to avoid pre-generating all points."""
        candidates = []
        max_attempts = self.n_candidates_per_iter * 10
        attempts = 0

        # Generate candidates on the fly
        while len(candidates) < self.n_candidates_per_iter and attempts < max_attempts:
            candidate = tuple(
                np.random.randint(
                    self.problem.variables_range[0][0],
                    self.problem.variables_range[0][1] + 1,
                )
                for _ in range(self.problem.num_of_variables)
            )

            # Check if already evaluated
            if candidate not in evaluated_set and candidate not in [tuple(c) for c in candidates]:
                candidates.append(list(candidate))

            attempts += 1

        if len(candidates) == 0:
            # As a fallback, generate one random candidate
            candidates = [
                [
                    np.random.randint(
                        self.problem.variables_range[0][0],
                        self.problem.variables_range[0][1] + 1,
                    )
                    for _ in range(self.problem.num_of_variables)
                ]
            ]

        return candidates
