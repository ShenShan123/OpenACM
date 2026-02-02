"""
MOEAD genetic algorithm utilities.
"""

import random

import numpy as np

from moead_utils import cpt_tchbycheff


def discrete_crossover(moead, parent1_features, parent2_features):
    """
    Single-point crossover for discrete variables.
    Returns two children.
    """
    var_num = len(parent1_features)
    child1 = parent1_features[:]
    child2 = parent2_features[:]

    if random.random() < 0.9:
        point = random.randint(1, var_num - 1)
        child1 = parent1_features[:point] + parent2_features[point:]
        child2 = parent2_features[:point] + parent1_features[point:]

    return child1, child2


def discrete_mutation(moead, individual_features):
    """
    Random mutation for discrete variables.
    Uses 1/var_num mutation rate per variable.
    """
    var_num = len(individual_features)
    mutated = individual_features[:]

    mutation_rate = 1.0 / var_num

    for i in range(var_num):
        if random.random() < mutation_rate:
            low, high = moead.problem.variables_range[i]
            current_value = mutated[i]
            candidates = [v for v in range(int(low), int(high) + 1) if v != current_value]
            if candidates:
                mutated[i] = random.choice(candidates)
            else:
                mutated[i] = int(current_value)

    for i in range(var_num):
        low, high = moead.problem.variables_range[i]
        if mutated[i] < low:
            mutated[i] = int(low)
        elif mutated[i] > high:
            mutated[i] = int(high)

    return mutated


def generate_offspring(moead, gen, wi, parent_idx1, parent_idx2):
    """
    Generate one offspring.

    Args:
        gen: current generation index
        wi: weight vector index
        parent_idx1, parent_idx2: parent indices

    Returns:
        A new offspring individual.
    """
    # Get parent individuals
    p1 = moead.Pop[parent_idx1]
    p2 = moead.Pop[parent_idx2]

    # Crossover: create two children, randomly pick one
    child1_features, child2_features = discrete_crossover(moead, p1.features, p2.features)

    # Randomly select one child
    child_features = child1_features if random.random() < 0.5 else child2_features

    # Mutation
    child_features = discrete_mutation(moead, child_features)

    # Create child individual object
    child = moead.problem.generate_individual()
    child.features = child_features
    moead.problem.calculate_objectives(child)

    return child


def envolution(moead):
    """
    Main MOEAD evolution loop.
    """
    from moead_utils import update_Z, update_BTX, update_EP_By_Individual
    from tqdm import tqdm

    print("\nStarting MOEAD optimization...")
    print(
        f"Population size: {moead.Pop_size}, "
        f"Generations: {moead.max_gen}, "
        f"Neighborhood size: {moead.T_size}"
    )
    print("-" * 70)

    # Use tqdm progress bar
    for gen in tqdm(range(moead.max_gen), desc="Evolution progress"):
        moead.gen = gen

        # Evolve each individual
        for pi in range(moead.Pop_size):
            # Neighborhood of individual pi
            Bi = moead.W_Bi_T[pi]

            # Randomly select two different indices from neighbors (per MOEAD paper)
            k = random.randint(0, moead.T_size - 1)
            l = random.randint(0, moead.T_size - 1)
            while l == k:
                l = random.randint(0, moead.T_size - 1)

            ik = Bi[k]
            il = Bi[l]

            # Step 2.1) Reproduction: generate new solution y (use neighbors x_k and x_l)
            new_individual = generate_offspring(moead, gen, pi, ik, il)

            # Step 2.2) Improvement: repair/improve (handled in crossover/mutation for discrete vars)

            # Step 2.3) Update z: update reference point (unconditional, per paper)
            update_Z(moead, new_individual)

            # Step 2.4) Update neighboring solutions
            # For each j in B(i): if g_te(y|lambda_j,z) <= g_te(x_j|lambda_j,z), then x_j = y
            update_BTX(moead, Bi, new_individual)

            # Step 2.5) Update EP: update Pareto front (unconditional; dominance check inside)
            update_EP_By_Individual(moead, pi, new_individual)

        # Log every 10 generations
        if (gen + 1) % 10 == 0 or gen == 0:
            tqdm.write(
                "Iter {:4d}/{}, Pareto: {:3d} solutions, Z: [{:.6f}, {:.6f}]".format(
                    gen + 1,
                    moead.max_gen,
                    len(moead.EP_X_ID),
                    moead.Z[0],
                    moead.Z[1],
                )
            )
    print("\n" + "-" * 70)
    print(f"Optimization complete! Final Pareto front: {len(moead.EP_X_ID)} solutions")

    return moead.EP_X_ID
