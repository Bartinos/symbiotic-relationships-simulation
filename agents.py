from mesa.discrete_space import CellAgent, FixedAgent, CellCollection
import math

class Animal(CellAgent):
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0.0):
        super().__init__(model)
        self.cell = cell
        self.energy = initial_energy
        self.p_reproduce = p_reproduce
        self.energy_from_food = energy_from_food
        self.symbiotic_property = symbiotic_property
        self.mutation_chance = mutation_chance
        self.mutation_effectiveness = mutation_effectiveness
        
    def feed(self):
        """Abstract method to be implemented by subclasses."""
        
    def step(self):
        self.energy -= 1
        if self.energy <= 0:
            self.remove()
            return

        self.move()
        self.feed()
        
        if self.random.random() < self.p_reproduce:
            self.reproduce()
    
    def move(self):
        self.cell=self.cell.neighborhood.select_random_cell()
        
    def get_symbiotic_property_for_reproduce(self):
        return self.symbiotic_property + self.random.uniform(-self.mutation_effectiveness, self.mutation_effectiveness) if self.random.random() <= self.mutation_chance else self.symbiotic_property
        
    def reproduce(self):
        # """Abstract method to be implemented by subclasses."""
        self.energy /= 2
        self.__class__(
            model = self.model,
            initial_energy = self.energy,
            p_reproduce = self.p_reproduce,
            energy_from_food = self.energy_from_food,
            cell = self.cell,
            symbiotic_property = self.get_symbiotic_property_for_reproduce()
        )


        
class Frog(Animal):
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0):
        super().__init__(model, initial_energy, p_reproduce, energy_from_food, mutation_chance, mutation_effectiveness, cell, symbiotic_property)
        self.symbiotic_property = self.random.random()*2-1

    def feed(self):
        """If possible, eat an ant at current location."""
        ant = [obj for obj in self.cell.agents if isinstance(obj, Ant)]
        if ant:  # If there are any ant present
            ant_to_eat = self.random.choice(ant)
            self.energy += self.energy_from_food
            ant_to_eat.remove()
    
    def move(self):
        """
        Movement rules:
        1. If any neighboring cell (radius=1) has an ant → always move there.
        2. If no ants:
            - Roll chance based on symbiotic_property.
            - If success: find spiders in radius=2.
            - Move ONE STEP toward the nearest spider.
        3. Otherwise: random step to a radius=1 neighbor.
        """

        # 1) Check radius=1 for ants (normal Moore neighborhood) 
        neighbors_r1 = self.cell.get_neighborhood(radius=1).cells
        cells_with_ant = [
            cell for cell in neighbors_r1
            if any(isinstance(obj, Ant) for obj in cell.agents)
        ]

        if cells_with_ant:
            # Always choose one ant cell
            self.cell = self.random.choice(cells_with_ant)
            return


        # 2) No ants -> roll symbiotic chance 
        if self.symbiotic_property > 0:
            if self.random.random() < self.symbiotic_property:

                # radius=2 neighborhood for spider search
                neighbors_r2 = self.cell.get_neighborhood(radius=2).cells

                # Cells containing spiders
                spider_cells = [
                    cell for cell in neighbors_r2
                    if any(isinstance(obj, Spider) for obj in cell.agents)
                ]

                if len(spider_cells) > 0:
                    # Find nearest spider cell
                    fx, fy = self.cell.coordinate

                    def dist(cell):
                        x, y = cell.coordinate
                        return max(abs(x - fx), abs(y - fy))  # Chebyshev distance

                    target_spider_cell = spider_cells[0]
                    sx, sy = target_spider_cell.coordinate

                    # ONE-STEP movement toward spider
                    step_x = fx + (1 if sx > fx else -1 if sx < fx else 0)
                    step_y = fy + (1 if sy > fy else -1 if sy < fy else 0)

                    # Find the cell that corresponds to that coordinate
                    target_neighbor = next(
                        (c for c in neighbors_r1 if c.coordinate == (step_x, step_y)),
                        None
                    )

                    # Move if the step is valid
                    if target_neighbor:
                        self.cell = target_neighbor
                        return
        elif self.symbiotic_property < 0:
            if self.random.random() < (self.symbiotic_property * -1.0):

                # radius=2 neighborhood for spider search
                neighbors_r2 = self.cell.get_neighborhood(radius=2).cells

                # Cells containing spiders
                spider_cells = [
                    cell for cell in neighbors_r2
                    if any(isinstance(obj, Spider) for obj in cell.agents)
                ]

                if len(spider_cells) > 0:
                    # Find nearest spider cell
                    fx, fy = self.cell.coordinate

                    def dist(cell):
                        x, y = cell.coordinate
                        return max(abs(x - fx), abs(y - fy))  # Chebyshev distance

                    target_spider_cell = spider_cells[0]
                    sx, sy = target_spider_cell.coordinate

                    # ONE-STEP movement toward spider
                    step_x = fx + (-1 if sx > fx else 1 if sx < fx else 0)
                    step_y = fy + (-1 if sy > fy else 1 if sy < fy else 0)

                    # Find the cell that corresponds to that coordinate
                    target_neighbor = next(
                        (c for c in neighbors_r1 if c.coordinate == (step_x, step_y)),
                        None
                    )

                    # Move if the step is valid
                    if target_neighbor:
                        self.cell = target_neighbor
                        return


     # --- 3) Default random radius-1 movement ---
        self.cell = self.random.choice(neighbors_r1)

    # def reproduce(self):
        
    #     # self.energy /= 2
    #     self.__class__(
    #         model = self.model,
    #         initial_energy = self.energy,
    #         # self.p_reproduce,
    #         # self.energy_from_food,
    #         cell = self.cell,
    #     )
        

        
class Spider(Animal):
    def __init__(self, model, nest, initial_energy=50, p_reproduce=0.1, energy_from_food=50, cell=None, symbiotic_property = 0.5):
        super().__init__(model=model, 
                         initial_energy=initial_energy, 
                         p_reproduce=p_reproduce, 
                         energy_from_food=energy_from_food, 
                         cell=cell, 
                         symbiotic_property=symbiotic_property)
        self.nest = nest
        self.symbiotic_property = self.random.random()


    def feed(self):
        spider_hit_chance = 0.4
        """If possible, eat a snake at current location."""
        snake = [obj for obj in self.cell.agents if isinstance(obj, Snake)]
        if snake:  # If there are any snake present
            snake_to_eat = self.random.choice(snake)
            self.energy += self.energy_from_food
            snake_to_eat.remove()
            return
        
        ant = [obj for obj in self.cell.agents if isinstance(obj, Ant)]
        if ant and self.random.random() <= spider_hit_chance:  # If there are any ant present
            ant_to_eat = self.random.choice(ant)
            ant_to_eat.remove()
            return
        
        # frog = [obj for obj in self.cell.agents if isinstance(obj, Frog)]
        # if frog and self.random.random() <= self.symbiotic_property:  # If there are any frog present
        #     frog_to_eat = self.random.choice(frog)
        #     self.energy += 1 #might want to change this value later on
        #     frog_to_eat.remove()
        

    def move(self):
        spider_to_ant_chance = 0.50
        """Move to a neighboring cell, preferably one with frog."""
        cells_with_snake = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Snake) for obj in cell.agents)
        )
        cells_with_ant = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Ant) for obj in cell.agents)
        )
        cells_with_frog = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Frog) for obj in cell.agents)
        )
        explore_factor = 15.0 # Change this value if desired, larger -> more tendency to move away from nest
        target_cells = None
        if len(cells_with_snake) > 0:
            target_cells = cells_with_snake
        elif self.random.random() <= spider_to_ant_chance and len(cells_with_ant) > 0:
            target_cells = cells_with_ant
        elif self.random.random() <= self.symbiotic_property and len(cells_with_frog) > 0:
            target_cells = cells_with_frog
        elif math.dist(self.cell.coordinate, self.get_nest_center()) / explore_factor > self.random.random():
            target_cells = self.determine_cells_to_return()
        else:
            target_cells = self.cell.neighborhood
            
        self.cell = target_cells.select_random_cell()
    
    def get_nest_center(self):
        
        return (self.nest[1][0] + 1, self.nest[1][1] + 1) # This assumes the nest location + 1 is the center of the nest, should be dynamically retrieved based on the nest_size

    def determine_cells_to_return(self):
        destination = self.get_nest_center()
        current_location = self.cell.coordinate
        delta = (destination[0] - current_location[0] , destination[1] - current_location[1]) # Use delta to estimate direction of nest
        
        neighbors_cells = self.cell.neighborhood.cells        
        target_cells = None
        
        # Neighborhood indexing for cursed code:
        # 2 4 7
        # 1 X 6
        # 0 3 5
        if (delta[0] == 0 and delta[1] == 0) or current_location[0] == 0 or current_location[0] == self.model.width-1 or current_location[1] == 0 or current_location[1] == self.model.height-1:  
            # Else we get delta (0, 0) meaning we are located at the nest or if we are at the boundary, just load new neighbors
            target_cells = CellCollection(neighbors_cells)                       
        elif delta[0] < 0 and delta[1] < 0: # LEFT DOWN
            target_cells = CellCollection([neighbors_cells[0], neighbors_cells[1], neighbors_cells[3]])
        elif delta[0] < 0 and delta[1] > 0: # LEFT UP
            target_cells = CellCollection([neighbors_cells[1], neighbors_cells[2], neighbors_cells[4]])
        elif delta[0] > 0 and delta[1] > 0: # RIGHT UP           
            target_cells = CellCollection([neighbors_cells[4], neighbors_cells[7], neighbors_cells[6]])
        elif delta[0] > 0 and delta[1] < 0: # RIGHT DOWN
            target_cells = CellCollection([neighbors_cells[6], neighbors_cells[5], neighbors_cells[3]])
        elif delta[0] == 0 and delta[1] > 0: # UP
            target_cells = CellCollection([neighbors_cells[2], neighbors_cells[4], neighbors_cells[7]])
        elif delta[0] == 0 and delta[1] < 0: # DOWN
            target_cells = CellCollection([neighbors_cells[0], neighbors_cells[5], neighbors_cells[3]])        
        elif delta[0] < 0 and delta[1] == 0: # LEFT
            target_cells = CellCollection([neighbors_cells[0], neighbors_cells[1], neighbors_cells[2]])
        elif delta[0] > 0 and delta[1] == 0: # RIGHT
            target_cells = CellCollection([neighbors_cells[7], neighbors_cells[6], neighbors_cells[5]]) 
        return target_cells
        

    def reproduce(self):
        if "nest" not in self.model.get_zone_at(self.cell.coordinate[0], self.cell.coordinate[1]):
            return
        
        cells_with_egg = self.cell.get_neighborhood(radius=2).select(
            lambda cell: any(isinstance(obj, Egg) for obj in cell.agents)
        )
        
        eggs_in_nest_amount = len(cells_with_egg.cells)
        max_eggs_in_nest = 16 # Tweak?
        
        if eggs_in_nest_amount < max_eggs_in_nest and len([egg for egg in self.cell.agents if isinstance(egg, Egg)]) == 0:
            Egg.create_agents(
                self.model,
                1,
                cell=self.cell,
                nest = self.nest,
                symbiotic_property = self.get_symbiotic_property_for_reproduce()
                )

class Ant(Animal):
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0):
        super().__init__(model, initial_energy, p_reproduce, energy_from_food, mutation_chance, mutation_effectiveness, cell, symbiotic_property)
    
    def move(self):
        cells_with_egg = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Egg) for obj in cell.agents)
        )
        target_cells = (
            cells_with_egg if len(cells_with_egg) > 0 else self.cell.neighborhood
        )
        self.cell = target_cells.select_random_cell()
    
    
class Snake(Animal):
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0):
        super().__init__(model, initial_energy, p_reproduce, energy_from_food, mutation_chance, mutation_effectiveness, cell, symbiotic_property)
    
    def feed(self):
        """If possible, eat a frog at current location."""
        frog = [obj for obj in self.cell.agents if isinstance(obj, Frog)]
        if frog:  # If there are any frog present
            frog_to_eat = self.random.choice(frog)
            self.energy += self.energy_from_food
            frog_to_eat.remove()

    def move(self):
        """Move to a neighboring cell, preferably one with frog."""
        cells_with_sheep = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Frog) for obj in cell.agents)
        )
        target_cells = (
            cells_with_sheep if len(cells_with_sheep) > 0 else self.cell.neighborhood
        )
        self.cell = target_cells.select_random_cell()

class Egg(CellAgent):
    def __init__(self, model, nest,symbiotic_property, cell=None , hp = 5):
        super().__init__(model)
        self.cell = cell
        self.hp = hp
        self.egg_placement_step = self.model.steps
        self.nest = nest
        self.symbiotic_property = symbiotic_property

    def step(self):
        if self.is_ant_nearby():
            self.hp -= 1
        if self.hp <= 0:
            self.remove() 
        if self.model.steps - self.egg_placement_step >= 5 and self.hp > 0:
            self.hatch()
            self.remove()
            pass

    def is_ant_nearby(self):
        nearby_ants = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Ant) for obj in cell.agents))
        return len(nearby_ants) > 0

    def hatch(self):
        # nest_key = self.model.get_zone_at(self.cell.coordinate[0], self.cell.coordinate[1])
        # nest = self.model.zones.get(nest_key)
        Spider.create_agents(
                self.model,
                1, # Ant amount
                cell=self.cell,
                symbiotic_property = self.symbiotic_property,
                nest =self.nest)

 