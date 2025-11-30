
from mesa.discrete_space import OrthogonalMooreGrid, CellAgent, FixedAgent, CellCollection
from mesa.experimental.devs import ABMSimulator
import pandas as pd
from model import SymbioticRelationshipsModel
from mesa import batch_run
import os

if __name__ == '__main__':

    params = {#We set our parameters
        "initial_frogs": [50, 80, 100],
        "initial_snakes": [5, 30, 100],
        "initial_ants": [10, 40, 100],
        "grid_size": [32, 64, 128],
        "nest_density": [0.6, 0.75],
        "ant_spawn_rate": [8, 12, 16, 20]
    }
    
    params2 = {
        "initial_frogs": [80, 100],
        "initial_snakes": [ 50, 100],
        "initial_ants": [ 40, 100],
        "grid_size": [32, 64, 128, 256],
        "nest_density": [0.6, 0.75],
        "ant_spawn_rate": [ 16, 20]
    }
    
    params3 = {
        "initial_frogs": [100],
        "initial_snakes": [100],
        "initial_ants": [ 40],
        "grid_size": [64],
        "nest_density": [0.75],
        "ant_spawn_rate": [16],
        "seed": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }

    # We do a parameter sweep here
    resultsEXPERIMENT1_1seed = batch_run(
        SymbioticRelationshipsModel,
        parameters=params3,
        iterations=1, # we now explicitly set seeds to run through
        max_steps=15000,
        
        data_collection_period=1,  # Need to collect every step
        number_processes=None, # We use all the threads
        display_progress=True,
    )

    exp1_df = pd.DataFrame(resultsEXPERIMENT1_1seed)

    if "output" not in os.listdir("."): # create output directory if not present
        os.mkdir("output")

    exp1_df.to_csv("output/exp_sym_specific_1_seeds.csv") # TODO: incremental?


