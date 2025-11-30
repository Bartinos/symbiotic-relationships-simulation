from mesa.discrete_space import CellAgent, FixedAgent, CellCollection
import math

class Animal(CellAgent): #We initalise an Animal class, which inherits from Mesa's CellAgent, which will be given to all of our Animal subclasses
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0.0):
        super().__init__(model)
        self.cell = cell    #We set properties for our subclasses
        self.energy = initial_energy
        self.p_reproduce = p_reproduce
        self.energy_from_food = energy_from_food
        self.symbiotic_property = symbiotic_property
        self.mutation_chance = mutation_chance
        self.mutation_effectiveness = mutation_effectiveness
        
    def feed(self):
        """Abstract method to be implemented by subclasses."""
        
    def step(self): #These are the basic steps all of the subclasses follow, 
        self.energy -= 1 #All of our subclasses start with 50 total energy by default and lose 1 energy each step
        if self.energy <= 0:
            self.remove() #The agent gets removed when they have no energy left
            return

        self.move() #The Agents have a move function which make them able to move around the grid
        self.feed() #They also have a feed function which replenishes their total energy
        
        if self.random.random() < self.p_reproduce: #All of our subclasses also have a p_reproduce, the higher the p_reproduce the higher the chance of reproduction
            self.reproduce()
    
    def move(self): #All of our subclasses are able to move around on the grid, some with specific conditions
        self.cell=self.cell.neighborhood.select_random_cell()
        
    def get_symbiotic_property_for_reproduce(self): #This function changes the symbiotic property value of the newly hatched agent based on the symbiotic property value of the parent
        return self.symbiotic_property + self.random.uniform(-self.mutation_effectiveness, self.mutation_effectiveness) if self.random.random() <= self.mutation_chance else self.symbiotic_property
        
    def reproduce(self): #This is the reproduction function which is the default way of creating agents for our subclasses 
        self.energy /= 2 #We halve the energy so we don't get overrun by agents
        self.__class__( 
            model = self.model,
            initial_energy = self.energy,
            p_reproduce = self.p_reproduce,
            energy_from_food = self.energy_from_food,
            cell = self.cell,
            symbiotic_property = self.get_symbiotic_property_for_reproduce()
        )
        
class Spider(Animal): #We initialise the Spider class which inherits from the Animal class
    def __init__(self, model, nest, initial_energy=50, p_reproduce=0.1, energy_from_food=50, cell=None, symbiotic_property = 0.5):
        super().__init__(model=model, 
                         initial_energy=initial_energy, 
                         p_reproduce=p_reproduce, 
                         energy_from_food=energy_from_food, 
                         cell=cell, 
                         symbiotic_property=symbiotic_property)
        self.nest = nest #it creates a nest property since it will be linked to the nest
        #self.symbiotic_property = self.random.random()


    def feed(self): #the spider has a costum feed feature, it is the only class that can eat two different agents
        spider_hit_chance = 0.4 #the chance of hitting the ant, this is low since we want to motivate the frogs being close to the spiders to help with protecting the eggs
        """If possible, eat a snake at current location."""
        snake = [obj for obj in self.cell.agents if isinstance(obj, Snake)]
        if snake:  # If there are any snake present
            snake_to_eat = self.random.choice(snake)#Eats the snake
            self.energy += self.energy_from_food#Receives energy
            snake_to_eat.remove()#Snake gets deleted
            return #We return so in the event of a snake and an ant being stacked on one grid cell the spider can't eat them both
        
        ant = [obj for obj in self.cell.agents if isinstance(obj, Ant)]
        if ant and self.random.random() <= spider_hit_chance:  # If there are any ant present and if the spider hits
            ant_to_eat = self.random.choice(ant)#Eats the ant, we don't give the spider any energy since it is not a usefull energy source for them
            ant_to_eat.remove()#Ant gets deleted
            return
        
        # frog = [obj for obj in self.cell.agents if isinstance(obj, Frog)]
        # if frog and self.random.random() <= self.symbiotic_property:  # If there are any frog present
        #     frog_to_eat = self.random.choice(frog)
        #     self.energy += 1 #might want to change this value later on
        #     frog_to_eat.remove()
        
    def move(self): #Here we define the movement of the spider
        spider_to_ant_chance = 0.50 #This is the chance of the spider going to a cell with an ant on it on purpose, this is again to promote the frogs eating the ants
        """Move to a neighboring cell, preferably one with frog."""
        cells_with_snake = self.cell.neighborhood.select( #Selects a cell with a snake
            lambda cell: any(isinstance(obj, Snake) for obj in cell.agents)
        )
        cells_with_ant = self.cell.neighborhood.select( #Selects a cell with an ant
            lambda cell: any(isinstance(obj, Ant) for obj in cell.agents)
        )
        # cells_with_frog = self.cell.neighborhood.select(  
        #     lambda cell: any(isinstance(obj, Frog) for obj in cell.agents)
        # )
        explore_factor = 15.0 #This is the exploration value for the spider, change this value if desired, larger -> more tendency to move away from nest
        target_cells = None #Set target cell
        if len(cells_with_snake) > 0: #First check for snakes since this is the best food source
            target_cells = cells_with_snake
        elif self.random.random() <= spider_to_ant_chance and len(cells_with_ant) > 0: #Else check for ants, with a check to see if it purposefully moves to the ant
            target_cells = cells_with_ant
        # elif self.random.random() <= self.symbiotic_property and len(cells_with_frog) > 0:
        #     target_cells = cells_with_frog
        elif math.dist(self.cell.coordinate, self.get_nest_center()) / explore_factor > self.random.random(): #if it doesn't see any agent nearby it has a chance to move back to the center of its nest based on the exploration value
            target_cells = self.determine_cells_to_return()
        else:
            target_cells = self.cell.neighborhood#else go to any nearby cell
            
        self.cell = target_cells.select_random_cell()
    
    def get_nest_center(self): #To find the center of the nest
        
        return (self.nest[1][0] + 1, self.nest[1][1] + 1) # This assumes the nest location + 1 is the center of the nest, should be dynamically retrieved based on the nest_size

    def determine_cells_to_return(self): #To go back to the nest
        destination = self.get_nest_center() #receives the center of the nest
        current_location = self.cell.coordinate #receives current coordinates
        delta = (destination[0] - current_location[0] , destination[1] - current_location[1]) # Use delta to estimate direction of nest
        
        neighbors_cells = self.cell.neighborhood.cells        
        target_cells = None
        
        #We use if statements to make the spider able to return to the nest based on its delta and the indexing of the nest cells
        # Neighborhood indexing for cursed code:
        # 2 4 7
        # 1 X 6
        # 0 3 5
        if (delta[0] == 0 and delta[1] == 0) or current_location[0] == 0 or current_location[0] == self.model.width-1 or current_location[1] == 0 or current_location[1] == self.model.height-1:  
            # Else we get delta (0, 0) meaning we are located at the nest or if we are at the boundary, just load new neighbors
            target_cells = CellCollection(neighbors_cells, random=self.random)                       
        elif delta[0] < 0 and delta[1] < 0: # LEFT DOWN
            target_cells = CellCollection([neighbors_cells[0], neighbors_cells[1], neighbors_cells[3]], random=self.random)#it choses out of 3 different directions all of which preparing to go to the nest, in this case the spider is able to move down left and left down
        elif delta[0] < 0 and delta[1] > 0: # LEFT UP
            target_cells = CellCollection([neighbors_cells[1], neighbors_cells[2], neighbors_cells[4]], random=self.random)
        elif delta[0] > 0 and delta[1] > 0: # RIGHT UP           
            target_cells = CellCollection([neighbors_cells[4], neighbors_cells[7], neighbors_cells[6]], random=self.random)
        elif delta[0] > 0 and delta[1] < 0: # RIGHT DOWN
            target_cells = CellCollection([neighbors_cells[6], neighbors_cells[5], neighbors_cells[3]], random=self.random)
        elif delta[0] == 0 and delta[1] > 0: # UP
            target_cells = CellCollection([neighbors_cells[2], neighbors_cells[4], neighbors_cells[7]], random=self.random)
        elif delta[0] == 0 and delta[1] < 0: # DOWN
            target_cells = CellCollection([neighbors_cells[0], neighbors_cells[5], neighbors_cells[3]], random=self.random)        
        elif delta[0] < 0 and delta[1] == 0: # LEFT
            target_cells = CellCollection([neighbors_cells[0], neighbors_cells[1], neighbors_cells[2]], random=self.random)
        elif delta[0] > 0 and delta[1] == 0: # RIGHT
            target_cells = CellCollection([neighbors_cells[7], neighbors_cells[6], neighbors_cells[5]], random=self.random) 
        return target_cells
        
    def reproduce(self): #The reproduction of the snakes to only allow eggs to spawn in nests
        if "nest" not in self.model.get_zone_at(self.cell.coordinate[0], self.cell.coordinate[1]):
            return#Return if not in nest
        
        cells_with_egg = self.cell.get_neighborhood(radius=2).select( #Checks what cells have eggs in them 
            lambda cell: any(isinstance(obj, SpiderEgg) for obj in cell.agents)
        )
        
        eggs_in_nest_amount = len(cells_with_egg.cells) #Checks the amount of cells with eggs in them
        max_eggs_in_nest = 16 #Sets max amount of eggs in the nest to 16 
        
        if eggs_in_nest_amount < max_eggs_in_nest and len([egg for egg in self.cell.agents if isinstance(egg, SpiderEgg)]) == 0: #checks if it can lay an egg and lays one if it may
            SpiderEgg.create_agents(
                self.model,
                1,
                cell=self.cell,
                nest = self.nest, #Sets the nest of the new agent so the spider that hatches has the same nest 
                symbiotic_property = self.get_symbiotic_property_for_reproduce() #Give a symbiotic value with it
                )

class Ant(Animal): #The ant class inherits from the Animal class
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0):
        super().__init__(model, initial_energy, p_reproduce, energy_from_food, mutation_chance, mutation_effectiveness, cell, symbiotic_property)
    
    def move(self): #it's movements are default and only changes when it finds a cell with an egg in it
        cells_with_egg = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, SpiderEgg) for obj in cell.agents)#if there is an egg it goes to it
        )
        target_cells = (
            cells_with_egg if len(cells_with_egg) > 0 else self.cell.neighborhood
        )
        self.cell = target_cells.select_random_cell()
        #not that this class has no feed function since it only destroys spider eggs which is defined in the spideregg class section
    
class Snake(Animal):#Snake class also inherits from Animal
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0):
        super().__init__(model, initial_energy, p_reproduce, energy_from_food, mutation_chance, mutation_effectiveness, cell, symbiotic_property)
    
    def feed(self): #It eats any frog that is present
        """If possible, eat a frog at current location."""
        frog = [obj for obj in self.cell.agents if isinstance(obj, Frog)]
        if frog:  # If there are any frog present
            frog_to_eat = self.random.choice(frog)
            self.energy += self.energy_from_food #Receives energy
            frog_to_eat.remove() #Removes the frog

    def move(self): #It moves to cells with frogs
        """Move to a neighboring cell, preferably one with frog."""
        cells_with_frogs = self.cell.neighborhood.select( #checks for frogs
            lambda cell: any(isinstance(obj, Frog) for obj in cell.agents)
        )
        target_cells = (#moves to frog if possible
            cells_with_frogs if len(cells_with_frogs) > 0 else self.cell.neighborhood
        )
        self.cell = target_cells.select_random_cell()

class Frog(Animal):#Frog inherits from animal and has a costume symbiotic property function
    def __init__(self, model, initial_energy=50, p_reproduce=0.04, energy_from_food=50, mutation_chance=0.5, mutation_effectiveness=0.1, cell=None, symbiotic_property=0):
        super().__init__(model, initial_energy, p_reproduce, energy_from_food, mutation_chance, mutation_effectiveness, cell, symbiotic_property)
        self.symbiotic_property = self.random.random()*2-1

    def feed(self):
        """If possible, eat an ant at current location."""
        ant = [obj for obj in self.cell.agents if isinstance(obj, Ant)]
        if ant:  # If there are any ant present
            ant_to_eat = self.random.choice(ant)
            self.energy += self.energy_from_food #gets energy
            ant_to_eat.remove() #removes ant
    
    def move(self):
        # Check radius=1 for ants which is a normal mooregrid 
        neighbors_r1 = self.cell.get_neighborhood(radius=1).cells
        cells_with_ant = [
            cell for cell in neighbors_r1
            if any(isinstance(obj, Ant) for obj in cell.agents)
        ]

        if cells_with_ant:#if there is a cell with ant always choose that one
            self.cell = self.random.choice(cells_with_ant)
            return


        # If there are no ants the frog will roll symbiotic chance 
        if self.symbiotic_property > 0: #if the symbiotic property value is positive it tries to go to a spider
            if self.random.random() < self.symbiotic_property:

                # With radius=2 the frog uses neighborhood for spider search
                neighbors_r2 = self.cell.get_neighborhood(radius=2).cells

                # Cells containing spiders checks for spiders
                spider_cells = [
                    cell for cell in neighbors_r2
                    if any(isinstance(obj, Spider) for obj in cell.agents)
                ]

                if len(spider_cells) > 0: 
                    fx, fy = self.cell.coordinate

                    def dist(cell):
                        x, y = cell.coordinate
                        return max(abs(x - fx), abs(y - fy))  # Checks to go to spider cell

                    target_spider_cell = spider_cells[0]
                    sx, sy = target_spider_cell.coordinate

                    # Moves towards spider with 1 step
                    step_x = fx + (1 if sx > fx else -1 if sx < fx else 0)
                    step_y = fy + (1 if sy > fy else -1 if sy < fy else 0)

                    # Finds the cell that corresponds to that coordinate
                    target_neighbor = next(
                        (c for c in neighbors_r1 if c.coordinate == (step_x, step_y)),
                        None
                    )

                    # Moves if the step is valid
                    if target_neighbor:
                        self.cell = target_neighbor
                        return
        elif self.symbiotic_property < 0:
            if self.random.random() < (self.symbiotic_property * -1.0):#if the symbiotic property value is negative it tries to run from the spider

                # radius=2 neighborhood for spider search
                neighbors_r2 = self.cell.get_neighborhood(radius=2).cells

                # Cells containing spiders
                spider_cells = [
                    cell for cell in neighbors_r2
                    if any(isinstance(obj, Spider) for obj in cell.agents)
                ]

                if len(spider_cells) > 0:
                    fx, fy = self.cell.coordinate

                    def dist(cell):
                        x, y = cell.coordinate
                        return max(abs(x - fx), abs(y - fy))  # Checks to go to spider cell

                    target_spider_cell = spider_cells[0]
                    sx, sy = target_spider_cell.coordinate

                    # Moves 1 step to the spider
                    step_x = fx + (-1 if sx > fx else 1 if sx < fx else 0)
                    step_y = fy + (-1 if sy > fy else 1 if sy < fy else 0)

                    # Finds the cell that corresponds to that coordinate
                    target_neighbor = next(
                        (c for c in neighbors_r1 if c.coordinate == (step_x, step_y)),
                        None
                    )

                    # Moves if the step is valid
                    if target_neighbor:
                        self.cell = target_neighbor
                        return


     # Goes to a random neighbourhood space if nothing else qualifies 
        self.cell = self.random.choice(neighbors_r1)

class SpiderEgg(CellAgent): #This is the SpiderEgg Agent which cannot move but has some custom functions
    def __init__(self, model, nest,symbiotic_property, cell=None , hp = 5):#set hp to 5
        super().__init__(model) 
        self.cell = cell#set some parameters
        self.hp = hp
        self.egg_placement_step = self.model.steps
        self.nest = nest
        self.symbiotic_property = symbiotic_property

    def step(self): #For every stpe it checks if there is an ant nearby and receives damage if one is
        if self.is_ant_nearby():
            self.hp -= 1 #ant deals damage
        if self.hp <= 0:
            self.remove() #removes if hit points reach 0
        if self.model.steps - self.egg_placement_step >= 5 and self.hp > 0: #hatches after 5 steps
            self.hatch()
            self.remove() #removes the egg after it hatches
            pass

    def is_ant_nearby(self): #this function checks if there is an ant nearby
        nearby_ants = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Ant) for obj in cell.agents))
        return len(nearby_ants) > 0

    def hatch(self): #hatches a spider agent
        Spider.create_agents(
                self.model,
                1, 
                cell=self.cell,
                symbiotic_property = self.symbiotic_property,#gives the nest and symbiotic values to the spider
                nest =self.nest)

 