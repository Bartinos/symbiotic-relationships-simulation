from mesa import Model
from mesa.datacollection import DataCollector
from mesa.experimental.devs import ABMSimulator
from mesa.discrete_space import OrthogonalMooreGrid
import math
import numpy as np
from agents import *


class SymbioticRelationshipsModel(Model):
    def __init__(
        self,
        grid_size=32,
        initial_frogs=10,
        # initial_spiders=10,
        initial_ants=10,
        initial_snakes=10,
        mutation_rate=0.5,
        nest_density=0.75,
        seed=None,
        rng=None,
        p_reproduce_ant=0.04,
        p_reproduce_snake=0.04,
        p_reproduce_frog=0.04,
        p_reproduce_spider=0.04,
        ant_spawn_rate = 2,
        simulator: ABMSimulator = None,
    ):
        super().__init__(seed=seed, rng=rng)
        self.ant_spawn_rate = ant_spawn_rate
        if simulator is None:
            simulator = ABMSimulator()

        self.simulator = simulator
        self.simulator.setup(self)

        self.height = grid_size
        self.width = grid_size
        nest_density = 1 - nest_density
        # Create grid using experimental cell space
        self.grid = OrthogonalMooreGrid(
            [self.height, self.width],
            torus=False,  # Decide upon this!?
            capacity=math.inf,  #
            random=self.random,
        )
        
        # Create nest zone mapping for tracking
        self.zones = {}

        self.spider_nests = {}
        self.spider_nest_size = 3

        margin = self.spider_nest_size  # distance from walls to keep free
        x0 = margin
        y0 = margin
        x1 = self.width - margin
        y1 = self.height - margin
        dx = int(self.width * nest_density)
        dy = int(self.height * nest_density)

        nest_count = 0

        for x in range(x0, x1, dx):
            for y in range(y0, y1, dy):
                nest_count += 1

                nx = x - self.spider_nest_size // 2
                ny = y - self.spider_nest_size // 2
                self.spider_nests[f"nest{nest_count}"] = (nx, ny)

        # self.spider_nests = {
        #               "nest1": (4, 4),
        #               "nest2": (4, 26),
        #               "nest3": (26, 4),
        #               "nest4": (26, 26),
        # }

        for cell in self.grid.all_cells.cells:
            x, y = cell.coordinate

            # Mark spider nests
            for nest_name, nest_location in self.spider_nests.items():
                start_nest_x = nest_location[0]
                end_nest_x = nest_location[0] + self.spider_nest_size
                start_nest_y = nest_location[1]
                end_nest_y = nest_location[1] + self.spider_nest_size
                if (
                    x >= start_nest_x
                    and x < end_nest_x
                    and y >= start_nest_y
                    and y < end_nest_y
                ):
                    self.zones[(x, y)] = nest_name

        # Spawn spiders on their nests
        for nest_name, nest_location in self.spider_nests.items():
            Spider.create_agents(
                self,
                1,  # Spider amount
                nest=(nest_name, nest_location),
                cell=self.random.choices(
                    [
                        cell
                        for cell in self.grid.all_cells.cells
                        if cell.coordinate[0] == nest_location[0] + 1
                        and cell.coordinate[1] == nest_location[1] + 1
                    ],
                    k=1,
                ),  # This can't be right btw,
                p_reproduce=p_reproduce_spider,
            )

        # Set up data collection
        model_reporters = {
            "Spiders": lambda m: len(m.agents_by_type[Spider]),
            "Frogs": lambda m: len(m.agents_by_type[Frog]),
            "Ants": lambda m: len(m.agents_by_type[Ant]),
            "Snakes": lambda m: len(m.agents_by_type[Snake]),
            "Spider_Symb_Val": lambda m: np.mean(
                np.fromiter(
                    (spider.symbiotic_property for spider in m.agents_by_type[Spider]),
                    dtype=float,
                )
            ),
            "Frog_Symb_Val": lambda m: np.mean(
                np.fromiter(
                    (frog.symbiotic_property for frog in m.agents_by_type[Frog]),
                    dtype=float,
                )
            ),
        }

        self.datacollector = DataCollector(model_reporters)

        Frog.create_agents(
            self,
            initial_frogs,  # frog amount
            cell=self.random.choices(self.grid.all_cells.cells, k=initial_frogs),
            p_reproduce=p_reproduce_frog,
        )

        Snake.create_agents(
            self,
            initial_snakes,  # Snake amount
            cell=self.random.choices(self.grid.all_cells.cells, k=initial_snakes),
            p_reproduce=p_reproduce_snake,
        )

        Ant.create_agents(
            self,
            initial_ants,  # Ant amount
            cell=self.random.choices(self.grid.all_cells.cells, k=initial_ants),
            p_reproduce=p_reproduce_ant,
        )

        # Egg.create_agents(
        #     self,
        #     1, # Ant amount
        #     cell=self.random.choices(self.grid.all_cells.cells, k=1),
        # )

        # Collect initial data
        self.running = True
        self.datacollector.collect(self)

    def get_zone_at(self, x, y):
        return self.zones.get((x, y), "unmarked")

    def step(self):
        """Execute one step of the model."""
        self.agents_by_type[Ant].shuffle_do("step")
        self.agents_by_type[Snake].shuffle_do("step")
        self.agents_by_type[Frog].shuffle_do("step")
        self.agents_by_type[Spider].shuffle_do("step")
        try:
            self.agents_by_type[Egg].shuffle_do("step")
        except:
            pass

        # Collect data
        self.datacollector.collect(self)

        # Spawn ants every 2 ticks
        if self.steps % 2 == 0:
            Ant.create_agents(
                self, self.ant_spawn_rate, cell=self.random.choices(self.grid.all_cells.cells, k=self.ant_spawn_rate)  # Ant amount
            )  # Might spawn at unlucky place (against nest), will that be a problem?!?!
       