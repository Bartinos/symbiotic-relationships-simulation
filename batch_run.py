
from mesa.discrete_space import OrthogonalMooreGrid, CellAgent, FixedAgent, CellCollection
from mesa.experimental.devs import ABMSimulator
import pandas as pd
from model import SymbioticRelationshipsModel
from mesa import batch_run
import os

if __name__ == '__main__':

    params = {
        "initial_frogs": [50, 80, 100],
        "initial_snakes": [5, 15, 20, 50, 100],
        "initial_ants": [10, 30, 50, 100],
        "grid_size": [32],
        "nest_density": [0.3, 0.6, 0.75],  
    }

    # Run you parameter sweep experiment here
    resultsEXPERIMENT1_1seed = batch_run(
        SymbioticRelationshipsModel,
        parameters=params,
        iterations=1, # we now explicitly set seeds to run through
        max_steps=500,
        number_processes=None, # Use all threads
        data_collection_period=1,  # Need to collect every step
        display_progress=True,
    )

    exp1_df = pd.DataFrame(resultsEXPERIMENT1_1seed)

    if "output" not in os.listdir("."): # create output directory if not present
        os.mkdir("output")

    exp1_df.to_csv("output/exp.csv") # TODO: incremental?


