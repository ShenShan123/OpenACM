import numpy as np
from individual import Individual


def extract_pareto_front(Y_train):
    """
    Extract the Pareto front from objective values.
    Returns: indices of Pareto-optimal solutions.
    """
    n = len(Y_train)
    pareto_front_indices = []

    for i in range(n):
        is_dominated = False
        for j in range(n):
            if i == j:
                continue
            # Check if i is dominated by j (bi-objective minimization)
            if (
                Y_train[j][0] <= Y_train[i][0]
                and Y_train[j][1] <= Y_train[i][1]
                and (Y_train[j][0] < Y_train[i][0] or Y_train[j][1] < Y_train[i][1])
            ):
                is_dominated = True
                break

        if not is_dominated:
            pareto_front_indices.append(i)

    return pareto_front_indices


def dominates(y1, y2):
    """
    Check if y1 dominates y2 (bi-objective minimization).
    """
    return (
        y1[0] <= y2[0]
        and y1[1] <= y2[1]
        and (y1[0] < y2[0] or y1[1] < y2[1])
    )


def compute_hypervolume_2d(pareto_front, ref_point):
    """
    Compute 2D hypervolume.
    """
    if len(pareto_front) == 0:
        return 0.0

    # Sort by the first objective
    sorted_front = sorted(pareto_front, key=lambda x: x[0])

    hv = 0.0
    prev_y = ref_point[1]

    for point in sorted_front:
        if point[0] < ref_point[0] and point[1] < ref_point[1]:
            width = ref_point[0] - point[0]
            height = prev_y - point[1]
            hv += width * height
            prev_y = point[1]

    return hv


def compute_hypervolume_improvement(new_point, pareto_front, ref_point):
    """
    Compute hypervolume improvement after adding a new point.
    """
    # Check if the new point is within the reference point bounds
    if new_point[0] >= ref_point[0] or new_point[1] >= ref_point[1]:
        return 0.0

    # Check if the new point is dominated by the current front
    for pf_point in pareto_front:
        if dominates(pf_point, new_point):
            return 0.0

    # Compute current hypervolume
    hv_old = compute_hypervolume_2d(pareto_front, ref_point)

    # Build new front (add point and remove dominated points)
    new_front = [new_point]
    for pf_point in pareto_front:
        if not dominates(new_point, pf_point):
            new_front.append(pf_point)

    # Compute new hypervolume
    hv_new = compute_hypervolume_2d(new_front, ref_point)

    return max(0.0, hv_new - hv_old)


def monte_carlo_ehvi(
    mu_mred,
    sigma_mred,
    mu_pdp,
    sigma_pdp,
    pareto_front,
    ref_point,
    n_samples=200,
):
    """
    Monte Carlo estimate of expected hypervolume improvement (EHVI).

    Args:
        n_samples: number of Monte Carlo samples (default 200)

    Returns:
        Expected hypervolume improvement.
    """
    improvements = []

    for _ in range(n_samples):
        # Sample from GP predictive distribution
        sample_mred = np.random.normal(mu_mred, sigma_mred)
        sample_pdp = np.random.normal(mu_pdp, sigma_pdp)

        # Compute hypervolume improvement for this sample
        improvement = compute_hypervolume_improvement(
            [sample_mred, sample_pdp],
            pareto_front,
            ref_point,
        )
        improvements.append(improvement)

    return np.mean(improvements)


def create_individuals_from_front(X_front, Y_front):
    """
    Convert Pareto front arrays to a list of Individual objects.

    Args:
        X_front: array of shape (n, 9), design variables

    Returns:
        List of Individual objects.
    """
    individuals = []
    for i in range(len(X_front)):
        ind = Individual()
        ind.features = list(X_front[i])
        ind.objectives = list(Y_front[i])
        individuals.append(ind)
    return individuals
