"""
MOEAD optimizer for the multiplier problem.
Based on MOEAD-master/src/MOEAD_Main.py.
"""

import os
import time

import matplotlib
import matplotlib.pyplot as plt

from problem import Problem
from moead_utils import Load_W, cpt_W_Bi_T, Creat_Pop, cpt_Z, init_EP
from moead_ga_utils import envolution

matplotlib.use("Agg")  # Non-interactive backend


class MOEAD:
    """
    MOEAD algorithm class.
    Parameter parity with NSGA-II: 800 individuals, 1200 generations.
    """

    def __init__(self, problem, h=799, max_gen=1200, T_size=20, name="multiplier"):
        """
        Args:
            problem: Problem object defining the optimization task.
            h: divisions (generates h+1 weight vectors for 2 objectives)
            max_gen: max generations
            T_size: neighborhood size
            name: problem name used in weight file naming
        """
        self.problem = problem
        self.name = name
        self.h = h
        self.max_gen = max_gen
        self.T_size = T_size

        # Population
        self.Pop_size = -1  # Determined by number of weight vectors
        self.Pop = []  # Population of Individual objects

        # Weight vectors and neighborhood
        self.W = []  # Weight vector matrix
        self.W_Bi_T = []  # T neighbors for each weight vector

        # Reference point
        self.Z = []  # Ideal point

        # Pareto front
        self.EP_X_ID = []  # Indices of Pareto front individuals
        self.EP_X_FV = []  # Objective values of Pareto front individuals

        # Weight file path (module-relative to avoid cwd dependence)
        self.csv_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "vector_csv_file",
        )

        # Current generation
        self.gen = 0

        print("=" * 70)
        print("MOEAD optimizer initialized")
        print(f"Problem: {name}")
        print(f"Objectives: {problem.num_of_objectives}")
        print(f"Weight divisions H: {h} (will generate {h + 1} vectors)")
        print(f"Max generations: {max_gen}")
        print(f"Neighborhood size: {T_size}")
        print("=" * 70)

    def Init_data(self):
        """Initialize data structures."""
        print("\nInitializing MOEAD data structures...")

        # 1. Load or generate weight vectors
        Load_W(self)

        # 2. Compute neighborhoods
        cpt_W_Bi_T(self)

        # 3. Create initial population
        Creat_Pop(self)

        # 4. Initialize reference point Z
        cpt_Z(self)

        # 5. Initialize Pareto front
        init_EP(self)

        print("Initialization complete.\n")

    def run(self):
        """Run MOEAD optimization."""
        t = time.time()

        # Initialize
        self.Init_data()

        # Evolve
        EP_X_ID = envolution(self)

        dt = time.time() - t

        print(f"\nTotal time: {dt:.2f}s ({dt / 60:.2f} min)")

        return EP_X_ID

    def get_pareto_front(self):
        """
        Get Pareto front solutions.
        Returns: (states_list, objectives_list)
        """
        states = []
        objectives = []

        for idx in self.EP_X_ID:
            individual = self.Pop[idx]
            states.append(individual.features[:])
            objectives.append(individual.objectives[:])

        return states, objectives

    def save_results(self, output_file="moead_pareto_solutions.txt"):
        """Save Pareto front results."""
        states, objectives = self.get_pareto_front()

        with open(output_file, "w") as f:
            for state, obj in zip(states, objectives):
                state_str = ",".join(map(str, state))
                f.write(f"{state_str}\t{obj[0]:.6f}\t{obj[1]:.6f}\n")

        print(f"\nPareto front saved to: {output_file}")
        print(f"Total solutions: {len(states)}")

    def plot_pareto_front(self, output_file="moead_pareto_front.png"):
        """Plot Pareto front."""
        states, objectives = self.get_pareto_front()

        if len(objectives) == 0:
            print("Warning: Pareto front is empty; cannot plot.")
            return

        # Extract two objectives
        obj1_values = [obj[0] for obj in objectives]
        obj2_values = [obj[1] for obj in objectives]

        plt.figure(figsize=(10, 8))
        plt.scatter(obj2_values, obj1_values, alpha=0.6, edgecolor="k", s=50)
        plt.xlabel("PDP (Delay * Power * 1e6)", fontsize=12)
        plt.ylabel("MRED (Mean Relative Error Distance)", fontsize=12)
        plt.title(f"MOEAD Pareto Front (Generation {self.max_gen})", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()

        print(f"Pareto front plot saved to: {output_file}")
