from utils import NSGA2Utils
from population import Population
from tqdm import tqdm


class Evolution:
    def __init__(
        self,
        problem,
        num_of_generations=1000,
        num_of_individuals=100,
        num_of_tour_particips=2,
        tournament_prob=0.9,
        crossover_param=2,
        mutation_param=5,
    ):
        self.utils = NSGA2Utils(
            problem,
            num_of_individuals,
            num_of_tour_particips,
            tournament_prob,
            crossover_param,
            mutation_param,
        )
        self.population = None
        self.num_of_generations = num_of_generations
        self.on_generation_finished = []
        self.num_of_individuals = num_of_individuals

    def evolve(self):
        print("\n" + "=" * 70)
        print("Starting NSGA-II optimization...")
        print(
            f"Population size: {self.num_of_individuals}, "
            f"Generations: {self.num_of_generations}"
        )
        print(
            f"Tournament params: {self.utils.num_of_tour_particips}, "
            f"Crossover: {self.utils.crossover_param}, "
            f"Mutation: {self.utils.mutation_param}"
        )
        print("=" * 70)

        self.population = self.utils.create_initial_population()
        self.utils.fast_nondominated_sort(self.population)
        for front in self.population.fronts:
            self.utils.calculate_crowding_distance(front)
        children = self.utils.create_children(self.population)
        returned_population = None

        print("\nStarting evolution iterations...")
        print("-" * 70)

        for i in tqdm(range(self.num_of_generations), desc="Evolution progress"):
            self.population.extend(children)
            self.utils.fast_nondominated_sort(self.population)
            new_population = Population()
            front_num = 0
            while (
                len(new_population) + len(self.population.fronts[front_num])
                <= self.num_of_individuals
            ):
                self.utils.calculate_crowding_distance(self.population.fronts[front_num])
                new_population.extend(self.population.fronts[front_num])
                front_num += 1
            self.utils.calculate_crowding_distance(self.population.fronts[front_num])
            self.population.fronts[front_num].sort(
                key=lambda individual: individual.crowding_distance,
                reverse=True,
            )
            new_population.extend(
                self.population.fronts[front_num][
                    0 : self.num_of_individuals - len(new_population)
                ]
            )
            returned_population = self.population
            self.population = new_population
            self.utils.fast_nondominated_sort(self.population)
            for front in self.population.fronts:
                self.utils.calculate_crowding_distance(front)
            children = self.utils.create_children(self.population)

            # Log every 10 generations
            if (i + 1) % 10 == 0 or i == 0:
                pareto_front = self.population.fronts[0]
                if len(pareto_front) > 0:
                    tqdm.write(
                        "Iter {:4d}/{}, Pareto: {:3d} solutions".format(
                            i + 1,
                            self.num_of_generations,
                            len(pareto_front),
                        )
                    )
        print("\n" + "-" * 70)
        print(
            f"Optimization complete! Final Pareto front: "
            f"{len(returned_population.fronts[0])} solutions"
        )
        print("=" * 70)

        return returned_population.fronts[0]
