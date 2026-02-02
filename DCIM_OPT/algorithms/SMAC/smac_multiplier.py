"""
Generic SMAC optimizer wrapper.

- Uses the provided Problem instance for objectives and variable ranges.
- Does not depend on GNN or multiplier-specific logic.
"""

from ConfigSpace import Configuration, ConfigurationSpace
import ConfigSpace.hyperparameters as CSH
from smac import HyperparameterOptimizationFacade, Scenario


class MultiplierSMACOptimizer:
    """
    Generic SMAC optimizer that works with any Problem.
    """

    def __init__(self, problem, max_trials=400, seed=42, aggregate_fn=None):
        self.problem = problem
        self.max_trials = max_trials
        self.seed = seed
        self.aggregate_fn = aggregate_fn
        self.cs = self._build_config_space()
        self.history = []
        self.best_state = None
        self.best_score = float("inf")
        self.best_objectives = None

    def _build_config_space(self):
        cs = ConfigurationSpace()
        for idx, (low, high) in enumerate(self.problem.variables_range):
            hp = CSH.UniformIntegerHyperparameter(
                f"x_{idx}",
                int(low),
                int(high),
                default_value=int((low + high) // 2),
            )
            cs.add_hyperparameter(hp)
        return cs

    def _config_to_state(self, config: Configuration):
        return [int(config[f"x_{i}"]) for i in range(self.problem.num_of_variables)]

    def _aggregate_objectives(self, objectives):
        if self.aggregate_fn is not None:
            return self.aggregate_fn(objectives)
        return sum(objectives) / len(objectives)

    def objective(self, config: Configuration, seed: int = 0) -> float:
        state = self._config_to_state(config)
        obj_values = [f(state) for f in self.problem.objectives]
        score = self._aggregate_objectives(obj_values)

        self.history.append(
            {
                "iteration": len(self.history),
                "state": state,
                "objectives": obj_values,
                "score": score,
            }
        )

        if score < self.best_score:
            self.best_score = score
            self.best_state = state[:]
            self.best_objectives = obj_values[:]

        return score

    def _pareto_filter(self, history):
        """Filter history to non-dominated solutions (minimize all objectives)."""
        def is_dominated(a, b):
            return (b[0] <= a[0] and b[1] <= a[1]) and (b[0] < a[0] or b[1] < a[1])

        pareto_entries = []
        for i, entry in enumerate(history):
            dominated = False
            for j, other in enumerate(history):
                if i == j:
                    continue
                if is_dominated(entry["objectives"], other["objectives"]):
                    dominated = True
                    break
            if not dominated:
                pareto_entries.append(entry)
        return pareto_entries

    def run(self, run_dir: str):
        scenario = Scenario(
            configspace=self.cs,
            deterministic=True,
            n_trials=self.max_trials,
            seed=self.seed,
            output_directory=run_dir,
        )

        smac = HyperparameterOptimizationFacade(
            scenario,
            self.objective,
            dask_client=None,
        )

        smac.optimize()
        pareto_history = self._pareto_filter(self.history)
        return self.best_state, self.best_objectives, pareto_history
