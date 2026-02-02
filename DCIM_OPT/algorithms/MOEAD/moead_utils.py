"""
MOEAD utility functions.
Adapted for discrete variable optimization.
"""

import os
import random
from math import sqrt

import numpy as np


def Load_W(moead):
    """Load weight vectors."""
    file = moead.name + ".csv"
    path = os.path.join(moead.csv_file_path, file)
    if not os.path.exists(path):
        print(f"Weight file not found: {path}")
        from moead_mean_vector import Mean_vector

        mv = Mean_vector(moead.h, moead.problem.num_of_objectives, path)
        mv.generate()
        print(f"Generated weight file: {path}")
    W = np.loadtxt(fname=path, delimiter=",")
    moead.Pop_size = W.shape[0]
    moead.W = W
    print(f"Loaded weight vectors: {W.shape[0]}")
    return W


def cpt_Z(moead):
    """Initialize reference point Z (large values for minimization)."""
    Z = []
    for _ in range(moead.problem.num_of_objectives):
        z_i = 1e10
        Z.append(z_i)
    moead.Z = Z
    return Z


def update_Z(moead, individual):
    """Update reference point Z with a new individual."""
    objectives = individual.objectives
    for j in range(moead.problem.num_of_objectives):
        if objectives[j] < moead.Z[j]:
            moead.Z[j] = objectives[j]


def cpt_W_Bi_T(moead):
    """Compute T nearest neighbors for each weight vector."""
    if moead.T_size < 1:
        return -1
    for bi in range(moead.W.shape[0]):
        Bi = moead.W[bi]
        # Euclidean distance
        DIS = np.sum((moead.W - Bi) ** 2, axis=1)
        # Find nearest T neighbors (excluding itself)
        B_T = np.argsort(DIS)
        B_T = B_T[1 : moead.T_size + 1]
        moead.W_Bi_T.append(B_T)
    print(f"Neighborhood computed; each individual has {moead.T_size} neighbors")


def Tchebycheff_dist(w, f, z):
    """Tchebycheff distance."""
    return w * abs(f - z)


def cpt_tchbycheff(moead, idx, individual):
    """
    Compute Tchebycheff scalarization value.
    idx: individual index in population (weight vector index)
    individual: Individual object
    """
    max_val = -1e10
    ri = moead.W[idx]
    F_X = individual.objectives

    for i in range(moead.problem.num_of_objectives):
        fi = Tchebycheff_dist(ri[i], F_X[i], moead.Z[i])
        if fi > max_val:
            max_val = fi
    return max_val


def update_BTX(moead, P_B, new_individual):
    """Update individuals in the neighborhood using the new individual."""
    for j in P_B:
        old_individual = moead.Pop[j]
        d_old = cpt_tchbycheff(moead, j, old_individual)
        d_new = cpt_tchbycheff(moead, j, new_individual)

        if d_new < d_old:
            # Replace with the new individual
            moead.Pop[j].features = new_individual.features[:]
            moead.Pop[j].objectives = new_individual.objectives[:]
            update_EP_By_ID(moead, j, new_individual.objectives)


def is_dominate(objectives1, objectives2):
    """
    Check if objectives1 dominates objectives2 (minimization).
    Dominates: no worse in all objectives and better in at least one.
    """
    better_in_any = False
    for f1, f2 in zip(objectives1, objectives2):
        if f1 > f2:
            return False
        if f1 < f2:
            better_in_any = True
    return better_in_any


def init_EP(moead):
    """Initialize Pareto front."""
    for pi in range(moead.Pop_size):
        individual = moead.Pop[pi]
        is_pareto = True

        for ppi in range(moead.Pop_size):
            if pi != ppi:
                other_individual = moead.Pop[ppi]
                if is_dominate(other_individual.objectives, individual.objectives):
                    is_pareto = False
                    break

        if is_pareto:
            moead.EP_X_ID.append(pi)
            moead.EP_X_FV.append(individual.objectives[:])
    print(f"Initial Pareto front: {len(moead.EP_X_ID)} solutions")


def update_EP_By_ID(moead, id, objectives):
    """If id is in EP, update its objective values."""
    if id in moead.EP_X_ID:
        position_pi = moead.EP_X_ID.index(id)
        moead.EP_X_FV[position_pi][:] = objectives[:]


def update_EP_By_Individual(moead, id_new, new_individual):
    """
    Update Pareto front based on a new individual (paper Step 2.5 + discrete tweaks).
    - Remove all EP vectors dominated by F(y').
    - If no EP vector dominates F(y'), add F(y') to EP.
    - For discrete problems, check for near-duplicate objective values.
    """
    objectives_new = new_individual.objectives
    features_new = new_individual.features

    # 1. Check if dominated by existing EP
    dominated_by_ep = False
    for ep_obj in moead.EP_X_FV:
        if is_dominate(ep_obj, objectives_new):
            dominated_by_ep = True
            break

    if dominated_by_ep:
        return

    # 2. Check for near-duplicate objective values (discrete-specific)
    # Use adaptive epsilon in normalized objective space
    epsilon = 0.001
    for ep_obj in moead.EP_X_FV:
        dist = ((ep_obj[0] - objectives_new[0]) ** 2 + (ep_obj[1] - objectives_new[1]) ** 2) ** 0.5
        if dist < epsilon:
            return

    # 3. Remove EP solutions dominated by the new one
    new_EP_X_ID = []
    new_EP_X_FV = []
    for i in range(len(moead.EP_X_ID)):
        if not is_dominate(objectives_new, moead.EP_X_FV[i]):
            new_EP_X_ID.append(moead.EP_X_ID[i])
            new_EP_X_FV.append(moead.EP_X_FV[i])

    moead.EP_X_ID = new_EP_X_ID
    moead.EP_X_FV = new_EP_X_FV

    # 4. Add new solution to EP
    moead.EP_X_ID.append(id_new)
    moead.EP_X_FV.append(objectives_new[:])


def Creat_Pop(moead):
    """Create initial population using the Problem class."""
    Pop = []
    print(f"Generating initial population: {moead.Pop_size} individuals...")

    for i in range(moead.Pop_size):
        individual = moead.problem.generate_individual()
        moead.problem.calculate_objectives(individual)
        Pop.append(individual)

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{moead.Pop_size}")

    moead.Pop = Pop
    print("Initial population generated")
    return Pop
